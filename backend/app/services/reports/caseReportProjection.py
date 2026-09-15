from __future__ import annotations

from app.models.case import Case
from app.models.caseRun import CaseAnalysisResult
from app.models.report import CaseReport
from app.schemas.reports import CaseReportRead, StructuredReport
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.reports.case_report_contracts import (
    CaseReportInput,
    CaseReportSource,
    CaseReportTechnicalAugmentation,
)
from app.services.reports.report_contracts import ReportGenerationConflict


def serialize_case_report(report: CaseReport) -> CaseReportRead:
    structured_report: StructuredReport | None = None
    if isinstance(report.structured_report, dict):
        structured_report = StructuredReport.model_validate(report.structured_report)
    validation_errors = report.validation_errors_json
    if not isinstance(validation_errors, list):
        validation_errors = []
    return CaseReportRead(
        report_id=report.id,
        version_number=report.version_number,
        idempotency_key=report.idempotency_key,
        case_id=report.case_id,
        analysis_result_id=report.analysis_result_id,
        retrieval_context_id=report.retrieval_context_id,
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


def build_case_report_input(
    case: Case,
    result: CaseAnalysisResult,
) -> CaseReportInput:
    if result.case_id != case.id:
        raise ReportGenerationConflict("case_analysis_mismatch", "Analysis result does not belong to this Case")
    if result.status != "validated":
        raise ReportGenerationConflict("case_analysis_unavailable", "Only a validated Case analysis can produce a report")
    if result.evidence_revision != case.evidence_revision:
        raise ReportGenerationConflict(
            "case_analysis_stale",
            "The selected Case analysis is based on a different evidence revision. Re-run analysis before generating a report.",
        )
    sources = [
        CaseReportSource(
            source_id=source.id,
            exact_text=source.exact_text,
            filename=source.document.filename if source.document else None,
        )
        for source in case.evidence_sources
        if source.archived_at is None
    ]
    if not sources:
        raise ReportGenerationConflict("case_report_input_invalid", "The Case has no active source evidence")
    trace = _validated_trace(result, case)
    return CaseReportInput(
        case_id=case.id,
        case_title=case.title or "CyberCase Investigation",
        analysis_result_id=result.id,
        evidence_revision=result.evidence_revision,
        sources=sources,
        analysis_answer=result.answer,
        analysis_summary=result.summary,
        analysis_trace=trace.model_dump(mode="json"),
        technical_augmentation=_technical_augmentation_input(result, trace),
        unresolved_issues=[gap.description for gap in trace.gaps],
    )


def _validated_trace(
    result: CaseAnalysisResult,
    case: Case,
) -> CaseAnalysisTrace:
    if not isinstance(result.trace_json, dict):
        raise ReportGenerationConflict("case_analysis_trace_missing", "The selected analysis has no validated trace")
    try:
        trace = CaseAnalysisTrace.model_validate(result.trace_json)
        if trace.analysis_mode != "case_overview":
            raise ValueError("analysis trace mode is not case_overview")
        return validate_case_trace(
            trace,
            _case_sources(case),
            _document_context(case),
            mitre_table=_mitre_table_for_validation(result),
        )
    except (CaseAnalysisFailure, ValueError) as error:
        raise ReportGenerationConflict("case_analysis_trace_invalid", "The selected analysis trace is invalid") from error


def _technical_augmentation_input(
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
    if augmentation.association_ids != [item.association_id for item in trace.mitre_associations]:
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


def _case_sources(case: Case) -> tuple[CaseAdmittedSource, ...]:
    return tuple(
        CaseAdmittedSource(str(source.id), source.exact_text)
        for source in case.evidence_sources
        if source.archived_at is None
    )


def _document_context(case: Case) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for source in case.evidence_sources:
        if source.archived_at is not None or not source.document_id or not source.document:
            continue
        provenance = source.provenance_json
        pages = provenance.get("pages") if isinstance(provenance, dict) else None
        if isinstance(pages, list):
            context.append(
                {
                    "source_id": str(source.id),
                    "documents": [{
                        "document_id": str(source.document_id),
                        "filename": source.document.filename,
                        "page_spans": pages,
                    }],
                }
            )
    return context


__all__ = ["build_case_report_input", "serialize_case_report"]
