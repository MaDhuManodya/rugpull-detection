"""
app/database/session.py
────────────────────────
Async SQLAlchemy 2.0 engine and session factory.
Provides the get_db dependency for FastAPI route injection.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# ── Engine ────────────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,  # test connections before use (prevents stale connections)
    echo=settings.debug,  # log SQL statements in debug mode
    echo_pool=False,
)

# ── Session Factory ───────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session per request.
    The session is automatically committed on success or rolled back on error.

    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_raw_session() -> AsyncSession:
    """
    Return a raw AsyncSession for use outside of FastAPI request context.
    Caller is responsible for committing/rolling back and closing.

    Usage (in Celery tasks, scripts, etc.):
        async with get_raw_session() as session:
            ...
    """
    return AsyncSessionLocal()
