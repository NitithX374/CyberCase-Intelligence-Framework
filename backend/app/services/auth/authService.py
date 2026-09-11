"""Authentication service for managing user persistence and token generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.models.user import User
from app.services.auth.oauthClients import OAuthUserProfile
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_create_oauth_user(
    db: AsyncSession,
    profile: OAuthUserProfile,
) -> User:
    """Find existing user by (provider, subject_id) or email, or create a new user."""
    query = select(User).where(
        User.oauth_provider == profile.provider,
        User.oauth_subject_id == profile.subject_id,
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    email = profile.email.strip().lower()
    if user is None:
        existing = await db.scalar(select(User).where(User.email == email))
        if existing is not None:
            raise HTTPException(409, "This email already has an account. Use its original sign-in method.")

    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            email_verified_at=datetime.now(timezone.utc),
            name=profile.name,
            avatar_url=profile.avatar_url,
            oauth_provider=profile.provider,
            oauth_subject_id=profile.subject_id,
        )
        db.add(user)
    else:
        if profile.name and user.name != profile.name:
            user.name = profile.name
        if profile.avatar_url and user.avatar_url != profile.avatar_url:
            user.avatar_url = profile.avatar_url

    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_dev_user(
    db: AsyncSession,
    email: str = "dev@cybercase.local",
    name: str = "Developer User",
    avatar_url: str | None = None,
) -> User:
    """Create or retrieve a developer user for local development and test runs."""
    profile = OAuthUserProfile(
        provider="local_dev",
        subject_id=f"dev_{email}",
        email=email,
        name=name,
        avatar_url=avatar_url,
    )
    return await get_or_create_oauth_user(db, profile)


def build_auth_cookie_options() -> dict[str, Any]:
    """Build standardized Set-Cookie options for JWT session cookie."""
    return {
        "key": settings.jwt_cookie_name,
        "httponly": True,
        "samesite": "lax",
        "secure": settings.jwt_cookie_secure,
        "max_age": settings.jwt_expire_minutes * 60,
        "path": "/",
    }


buildAuthCookieOptions = build_auth_cookie_options
getOrCreateDevUser = get_or_create_dev_user
getOrCreateOAuthUser = get_or_create_oauth_user

__all__ = [
    "buildAuthCookieOptions",
    "build_auth_cookie_options",
    "getOrCreateDevUser",
    "getOrCreateOAuthUser",
    "get_or_create_dev_user",
    "get_or_create_oauth_user",
]
