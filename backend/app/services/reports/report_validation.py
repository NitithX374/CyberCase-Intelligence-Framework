from __future__ import annotations

from app.schemas.reports import (
    PRELIMINARY_REPORT_SECTION_IDS,
    StructuredReport,
)
from app.services.reports.report_contracts import ReportValidationError


def validate_case_structured_report(
    report: StructuredReport,
    *,
    source_evidence_ids: set[str],
    mitre_ids: set[str],
) -> None:
    section_ids = tuple(section.section_id for section in report.sections)
    if section_ids != PRELIMINARY_REPORT_SECTION_IDS:
        raise ReportValidationError("Report sections do not match the required order")
    claim_ids: set[str] = set()
    for claim in report.claims:
        if claim.claim_id in claim_ids:
            raise ReportValidationError("Report claim identifiers must be unique")
        claim_ids.add(claim.claim_id)
        if not set(claim.source_evidence_ids).issubset(source_evidence_ids):
            raise ReportValidationError("A case report claim cites a non-evidence source")
        if not set(claim.mitre_technique_ids).issubset(mitre_ids):
            raise ReportValidationError("A report claim cites an unadmitted MITRE technique")


__all__ = [
    "validate_case_structured_report",
]
