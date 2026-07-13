from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.misc import SyllabusRequest
from app.models.user import User
from app.schemas.syllabus import StudyDay, SyllabusPlanOut, SyllabusRequestIn
from app.services.llm_service import llm_service

router = APIRouter(prefix="/syllabus", tags=["syllabus"])

SYSTEM_PROMPT = """You are an assistant that helps students cut bloated, padded
syllabi down to what is actually examinable. Given raw syllabus text, respond
with a JSON object with exactly these keys:
- "summary_bullets": array of short bullet strings summarizing the syllabus
- "examinable_topics": array of topic strings that are likely to be tested
- "dropped_topics": array of topic strings that read as padding/busywork and
  are unlikely to be examined
Respond with JSON only, no prose outside the JSON object."""


@router.post("", response_model=SyllabusPlanOut, status_code=201)
async def negotiate_syllabus(
    payload: SyllabusRequestIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await llm_service.complete_json(SYSTEM_PROMPT, f"TEST DATE: {payload.test_date}\nTEXT:\n{payload.raw_text}")

    examinable = result.get("examinable_topics", [])
    dropped = result.get("dropped_topics", [])
    summary_bullets = result.get("summary_bullets", examinable[:10])

    study_plan = _build_time_blocked_plan(examinable, payload.test_date)

    request_row = SyllabusRequest(
        raw_text=payload.raw_text,
        filtered_topics_json={"examinable": examinable, "dropped": dropped},
        study_plan_json={
            "test_date": payload.test_date.isoformat(),
            "days": [d.model_dump(mode="json") for d in study_plan],
        },
    )
    db.add(request_row)
    await db.commit()
    await db.refresh(request_row)

    return SyllabusPlanOut(
        request_id=request_row.id,
        summary_bullets=summary_bullets,
        filtered_examinable_topics=examinable,
        dropped_non_examinable_topics=dropped,
        study_plan=study_plan,
    )


def _build_time_blocked_plan(topics: list[str], test_date: date) -> list[StudyDay]:
    """Spreads topics evenly across the days remaining until the test date,
    capping at ~2.5 hours/day so the plan stays realistic rather than
    cramming everything into day one."""
    today = date.today()
    days_remaining = max((test_date - today).days, 1)
    if not topics:
        return []

    topics_per_day = max(1, -(-len(topics) // days_remaining))  # ceil division
    plan: list[StudyDay] = []
    for day_offset in range(days_remaining):
        chunk = topics[day_offset * topics_per_day : (day_offset + 1) * topics_per_day]
        if not chunk:
            break
        plan.append(
            StudyDay(
                date=today + timedelta(days=day_offset),
                topics=chunk,
                estimated_hours=min(2.5, 0.75 * len(chunk)),
            )
        )
    return plan
