"""JWT encoding and decoding helpers."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from app.config import settings


def create_access_token(
    user_id: uuid.UUID,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token for the given user."""
    if len(settings.jwt_secret_key) < 32:
        raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token. Returns None on failure/expiration."""
    if len(settings.jwt_secret_key) < 32:
        raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.PyJWTError:
        return None


createAccessToken = create_access_token
decodeAccessToken = decode_access_token

__all__ = [
    "createAccessToken",
    "create_access_token",
    "decodeAccessToken",
    "decode_access_token",
]
