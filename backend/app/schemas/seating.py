from pydantic import BaseModel, Field


class SeatConstraint(BaseModel):
    front_row_required: bool = False
    reason: str | None = None


class RosterStudent(BaseModel):
    name: str
    roll_number: str
    height_cm: float = Field(gt=50, lt=250)
    constraints: SeatConstraint | None = None


class SeatingRequest(BaseModel):
    roster: list[RosterStudent] = Field(min_length=1)
    rows: int = Field(gt=0, le=20)
    cols: int = Field(gt=0, le=20)
    # 0-indexed (row, col) of the teacher's podium and Kuddus's fixed seat.
    podium_position: tuple[int, int]
    kuddus_seat: tuple[int, int]
    # column indices that are aisle skips (no seat placed there)
    aisle_columns: list[int] = Field(default_factory=list)


class SeatAssignment(BaseModel):
    row: int
    col: int
    student_name: str | None
    roll_number: str | None
    height_cm: float | None
    is_aisle: bool = False
    sightline_blocked: bool = False


class SeatingResponse(BaseModel):
    layout_id: str
    grid: list[list[SeatAssignment]]
    average_sightline_score: float
    notes: list[str]
