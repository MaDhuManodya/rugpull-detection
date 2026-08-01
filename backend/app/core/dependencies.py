"""
app/core/dependencies.py
─────────────────────────
Shared FastAPI dependency-injection functions.
These are used across all API endpoints via Depends().
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException
from app.core.security import decode_access_token
from app.database.session import get_db

# ── Re-export DB dependency for clean imports ─────────────────
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]

# ── Security scheme ───────────────────────────────────────────
_bearer_scheme = HTTPBearer(auto_error=False)

BearerToken = Annotated[
    HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
]


async def get_current_user_id(credentials: BearerToken) -> str:
    """
    Extract and validate the JWT bearer token.
    Returns the user ID (subject) from the token payload.

    Raises:
        HTTPException 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload["sub"]
        return user_id
    except AuthenticationException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUserDep = Annotated[str, Depends(get_current_user_id)]


async def get_optional_user_id(credentials: BearerToken) -> str | None:
    """
    Same as get_current_user_id but returns None for unauthenticated requests.
    Useful for endpoints that are accessible to both authenticated and
    anonymous users (e.g., public read endpoints).
    """
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return payload["sub"]
    except AuthenticationException:
        return None


OptionalUserDep = Annotated[str | None, Depends(get_optional_user_id)]
