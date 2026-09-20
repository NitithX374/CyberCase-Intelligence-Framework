from __future__ import annotations

from dataclasses import dataclass

from app.schemas.reports import ReportClaim, StructuredReport
from app.services.analysis.contracts import CaseAnalysisClaim, CaseAnalysisTrace
from app.services.reports.content import (
    EPISTEMIC_STATUS_LABELS,
    SUPPORT_TYPE_LABELS,
)
from app.services.reports.contracts import CaseReportInput


@dataclass(frozen=True)
class ReportDisplaySource:
    label: str
    filename: str


@dataclass(frozen=True)
class ReportDisplayClaim:
    ordinal: int
    claim_id: str
    text: str
    support_label: str
    epistemic_label: str
    source_labels: tuple[str, ...]
    contradicting_source_labels: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    contradicting_quotes: tuple[str, ...]
    reasoning_summary: str | None


@dataclass(frozen=True)
class CaseReportDisplay:
    claims: tuple[ReportDisplayClaim, ...]
    sources: tuple[ReportDisplaySource, ...]


def build_case_report_display(
    report_input: CaseReportInput,
    report: StructuredReport,
) -> CaseReportDisplay:
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    source_labels = {
        source.source_id: f"E-{index:02d}"
        for index, source in enumerate(report_input.source_bundle.sources, 1)
    }
    sources = tuple(
        ReportDisplaySource(
            label=source_labels[source.source_id],
            filename=source.filename or "แหล่งข้อมูลที่ไม่ได้ระบุชื่อเอกสาร",
        )
        for source in report_input.source_bundle.sources
    )
    trace_claims = {claim.claim_id: claim for claim in trace.claims}
    seen_texts: set[str] = set()
    display_claims_list: list[ReportDisplayClaim] = []
    ordinal = 1
    for claim in report.claims:
        clean = claim.text.strip()
        if clean in seen_texts:
            continue
        seen_texts.add(clean)
        display_claims_list.append(
            display_claim(ordinal, claim, trace_claims.get(claim.claim_id), source_labels)
        )
        ordinal += 1
    claims = tuple(display_claims_list)
    return CaseReportDisplay(claims=claims, sources=sources)


def display_claim(
    ordinal: int,
    report_claim: ReportClaim,
    source_claim: CaseAnalysisClaim | None,
    source_labels: dict[str, str],
) -> ReportDisplayClaim:
    trace_claim = source_claim
    supporting_source_ids = (
        trace_claim.supporting_source_ids if trace_claim is not None else report_claim.source_ids
    )
    source_labels_for_claim = labels_for_sources(supporting_source_ids, source_labels)
    contradicting_source_labels = labels_for_sources(
        getattr(trace_claim, "contradicting_source_ids", []),
        source_labels,
    )
    supporting_quotes = quotes_from_citations(getattr(trace_claim, "supporting_citations", []))
    contradicting_quotes = quotes_from_citations(
        getattr(trace_claim, "contradicting_citations", [])
    )
    return ReportDisplayClaim(
        ordinal=ordinal,
        claim_id=report_claim.claim_id,
        text=report_claim.text,
        support_label=SUPPORT_TYPE_LABELS[report_claim.support_type],
        epistemic_label=EPISTEMIC_STATUS_LABELS.get(
            getattr(trace_claim, "epistemic_status", "unknown"),
            "ไม่ระบุสถานะ",
        ),
        source_labels=source_labels_for_claim,
        contradicting_source_labels=contradicting_source_labels,
        supporting_quotes=supporting_quotes,
        contradicting_quotes=contradicting_quotes,
        reasoning_summary=getattr(trace_claim, "reasoning_summary", None),
    )


def labels_for_sources(source_ids: list[str], source_labels: dict[str, str]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            source_labels[source_id] for source_id in source_ids if source_id in source_labels
        )
    )


def quotes_from_citations(citations: list[object]) -> tuple[str, ...]:
    return tuple(
        citation.exact_quote
        for citation in citations
        if isinstance(getattr(citation, "exact_quote", None), str) and citation.exact_quote.strip()
    )


__all__ = [
    "CaseReportDisplay",
    "ReportDisplayClaim",
    "ReportDisplaySource",
    "build_case_report_display",
]
