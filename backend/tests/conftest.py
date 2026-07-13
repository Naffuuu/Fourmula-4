import os

os.environ.setdefault("APP_SECRET_KEY", "test-secret-key")
os.environ.setdefault("ROLL_NUMBER_PEPPER", "test-pepper")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.models import Base


@pytest_asyncio.fixture
async def test_engine():
    """A fresh in-memory SQLite DB per test — fast, no external MySQL needed
    for the test suite. StaticPool keeps the same in-memory DB alive across
    the async connections FastAPI's dependency injection opens per request."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine):
    from app.main import app

    session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"
