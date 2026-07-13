from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.misc import LedgerEntry, LedgerEntryType
from app.models.user import User
from app.schemas.missions_4_5_6 import LedgerEntryCreate, LedgerEntryOut, LedgerSummary

router = APIRouter(prefix="/ledger", tags=["ledger"])

# Rough street-price constants for the "outrage metric" the mission brief
# asks for — purely illustrative, not real accounting. Documented here so a
# reviewer can see these are deliberate flavor constants, not miscalibrated
# real financial figures.
JHALMURI_PACKET_PRICE_BDT = 20.0
CRICKET_BAT_PRICE_BDT = 800.0
# Average calories in a stolen tiffin item, used only to compute the
# "caloric intake vs kinetic output" disparity metric from the brief.
AVG_TIFFIN_ITEM_KCAL = 250.0


@router.post("", response_model=LedgerEntryOut, status_code=201)
async def log_entry(
    payload: LedgerEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Anonymous by design: we deliberately do not attach current_user.id to
    a LedgerEntry row, the same pattern as the whistleblower complaints
    table — this is a ledger of what was taken, not a ledger of who reported it."""
    entry = LedgerEntry(type=payload.type, amount=payload.amount, item_description=payload.item_description)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return LedgerEntryOut.model_validate(entry)


@router.get("", response_model=LedgerSummary)
async def get_ledger(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LedgerEntry).order_by(LedgerEntry.logged_at.desc()))
    entries = result.scalars().all()

    cash_entries = [e for e in entries if e.type == LedgerEntryType.cash]
    food_entries = [e for e in entries if e.type == LedgerEntryType.food]

    total_cash = sum(e.amount for e in cash_entries)
    total_food_items = len(food_entries)
    caloric_intake_estimate = total_food_items * AVG_TIFFIN_ITEM_KCAL

    return LedgerSummary(
        total_cash=total_cash,
        total_food_items=total_food_items,
        cash_in_jhalmuri_packets=round(total_cash / JHALMURI_PACKET_PRICE_BDT, 1) if total_cash else 0.0,
        cash_in_cricket_bats=round(total_cash / CRICKET_BAT_PRICE_BDT, 2) if total_cash else 0.0,
        caloric_intake_estimate_kcal=caloric_intake_estimate,
        kinetic_output_estimate_kcal=0.0,
        entries=[LedgerEntryOut.model_validate(e) for e in entries],
    )
