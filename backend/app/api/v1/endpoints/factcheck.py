from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.misc import RulebookEntry
from app.models.user import User
from app.schemas.missions_4_5_6 import FactCheckRequest, FactCheckResult
from app.services.embedding_service import RulebookIndex, best_match_openai

router = APIRouter(prefix="/factcheck", tags=["factchecker"])
settings = get_settings()

# A verdict this confident-or-below is treated as "insufficient evidence" and
# reported as FALSE with a low-confidence caveat rather than a false-positive
# TRUE — the seeded rulebook is small, so weak matches are common and should
# read as "not corroborated" rather than confidently wrong.
CONFIDENCE_FLOOR = 0.15


@router.post("", response_model=FactCheckResult)
async def fact_check(
    payload: FactCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RulebookEntry))
    rules = [{"rule_text": r.rule_text, "source_section": r.source_section} for r in result.scalars().all()]

    if not rules:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rulebook has not been seeded yet — run the seed script.",
        )

    if settings.openai_api_key:
        match = await best_match_openai(payload.claim, rules)
    else:
        index = RulebookIndex()
        index.build(rules)
        match = index.best_match(payload.claim)

    if match is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No rulebook entries to match against.")

    rule, score = match
    verdict = score >= CONFIDENCE_FLOOR

    return FactCheckResult(
        verdict=verdict,
        confidence=round(score, 3),
        matched_rule_text=rule["rule_text"],
        source_section=rule["source_section"],
    )
