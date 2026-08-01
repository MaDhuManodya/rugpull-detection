"""
alembic/env.py
──────────────
Alembic migration environment for async SQLAlchemy.
Reads DATABASE_URL_SYNC from .env for synchronous migrations.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Load the Alembic config object from alembic.ini
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Load application models ───────────────────────────────────
# Import Base first, then all models to register them on the metadata.
# ADD NEW MODEL IMPORTS HERE as they are created in Phase 2.
from app.database.base import Base  # noqa: E402

# Import all models so Base.metadata knows about them
import app.models  # noqa: F401, E402

target_metadata = Base.metadata

# ── Database URL ──────────────────────────────────────────────
def get_database_url() -> str:
    """
    Retrieve database URL from environment.
    Uses the synchronous psycopg2 URL for Alembic migrations.
    """
    url = os.environ.get("DATABASE_URL_SYNC") or os.environ.get("DATABASE_URL", "")
    # Convert async URL to sync if needed
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if not url:
        raise ValueError("DATABASE_URL_SYNC or DATABASE_URL must be set in environment.")
    return url


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL scripts)."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine (for use with asyncpg)."""
    url = get_database_url()
    connectable = create_async_engine(
        url.replace("postgresql+psycopg2://", "postgresql+asyncpg://"),
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    url = get_database_url()
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
