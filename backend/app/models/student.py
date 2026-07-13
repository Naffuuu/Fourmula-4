import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Student(Base):
    """Roster entry used by the seating planner (Mission 2). Distinct from
    `User` because a roster can be uploaded in bulk (name/roll/height) before
    every student necessarily has a login — a captain builds the seating
    chart from the roster, not from logged-in accounts."""

    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    roll_number_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    # e.g. {"front_row_required": true, "reason": "vision"} — hard constraints
    # the seating algorithm must respect regardless of height ordering.
    seat_constraints: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    role: Mapped[str] = mapped_column(String(30), default="student", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
