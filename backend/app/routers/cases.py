"""Case aggregate HTTP endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate
from app.services.auth.dependencies import get_current_user
from app.services.cases import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseRead], status_code=status.HTTP_200_OK)
async def list_cases(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).list_cases(user_id=user.id)


@router.get("/{case_id}", response_model=CaseRead, status_code=status.HTTP_200_OK)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).get_case(case_id, user_id=user.id)


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    request: CaseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).create_case(request, user_id=user.id)


@router.patch("/{case_id}", response_model=CaseRead, status_code=status.HTTP_200_OK)
async def update_case(
    case_id: UUID,
    request: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).update_case(case_id, request, user_id=user.id)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    await CaseService(db).delete_case(case_id, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router"]
