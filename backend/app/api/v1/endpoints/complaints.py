from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.complaint import Complaint, ComplaintStatus, Strike
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintCreate, ComplaintOut, StrikeSummary
from app.services.anonymity_service import anonymize_submitter
from app.services.exif_service import strip_exif_and_store

router = APIRouter(prefix="/complaints", tags=["whistleblower"])

STRIKE_MAX = 3

# In-memory holding area mapping an upload id -> stored evidence URL, so the
# two-step "upload evidence, then submit complaint referencing it" flow
# doesn't require a half-created Complaint row. Fine for hackathon scale;
# a real deployment would use a short-lived DB table or object-store
# presigned-upload pattern instead.
_pending_evidence: dict[str, str] = {}


@router.post("/evidence", status_code=status.HTTP_201_CREATED)
async def upload_evidence(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Strips EXIF metadata before persisting (see exif_service.py) so a
    photo's embedded GPS/device data can't re-identify the submitter."""
    import uuid

    url = await strip_exif_and_store(file)
    upload_id = str(uuid.uuid4())
    _pending_evidence[upload_id] = url
    return {"upload_id": upload_id, "evidence_url": url}


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def submit_complaint(
    payload: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence_url = None
    if payload.evidence_upload_id:
        evidence_url = _pending_evidence.pop(payload.evidence_upload_id, None)
        if evidence_url is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown or expired evidence upload.")

    complaint = Complaint(
        category=payload.category,
        description=payload.description,
        evidence_url=evidence_url,
        # The one line that matters: we never write current_user.id anywhere
        # on this row. See anonymity_service.py for why this is safe even if
        # the DB is later compromised.
        anonymized_submitter_ref=anonymize_submitter(current_user.id),
    )
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)
    return ComplaintOut.model_validate(complaint)


@router.get("", response_model=list[ComplaintOut])
async def list_complaints(
    current_user: User = Depends(require_roles(UserRole.second_captain, UserRole.third_captain)),
    db: AsyncSession = Depends(get_db),
):
    """Captains can review complaints for triage, but note this list never
    exposes who filed what — only category/description/status."""
    result = await db.execute(select(Complaint).order_by(Complaint.created_at.desc()))
    return [ComplaintOut.model_validate(c) for c in result.scalars().all()]


@router.post("/{complaint_id}/strike", response_model=StrikeSummary, status_code=status.HTTP_201_CREATED)
async def issue_strike(
    complaint_id: str,
    current_user: User = Depends(require_roles(UserRole.second_captain, UserRole.third_captain)),
    db: AsyncSession = Depends(get_db),
):
    complaint = await db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found.")

    current_max_result = await db.execute(select(func.max(Strike.warning_level)))
    current_max = current_max_result.scalar() or 0
    next_level = min(current_max + 1, STRIKE_MAX)

    strike = Strike(complaint_id=complaint.id, warning_level=next_level)
    complaint.status = ComplaintStatus.resolved
    db.add(strike)
    await db.commit()

    return StrikeSummary(warning_level=next_level, strike_count=next_level, strike_max=STRIKE_MAX)
