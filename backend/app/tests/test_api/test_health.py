"""
app/tests/test_api/test_health.py
───────────────────────────────────
Tests for GET /api/v1/health
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    """Health endpoint must return HTTP 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_structure(client: AsyncClient) -> None:
    """Health response must contain required keys."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert "api" in data
    assert "database" in data
    assert "timestamp" in data
    assert data["api"]["version"] is not None


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Root endpoint must return API name and version."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
