from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import status

from app.models.case import Case
from app.models.caseMaterials import (
    CaseDocument,
    CaseEvidenceSnapshot,
    DocumentExtraction,
    EvidenceRevision,
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
            content_sha256=hashlib.sha256(content).hexdigest(),
            content_bytes=content,
        )
        self.db.add(document)
        await self.db.flush()
        extraction_record = DocumentExtraction(
            document_id=document.id,
            revision=1,
            provider=_required_string(extraction, "provider"),
            config_json=_dictionary(extraction.get("config_json")),
            extracted_text=extracted_text,
            text_sha256=hashlib.sha256(extracted_text.encode("utf-8")).hexdigest(),
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
            .options(selectinload(EvidenceSource.revisions))
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
                source_metadata_json={"admission": "explicit_review"},
            )
            self.db.add(source)
            await self.db.flush()
        elif source.archived_at is not None:
            source.archived_at = None
        revision_number = await self._next_revision(source.id)
        revision = EvidenceRevision(
            source_id=source.id,
            revision=revision_number,
            exact_text=extraction.extracted_text,
            text_sha256=hashlib.sha256(extraction.extracted_text.encode("utf-8")).hexdigest(),
            provenance_json=provenance,
            extraction_id=extraction.id,
        )
        self.db.add(revision)
        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(source, attribute_names=["revisions"])
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
            source_metadata_json=source_metadata_json or {},
        )
        self.db.add(source)
        await self.db.flush()
        revision = EvidenceRevision(
            source_id=source.id,
            revision=1,
            exact_text=normalized_text,
            text_sha256=hashlib.sha256(normalized_text.encode("utf-8")).hexdigest(),
            provenance_json=deepcopy(provenance_json),
        )
        self.db.add(revision)
        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(source, attribute_names=["revisions"])
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
            .options(selectinload(EvidenceSource.revisions))
            .where(EvidenceSource.id == source_id, EvidenceSource.case_id == case.id)
            .with_for_update()
        )
        source = result.scalar_one_or_none()
        if source is None:
            raise CaseMaterialsError("evidence_source_not_found", "Evidence source not found", 404)
        if source.archived_at is not None:
            raise CaseMaterialsError("evidence_source_archived", "Archived evidence source cannot be edited")
        next_revision = max((item.revision for item in source.revisions), default=0) + 1
        provenance = bind_exact_page_spans(provenance_json, normalized_text)
        self.db.add(
            EvidenceRevision(
                source_id=source.id,
                revision=next_revision,
                exact_text=normalized_text,
                text_sha256=hashlib.sha256(normalized_text.encode("utf-8")).hexdigest(),
                provenance_json=provenance,
            )
        )
        case.evidence_revision += 1
        await self.db.flush()
        await self.db.refresh(source, attribute_names=["revisions"])
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
            .options(selectinload(EvidenceSource.revisions), selectinload(EvidenceSource.document))
            .where(EvidenceSource.case_id == case_id)
            .order_by(EvidenceSource.created_at, EvidenceSource.id)
        )
        return list(result.scalars().unique().all())

    async def getEvidenceSnapshot(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        snapshot_id: UUID,
    ) -> CaseEvidenceSnapshot:
        await self.getOwnedCase(case_id, user_id)
        result = await self.db.execute(
            select(CaseEvidenceSnapshot).where(
                CaseEvidenceSnapshot.id == snapshot_id,
                CaseEvidenceSnapshot.case_id == case_id,
            )
        )
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            raise CaseMaterialsError("evidence_snapshot_not_found", "Evidence snapshot not found", 404)
        return snapshot

    async def _next_revision(self, source_id: UUID) -> int:
        result = await self.db.execute(
            select(func.max(EvidenceRevision.revision)).where(EvidenceRevision.source_id == source_id)
        )
        return (result.scalar_one() or 0) + 1


def _required_string(value: dict[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise CaseMaterialsError("extraction_metadata_invalid", f"Extraction {key} is required")
    return item.strip()


def _dictionary(value: object) -> dict[str, object]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return deepcopy(value) if isinstance(value, list) else []


SNAPSHOT_FORMAT_VERSION = "case_evidence_snapshot_v1"


def canonicalJson(value: object) -> str:
    import json
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _active_revision(source: EvidenceSource) -> EvidenceRevision | None:
    revisions = [revision for revision in source.revisions if revision.archived_at is None]
    return max(revisions, key=lambda revision: revision.revision) if revisions else None


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


async def buildCaseEvidenceSnapshot(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseEvidenceSnapshot:
    result = await db.execute(
        select(Case)
        .options(
            selectinload(Case.evidence_sources)
            .selectinload(EvidenceSource.revisions),
            selectinload(Case.evidence_sources)
            .selectinload(EvidenceSource.document),
        )
        .where(Case.id == case_id)
        .with_for_update()
    )
    case = result.scalar_one_or_none()
    if case is None or case.user_id != user_id:
        raise CaseMaterialsError("case_not_found", "Case not found", 404)

    selected: list[tuple[EvidenceSource, EvidenceRevision]] = []
    for source in sorted(case.evidence_sources, key=lambda item: (item.created_at, str(item.id))):
        if source.archived_at is not None:
            continue
        revision = _active_revision(source)
        if revision is None:
            raise CaseMaterialsError(
                "evidence_revision_missing",
                "An active evidence source has no active admitted revision",
            )
        if not revision.exact_text.strip():
            raise CaseMaterialsError("evidence_text_empty", "Admitted evidence text is empty")
        selected.append((source, revision))
    if not selected:
        raise CaseMaterialsError("case_evidence_missing", "Add and admit case material before analysis")

    manifest: list[dict[str, object]] = []
    sections: list[str] = []
    for source, revision in selected:
        provenance = deepcopy(revision.provenance_json)
        provenance_hash = hashlib.sha256(canonicalJson(provenance).encode("utf-8")).hexdigest()
        entry = {
            "source_id": str(source.id),
            "source_kind": source.source_kind,
            "revision_id": str(revision.id),
            "revision": revision.revision,
            "exact_text": revision.exact_text,
            "text_sha256": revision.text_sha256,
            "provenance": provenance,
            "provenance_sha256": provenance_hash,
        }
        if source.document is not None:
            entry["document_id"] = str(source.document.id)
            entry["filename"] = source.document.filename
        manifest.append(entry)
        sections.append(f"[{_source_label(source)} · SOURCE {source.id} · REVISION {revision.revision}]\n{revision.exact_text.strip()}")

    input_text = "\n\n".join(sections)
    text_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()
    manifest_hash = hashlib.sha256(canonicalJson(manifest).encode("utf-8")).hexdigest()
    existing_result = await db.execute(
        select(CaseEvidenceSnapshot).where(
            CaseEvidenceSnapshot.case_id == case.id,
            CaseEvidenceSnapshot.evidence_revision == case.evidence_revision,
            CaseEvidenceSnapshot.manifest_sha256 == manifest_hash,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing is not None:
        return existing

    snapshot = CaseEvidenceSnapshot(
        case_id=case.id,
        evidence_revision=case.evidence_revision,
        format_version=SNAPSHOT_FORMAT_VERSION,
        manifest_json=manifest,
        input_text=input_text,
        text_sha256=text_hash,
        manifest_sha256=manifest_hash,
    )
    db.add(snapshot)
    await db.flush()
    return snapshot


__all__ = [
    "CaseMaterialsError",
    "CaseMaterialsService",
    "SNAPSHOT_FORMAT_VERSION",
    "buildCaseEvidenceSnapshot",
    "canonicalJson",
]
