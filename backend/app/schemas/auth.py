"""Pydantic schemas for authentication and user profiles."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    avatar_url: str | None = None
    oauth_provider: str
    created_at: datetime


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class DevLoginRequest(BaseModel):
    email: str = Field(default="dev@cybercase.local", description="Developer user email")
    name: str = Field(default="Developer User", description="Display name for testing")
    avatar_url: str | None = Field(default=None, description="Optional avatar URL")


class PasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(PasswordLoginRequest):
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=12, max_length=128)
