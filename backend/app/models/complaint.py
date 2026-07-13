import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ComplaintCategory(str, enum.Enum):
    tiffin_theft = "tiffin_theft"
    bribes = "bribes"
    syllabus_bloat = "syllabus_bloat"
    sports_abuse = "sports_abuse"
    seating_abuse = "seating_abuse"


class ComplaintStatus(str, enum.Enum):
    open = "open"
    under_review = "under_review"
    resolved = "resolved"
    dismissed = "dismissed"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category: Mapped[ComplaintCategory] = mapped_column(Enum(ComplaintCategory), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # k-anonymity bucket reference, NOT a user_id — see anonymity_service.py.
    # Deliberately cannot be joined back to `users` in a single query.
    anonymized_submitter_ref: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus), nullable=False, default=ComplaintStatus.open
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    strikes: Mapped[list["Strike"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")


class Strike(Base):
    __tablename__ = "strikes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("complaints.id", ondelete="CASCADE"), index=True
    )
    warning_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, or 3
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    complaint: Mapped["Complaint"] = relationship(back_populates="strikes")
