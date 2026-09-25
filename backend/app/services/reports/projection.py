from __future__ import annotations

from pydantic import ValidationError

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.report import CaseReport
from app.schemas.reports import CaseReportContent, CaseReportRead
from app.services.analysis.contracts import (
    CaseAnalysisTrace,
    CaseFollowupExchange,
    followup_history_of_snapshot,
)
from app.services.analysis.steps.technical_context import CaseTechnicalAugmentation
from app.services.reports.contracts import CaseReportInput, ReportGenerationConflict
from app.services.sources.case_source_bundle import (
    CaseSourceBundle,
    case_source_bundle_for_analysis,
    source_ids_of_sources_read,
)


def serialize_case_report(report: CaseReport) -> CaseReportRead:
    return CaseReportRead(
        report_id=report.id,
        version_number=report.version_number,
        case_id=report.case_id,
        analysis_result_id=report.analysis_result_id,
        report=stored_content(report),
        created_at=report.created_at,
    )


def stored_content(report: CaseReport) -> CaseReportContent:
    try:
        return CaseReportContent.model_validate(report.structured_report)
    except ValidationError as error:
        raise ReportGenerationConflict(
            "case_report_outdated",
            "This report was stored in an older format and can no longer be shown",
        ) from error


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
    source_bundle = recorded_source_bundle(case, result)
    if not source_bundle.sources:
        raise ReportGenerationConflict(
            "case_report_input_invalid", "The Case has no active sources"
        )
    trace = validated_trace(result)
    return CaseReportInput(
        case_id=case.id,
        case_title=case.title or "CyberCase Investigation",
        analysis_result_id=result.id,
        analysis_created_at=result.created_at,
        source_bundle=source_bundle,
        analysis_summary=result.summary,
        analysis_trace=trace,
        technical_augmentation=recorded_augmentation(result),
        followup_history=recorded_followup_history(result),
    )


def recorded(result: CaseAnalysisResult) -> dict[str, object]:
    return result.external_context_json if isinstance(result.external_context_json, dict) else {}


def recorded_source_bundle(case: Case, result: CaseAnalysisResult) -> CaseSourceBundle:
    context = recorded(result)
    if "sources_read" not in context:
        raise ReportGenerationConflict(
            "analysis_source_snapshot_missing",
            "The analysis did not record the sources it read",
        )
    try:
        return case_source_bundle_for_analysis(
            case, result, source_ids_of_sources_read(context["sources_read"])
        )
    except ValueError as error:
        raise ReportGenerationConflict(
            "analysis_source_snapshot_invalid",
            "The sources recorded by the analysis are invalid or no longer exist",
        ) from error


def recorded_followup_history(result: CaseAnalysisResult) -> tuple[CaseFollowupExchange, ...]:
    context = recorded(result)
    if "followup_history" not in context:
        raise ReportGenerationConflict(
            "analysis_followup_snapshot_missing",
            "The analysis did not record the follow-up answers it read",
        )
    try:
        return followup_history_of_snapshot(context["followup_history"])
    except ValueError as error:
        raise ReportGenerationConflict(
            "analysis_followup_snapshot_invalid",
            "The follow-up answers recorded by the analysis are invalid",
        ) from error


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


def recorded_augmentation(result: CaseAnalysisResult) -> CaseTechnicalAugmentation | None:
    raw = recorded(result).get("technical_augmentation")
    if raw is None:
        return None
    try:
        return CaseTechnicalAugmentation.model_validate(raw)
    except ValidationError as error:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted Case technical augmentation outcome is invalid",
        ) from error


__all__ = ["build_case_report_input", "serialize_case_report", "stored_content"]
