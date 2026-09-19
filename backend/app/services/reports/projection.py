from __future__ import annotations

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.report import CaseReport
from app.schemas.reports import CaseReportRead, StructuredReport
from app.services.case_analysis.contracts import (
    CaseAnalysisTrace,
)
from app.services.reports.contracts import (
    CaseReportInput,
    CaseReportTechnicalAugmentation,
    ReportGenerationConflict,
)
from app.services.sources.case_source_bundle import (
    case_source_bundle_for_analysis,
)


def serialize_case_report(report: CaseReport) -> CaseReportRead:
    return CaseReportRead(
        report_id=report.id,
        version_number=report.version_number,
        case_id=report.case_id,
        analysis_result_id=report.analysis_result_id,
        report=StructuredReport.model_validate(report.structured_report),
        created_at=report.created_at,
    )


def build_case_report_input(
    case: Case,
    result: CaseAnalysisResult,
) -> CaseReportInput:
    if result.case_id != case.id:
        raise ReportGenerationConflict(
            "case_analysis_mismatch", "Analysis result does not belong to this Case"
        )
    if result.status != "validated":
        raise ReportGenerationConflict(
            "case_analysis_unavailable", "Only a validated Case analysis can produce a report"
        )
    source_bundle = case_source_bundle_for_analysis(case, result)
    if not source_bundle.sources:
        raise ReportGenerationConflict(
            "case_report_input_invalid", "The Case has no active sources"
        )
    trace = validated_trace(result)
    return CaseReportInput(
        case_id=case.id,
        case_title=case.title or "CyberCase Investigation",
        analysis_result_id=result.id,
        source_bundle=source_bundle,
        analysis_summary=result.summary,
        analysis_trace=trace.model_dump(mode="json"),
        technical_augmentation=technical_augmentation_input(result, trace),
        unresolved_issues=[gap.description for gap in trace.gaps],
    )


def validated_trace(
    result: CaseAnalysisResult,
) -> CaseAnalysisTrace:
    if not isinstance(result.trace_json, dict):
        raise ReportGenerationConflict(
            "case_analysis_trace_missing", "The selected analysis has no validated trace"
        )
    try:
        trace = CaseAnalysisTrace.model_validate(result.trace_json)
        if trace.analysis_mode != "case_overview":
            raise ValueError("analysis trace mode is not case_overview")
        return trace
    except ValueError as error:
        raise ReportGenerationConflict(
            "case_analysis_trace_invalid", "The selected analysis trace is invalid"
        ) from error


def technical_augmentation_input(
    result: CaseAnalysisResult,
    trace: CaseAnalysisTrace,
) -> CaseReportTechnicalAugmentation | None:
    metadata = (
        result.external_context_json if isinstance(result.external_context_json, dict) else {}
    )
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
    validate_augmentation_outcome(augmentation, trace)
    return augmentation


def validate_augmentation_outcome(
    augmentation: CaseReportTechnicalAugmentation,
    trace: CaseAnalysisTrace,
) -> None:
    has_context = bool(augmentation.retrieval_context_id)
    has_rows = bool(augmentation.mitre_table)
    has_associations = bool(trace.mitre_associations)
    if augmentation.status == "not_applicable":
        valid = (
            augmentation.applicability.decision == "SKIP"
            and not has_context
            and not has_rows
            and not has_associations
        )
    elif augmentation.status == "insufficient_context":
        valid = (
            augmentation.applicability.decision == "RETRIEVE"
            and has_context
            and not has_associations
        )
    elif (
        augmentation.status == "retrieved_from_rag"
        or augmentation.status == "retrieved_without_supported_match"
    ):
        valid = (
            augmentation.applicability.decision == "RETRIEVE"
            and has_context
            and has_rows
            and not has_associations
        )
    elif augmentation.status == "retrieved_with_matches":
        valid = (
            augmentation.applicability.decision == "RETRIEVE"
            and has_context
            and has_rows
            and has_associations
        )
    else:
        valid = bool(augmentation.failure_code) and not has_associations
    if not valid:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted technical augmentation outcome is internally inconsistent",
        )


__all__ = ["build_case_report_input", "serialize_case_report"]
