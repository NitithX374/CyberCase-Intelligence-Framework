from __future__ import annotations

from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guard import get_current_user
from app.database import get_db
from app.models.user import User
from app.sources.ingestion.service import build_document_ingestion_service, read_limited
from app.sources.schemas import CaseDocumentRead, CaseSourceCreate, CaseSourceRead
from app.sources.service import SourceService

router = APIRouter(prefix="/cases/{case_id}", tags=["case-sources"])


@router.get("/sources", response_model=list[CaseSourceRead])
async def list_case_sources(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await SourceService(db).list_sources(case_id, user.id)


@router.post("/sources", response_model=CaseSourceRead, status_code=status.HTTP_201_CREATED)
async def add_case_source(
    case_id: UUID,
    request: CaseSourceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    async with db.begin():
        return await SourceService(db).add_text_source(
            case_id=case_id,
            user_id=user.id,
            source_kind=request.source_kind,
            text=request.exact_text,
            provenance_json=request.provenance_json,
            source_metadata_json=request.source_metadata_json,
        )


document_router = APIRouter(prefix="/cases/{case_id}", tags=["case-documents"])


@document_router.get("/documents/{document_id}/content", response_class=Response)
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


@document_router.post(
    "/documents", response_model=CaseDocumentRead, status_code=status.HTTP_201_CREATED
)
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


@document_router.post("/documents/{document_id}/reingest", response_model=CaseSourceRead)
async def reingest_case_document(
    case_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    async with db.begin():
        document = await SourceService(db).document_content(case_id, document_id, user.id)
    service = build_document_ingestion_service()
    try:
        ingested = await service.ingest(document.content_bytes, document.filename)
    finally:
        await service.aclose()
    async with db.begin():
        return await SourceService(db).update_document_extraction(
            case_id=case_id,
            user_id=user.id,
            document_id=document_id,
            ingested=ingested,
        )


__all__ = ["document_router", "router"]
