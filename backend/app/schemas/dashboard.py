from pydantic import BaseModel


class DashboardSummary(BaseModel):
    strike_count: int
    strike_max: int = 3
    open_sos_alerts: int
    recent_complaints_count: int
    recent_complaints_capacity: int = 10
    recent_complaint_categories: list[str]
    days_until_test: int | None = None
    next_test_date: str | None = None
