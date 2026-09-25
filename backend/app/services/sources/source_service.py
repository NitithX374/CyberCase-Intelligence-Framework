from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, undefer

from app.errors import AppError
from app.models.sources import CaseDocument, CaseSource
from app.services.cases.ownership import owned_case
from app.services.document_ingestion.provenance import bind_exact_page_spans


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
        filename: str,
        mime_type: str,
        content: bytes,
        extraction: dict[str, object],
    ) -> CaseDocument:
        case = await owned_case(self.db, case_id, user_id, lock=True)
        extracted_text = extraction.get("extracted_text")
        if not isinstance(extracted_text, str):
            raise SourceError("extraction_text_missing", "Document extraction text is missing")
        if not extracted_text.strip():
            raise SourceError("extraction_text_empty", "Document extraction text is empty")
        document = CaseDocument(
            case_id=case.id,
            filename=filename,
            mime_type=mime_type,
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
                exact_text=extracted_text,
                provenance_json=build_document_provenance(
                    as_dictionary(extraction.get("provenance_json")),
                    extracted_text,
                    required_string(extraction, "provider"),
                ),
                source_metadata_json={"received_via": "document_upload"},
            )
        )
        case.source_revision += 1
        await self.db.flush()
        return document

    async def list_documents(self, case_id: UUID, user_id: UUID | None) -> list[CaseDocument]:
        await owned_case(self.db, case_id, user_id)
        result = await self.db.execute(
            select(CaseDocument)
            .where(CaseDocument.case_id == case_id)
            .order_by(CaseDocument.created_at, CaseDocument.id)
        )
        return list(result.scalars().all())

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
        normalized_text = text.strip()
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
            .where(CaseSource.case_id == case_id, CaseSource.archived_at.is_(None))
            .order_by(CaseSource.created_at, CaseSource.id)
        )
        return list(result.scalars().unique().all())


def required_string(value: dict[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise SourceError("extraction_metadata_invalid", f"Extraction {key} is required")
    return item.strip()


def as_dictionary(value: object) -> dict[str, object]:
    return deepcopy(value) if isinstance(value, dict) else {}


def build_document_provenance(
    read: dict[str, object], text: str, provider: str
) -> dict[str, object]:
    provenance = bind_exact_page_spans(read, text)
    extraction_method = read.get("extraction_method") or provider
    if extraction_method:
        provenance["extraction_method"] = str(extraction_method)
    if provider:
        provenance["provider"] = provider

    verification_status = read.get("verification_status")
    if not verification_status:
        statuses = [
            page.get("verification_status")
            for page in provenance.get("pages", [])
            if isinstance(page, dict) and page.get("verification_status")
        ]
        if any(value == "needs_review" for value in statuses):
            verification_status = "needs_review"
        elif any(value == "machine_read" for value in statuses) or extraction_method in (
            "document_recognition",
            "ocr",
        ):
            verification_status = "machine_read"
        else:
            verification_status = "native"
    provenance["verification_status"] = str(verification_status)

    confidence_status = read.get("confidence_status")
    if not confidence_status:
        confidence_status = (
            "not_reported"
            if extraction_method in ("document_recognition", "ocr", "hybrid")
            else "not_applicable"
        )
    provenance["confidence_status"] = str(confidence_status)
    provenance["minimum_confidence"] = None
    return provenance


__all__ = [
    "SourceError",
    "SourceService",
]
