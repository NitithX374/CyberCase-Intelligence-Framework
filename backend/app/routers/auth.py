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
from app.services.auth.authService import (
    build_auth_cookie_options,
    get_or_create_dev_user,
    get_or_create_oauth_user,
)
from app.services.auth.dependencies import get_current_user, get_optional_user
from app.services.auth.jwt import create_access_token
from app.services.auth.oauthClients import get_oauth_client

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login/{provider}", summary="Initiate OAuth login flow")
async def oauth_login(
    provider: str,
    redirect: str | None = Query(default=None, description="Optional post-login redirect path"),
) -> RedirectResponse:
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
    response.set_cookie(
        "oauth_state",
        f"{provider}:{state}",
        httponly=True,
        secure=settings.jwt_cookie_secure,
        samesite="lax",
        max_age=600,
        path="/api/v1/auth",
    )
    if redirect and redirect.startswith("/") and not redirect.startswith("//"):
        response.set_cookie(
            "oauth_redirect",
            redirect,
            httponly=True,
            secure=settings.jwt_cookie_secure,
            samesite="lax",
            max_age=600,
            path="/api/v1/auth",
        )
    return response


@router.get("/callback/{provider}", summary="OAuth callback handler")
async def oauth_callback(
    provider: str,
    request: Request,
    code: str | None = Query(default=None, description="OAuth authorization code"),
    state: str | None = Query(default=None, description="OAuth state parameter"),
    error: str | None = Query(default=None, description="OAuth provider error code"),
    error_description: str | None = Query(default=None, description="OAuth provider error description"),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Exchange authorization code for user profile, issue session cookie, and redirect to frontend."""
    def _login_redirect(err_code: str) -> RedirectResponse:
        resp = RedirectResponse(
            url=f"{settings.frontend_base_url}/login?error={err_code}",
            status_code=status.HTTP_302_FOUND,
        )
        resp.delete_cookie("oauth_state", path="/api/v1/auth")
        resp.delete_cookie("oauth_redirect", path="/api/v1/auth")
        return resp

    if error:
        return _login_redirect("cancelled" if "denied" in error.lower() or "cancel" in error.lower() else "oauth_failed")

    if not code:
        raise HTTPException(400, "Missing OAuth code; please start sign-in again")

    expected = request.cookies.get("oauth_state")
    if not state or not expected or not secrets.compare_digest(expected, f"{provider}:{state}"):
        raise HTTPException(400, "Invalid OAuth state; please start sign-in again")

    try:
        client = get_oauth_client(provider)
        profile = await client.exchange_code_for_profile(code)
    except ValueError:
        return _login_redirect("oauth_failed")
    except Exception:
        return _login_redirect("oauth_failed")

    try:
        user = await get_or_create_oauth_user(db, profile)
    except HTTPException as http_exc:
        if http_exc.status_code == 409:
            return _login_redirect("account_exists_with_password")
        return _login_redirect("oauth_failed")
    except Exception:
        return _login_redirect("oauth_failed")

    token = create_access_token(user_id=user.id, email=user.email)

    target_path = "/case"
    saved_redirect = request.cookies.get("oauth_redirect")
    if saved_redirect and saved_redirect.startswith("/") and not saved_redirect.startswith("//"):
        target_path = saved_redirect

    redirect_target = f"{settings.frontend_base_url}{target_path}"
    response = RedirectResponse(url=redirect_target, status_code=status.HTTP_302_FOUND)

    cookie_opts = build_auth_cookie_options()
    response.set_cookie(value=token, **cookie_opts)
    response.delete_cookie("oauth_state", path="/api/v1/auth")
    response.delete_cookie("oauth_redirect", path="/api/v1/auth")
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
    enabled = bool(settings.oauth_google_client_id and settings.oauth_google_client_secret)
    return ["google"] if enabled else []
