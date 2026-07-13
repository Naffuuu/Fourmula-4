from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.misc import SeatingLayout
from app.models.user import User
from app.schemas.seating import SeatAssignment, SeatingRequest, SeatingResponse
from app.services.seating_algorithm import generate_seating

router = APIRouter(prefix="/seating", tags=["seating"])


@router.post("/generate", response_model=SeatingResponse, status_code=201)
async def generate_seating_layout(
    payload: SeatingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    roster_dicts = [
        {
            "name": s.name,
            "roll_number": s.roll_number,
            "height_cm": s.height_cm,
            "constraints": s.constraints.model_dump() if s.constraints else None,
        }
        for s in payload.roster
    ]

    plan = generate_seating(
        roster=roster_dicts,
        rows=payload.rows,
        cols=payload.cols,
        podium_position=payload.podium_position,
        kuddus_seat=payload.kuddus_seat,
        aisle_columns=payload.aisle_columns,
    )

    layout = SeatingLayout(
        grid_config_json={
            "rows": payload.rows,
            "cols": payload.cols,
            "podium_position": list(payload.podium_position),
            "kuddus_seat": list(payload.kuddus_seat),
            "aisle_columns": payload.aisle_columns,
            "grid": plan.grid,
            "average_sightline_score": plan.average_sightline_score,
        }
    )
    db.add(layout)
    await db.commit()
    await db.refresh(layout)

    grid_out = [[SeatAssignment(**cell) for cell in row] for row in plan.grid]
    return SeatingResponse(
        layout_id=layout.id,
        grid=grid_out,
        average_sightline_score=plan.average_sightline_score,
        notes=plan.notes,
    )
