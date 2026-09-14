from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import status

from app.models.case import Case
from app.models.caseMaterials import (
    CaseDocument,
    DocumentExtraction,
    EvidenceSource,
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

    async def getOwnedCase(self, case_id: UUID, user_id: UUID | None, *, lock: bool = False) -> Case:
        statement = select(Case).where(Case.id == case_id)
        if lock:
            statement = statement.with_for_update()
        result = await self.db.execute(statement)
        case = result.scalar_one_or_none()
        if case is None or case.user_id != user_id:
            raise CaseMaterialsError("case_not_found", "Case not found", 404)
        return case

    async def addDocument(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        filename: str,
        mime_type: str,
        content: bytes,
        extraction: dict[str, object],
    ) -> CaseDocument:
        case = await self.getOwnedCase(case_id, user_id, lock=True)
        extracted_text = extraction.get("extracted_text")
        if not isinstance(extracted_text, str):
            raise CaseMaterialsError("extraction_text_missing", "Document extraction text is missing")
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
            provider=_required_string(extraction, "provider"),
            config_json=_dictionary(extraction.get("config_json")),
            extracted_text=extracted_text,
            provenance_json=_dictionary(extraction.get("provenance_json")),
            warnings_json=_list(extraction.get("warnings_json")),
        )
        self.db.add(extraction_record)
        await self.db.flush()
        await self.db.refresh(document, attribute_names=["extractions"])
        return document

    async def listDocuments(self, case_id: UUID, user_id: UUID | None) -> list[CaseDocument]:
        await self.getOwnedCase(case_id, user_id)
        result = await self.db.execute(
            select(CaseDocument)
            .options(selectinload(CaseDocument.extractions))
            .where(CaseDocument.case_id == case_id)
            .order_by(CaseDocument.created_at, CaseDocument.id)
        )
        return list(result.scalars().unique().all())

    async def admitExtraction(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        extraction_id: UUID,
    ) -> EvidenceSource:
        case = await self.getOwnedCase(case_id, user_id, lock=True)
        extraction_result = await self.db.execute(
            select(DocumentExtraction)
            .options(selectinload(DocumentExtraction.document))
            .where(DocumentExtraction.id == extraction_id)
            .with_for_update()
        )
        extraction = extraction_result.scalar_one_or_none()
        if extraction is None or extraction.document.case_id != case.id:
            raise CaseMaterialsError("extraction_not_found", "Document extraction not found", 404)
        if not extraction.extracted_text.strip():
            raise CaseMaterialsError("extraction_text_empty", "Only non-empty extracted text can be admitted")
        provenance = bind_exact_page_spans(
            extraction.provenance_json,
            extraction.extracted_text,
        )
        provenance["extraction_id"] = str(extraction.id)
        if extraction.warnings_json:
            provenance["warnings"] = list(extraction.warnings_json)
        extraction_method = (
            extraction.provenance_json.get("extraction_method")
            or extraction.provider
        )
        if extraction_method:
            provenance["extraction_method"] = str(extraction_method)
        if extraction.provider:
            provenance["provider"] = extraction.provider

        verification_status = extraction.provenance_json.get("verification_status")
        if not verification_status:
            statuses = [
                region.get("verification_status")
                for page in provenance.get("pages", [])
                if isinstance(page, dict)
                for region in page.get("regions", [])
                if isinstance(region, dict) and region.get("verification_status")
            ]
            if any(s == "needs_review" for s in statuses):
                verification_status = "needs_review"
            elif any(s == "machine_read" for s in statuses):
                verification_status = "machine_read"
            elif extraction_method in ("document_recognition", "ocr"):
                verification_status = "machine_read"
            else:
                verification_status = "native"
        provenance["verification_status"] = str(verification_status)

        confidence_status = extraction.provenance_json.get("confidence_status")
        if not confidence_status:
            confidences = [
                float(region["recognition_confidence"])
                for page in provenance.get("pages", [])
                if isinstance(page, dict)
                for region in page.get("regions", [])
                if isinstance(region, dict) and region.get("recognition_confidence") is not None
            ]
            if confidences:
                confidence_status = "reported"
                provenance["minimum_confidence"] = min(confidences)
            else:
                confidence_status = (
                    "not_reported"
                    if extraction_method in ("document_recognition", "ocr")
                    else "not_applicable"
                )
                provenance["minimum_confidence"] = None
        provenance["confidence_status"] = str(confidence_status)

        source_result = await self.db.execute(
            select(EvidenceSource)
            .where(
                EvidenceSource.case_id == case.id,
                EvidenceSource.document_id == extraction.document_id,
                EvidenceSource.source_kind == "reviewed_document",
            )
            .order_by(EvidenceSource.created_at)
            .with_for_update()
        )
        source = source_result.scalars().first()
        if source is None:
            source = EvidenceSource(
                case_id=case.id,
                source_kind="reviewed_document",
                document_id=extraction.document_id,
                exact_text=extraction.extracted_text,
                provenance_json=provenance,
                source_metadata_json={"admission": "explicit_review"},
            )
            self.db.add(source)
            await self.db.flush()
        else:
            source.exact_text = extraction.extracted_text
            source.provenance_json = provenance
            if source.archived_at is not None:
                source.archived_at = None

        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def admitText(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        source_kind: str,
        exact_text: str,
        provenance_json: dict[str, object],
        source_metadata_json: dict[str, object] | None = None,
        origin_message_id: UUID | None = None,
    ) -> EvidenceSource:
        if source_kind not in {"narrative", "followup_answer", "clarification_answer", "explicit_chat_addition"}:
            raise CaseMaterialsError("evidence_source_kind_invalid", "Unsupported native evidence source kind")
        persisted_kind = (
            "followup_answer"
            if source_kind in {"followup_answer", "clarification_answer"}
            else "narrative"
        )
        normalized_text = exact_text.strip()
        if not normalized_text:
            raise CaseMaterialsError("evidence_text_empty", "Admitted evidence text is empty")
        case = await self.getOwnedCase(case_id, user_id, lock=True)
        source = EvidenceSource(
            case_id=case.id,
            source_kind=persisted_kind,
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

    async def addRevision(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        source_id: UUID,
        exact_text: str,
        provenance_json: dict[str, object],
    ) -> EvidenceSource:
        normalized_text = exact_text.strip()
        if not normalized_text:
            raise CaseMaterialsError("evidence_text_empty", "Admitted evidence text is empty")
        case = await self.getOwnedCase(case_id, user_id, lock=True)
        result = await self.db.execute(
            select(EvidenceSource)
            .where(EvidenceSource.id == source_id, EvidenceSource.case_id == case.id)
            .with_for_update()
        )
        source = result.scalar_one_or_none()
        if source is None:
            raise CaseMaterialsError("evidence_source_not_found", "Evidence source not found", 404)
        if source.archived_at is not None:
            raise CaseMaterialsError("evidence_source_archived", "Archived evidence source cannot be edited")
        provenance = bind_exact_page_spans(provenance_json, normalized_text)
        source.exact_text = normalized_text
        source.provenance_json = provenance
        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def archiveSource(self, *, case_id: UUID, user_id: UUID | None, source_id: UUID) -> None:
        case = await self.getOwnedCase(case_id, user_id, lock=True)
        result = await self.db.execute(
            select(EvidenceSource)
            .where(EvidenceSource.id == source_id, EvidenceSource.case_id == case.id)
            .with_for_update()
        )
        source = result.scalar_one_or_none()
        if source is None:
            raise CaseMaterialsError("evidence_source_not_found", "Evidence source not found", 404)
        if source.archived_at is None:
            source.archived_at = datetime.now(timezone.utc)
            case.evidence_revision += 1

    async def listEvidence(self, case_id: UUID, user_id: UUID | None) -> list[EvidenceSource]:
        await self.getOwnedCase(case_id, user_id)
        result = await self.db.execute(
            select(EvidenceSource)
            .options(selectinload(EvidenceSource.document))
            .where(EvidenceSource.case_id == case_id)
            .order_by(EvidenceSource.created_at, EvidenceSource.id)
        )
        return list(result.scalars().unique().all())


def _required_string(value: dict[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise CaseMaterialsError("extraction_metadata_invalid", f"Extraction {key} is required")
    return item.strip()


def _dictionary(value: object) -> dict[str, object]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return deepcopy(value) if isinstance(value, list) else []


def _source_label(source: EvidenceSource) -> str:
    if source.document is not None:
        return f"DOCUMENT {source.document.filename}"
    return {
        "narrative": "CASE NARRATIVE",
        "followup_answer": "FOLLOW-UP ANSWER",
        "clarification_answer": "CLARIFICATION ANSWER",
        "explicit_chat_addition": "ADDED CASE INFORMATION",
        "legacy_unbound": "LEGACY CASE MATERIAL",
    }.get(source.source_kind, "CASE MATERIAL")


@dataclass(frozen=True)
class AssembledCaseEvidence:
    input_text: str
    active_sources: list[EvidenceSource]
    evidence_revision: int

    @property
    def id(self) -> UUID:
        return self.active_sources[0].id if self.active_sources else UUID("00000000-0000-0000-0000-000000000000")

    @property
    def manifest_json(self) -> list[dict[str, object]]:
        return [
            {
                "source_id": str(s.id),
                "source_kind": s.source_kind,
                "document_id": str(s.document_id) if s.document_id else None,
                "filename": s.document.filename if s.document else None,
                "provenance_json": s.provenance_json,
            }
            for s in self.active_sources
        ]

    @property
    def text_sha256(self) -> str:
        return ""

    @property
    def format_version(self) -> str:
        return "case_evidence_snapshot_v1"


async def assembleCaseEvidence(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> AssembledCaseEvidence:
    result = await db.execute(
        select(Case)
        .options(
            selectinload(Case.evidence_sources).selectinload(EvidenceSource.document),
        )
        .where(Case.id == case_id)
        .with_for_update()
    )
    case = result.scalar_one_or_none()
    if case is None or (user_id is not None and case.user_id != user_id):
        raise CaseMaterialsError("case_not_found", "Case not found", 404)

    selected: list[EvidenceSource] = []
    for source in sorted(case.evidence_sources, key=lambda item: (item.created_at, str(item.id))):
        if source.archived_at is not None:
            continue
        if not source.exact_text.strip():
            raise CaseMaterialsError("evidence_text_empty", "Admitted evidence text is empty")
        selected.append(source)
    if not selected:
        raise CaseMaterialsError("case_evidence_missing", "Add and admit case material before analysis")

    sections: list[str] = []
    for source in selected:
        sections.append(
            f"[{_source_label(source)} · SOURCE {source.id}]\n{source.exact_text.strip()}"
        )

    input_text = "\n\n".join(sections)
    return AssembledCaseEvidence(
        input_text=input_text,
        active_sources=selected,
        evidence_revision=case.evidence_revision,
    )


# Compatibility alias for buildCaseEvidenceSnapshot
buildCaseEvidenceSnapshot = assembleCaseEvidence


__all__ = [
    "AssembledCaseEvidence",
    "CaseMaterialsError",
    "CaseMaterialsService",
    "assembleCaseEvidence",
    "buildCaseEvidenceSnapshot",
]
