"""FastAPI dependencies for resolving the authenticated user."""

from __future__ import annotations

import uuid
from typing import Annotated

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.auth.jwt import decode_access_token
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _extract_token_from_request(request: Request) -> str | None:
    """Extract token from Authorization header or HTTP-only auth cookie."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return token

    cookie_token = request.cookies.get(settings.jwt_cookie_name)
    if cookie_token:
        return cookie_token

    return None


async def get_optional_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """Resolve current user if a valid token exists, otherwise return None."""
    token = _extract_token_from_request(request)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id_raw = payload.get("sub")
    if not user_id_raw:
        return None

    try:
        user_id = uuid.UUID(str(user_id_raw))
    except (ValueError, TypeError):
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


async def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    """Enforce that an authenticated user is present. Raises 401 if not."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
