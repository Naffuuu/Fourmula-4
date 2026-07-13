from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.complaint import Complaint, ComplaintStatus, Strike
from app.models.misc import SosAlert, SosStatus, SyllabusRequest
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

STRIKE_MAX = 3


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Strike count: highest warning_level ever issued, capped at STRIKE_MAX.
    # (A school-wide counter for the hackathon demo — a real deployment would
    # scope this per-target-teacher rather than globally.)
    # Strike count now reflects the total number of open/under-review complaints
    # rather than only captain-issued warning strikes. This gives users immediate
    # feedback after filing a report.
    complaint_result = await db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.status.in_([ComplaintStatus.open, ComplaintStatus.under_review]))
    )
    strike_count = min(complaint_result.scalar() or 0, STRIKE_MAX)

    open_sos_result = await db.execute(select(func.count()).select_from(SosAlert).where(SosAlert.status == SosStatus.active))
    open_sos_alerts = open_sos_result.scalar() or 0

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_complaints_result = await db.execute(
        select(Complaint).where(Complaint.created_at >= week_ago)
    )
    recent_complaints = recent_complaints_result.scalars().all()

    categories = sorted({c.category.value.replace("_", " ").title() for c in recent_complaints})

    # Countdown to the soonest upcoming syllabus test_date stashed in a
    # syllabus request's study_plan_json, if any exist.
    days_until_test = None
    latest_request_result = await db.execute(
        select(SyllabusRequest).order_by(SyllabusRequest.created_at.desc()).limit(1)
    )
    latest_request = latest_request_result.scalar_one_or_none()
    if latest_request and latest_request.study_plan_json:
        test_date_str = latest_request.study_plan_json.get("test_date")
        if test_date_str:
            test_date = date.fromisoformat(test_date_str)
            days_until_test = max((test_date - date.today()).days, 0)
            next_test_date = test_date.isoformat()

    return DashboardSummary(
        strike_count=strike_count,
        strike_max=STRIKE_MAX,
        open_sos_alerts=open_sos_alerts,
        recent_complaints_count=len(recent_complaints),
        recent_complaint_categories=categories,
        days_until_test=days_until_test,
        next_test_date=next_test_date,
    )
