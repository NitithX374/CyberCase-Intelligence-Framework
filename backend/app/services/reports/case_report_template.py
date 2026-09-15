from __future__ import annotations

import time

from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.reports.case_report_content import (
    build_case_report_claims,
    build_case_report_limitations,
    build_case_report_sections,
)
from app.services.reports.case_report_contracts import (
    CaseReportInput,
    ReportRunResult,
    native_source_ids,
    validate_case_structured_report,
)
from app.schemas.reports import StructuredReport

CASE_REPORT_PROMPT_VERSION = "deterministic_case_readable_report_v2"


async def run_case_report_generation(report_input: CaseReportInput) -> ReportRunResult:
    started = time.perf_counter()
    try:
        report = build_case_template_report(report_input)
        trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
        validate_case_structured_report(
            report,
            source_evidence_ids=native_source_ids(report_input),
            mitre_ids={association.technique_id for association in trace.mitre_associations},
        )
        return ReportRunResult(
            status="completed",
            report=report,
            prompt_version=CASE_REPORT_PROMPT_VERSION,
            provider="deterministic",
            model="case-template",
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
    except Exception as error:
        return ReportRunResult(
            status="failed",
            report=None,
            prompt_version=CASE_REPORT_PROMPT_VERSION,
            provider="deterministic",
            model="case-template",
            validation_errors=(str(error),),
            failure_code="case_report_generation_failed",
            failure_message="The Case report could not be generated from the selected analysis.",
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )


def build_case_template_report(
    report_input: CaseReportInput,
) -> StructuredReport:
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    claims = build_case_report_claims(report_input, trace)
    sections = build_case_report_sections(report_input, trace)
    limitations = build_case_report_limitations(report_input)
    return StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title=report_input.case_title or "รายงานสรุปผลการวิเคราะห์คดีเบื้องต้น",
        sections=sections,
        claims=claims,
        limitations=limitations,
    )


__all__ = [
    "CASE_REPORT_PROMPT_VERSION",
    "build_case_template_report",
    "run_case_report_generation",
]
