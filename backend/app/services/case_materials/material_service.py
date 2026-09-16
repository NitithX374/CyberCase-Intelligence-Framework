from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import status

from app.models.case import Case
from app.models.case_materials import (
    CaseDocument,
    CaseSource,
    DocumentExtraction,
)
from app.services.document_ingestion.provenance import bind_exact_page_spans


class CaseMaterialsError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class CaseMaterialsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_owned_case(self, case_id: UUID, user_id: UUID | None, *, lock: bool = False) -> Case:
        statement = select(Case).where(Case.id == case_id)
        if lock:
            statement = statement.with_for_update()
        result = await self.db.execute(statement)
        case = result.scalar_one_or_none()
        if case is None or case.user_id != user_id:
            raise CaseMaterialsError("case_not_found", "Case not found", 404)
        return case

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
        case = await self.get_owned_case(case_id, user_id, lock=True)
        extracted_text = extraction.get("extracted_text")
        if not isinstance(extracted_text, str):
            raise CaseMaterialsError("extraction_text_missing", "Document extraction text is missing")
        if not extracted_text.strip():
            raise CaseMaterialsError("extraction_text_empty", "Document extraction text is empty")
        document = CaseDocument(
            case_id=case.id,
            filename=filename,
            mime_type=mime_type,
            size_bytes=len(content),
            content_bytes=content,
        )
        self.db.add(document)
        await self.db.flush()
        extraction_record = DocumentExtraction(
            document_id=document.id,
            provider=required_string(extraction, "provider"),
            config_json=as_dictionary(extraction.get("config_json")),
            extracted_text=extracted_text,
            provenance_json=as_dictionary(extraction.get("provenance_json")),
            warnings_json=as_list(extraction.get("warnings_json")),
        )
        self.db.add(extraction_record)
        await self.db.flush()
        case_source = CaseSource(
            case_id=case.id,
            source_kind="document",
            document_id=document.id,
            exact_text=extracted_text,
            provenance_json=build_document_provenance(extraction_record),
            source_metadata_json={"received_via": "document_upload"},
        )
        self.db.add(case_source)
        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(document, attribute_names=["extractions"])
        return document

    async def list_documents(self, case_id: UUID, user_id: UUID | None) -> list[CaseDocument]:
        await self.get_owned_case(case_id, user_id)
        result = await self.db.execute(
            select(CaseDocument)
            .options(selectinload(CaseDocument.extractions))
            .where(CaseDocument.case_id == case_id)
            .order_by(CaseDocument.created_at, CaseDocument.id)
        )
        return list(result.scalars().unique().all())

    async def add_text_source(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        source_kind: str,
        text: str,
        provenance_json: dict[str, object],
        source_metadata_json: dict[str, object] | None = None,
        origin_message_id: UUID | None = None,
    ) -> CaseSource:
        if source_kind not in {"narrative", "followup_answer"}:
            raise CaseMaterialsError("evidence_source_kind_invalid", "Unsupported native evidence source kind")
        normalized_text = text.strip()
        if not normalized_text:
            raise CaseMaterialsError("evidence_text_empty", "Case evidence text is empty")
        case = await self.get_owned_case(case_id, user_id, lock=True)
        source = CaseSource(
            case_id=case.id,
            source_kind=source_kind,
            origin_message_id=origin_message_id,
            exact_text=normalized_text,
            provenance_json=deepcopy(provenance_json),
            source_metadata_json=source_metadata_json or {},
        )
        self.db.add(source)
        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def list_sources(self, case_id: UUID, user_id: UUID | None) -> list[CaseSource]:
        await self.get_owned_case(case_id, user_id)
        result = await self.db.execute(
            select(CaseSource)
            .options(selectinload(CaseSource.document))
            .where(CaseSource.case_id == case_id)
            .order_by(CaseSource.created_at, CaseSource.id)
        )
        return list(result.scalars().unique().all())


def required_string(value: dict[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise CaseMaterialsError("extraction_metadata_invalid", f"Extraction {key} is required")
    return item.strip()


def as_dictionary(value: object) -> dict[str, object]:
    return deepcopy(value) if isinstance(value, dict) else {}


def as_list(value: object) -> list[object]:
    return deepcopy(value) if isinstance(value, list) else []


def build_document_provenance(extraction: DocumentExtraction) -> dict[str, object]:
    provenance = bind_exact_page_spans(
        extraction.provenance_json,
        extraction.extracted_text,
    )
    provenance["extraction_id"] = str(extraction.id)
    if extraction.warnings_json:
        provenance["warnings"] = list(extraction.warnings_json)
    extraction_method = extraction.provenance_json.get("extraction_method") or extraction.provider
    if extraction_method:
        provenance["extraction_method"] = str(extraction_method)
    if extraction.provider:
        provenance["provider"] = extraction.provider

    verification_status = extraction.provenance_json.get("verification_status")
    if not verification_status:
        statuses = [
            page.get("verification_status")
            for page in provenance.get("pages", [])
            if isinstance(page, dict) and page.get("verification_status")
        ]
        if any(value == "needs_review" for value in statuses):
            verification_status = "needs_review"
        elif any(value == "machine_read" for value in statuses):
            verification_status = "machine_read"
        elif extraction_method in ("document_recognition", "ocr"):
            verification_status = "machine_read"
        else:
            verification_status = "native"
    provenance["verification_status"] = str(verification_status)

    confidence_status = extraction.provenance_json.get("confidence_status")
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
    "CaseMaterialsError",
    "CaseMaterialsService",
]
