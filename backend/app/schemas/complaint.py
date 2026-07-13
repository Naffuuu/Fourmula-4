from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.complaint import ComplaintCategory, ComplaintStatus


class ComplaintCreate(BaseModel):
    category: ComplaintCategory
    description: str = Field(min_length=10, max_length=4000)
    # Set after upload via the /complaints/evidence endpoint; not accepted as
    # an arbitrary client-supplied URL string to avoid SSRF/spoofed evidence.
    evidence_upload_id: str | None = None


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: ComplaintCategory
    description: str
    evidence_url: str | None
    status: ComplaintStatus
    created_at: datetime


class StrikeSummary(BaseModel):
    warning_level: int
    strike_count: int
    strike_max: int = 3
