from __future__ import annotations

from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.routers.errors import ingestion_http_error, source_http_error
from app.schemas.sources import CaseDocumentRead
from app.services.auth.dependencies import get_current_user
from app.services.document_ingestion.contracts import DocumentIngestionError
from app.services.document_ingestion.service import build_document_ingestion_service, read_limited
from app.services.sources.document_content import get_owned_document_content
from app.services.sources.source_service import SourceError, SourceService

router = APIRouter(prefix="/cases/{case_id}", tags=["case-documents"])


@router.get("/documents", response_model=list[CaseDocumentRead])
async def list_case_documents(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await SourceService(db).list_documents(case_id, user.id)
    except SourceError as error:
        raise source_http_error(error) from error


@router.get("/documents/{document_id}/content", response_class=Response)
async def get_case_document_content(
    case_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        document = await get_owned_document_content(
            db,
            case_id=case_id,
            document_id=document_id,
            user_id=user.id,
        )
    except SourceError as error:
        raise source_http_error(error) from error
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
    await commit_dependency_transaction(db)
    service = build_document_ingestion_service()
    try:
        content = await read_limited(file)
        ingested = await service.ingest(content, file.filename or "document")
    except DocumentIngestionError as error:
        raise ingestion_http_error(error) from error
    finally:
        await service.aclose()
    extraction = {
        "provider": ingested.extraction_method.value,
        "extracted_text": ingested.full_text,
        "provenance_json": {
            "document_id": ingested.document_id,
            "media_type": ingested.media_type,
            "extraction_method": ingested.extraction_method.value,
            "pages": [page.model_dump(mode="json") for page in ingested.pages],
            "warnings": list(ingested.warnings),
        },
    }
    try:
        async with db.begin():
            return await SourceService(db).add_document(
                case_id=case_id,
                user_id=user.id,
                filename=ingested.filename,
                mime_type=ingested.media_type,
                content=content,
                extraction=extraction,
            )
    except SourceError as error:
        raise source_http_error(error) from error


__all__ = ["router"]
