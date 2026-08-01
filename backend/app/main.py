"""
app/main.py
────────────
FastAPI application factory and lifespan manager.
This is the entry point for the Rugpull Detection API.

Research Project: Early Rug Pull Detection in Blockchain
Using Graph Neural Networks and Temporal Learning
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import RugpullBaseException
from app.core.logging import configure_logging, get_logger
from app.database.init_db import close_db, init_db

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """
    Application lifespan context manager.
    Runs startup logic before yielding, then shutdown logic after.
    """
    # ── Startup ───────────────────────────────────────────────
    configure_logging()
    logger.info(
        "Starting Rugpull Detection API",
        version=settings.app_version,
        env=settings.app_env,
        debug=settings.debug,
    )

    # Initialise database connection
    await init_db()
    logger.info("Application startup complete.")

    yield  # ← API is live here

    # ── Shutdown ──────────────────────────────────────────────
    logger.info("Shutting down Rugpull Detection API...")
    await close_db()
    logger.info("Shutdown complete.")


def create_application() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI instance.
    """
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Early Rug Pull Detection in Blockchain Using Graph Neural Networks "
            "and Temporal Learning — Research API"
        ),
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Exception Handlers ────────────────────────────────────
    @app.exception_handler(RugpullBaseException)
    async def rugpull_exception_handler(
        request: Request, exc: RugpullBaseException
    ) -> JSONResponse:
        logger.warning(
            "Application exception",
            error_code=exc.error_code,
            message=exc.message,
            path=str(request.url),
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception",
            path=str(request.url),
            error=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {},
            },
        )

    # ── Routers ───────────────────────────────────────────────
    from app.api.v1.router import api_v1_router

    app.include_router(api_v1_router, prefix="/api/v1")

    # ── Root endpoint ─────────────────────────────────────────
    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root() -> dict[str, Any]:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
        }

    return app


# Create the application instance
app = create_application()
