import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SeatingLayout(Base):
    __tablename__ = "seating_layouts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Full grid: rows/cols, per-seat student ref, podium position, Kuddus seat,
    # and the sightline score per column — see seating_algorithm.py.
    grid_config_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SyllabusRequest(Base):
    __tablename__ = "syllabus_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    filtered_topics_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    study_plan_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LedgerEntryType(str, enum.Enum):
    cash = "cash"
    food = "food"


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type: Mapped[LedgerEntryType] = mapped_column(Enum(LedgerEntryType), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    item_description: Mapped[str] = mapped_column(String(255), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SosStatus(str, enum.Enum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"


class SosAlert(Base):
    __tablename__ = "sos_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[SosStatus] = mapped_column(Enum(SosStatus), nullable=False, default=SosStatus.active)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RulebookEntry(Base):
    __tablename__ = "rulebook_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON list[float] — kept as JSON rather than a vector column so this runs
    # on stock MySQL without a vector extension; embedding_service.py does the
    # cosine similarity in Python at query time (fine at seed-data scale).
    embedding_vector: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source_section: Mapped[str] = mapped_column(String(120), nullable=False)
