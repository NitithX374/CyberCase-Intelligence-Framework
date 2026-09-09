"""Authentication API router for OAuth login, callbacks, user profile, and dev-mode login."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import AuthTokenResponse, DevLoginRequest, UserRead
from app.services.auth.auth_service import (
    build_auth_cookie_options,
    get_or_create_dev_user,
    get_or_create_oauth_user,
)
from app.services.auth.dependencies import get_current_user, get_optional_user
from app.services.auth.jwt import create_access_token
from app.services.auth.oauth_clients import get_oauth_client

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login/{provider}", summary="Initiate OAuth login flow")
async def oauth_login(provider: str) -> RedirectResponse:
    """Redirect user to OAuth provider's authorization screen."""
    try:
        client = get_oauth_client(provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    state = secrets.token_urlsafe(32)
    auth_url = client.get_authorization_url(state=state)
    response = RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie("oauth_state", f"{provider}:{state}", httponly=True, secure=settings.jwt_cookie_secure, samesite="lax", max_age=600, path="/api/v1/auth")
    return response


@router.get("/callback/{provider}", summary="OAuth callback handler")
async def oauth_callback(
    provider: str,
    request: Request,
    code: str = Query(..., description="OAuth authorization code"),
    state: str | None = Query(default=None, description="OAuth state parameter"),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Exchange authorization code for user profile, issue session cookie, and redirect to frontend."""
    expected = request.cookies.get("oauth_state")
    if not state or not expected or not secrets.compare_digest(expected, f"{provider}:{state}"):
        raise HTTPException(400, "Invalid OAuth state; please start sign-in again")
    try:
        client = get_oauth_client(provider)
        profile = await client.exchange_code_for_profile(code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth sign-in failed; please try again",
        )

    user = await get_or_create_oauth_user(db, profile)
    token = create_access_token(user_id=user.id, email=user.email)

    redirect_target = f"{settings.frontend_base_url}/chat"
    response = RedirectResponse(url=redirect_target, status_code=status.HTTP_302_FOUND)

    cookie_opts = build_auth_cookie_options()
    response.set_cookie(value=token, **cookie_opts)
    response.delete_cookie("oauth_state", path="/api/v1/auth")
    return response


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
    """Simulate OAuth login locally for development and automated testing."""
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


@router.get("/providers")
async def available_providers() -> list[str]:
    return [provider for provider, enabled in (
        ("google", settings.oauth_google_client_id and settings.oauth_google_client_secret),
        ("github", settings.oauth_github_client_id and settings.oauth_github_client_secret),
    ) if enabled]
