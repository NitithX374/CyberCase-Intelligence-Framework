from __future__ import annotations

from app.schemas.reports import StructuredReport
from app.services.reports.report_analysis_projection import (
    _analysis_text,
    _claim_source_ids,
    _clean_inline,
    _list_items,
    _section_body,
    _source_label,
    _trace_claims,
    _unique,
)
from app.services.reports.report_contracts import ReportInputSnapshot
from app.services.reports.report_view_model_contracts import (
    EvidenceViewRow,
    ReportLanguage,
    UnresolvedIssueViewRow,
)


def project_finding_rows(
    structured: StructuredReport | None,
    snapshot: ReportInputSnapshot | None,
    *,
    language: ReportLanguage,
) -> list[EvidenceViewRow]:
    rows = _trace_finding_rows(snapshot, language)
    if rows or structured is None:
        return rows
    return _structured_finding_rows(structured, snapshot, language)


def project_unresolved_issues(
    snapshot: ReportInputSnapshot | None,
    *,
    language: ReportLanguage,
) -> list[UnresolvedIssueViewRow]:
    tokens = (
        ("ข้อสังเกตหรือข้อมูลที่ยังไม่แน่นอน", "ข้อมูลที่ยังไม่แน่นอน")
        if language == "th"
        else ("uncertain", "unconfirmed", "not established")
    )
    items = _list_items(_section_body(_analysis_text(snapshot), tokens))
    if not items:
        items = [
            _clean_inline(claim.get("text"))
            for claim in _trace_claims(snapshot)
            if claim.get("epistemic_status")
            in {"not_established", "explicitly_unknown"}
        ]
    if snapshot is not None:
        items.extend(snapshot.unresolved_issues)
    return [
        UnresolvedIssueViewRow(
            description=item,
            category="ประเด็นที่ต้องยืนยัน" if language == "th" else "Requires verification",
            reason=(
                "ปรากฏเป็นข้อมูลที่ยังไม่แน่นอนในบทวิเคราะห์"
                if language == "th"
                else "Recorded as unresolved in the analysis"
            ),
        )
        for item in _unique(item for item in items if item)
    ]


def _trace_finding_rows(
    snapshot: ReportInputSnapshot | None,
    language: ReportLanguage,
) -> list[EvidenceViewRow]:
    rows: list[EvidenceViewRow] = []
    for claim in _trace_claims(snapshot):
        text = _clean_inline(claim.get("text"))
        status = str(claim.get("epistemic_status") or "reported")
        if not text or status in {"not_established", "explicitly_unknown"}:
            continue
        rows.append(
            EvidenceViewRow(
                item_id=str(claim.get("claim_id") or f"F-{len(rows) + 1:02d}"),
                title="ข้อเท็จจริงที่รายงาน" if language == "th" else "Reported finding",
                artifact_type=_finding_type(status, language),
                description=text,
                source_type=_source_label(
                    _claim_source_ids(claim),
                    snapshot,
                    language,
                ),
                confidence=status,
            )
        )
    return rows


def _structured_finding_rows(
    structured: StructuredReport,
    snapshot: ReportInputSnapshot | None,
    language: ReportLanguage,
) -> list[EvidenceViewRow]:
    rows: list[EvidenceViewRow] = []
    for claim in structured.claims:
        if claim.claim_id == "R-01" or not claim.text.strip():
            continue
        rows.append(
            EvidenceViewRow(
                item_id=claim.claim_id,
                title="ข้อเท็จจริงที่รายงาน" if language == "th" else "Reported finding",
                artifact_type="ข้อมูลจากบทวิเคราะห์"
                if language == "th"
                else "Analysis record",
                description=_clean_inline(claim.text),
                source_type=_source_label(claim.source_message_ids, snapshot, language),
                confidence=claim.support_type,
            )
        )
    return rows


def _finding_type(status: str, language: ReportLanguage) -> str:
    if status == "reported":
        return "ข้อมูลที่ระบุในสำนวน" if language == "th" else "Reported material"
    return "ข้อสังเกตเชิงวิเคราะห์" if language == "th" else "Analytical observation"


__all__ = ["project_finding_rows", "project_unresolved_issues"]
