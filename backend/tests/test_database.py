"""
Database session and engine tests.

Phase 1: verifies that the engine and session factory are created
correctly. Real query tests are added in Phase 2 when models exist.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.database.session import get_engine, get_session_factory


def test_get_engine_returns_async_engine():
    engine = get_engine()
    assert isinstance(engine, AsyncEngine)


def test_get_engine_is_cached():
    """Engine must be a singleton — same object on repeated calls."""
    e1 = get_engine()
    e2 = get_engine()
    assert e1 is e2


def test_get_session_factory_is_cached():
    f1 = get_session_factory()
    f2 = get_session_factory()
    assert f1 is f2


@pytest.mark.asyncio
async def test_session_factory_yields_async_session():
    factory = get_session_factory()
    async with factory() as session:
        assert isinstance(session, AsyncSession)
