"""
app/database/init_db.py
────────────────────────
Database initialisation helper.
Creates all tables and runs startup checks.
Used during app lifespan startup.
"""

from __future__ import annotations

from sqlalchemy import text

from app.core.logging import get_logger
from app.database.base import Base
from app.database.session import engine

logger = get_logger(__name__)


async def init_db() -> None:
    """
    Initialise the database:
    1. Verify connectivity
    2. Create all tables that don't exist (safe for development)

    NOTE: In production, use Alembic migrations instead of create_all().
    This function is safe to call repeatedly (idempotent).
    """
    logger.info("Initialising database connection...")

    async with engine.begin() as conn:
        # Verify we can reach the database
        result = await conn.execute(text("SELECT 1"))
        result.fetchone()
        logger.info("Database connection verified.")

        # Import all models so they are registered on the Base metadata
        # before create_all is called. This import chain must include
        # every model module to ensure the table exists.
        import app.models  # noqa: F401 — side-effect import registers models

        # Only create tables in development; production uses Alembic
        from app.core.config import get_settings

        settings = get_settings()
        if settings.is_development:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created (development mode).")

    logger.info("Database initialisation complete.")


async def close_db() -> None:
    """Dispose the connection pool gracefully on application shutdown."""
    logger.info("Closing database connection pool...")
    await engine.dispose()
    logger.info("Database connection pool closed.")
