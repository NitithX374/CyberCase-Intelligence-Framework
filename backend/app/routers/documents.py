from __future__ import annotations

from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.sources import CaseDocumentRead
from app.services.auth.dependencies import get_current_user
from app.services.document_ingestion.service import build_document_ingestion_service, read_limited
from app.services.sources.source_service import SourceService

router = APIRouter(prefix="/cases/{case_id}", tags=["case-documents"])


@router.get("/documents", response_model=list[CaseDocumentRead])
async def list_case_documents(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await SourceService(db).list_documents(case_id, user.id)


@router.get("/documents/{document_id}/content", response_class=Response)
async def get_case_document_content(
    case_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    document = await SourceService(db).document_content(case_id, document_id, user.id)
    return Response(
        content=document.content_bytes,
        media_type=document.mime_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quote(document.filename)}",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/documents", response_model=CaseDocumentRead, status_code=status.HTTP_201_CREATED)
async def add_case_document(
    case_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = build_document_ingestion_service()
    try:
        content = await read_limited(file)
        ingested = await service.ingest(content, file.filename or "document")
    finally:
        await service.aclose()
    async with db.begin():
        return await SourceService(db).add_document(
            case_id=case_id, user_id=user.id, ingested=ingested, content=content
        )


__all__ = ["router"]
