from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base — every model in app/models imports this so
    Alembic's autogenerate can discover them all via a single metadata object."""

    pass
