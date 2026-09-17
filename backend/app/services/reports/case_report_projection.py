from __future__ import annotations

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult
from app.models.report import CaseReport
from app.schemas.reports import CaseReportRead, StructuredReport
from app.services.case_analysis.contracts import (
    CaseAnalysisTrace,
)
from app.services.case_materials.case_source_bundle import (
    CaseSourceBundle,
    case_source_bundle_for_analysis,
)
from app.services.reports.case_report_contracts import (
    CaseReportInput,
    CaseReportTechnicalAugmentation,
    ReportGenerationConflict,
)


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
    source_bundle = case_source_bundle_for_analysis(case, result)
    if not source_bundle.sources:
        raise ReportGenerationConflict("case_report_input_invalid", "The Case has no active source evidence")
    trace = validated_trace(result)
    return CaseReportInput(
        case_id=case.id,
        case_title=case.title or "CyberCase Investigation",
        analysis_result_id=result.id,
        source_bundle=source_bundle,
        analysis_answer=result.answer,
        analysis_summary=result.summary,
        analysis_trace=trace.model_dump(mode="json"),
        technical_augmentation=technical_augmentation_input(result, trace),
        unresolved_issues=[gap.description for gap in trace.gaps],
    )


def validated_trace(
    result: CaseAnalysisResult,
) -> CaseAnalysisTrace:
    if not isinstance(result.trace_json, dict):
        raise ReportGenerationConflict("case_analysis_trace_missing", "The selected analysis has no validated trace")
    try:
        trace = CaseAnalysisTrace.model_validate(result.trace_json)
        if trace.analysis_mode != "case_overview":
            raise ValueError("analysis trace mode is not case_overview")
        return trace
    except ValueError as error:
        raise ReportGenerationConflict("case_analysis_trace_invalid", "The selected analysis trace is invalid") from error


def technical_augmentation_input(
    result: CaseAnalysisResult,
    trace: CaseAnalysisTrace,
) -> CaseReportTechnicalAugmentation | None:
    metadata = result.external_context_json if isinstance(result.external_context_json, dict) else {}
    raw = metadata.get("technical_augmentation")
    if not isinstance(raw, dict):
        return None
    raw_status = raw.get("status")
    status = str(raw_status) if raw_status else "not_applicable"
    retrieval_context_id = raw.get("retrieval_context_id")
    if retrieval_context_id is not None and not isinstance(retrieval_context_id, str):
        retrieval_context_id = str(retrieval_context_id)
    raw_table = raw.get("mitre_table")
    mitre_table = [
        dict(item)
        for item in raw_table
        if isinstance(item, dict)
    ] if isinstance(raw_table, list) else []
    raw_associations = raw.get("association_ids")
    association_ids = [
        str(item)
        for item in raw_associations
        if isinstance(item, (str, int))
    ] if isinstance(raw_associations, list) else []
    failure_code = str(raw["failure_code"]) if raw.get("failure_code") else None
    return CaseReportTechnicalAugmentation(
        status=status,
        retrieval_context_id=retrieval_context_id,
        retrieval_context_reused=bool(raw.get("retrieval_context_reused", False)),
        mitre_table=mitre_table,
        association_ids=association_ids,
        failure_code=failure_code,
    )


__all__ = ["build_case_report_input", "serialize_case_report"]
