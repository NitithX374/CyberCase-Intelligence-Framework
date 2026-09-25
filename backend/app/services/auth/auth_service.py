from __future__ import annotations

from typing import Any

from fastapi import status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.errors import AppError
from app.models.user import User
from app.schemas.auth import PasswordLoginRequest, RegisterRequest
from app.services.auth.credentials import hash_password, verify_password

UNIQUE_VIOLATION = "23505"


async def register_user(db: AsyncSession, payload: RegisterRequest) -> User:
    name = payload.name.strip()
    if not name:
        raise AppError(
            "display_name_required",
            "Display name is required",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    user = User(
        email=str(payload.email).lower(),
        name=name,
        password_hash=await run_in_threadpool(hash_password, payload.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        if getattr(error.orig, "sqlstate", None) != UNIQUE_VIOLATION:
            raise
        raise AppError("account_exists", "An account already exists for this email") from error
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, payload: PasswordLoginRequest) -> User:
    user = await db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not user.password_hash:
        await run_in_threadpool(hash_password, payload.password)
        raise invalid_credentials()
    if not await run_in_threadpool(verify_password, payload.password, user.password_hash):
        raise invalid_credentials()
    return user


def invalid_credentials() -> AppError:
    return AppError(
        "credentials_invalid", "Incorrect email or password", status.HTTP_401_UNAUTHORIZED
    )


def build_auth_cookie_options() -> dict[str, Any]:
    return {
        "key": settings.jwt_cookie_name,
        "httponly": True,
        "samesite": "lax",
        "secure": settings.jwt_cookie_secure,
        "max_age": settings.jwt_expire_minutes * 60,
        "path": "/",
    }


__all__ = [
    "authenticate",
    "build_auth_cookie_options",
    "register_user",
]
