from __future__ import annotations

import hashlib
import json

from app.schemas.reports import (
    PRELIMINARY_REPORT_SECTION_IDS,
    StructuredReport,
)
from app.services.reports.case_report_contracts import CaseReportInputSnapshot
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
        if claim.source_message_ids:
            raise ReportValidationError("Case reports cannot cite chat message IDs")
        if not set(claim.source_evidence_ids).issubset(source_evidence_ids):
            raise ReportValidationError("A case report claim cites a non-evidence source")
        if not set(claim.mitre_technique_ids).issubset(mitre_ids):
            raise ReportValidationError("A report claim cites an unadmitted MITRE technique")


def source_snapshot_hash(
    snapshot: CaseReportInputSnapshot | dict[str, object],
) -> str:
    payload = snapshot.model_dump(mode="json") if hasattr(snapshot, "model_dump") else dict(snapshot)
    payload.pop("created_at", None)
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


__all__ = [
    "source_snapshot_hash",
    "validate_case_structured_report",
]
