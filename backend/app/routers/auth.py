"""Authentication API router for registration, login, user profile, and dev-mode login."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    DevLoginRequest,
    PasswordLoginRequest,
    RegisterRequest,
    UserRead,
)
from app.services.auth.auth_service import (
    build_auth_cookie_options,
    get_or_create_dev_user,
)
from app.services.auth.dependencies import get_current_user, get_optional_user
from app.services.auth.jwt import create_access_token
from app.services.auth.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


def start_password_session(user: User, response: Response) -> UserRead:
    token = create_access_token(user.id, user.email)
    response.set_cookie(value=token, **build_auth_cookie_options())
    response.headers["Cache-Control"] = "no-store"
    return UserRead.model_validate(user)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    email = str(payload.email).lower()
    name = payload.name.strip()
    if not name:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Display name is required")
    user = User(
        id=uuid.uuid4(),
        email=email,
        name=name,
        oauth_provider="password",
        oauth_subject_id=email,
        password_hash=await run_in_threadpool(hash_password, payload.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An account already exists for this email") from error
    await db.refresh(user)
    return start_password_session(user, response)


@router.post("/login", response_model=UserRead)
async def login(
    payload: PasswordLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not user.password_hash:
        await run_in_threadpool(hash_password, payload.password)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not await run_in_threadpool(verify_password, payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return start_password_session(user, response)


@router.get("/me", response_model=UserRead, summary="Get current authenticated user")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Return user profile for the currently logged-in user."""
    return UserRead.model_validate(current_user)


@router.get("/session", response_model=UserRead | None, summary="Get optional session user")
async def get_session(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> UserRead | None:
    """Return user profile if logged in, or null without 401 challenge."""
    if user is None:
        return None
    return UserRead.model_validate(user)


@router.post("/logout", summary="Log out user and clear session cookie")
async def logout(response: Response) -> dict[str, str]:
    """Clear session cookie and log out."""
    response.delete_cookie(
        key=settings.jwt_cookie_name,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}


@router.post(
    "/dev-login",
    response_model=AuthTokenResponse,
    summary="Local developer login for testing",
)
async def dev_login(
    payload: DevLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    """Simulate login locally for development and automated testing."""
    if not settings.auth_dev_login_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer login is disabled in this environment",
        )

    user = await get_or_create_dev_user(
        db,
        email=payload.email,
        name=payload.name,
        avatar_url=payload.avatar_url,
    )
    token = create_access_token(user_id=user.id, email=user.email)

    cookie_opts = build_auth_cookie_options()
    response.set_cookie(value=token, **cookie_opts)

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
        user=UserRead.model_validate(user),
    )
