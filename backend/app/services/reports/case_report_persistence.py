from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.case import Case
from app.models.caseMaterials import EvidenceSource
from app.models.caseRun import CaseAnalysisResult
from app.models.report import CaseReport
from app.schemas.reports import CaseReportCreate, ChatReportRead, StructuredReport
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.reports.case_report_contracts import (
    CaseReportInputSnapshot,
    CaseReportSource,
    CaseReportTechnicalAugmentation,
    native_source_ids,
)
from app.services.reports.case_report_pdf import render_case_report_pdf
from app.services.reports.case_report_template import run_case_report_generation
from app.services.reports.report_contracts import ReportGenerationConflict, ReportNotFound
from app.services.reports.report_validation import validate_case_structured_report


def _report_retrieval_context_id(report: CaseReport) -> str | None:
    return report.retrieval_context_id


def serialize_chat_report(report: CaseReport) -> ChatReportRead:
    structured_report: StructuredReport | None = None
    if isinstance(report.structured_report, dict):
        structured_report = StructuredReport.model_validate(report.structured_report)
    validation_errors = report.validation_errors_json
    if not isinstance(validation_errors, list):
        validation_errors = []
    return ChatReportRead(
        report_id=report.id,
        version_number=report.version_number,
        idempotency_key=report.idempotency_key,
        case_id=report.case_id,
        analysis_result_id=report.analysis_result_id,
        source_reference_type="case_evidence",
        retrieval_context_id=_report_retrieval_context_id(report),
        prompt_version=report.prompt_version,
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
    )


def build_case_report_snapshot(
    case: Case,
    result: CaseAnalysisResult,
) -> CaseReportInputSnapshot:
    if result.case_id != case.id:
        raise ReportGenerationConflict("case_analysis_mismatch", "Analysis result does not belong to this Case")
    if result.status != "validated":
        raise ReportGenerationConflict("case_analysis_unavailable", "Only a validated Case analysis can produce a report")
    evidence_rev = (
        getattr(result.snapshot, "evidence_revision", result.evidence_revision)
        if hasattr(result, "snapshot") and result.snapshot
        else result.evidence_revision
    )
    if evidence_rev != case.evidence_revision:
        raise ReportGenerationConflict(
            "case_analysis_stale",
            "The selected Case analysis is based on a different evidence revision. Re-run analysis before generating a report.",
        )
    sources = [
        CaseReportSource(
            source_id=s.id,
            source_kind=s.source_kind,
            revision=1,
            exact_text=s.exact_text,
            provenance_json=s.provenance_json,
            document_id=s.document_id,
            filename=s.document.filename if s.document else None,
        )
        for s in case.evidence_sources
        if s.archived_at is None
    ]
    if not sources and hasattr(result, "snapshot") and result.snapshot:
        manifest = getattr(result.snapshot, "manifest_json", None)
        if isinstance(manifest, list):
            sources = [
                CaseReportSource(
                    source_id=item.get("source_id", ""),
                    source_kind=item.get("source_kind", "narrative"),
                    revision=item.get("revision", 1),
                    exact_text=item.get("exact_text", ""),
                    provenance_json=item.get("provenance") or item.get("provenance_json") or {},
                    document_id=item.get("document_id"),
                    filename=item.get("filename"),
                )
                for item in manifest
                if isinstance(item, dict)
            ]
    if not sources:
        raise ReportGenerationConflict("case_snapshot_invalid", "The Case has no active source evidence")
    trace = _validated_trace(result, case, sources=sources)
    technical_augmentation = _technical_augmentation_snapshot(result, trace)
    return CaseReportInputSnapshot(
        case_id=case.id,
        case_title=case.title or "CyberCase Investigation",
        analysis_result_id=result.id,
        evidence_revision=evidence_rev,
        created_at=datetime.now(timezone.utc),
        sources=sources,
        analysis_answer=result.answer,
        analysis_summary=result.summary,
        analysis_trace=trace.model_dump(mode="json"),
        retrieval_context_id=result.retrieval_context_id,
        technical_augmentation=technical_augmentation,
        unresolved_issues=[gap.description for gap in trace.gaps],
    )


def _validated_trace(
    result: CaseAnalysisResult,
    case: Case,
    sources: list[CaseReportSource] | None = None,
) -> CaseAnalysisTrace:
    if not isinstance(result.trace_json, dict):
        raise ReportGenerationConflict("case_analysis_trace_missing", "The selected analysis has no validated trace")
    try:
        trace = CaseAnalysisTrace.model_validate(result.trace_json)
        if trace.analysis_mode != "case_overview":
            raise ValueError("analysis trace mode is not case_overview")
        mitre_table = _mitre_table_for_validation(result)
        return validate_case_trace(
            trace,
            _case_sources(case, sources=sources),
            _document_context(case),
            mitre_table=mitre_table,
        )
    except (CaseAnalysisFailure, ValueError) as error:
        raise ReportGenerationConflict("case_analysis_trace_invalid", "The selected analysis trace is invalid") from error


def _technical_augmentation_snapshot(
    result: CaseAnalysisResult,
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


def _case_sources(
    case: Case,
    sources: list[CaseReportSource] | None = None,
) -> tuple[CaseAdmittedSource, ...]:
    if case.evidence_sources:
        return tuple(
            CaseAdmittedSource(
                str(source.id),
                1,
                source.exact_text,
            )
            for source in case.evidence_sources
            if source.archived_at is None
        )
    if sources:
        return tuple(
            CaseAdmittedSource(
                str(s.source_id),
                s.revision,
                s.exact_text,
            )
            for s in sources
        )
    return ()


def _document_context(case: Case) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for source in case.evidence_sources:
        if source.archived_at is not None or not source.document_id or not source.document:
            continue
        provenance = source.provenance_json
        if not isinstance(provenance, dict):
            continue
        pages = provenance.get("pages")
        if isinstance(pages, list):
            context.append(
                {
                    "source_id": str(source.id),
                    "documents": [{"document_id": str(source.document_id), "filename": source.document.filename, "page_spans": pages}],
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
            result = await self._selected_result(case, request.analysis_result_id)
            snapshot = build_case_report_snapshot(case, result)
            idempotency_key = request.idempotency_key or f"report-{result.id}-{case.evidence_revision}"
            existing = await self._existing_report(case.id, idempotency_key)
            if existing is not None:
                return serialize_chat_report(existing)
            generation = await run_case_report_generation(snapshot)
            retrieval_id = getattr(result, "retrieval_context_id", None)
            report = CaseReport(
                case_id=case.id,
                analysis_result_id=result.id,
                version_number=await self._next_version(case.id),
                idempotency_key=idempotency_key,
                retrieval_context_id=retrieval_id,
                prompt_version=generation.prompt_version,
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
            select(CaseReport)
            .where(CaseReport.case_id == case_id)
            .order_by(CaseReport.version_number.desc())
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
        case = await self._owned_case(case_id, user_id)
        report = await self._report(case_id, report_id)
        if report.status != "completed" or not isinstance(report.structured_report, dict):
            raise ReportGenerationConflict("report_pdf_requires_validated_report", "Only a completed validated report can be exported.")
        result = await self._selected_result(case, report.analysis_result_id)
        snapshot = build_case_report_snapshot(case, result)
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
        pdf_bytes = render_case_report_pdf(
            snapshot,
            structured,
            report.id,
        )
        return pdf_bytes, f"case_report_v{report.version_number}.pdf"

    async def _locked_case(self, case_id: UUID, user_id: UUID | None) -> Case:
        result = await self.db.execute(
            select(Case)
            .options(selectinload(Case.evidence_sources).selectinload(EvidenceSource.document))
            .where(Case.id == case_id)
            .with_for_update()
        )
        case = result.scalar_one_or_none()
        if case is None or case.user_id != user_id:
            raise ReportNotFound("case_not_found", "Case not found")
        return case

    async def _owned_case(self, case_id: UUID, user_id: UUID | None) -> Case:
        result = await self.db.execute(
            select(Case)
            .options(selectinload(Case.evidence_sources).selectinload(EvidenceSource.document))
            .where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        if case is None or case.user_id != user_id:
            raise ReportNotFound("case_not_found", "Case not found")
        return case

    async def _selected_result(self, case: Case, analysis_result_id: UUID | None) -> CaseAnalysisResult:
        result_id = analysis_result_id or case.latest_analysis_result_id
        if result_id is None:
            raise ReportGenerationConflict("case_analysis_missing", "No Case analysis result is available")
        result = await self.db.execute(
            select(CaseAnalysisResult)
            .where(CaseAnalysisResult.id == result_id, CaseAnalysisResult.case_id == case.id)
        )
        persisted = result.scalar_one_or_none()
        if persisted is None:
            raise ReportNotFound("case_analysis_not_found", "The selected Case analysis result was not found")
        return persisted

    async def _existing_report(self, case_id: UUID, idempotency_key: str) -> CaseReport | None:
        result = await self.db.execute(
            select(CaseReport).where(CaseReport.case_id == case_id, CaseReport.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def _report(self, case_id: UUID, report_id: UUID) -> CaseReport:
        result = await self.db.execute(
            select(CaseReport).where(CaseReport.id == report_id, CaseReport.case_id == case_id)
        )
        report = result.scalar_one_or_none()
        if report is None:
            raise ReportNotFound("report_not_found", "Case report not found")
        return report

    async def _next_version(self, case_id: UUID) -> int:
        result = await self.db.scalar(
            select(func.coalesce(func.max(CaseReport.version_number), 0)).where(CaseReport.case_id == case_id)
        )
        return int(result or 0) + 1


__all__ = [
    "CaseReportService",
    "build_case_report_snapshot",
    "serialize_chat_report",
]
