from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.misc import LedgerEntryType, SosStatus


# ---- Mission 4: Ledger ----
class LedgerEntryCreate(BaseModel):
    type: LedgerEntryType
    amount: float = Field(gt=0)
    item_description: str = Field(min_length=1, max_length=255)


class LedgerEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: LedgerEntryType
    amount: float
    item_description: str
    logged_at: datetime


class LedgerSummary(BaseModel):
    total_cash: float
    total_food_items: int
    # amount / a jhalmuri packet's average street price, purely for the
    # "outrage metric" the mission brief asks for — not real accounting.
    cash_in_jhalmuri_packets: float
    cash_in_cricket_bats: float
    caloric_intake_estimate_kcal: float
    kinetic_output_estimate_kcal: float = 0.0
    entries: list[LedgerEntryOut]


# ---- Mission 5: SOS ----
class SosAlertCreate(BaseModel):
    location: str = Field(min_length=1, max_length=120)


class SosAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    location: str
    status: SosStatus
    triggered_at: datetime
    resolved_at: datetime | None = None


# ---- Mission 6: Fact-checker ----
class FactCheckRequest(BaseModel):
    claim: str = Field(min_length=3, max_length=500)


class FactCheckResult(BaseModel):
    verdict: bool
    confidence: float = Field(ge=0, le=1)
    matched_rule_text: str
    source_section: str
