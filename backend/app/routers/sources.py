"""The sources a case is analysed from."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.routers.errors import source_http_error
from app.schemas.sources import CaseSourceCreate, CaseSourceRead
from app.services.auth.dependencies import get_current_user
from app.services.sources import SourceError, SourceService

router = APIRouter(prefix="/cases/{case_id}", tags=["case-sources"])


@router.get("/sources", response_model=list[CaseSourceRead])
async def list_case_sources(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await SourceService(db).list_sources(case_id, user.id)
    except SourceError as error:
        raise source_http_error(error) from error


@router.post("/sources", response_model=CaseSourceRead, status_code=status.HTTP_201_CREATED)
async def add_case_source(
    case_id: UUID,
    request: CaseSourceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            return await SourceService(db).add_text_source(
                case_id=case_id,
                user_id=user.id,
                source_kind=request.source_kind,
                text=request.exact_text,
                provenance_json=request.provenance_json,
                source_metadata_json=request.source_metadata_json,
            )
    except SourceError as error:
        raise source_http_error(error) from error


__all__ = ["router"]
