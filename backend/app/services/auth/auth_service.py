from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User


async def get_or_create_dev_user(
    db: AsyncSession,
    email: str = "dev@cybercase.local",
    name: str = "Developer User",
) -> User:
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
            email_verified_at=datetime.now(UTC),
            name=name,
            oauth_provider="local_dev",
            oauth_subject_id=subject_id,
        )
        db.add(user)
    else:
        if name and user.name != name:
            user.name = name

    await db.commit()
    await db.refresh(user)
    return user


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
    "build_auth_cookie_options",
    "get_or_create_dev_user",
]
