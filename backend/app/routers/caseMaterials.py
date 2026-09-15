from __future__ import annotations

from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.caseMaterials import (
    CaseDocumentRead,
    CaseEvidenceCreate,
    EvidenceSourceRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.case_materials import (
    CaseMaterialsError,
    CaseMaterialsService,
    get_owned_document_content,
)
from app.services.document_ingestion import DocumentIngestionError
from app.services.document_ingestion import (
    build_document_ingestion_service,
    read_limited,
)

router = APIRouter(prefix="/cases/{case_id}", tags=["case-materials"])


def materials_http_error(error: CaseMaterialsError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


def ingestion_http_error(error: DocumentIngestionError) -> HTTPException:
    status_code = (
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        if error.code == "unsupported_document_type"
        else status.HTTP_413_CONTENT_TOO_LARGE
        if error.code.endswith("limit_exceeded")
        else status.HTTP_422_UNPROCESSABLE_CONTENT
    )
    return HTTPException(
        status_code=status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.get("/documents", response_model=list[CaseDocumentRead])
async def list_case_documents(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseMaterialsService(db).list_documents(case_id, user.id)
    except CaseMaterialsError as error:
        raise materials_http_error(error) from error


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
    except CaseMaterialsError as error:
        raise materials_http_error(error) from error
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
    try:
        content = await read_limited(file)
        ingested = await build_document_ingestion_service().ingest(content, file.filename or "document")
    except DocumentIngestionError as error:
        raise ingestion_http_error(error) from error
    extraction = {
        "provider": ingested.extraction_method.value,
        "config_json": {"mode": ingested.mode.value},
        "extracted_text": ingested.full_text,
        "provenance_json": {
            "document_id": ingested.document_id,
            "media_type": ingested.media_type,
            "extraction_method": ingested.extraction_method.value,
            "mode": ingested.mode.value,
            "pages": [page.model_dump(mode="json") for page in ingested.pages],
            "warnings": list(ingested.warnings),
        },
        "warnings_json": list(ingested.warnings),
    }
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            return await CaseMaterialsService(db).add_document(
                case_id=case_id,
                user_id=user.id,
                filename=ingested.filename,
                mime_type=ingested.media_type,
                content=content,
                extraction=extraction,
            )
    except CaseMaterialsError as error:
        raise materials_http_error(error) from error


@router.get("/evidence", response_model=list[EvidenceSourceRead])
async def list_case_evidence(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseMaterialsService(db).list_evidence(case_id, user.id)
    except CaseMaterialsError as error:
        raise materials_http_error(error) from error


@router.post("/evidence", response_model=EvidenceSourceRead, status_code=status.HTTP_201_CREATED)
async def add_case_evidence(
    case_id: UUID,
    request: CaseEvidenceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            return await CaseMaterialsService(db).add_evidence_text(
                case_id=case_id,
                user_id=user.id,
                source_kind=request.source_kind,
                exact_text=request.exact_text,
                provenance_json=request.provenance_json,
                source_metadata_json=request.source_metadata_json,
            )
    except CaseMaterialsError as error:
        raise materials_http_error(error) from error


__all__ = ["router"]
