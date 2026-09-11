from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.caseMaterials import (
    AdmitExtractionRequest,
    CaseDocumentRead,
    CaseEvidenceCreate,
    CaseEvidenceSnapshotRead,
    EvidenceSourceRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.case_materials import (
    CaseMaterialsError,
    CaseMaterialsService,
    buildCaseEvidenceSnapshot,
)
from app.services.document_ingestion import DocumentIngestionError
from app.routers.documentIngestion import _build_service, _read_limited

router = APIRouter(prefix="/cases/{case_id}", tags=["case-materials"])


def _materials_http_error(error: CaseMaterialsError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


def _ingestion_http_error(error: DocumentIngestionError) -> HTTPException:
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
        return await CaseMaterialsService(db).listDocuments(case_id, user.id)
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.post("/documents", response_model=CaseDocumentRead, status_code=status.HTTP_201_CREATED)
async def add_case_document(
    case_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content = await _read_limited(file, settings.document_ingestion_max_bytes)
    try:
        ingested = await _build_service().ingest(content, file.filename or "document")
    except DocumentIngestionError as error:
        raise _ingestion_http_error(error) from error
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
        },
        "warnings_json": list(ingested.warnings),
    }
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            return await CaseMaterialsService(db).addDocument(
                case_id=case_id,
                user_id=user.id,
                filename=ingested.filename,
                mime_type=ingested.media_type,
                content=content,
                extraction=extraction,
            )
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.post("/documents/{document_id}/admit", response_model=EvidenceSourceRead, status_code=status.HTTP_201_CREATED)
async def admit_case_document(
    case_id: UUID,
    document_id: UUID,
    request: AdmitExtractionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            service = CaseMaterialsService(db)
            await service.getOwnedCase(case_id, user.id)
            source = await service.admitExtraction(
                case_id=case_id,
                user_id=user.id,
                extraction_id=request.extraction_id,
            )
            if source.document_id != document_id:
                raise CaseMaterialsError("document_not_found", "Document not found", 404)
            return source
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.get("/evidence", response_model=list[EvidenceSourceRead])
async def list_case_evidence(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseMaterialsService(db).listEvidence(case_id, user.id)
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.get("/evidence/snapshots/{snapshot_id}", response_model=CaseEvidenceSnapshotRead)
async def get_case_evidence_snapshot(
    case_id: UUID,
    snapshot_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseMaterialsService(db).getEvidenceSnapshot(
            case_id=case_id,
            user_id=user.id,
            snapshot_id=snapshot_id,
        )
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


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
            return await CaseMaterialsService(db).admitText(
                case_id=case_id,
                user_id=user.id,
                source_kind=request.source_kind,
                exact_text=request.exact_text,
                provenance_json=request.provenance_json,
                source_metadata_json=request.source_metadata_json,
            )
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.post("/evidence/{source_id}/revisions", response_model=EvidenceSourceRead, status_code=status.HTTP_201_CREATED)
async def revise_case_evidence(
    case_id: UUID,
    source_id: UUID,
    request: CaseEvidenceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            return await CaseMaterialsService(db).addRevision(
                case_id=case_id,
                user_id=user.id,
                source_id=source_id,
                exact_text=request.exact_text,
                provenance_json=request.provenance_json,
            )
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.post("/evidence/{source_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_case_evidence(
    case_id: UUID,
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            await CaseMaterialsService(db).archiveSource(
                case_id=case_id,
                user_id=user.id,
                source_id=source_id,
            )
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


@router.post("/evidence/snapshot", response_model=CaseEvidenceSnapshotRead, status_code=status.HTTP_201_CREATED)
async def create_case_evidence_snapshot(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            return await buildCaseEvidenceSnapshot(db, case_id=case_id, user_id=user.id)
    except CaseMaterialsError as error:
        raise _materials_http_error(error) from error


__all__ = ["router"]
