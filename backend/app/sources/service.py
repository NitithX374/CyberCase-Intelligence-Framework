from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, undefer

from app.cases.ownership import owned_case
from app.errors import AppError
from app.models.document import CaseDocument
from app.models.source import CaseSource
from app.sources.ingestion.contracts import IngestedDocument
from app.sources.ingestion.provenance import bind_exact_page_spans


class SourceError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class SourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_document(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        ingested: IngestedDocument,
        content: bytes,
    ) -> CaseDocument:
        case = await owned_case(self.db, case_id, user_id, lock=True)
        if not ingested.full_text.strip():
            raise SourceError("extraction_text_empty", "Document extraction text is empty")
        document = CaseDocument(
            case_id=case.id,
            filename=ingested.filename,
            mime_type=ingested.media_type,
            size_bytes=len(content),
            content_bytes=content,
        )
        self.db.add(document)
        await self.db.flush()
        self.db.add(
            CaseSource(
                case_id=case.id,
                source_kind="document",
                document_id=document.id,
                exact_text=ingested.full_text,
                provenance_json=document_provenance(ingested),
                source_metadata_json={"received_via": "document_upload"},
            )
        )
        case.source_revision += 1
        await self.db.flush()
        return document

    async def document_content(
        self, case_id: UUID, document_id: UUID, user_id: UUID | None
    ) -> CaseDocument:
        await owned_case(self.db, case_id, user_id)
        document = await self.db.scalar(
            select(CaseDocument)
            .options(undefer(CaseDocument.content_bytes))
            .where(CaseDocument.id == document_id, CaseDocument.case_id == case_id)
        )
        if document is None:
            raise SourceError("document_not_found", "Document not found", status.HTTP_404_NOT_FOUND)
        return document

    async def add_text_source(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        source_kind: str,
        text: str,
        provenance_json: dict[str, object],
        source_metadata_json: dict[str, object] | None = None,
    ) -> CaseSource:
        if source_kind != "narrative":
            raise SourceError("source_kind_invalid", "Unsupported native source kind")
        normalized_text = text.replace("\x00", "").strip()
        if not normalized_text:
            raise SourceError("source_text_empty", "The case source text is empty")
        case = await owned_case(self.db, case_id, user_id, lock=True)
        source = CaseSource(
            case_id=case.id,
            source_kind=source_kind,
            exact_text=normalized_text,
            provenance_json=deepcopy(provenance_json),
            source_metadata_json=source_metadata_json or {},
        )
        self.db.add(source)
        case.source_revision += 1
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def list_sources(self, case_id: UUID, user_id: UUID | None) -> list[CaseSource]:
        await owned_case(self.db, case_id, user_id)
        result = await self.db.execute(
            select(CaseSource)
            .options(selectinload(CaseSource.document))
            .where(CaseSource.case_id == case_id)
            .order_by(CaseSource.created_at, CaseSource.id)
        )
        return list(result.scalars().unique().all())


def document_provenance(ingested: IngestedDocument) -> dict[str, object]:
    pages = [page.model_dump(mode="json") for page in ingested.pages]
    return {
        **bind_exact_page_spans({"pages": pages}, ingested.full_text),
        "extraction_method": ingested.extraction_method.value,
        "verification_status": ingested.verification_status,
        "warnings": list(ingested.warnings),
    }


__all__ = [
    "SourceError",
    "SourceService",
]
