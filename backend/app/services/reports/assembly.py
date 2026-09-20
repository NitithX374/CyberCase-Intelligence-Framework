from __future__ import annotations

from app.schemas.reports import StructuredReport
from app.services.analysis.contracts import CaseAnalysisTrace
from app.services.reports.content import (
    build_case_report_claims,
    build_case_report_limitations,
    build_case_report_sections,
)
from app.services.reports.contracts import (
    CaseReportInput,
    case_source_ids,
    validate_case_structured_report,
)


def build_case_report(report_input: CaseReportInput) -> StructuredReport:
    """Render the report from the saved analysis.

    Checked once, here. A failure means the renderer is wrong, so it raises
    rather than being stored as a report that failed.
    """

    report = build_case_template_report(report_input)
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    validate_case_structured_report(
        report,
        allowed_source_ids=case_source_ids(report_input),
        mitre_ids={association.technique_id for association in trace.mitre_associations},
    )
    return report


def build_case_template_report(
    report_input: CaseReportInput,
) -> StructuredReport:
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    claims = build_case_report_claims(report_input, trace)
    sections = build_case_report_sections(report_input, trace)
    limitations = build_case_report_limitations(report_input, trace)
    return StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title=report_input.case_title or "รายงานสรุปผลการวิเคราะห์คดีเบื้องต้น",
        sections=sections,
        claims=claims,
        limitations=limitations,
    )


__all__ = [
    "build_case_report",
    "build_case_template_report",
]
