"""
app/api/v1/endpoints/health.py
────────────────────────────────
Health check endpoint.
GET /api/v1/health — Returns system status, DB connectivity, and version info.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

_startup_time = datetime.now(tz=timezone.utc)


@router.get(
    "",
    summary="Health Check",
    description="Returns API health status, database connectivity, and system information.",
    response_model=dict[str, Any],
)
async def health_check(db: DatabaseDep) -> dict[str, Any]:
    """
    System health check endpoint.

    Verifies:
    - API is running
    - Database is reachable
    - Returns version and uptime info
    """
    db_status = "healthy"
    db_error: str | None = None

    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "unhealthy"
        db_error = str(exc)
        logger.error("Health check: database unreachable", error=str(exc))

    uptime_seconds = (
        datetime.now(tz=timezone.utc) - _startup_time
    ).total_seconds()

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "api": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "uptime_seconds": round(uptime_seconds, 2),
        },
        "database": {
            "status": db_status,
            "error": db_error,
        },
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
