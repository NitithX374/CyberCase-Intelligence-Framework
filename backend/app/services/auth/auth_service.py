"""Authentication service for managing user persistence and token generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_create_dev_user(
    db: AsyncSession,
    email: str = "dev@cybercase.local",
    name: str = "Developer User",
    avatar_url: str | None = None,
) -> User:
    """Create or retrieve a developer user for local development and test runs."""
    normalized_email = email.strip().lower()
    subject_id = f"dev_{normalized_email}"
    query = select(User).where(
        User.oauth_provider == "local_dev",
        User.oauth_subject_id == subject_id,
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=normalized_email,
            email_verified_at=datetime.now(timezone.utc),
            name=name,
            avatar_url=avatar_url,
            oauth_provider="local_dev",
            oauth_subject_id=subject_id,
        )
        db.add(user)
    else:
        if name and user.name != name:
            user.name = name
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(user)
    return user


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


__all__ = [
    "build_auth_cookie_options",
    "get_or_create_dev_user",
]
