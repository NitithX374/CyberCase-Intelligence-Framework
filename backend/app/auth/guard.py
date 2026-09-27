from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.auth.credentials import decode_access_token
from app.config import settings
from app.database import get_db
from app.models.user import User


async def get_optional_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    token = request.cookies.get(settings.jwt_cookie_name)
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

    user = await db.scalar(select(User).where(User.id == user_id))
    await db.commit()
    return user


async def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


async def guard_browser_request(request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in settings.cors_origins_list:
            return JSONResponse({"detail": "Untrusted request origin"}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith("/api/v1/auth"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
    return response
