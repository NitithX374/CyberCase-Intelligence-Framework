import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.database import get_db
from app.models.user import User
from app.schemas.auth import PasswordLoginRequest, RegisterRequest, UserRead
from app.services.auth.authService import build_auth_cookie_options
from app.services.auth.jwt import create_access_token
from app.services.auth.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


def start_session(user: User, response: Response) -> UserRead:
    token = create_access_token(user.id, user.email)
    response.set_cookie(value=token, **build_auth_cookie_options())
    response.headers["Cache-Control"] = "no-store"
    return UserRead.model_validate(user)


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    email = str(payload.email).lower()
    name = payload.name.strip()
    if not name:
        raise HTTPException(422, "Display name is required")
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
        raise HTTPException(409, "An account already exists for this email") from error
    await db.refresh(user)
    return start_session(user, response)


@router.post("/login", response_model=UserRead)
async def login(
    payload: PasswordLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not user.password_hash:
        await run_in_threadpool(hash_password, payload.password)
        raise HTTPException(401, "Incorrect email or password")
    if not await run_in_threadpool(
        verify_password, payload.password, user.password_hash
    ):
        raise HTTPException(401, "Incorrect email or password")
    return start_session(user, response)
