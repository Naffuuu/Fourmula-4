from datetime import date

from pydantic import BaseModel, Field


class SyllabusRequestIn(BaseModel):
    raw_text: str = Field(min_length=20, max_length=20000)
    test_date: date


class StudyDay(BaseModel):
    date: date
    topics: list[str]
    estimated_hours: float


class SyllabusPlanOut(BaseModel):
    request_id: str
    summary_bullets: list[str]
    filtered_examinable_topics: list[str]
    dropped_non_examinable_topics: list[str]
    study_plan: list[StudyDay]
