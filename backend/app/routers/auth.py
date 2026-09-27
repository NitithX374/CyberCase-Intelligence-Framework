from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import PasswordLoginRequest, RegisterRequest, UserRead
from app.services.auth.auth_service import (
    authenticate,
    build_auth_cookie_options,
    register_user,
)
from app.services.auth.credentials import create_access_token
from app.services.auth.dependencies import get_optional_user

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
    return start_password_session(await register_user(db, payload), response)


@router.post("/login", response_model=UserRead)
async def login(
    payload: PasswordLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    return start_password_session(await authenticate(db, payload), response)


@router.get("/session", response_model=UserRead | None, summary="Get optional session user")
async def get_session(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> UserRead | None:
    if user is None:
        return None
    return UserRead.model_validate(user)


@router.post("/logout", summary="Log out user and clear session cookie")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=settings.jwt_cookie_name,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}
