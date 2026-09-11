from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult
from app.models.chat import ChatMessage, ChatThread
from app.models.report import ChatReport
from app.schemas.reports import CaseReportCreate, ChatReportRead, StructuredReport
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_materials import canonicalJson
from app.services.reports.case_report_contracts import (
    CaseReportInputSnapshot,
    CaseReportSource,
    CaseReportTechnicalAugmentation,
    native_source_ids,
)
from app.services.reports.case_report_pdf import render_case_report_pdf
from app.services.reports.case_report_template import run_case_report_generation
from app.services.reports.report_contracts import ReportGenerationConflict, ReportNotFound
from app.services.reports.report_validation import (
    source_snapshot_hash,
    validate_case_structured_report,
)


def _report_retrieval_context_id(report: ChatReport) -> str | None:
    if not isinstance(report.source_snapshot_json, dict):
        return None
    value = report.source_snapshot_json.get("retrieval_context_id")
    return value.strip() if isinstance(value, str) and value.strip() else None


def serialize_chat_report(report: ChatReport) -> ChatReportRead:
    structured_report: StructuredReport | None = None
    if isinstance(report.structured_report, dict):
        structured_report = StructuredReport.model_validate(report.structured_report)
    validation_errors = report.validation_errors_json
    if not isinstance(validation_errors, list):
        validation_errors = []
    return ChatReportRead(
        report_id=report.id,
        thread_id=report.thread_id,
        version_number=report.version_number,
        idempotency_key=report.idempotency_key,
        source_snapshot_hash=report.source_snapshot_hash,
        analysis_message_id=report.analysis_message_id,
        case_id=report.case_id,
        analysis_result_id=report.analysis_result_id,
        evidence_snapshot_id=report.evidence_snapshot_id,
        source_reference_type=(
            "case_evidence" if report.analysis_result_id is not None else "legacy_chat"
        ),
        retrieval_context_id=_report_retrieval_context_id(report),
        prompt_version=report.prompt_version,
        provider=report.provider,
        model=report.model,
        decoding_settings=dict(report.decoding_settings or {}),
        persistence_status=report.status,
        validation_status=report.validation_status,
        report=structured_report,
        validation_errors=[str(error) for error in validation_errors],
        failure_code=report.failure_code,
        failure_message=report.failure_message,
        created_at=report.created_at,
        finished_at=report.finished_at,
        latency_ms=report.latency_ms,
        input_tokens=report.input_tokens,
        output_tokens=report.output_tokens,
        source_snapshot=report.source_snapshot_json if isinstance(report.source_snapshot_json, dict) else None,
    )


def build_case_report_snapshot(
    case: Case,
    result: CaseAnalysisResult,
    thread: ChatThread,
) -> CaseReportInputSnapshot:
    if result.case_id != case.id:
        raise ReportGenerationConflict("case_analysis_mismatch", "Analysis result does not belong to this Case")
    if result.status != "validated":
        raise ReportGenerationConflict("case_analysis_unavailable", "Only a validated Case analysis can produce a report")
    snapshot = result.snapshot
    if snapshot is None or snapshot.case_id != case.id or result.snapshot_id != snapshot.id:
        raise ReportGenerationConflict("case_snapshot_missing", "The selected analysis snapshot is unavailable")
    trace = _validated_trace(result, snapshot)
    technical_augmentation = _technical_augmentation_snapshot(result, snapshot, trace)
    sources = _snapshot_sources(snapshot)
    return CaseReportInputSnapshot(
        case_id=case.id,
        thread_id=thread.id,
        thread_title=thread.title,
        analysis_result_id=result.id,
        evidence_snapshot_id=snapshot.id,
        evidence_revision=snapshot.evidence_revision,
        created_at=datetime.now(timezone.utc),
        sources=sources,
        evidence_sha256=snapshot.text_sha256,
        manifest_sha256=snapshot.manifest_sha256,
        analysis_answer=result.answer,
        analysis_summary=result.summary,
        analysis_trace=trace.model_dump(mode="json"),
        retrieval_context_id=result.retrieval_context_id,
        technical_augmentation=technical_augmentation,
        unresolved_issues=[gap.description for gap in trace.gaps],
    )


def _validated_trace(
    result: CaseAnalysisResult,
    snapshot: CaseEvidenceSnapshot,
) -> CaseAnalysisTrace:
    if not isinstance(result.trace_json, dict):
        raise ReportGenerationConflict("case_analysis_trace_missing", "The selected analysis has no validated trace")
    try:
        trace = CaseAnalysisTrace.model_validate(result.trace_json)
        if trace.analysis_mode != "case_overview" or trace.evidence_sha256 != snapshot.text_sha256:
            raise ValueError("analysis trace is not bound to the selected Case snapshot")
        mitre_table = _mitre_table_for_validation(result)
        return validate_case_trace(
            trace,
            _case_sources(snapshot),
            _document_context(snapshot),
            mitre_table=mitre_table,
        )
    except (CaseAnalysisFailure, ValueError) as error:
        raise ReportGenerationConflict("case_analysis_trace_invalid", "The selected analysis trace is invalid") from error


def _technical_augmentation_snapshot(
    result: CaseAnalysisResult,
    snapshot: CaseEvidenceSnapshot,
    trace: CaseAnalysisTrace,
) -> CaseReportTechnicalAugmentation | None:
    metadata = result.provider_metadata_json if isinstance(result.provider_metadata_json, dict) else {}
    raw = metadata.get("technical_augmentation")
    if raw is None:
        return None
    try:
        augmentation = CaseReportTechnicalAugmentation.model_validate(raw)
    except Exception as error:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted Case technical augmentation outcome is invalid",
        ) from error
    if augmentation.query_sha256 != hashlib.sha256(snapshot.input_text.encode("utf-8")).hexdigest():
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted Case technical augmentation query is not bound to the evidence snapshot",
        )
    if augmentation.retrieval_context_id != trace.retrieval_context_id:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted technical retrieval context is not bound to the analysis trace",
        )
    trace_association_ids = [item.association_id for item in trace.mitre_associations]
    if augmentation.association_ids != trace_association_ids:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted technical associations are not bound to the analysis trace",
        )
    _validate_augmentation_outcome(augmentation, trace)
    return augmentation


def _validate_augmentation_outcome(
    augmentation: CaseReportTechnicalAugmentation,
    trace: CaseAnalysisTrace,
) -> None:
    has_context = bool(augmentation.retrieval_context_id)
    has_rows = bool(augmentation.mitre_table)
    has_associations = bool(trace.mitre_associations)
    if augmentation.status == "not_applicable":
        valid = augmentation.applicability.decision == "SKIP" and not has_context and not has_rows and not has_associations
    elif augmentation.status == "insufficient_context":
        valid = augmentation.applicability.decision == "RETRIEVE" and has_context and not has_associations
    elif augmentation.status == "retrieved_without_supported_match":
        valid = augmentation.applicability.decision == "RETRIEVE" and has_context and has_rows and not has_associations
    elif augmentation.status == "retrieved_with_matches":
        valid = augmentation.applicability.decision == "RETRIEVE" and has_context and has_rows and has_associations
    else:
        valid = bool(augmentation.failure_code) and not has_associations
    if not valid:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted technical augmentation outcome is internally inconsistent",
        )


def _mitre_table_for_validation(result: CaseAnalysisResult) -> list[dict[str, object]]:
    metadata = result.provider_metadata_json if isinstance(result.provider_metadata_json, dict) else {}
    raw = metadata.get("technical_augmentation")
    table = raw.get("mitre_table", []) if isinstance(raw, dict) else metadata.get("mitre_table", [])
    return [dict(item) for item in table if isinstance(item, dict)] if isinstance(table, list) else []


def _snapshot_sources(snapshot: CaseEvidenceSnapshot) -> list[CaseReportSource]:
    _ensure_snapshot_hashes(snapshot)
    if not isinstance(snapshot.manifest_json, list) or not snapshot.manifest_json:
        raise ReportGenerationConflict("case_snapshot_invalid", "The selected Case snapshot has no source manifest")
    sources: list[CaseReportSource] = []
    for entry in snapshot.manifest_json:
        if not isinstance(entry, dict):
            raise ReportGenerationConflict("case_snapshot_invalid", "The Case snapshot manifest is invalid")
        try:
            source = CaseReportSource.model_validate(
                {
                    "source_id": entry["source_id"],
                    "source_kind": entry["source_kind"],
                    "revision_id": entry["revision_id"],
                    "revision": entry["revision"],
                    "exact_text": entry["exact_text"],
                    "text_sha256": entry["text_sha256"],
                    "provenance_json": entry["provenance"],
                    "document_id": entry.get("document_id"),
                    "filename": entry.get("filename"),
                }
            )
        except Exception as error:
            raise ReportGenerationConflict("case_snapshot_invalid", "The Case snapshot source binding is invalid") from error
        if hashlib.sha256(source.exact_text.encode("utf-8")).hexdigest() != source.text_sha256:
            raise ReportGenerationConflict("case_snapshot_invalid", "The Case snapshot source hash is invalid")
        sources.append(source)
    return sources


def _ensure_snapshot_hashes(snapshot: CaseEvidenceSnapshot) -> None:
    if snapshot.format_version != "case_evidence_snapshot_v1":
        raise ReportGenerationConflict("case_snapshot_version_invalid", "The Case snapshot format is unsupported")
    if hashlib.sha256(snapshot.input_text.encode("utf-8")).hexdigest() != snapshot.text_sha256:
        raise ReportGenerationConflict("case_snapshot_invalid", "The Case snapshot text hash is invalid")
    if not isinstance(snapshot.manifest_json, list):
        raise ReportGenerationConflict("case_snapshot_invalid", "The Case snapshot manifest is invalid")
    manifest_hash = hashlib.sha256(canonicalJson(snapshot.manifest_json).encode("utf-8")).hexdigest()
    if manifest_hash != snapshot.manifest_sha256:
        raise ReportGenerationConflict("case_snapshot_invalid", "The Case snapshot manifest hash is invalid")


def _case_sources(snapshot: CaseEvidenceSnapshot) -> tuple[CaseAdmittedSource, ...]:
    return tuple(
        CaseAdmittedSource(
            str(source["source_id"]),
            int(source["revision"]),
            str(source["exact_text"]),
            str(source["text_sha256"]),
        )
        for source in snapshot.manifest_json
        if isinstance(source, dict)
    )


def _document_context(snapshot: CaseEvidenceSnapshot) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for entry in snapshot.manifest_json:
        if not isinstance(entry, dict):
            continue
        provenance = entry.get("provenance")
        if not isinstance(provenance, dict):
            continue
        if not all(isinstance(entry.get(key), str) for key in ("source_id", "document_id", "filename")):
            continue
        pages = provenance.get("pages")
        if isinstance(pages, list):
            context.append(
                {
                    "source_id": entry["source_id"],
                    "documents": [{"document_id": entry["document_id"], "filename": entry["filename"], "page_spans": pages}],
                }
            )
    return context


class CaseReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_report(
        self,
        case_id: UUID,
        request: CaseReportCreate,
        user_id: UUID | None,
    ) -> ChatReportRead:
        if not settings.chat_report_enabled:
            raise ReportGenerationConflict("report_generation_disabled", "Report generation is disabled by backend configuration.")
        async with self.db.begin():
            case = await self._locked_case(case_id, user_id)
            thread = await self._locked_or_create_thread(case)
            result = await self._selected_result(case, request.analysis_result_id)
            snapshot = build_case_report_snapshot(case, result, thread)
            snapshot_hash = source_snapshot_hash(snapshot)
            idempotency_key = request.idempotency_key or snapshot_hash
            existing = await self._existing_report(thread.id, idempotency_key)
            if existing is not None:
                if existing.source_snapshot_hash != snapshot_hash:
                    raise ReportGenerationConflict("report_idempotency_conflict", "The idempotency key belongs to another Case report snapshot.")
                return serialize_chat_report(existing)
            generation = await run_case_report_generation(snapshot)
            report = ChatReport(
                thread_id=thread.id,
                case_id=case.id,
                analysis_result_id=result.id,
                evidence_snapshot_id=result.snapshot_id,
                version_number=await self._next_version(thread.id),
                idempotency_key=idempotency_key,
                source_snapshot_json=snapshot.model_dump(mode="json"),
                source_snapshot_hash=snapshot_hash,
                analysis_message_id=await self._analysis_message_id(thread.id, result.id),
                retrieval_context_id=None,
                prompt_version=generation.prompt_version,
                provider=generation.provider,
                model=generation.model,
                decoding_settings={},
                status=generation.status,
                validation_status="validated" if generation.status == "completed" else "failed",
                validation_errors_json=list(generation.validation_errors),
                structured_report=generation.report.model_dump(mode="json") if generation.report else None,
                failure_code=generation.failure_code,
                failure_message=generation.failure_message,
                finished_at=datetime.now(timezone.utc),
                latency_ms=generation.latency_ms,
                input_tokens=generation.input_tokens,
                output_tokens=generation.output_tokens,
            )
            self.db.add(report)
            await self.db.flush()
            return serialize_chat_report(report)

    async def list_reports(self, case_id: UUID, user_id: UUID | None) -> list[ChatReportRead]:
        await self._owned_case(case_id, user_id)
        result = await self.db.execute(
            select(ChatReport)
            .where(ChatReport.case_id == case_id)
            .order_by(ChatReport.version_number.desc())
        )
        return [serialize_chat_report(report) for report in result.scalars().all()]

    async def get_report(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> ChatReportRead:
        await self._owned_case(case_id, user_id)
        return serialize_chat_report(await self._report(case_id, report_id))

    async def get_report_pdf(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> tuple[bytes, str]:
        await self._owned_case(case_id, user_id)
        report = await self._report(case_id, report_id, load_thread=True)
        if report.status != "completed" or not isinstance(report.structured_report, dict):
            raise ReportGenerationConflict("report_pdf_requires_validated_report", "Only a completed validated report can be exported.")
        snapshot = CaseReportInputSnapshot.model_validate(report.source_snapshot_json)
        structured = StructuredReport.model_validate(report.structured_report)
        validate_case_structured_report(
            structured,
            source_evidence_ids=native_source_ids(snapshot),
            mitre_ids={
                str(item["technique_id"])
                for item in snapshot.analysis_trace.get("mitre_associations", [])
                if isinstance(item, dict) and item.get("technique_id")
            },
        )
        if source_snapshot_hash(snapshot) != report.source_snapshot_hash:
            raise ReportGenerationConflict("report_snapshot_hash_invalid", "The persisted Case report snapshot hash is invalid.")
        content = await asyncio.to_thread(render_case_report_pdf, snapshot, structured, report.id)
        return content, f"cybercase-case-report-v{report.version_number}-{report.id}.pdf"

    async def _locked_case(self, case_id: UUID, user_id: UUID | None) -> Case:
        case = await self.db.scalar(select(Case).where(Case.id == case_id).with_for_update())
        if case is None or case.user_id != user_id:
            raise ReportNotFound("case_not_found", "Case not found")
        return case

    async def _owned_case(self, case_id: UUID, user_id: UUID | None) -> Case:
        case = await self.db.scalar(select(Case).where(Case.id == case_id))
        if case is None or case.user_id != user_id:
            raise ReportNotFound("case_not_found", "Case not found")
        return case

    async def _locked_or_create_thread(self, case: Case) -> ChatThread:
        thread = await self.db.scalar(select(ChatThread).where(ChatThread.id == case.id).with_for_update())
        if thread is None:
            thread = ChatThread(id=case.id, title=case.title, user_id=case.user_id)
            self.db.add(thread)
            await self.db.flush()
        return thread

    async def _selected_result(self, case: Case, result_id: UUID | None) -> CaseAnalysisResult:
        selected_id = result_id or case.latest_analysis_result_id
        if selected_id is None:
            raise ReportGenerationConflict("case_analysis_missing", "A completed Case analysis is required before generating a report.")
        result = await self.db.scalar(
            select(CaseAnalysisResult)
            .options(selectinload(CaseAnalysisResult.snapshot))
            .where(CaseAnalysisResult.id == selected_id, CaseAnalysisResult.case_id == case.id)
        )
        if result is None:
            raise ReportNotFound("case_analysis_not_found", "The selected Case analysis was not found")
        return result

    async def _existing_report(self, thread_id: UUID, key: str) -> ChatReport | None:
        return await self.db.scalar(
            select(ChatReport).where(ChatReport.thread_id == thread_id, ChatReport.idempotency_key == key)
        )

    async def _next_version(self, thread_id: UUID) -> int:
        current = await self.db.scalar(select(func.max(ChatReport.version_number)).where(ChatReport.thread_id == thread_id))
        return (current or 0) + 1

    async def _analysis_message_id(self, thread_id: UUID, result_id: UUID) -> UUID | None:
        return await self.db.scalar(
            select(ChatMessage.id)
            .where(
                ChatMessage.thread_id == thread_id,
                ChatMessage.analysis_result_id == result_id,
                ChatMessage.message_kind == "analysis_result",
            )
            .order_by(ChatMessage.ordinal.desc())
            .limit(1)
        )

    async def _report(
        self,
        case_id: UUID,
        report_id: UUID,
        *,
        load_thread: bool = False,
    ) -> ChatReport:
        statement = select(ChatReport).where(ChatReport.case_id == case_id, ChatReport.id == report_id)
        if load_thread:
            statement = statement.options(selectinload(ChatReport.thread))
        report = await self.db.scalar(statement)
        if report is None:
            raise ReportNotFound("case_report_not_found", "Case report not found")
        return report


__all__ = ["CaseReportService", "build_case_report_snapshot"]
