from __future__ import annotations

from app.reports.contracts import CaseReportInput
from app.reports.schemas import (
    ReportFinding,
    ReportMark,
    ReportPlace,
    ReportQuoteContext,
    ReportUnverifiedQuote,
)
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation

EPISTEMIC_STATUS_LABELS = {
    "reported": "ปรากฏในหลักฐาน",
    "suspected": "อยู่ระหว่างตรวจสอบ",
    "contradicted": "มีข้อมูลขัดแย้ง",
    "not_established": "ยังไม่ยืนยัน",
    "unknown": "ไม่ทราบ",
    "not_confirmed": "ยังไม่ยืนยัน",
}


def source_labels_for_report(report_input: CaseReportInput) -> dict[str, str]:
    labels = {
        source.source_id: f"E-{index:02d}"
        for index, source in enumerate(report_input.source_bundle.sources, 1)
    }
    answered = [item for item in report_input.followup_history if item.is_answered]
    labels.update({item.qa_id: f"Q-{index:02d}" for index, item in enumerate(answered, 1)})
    return labels


def labels_for_sources(source_ids: list[str], source_labels: dict[str, str]) -> list[str]:
    return list(
        dict.fromkeys(
            source_labels[source_id] for source_id in source_ids if source_id in source_labels
        )
    )


def reference_labels(
    claim_ids: list[str],
    claims_by_id: dict[str, CaseAnalysisClaim],
    source_labels: dict[str, str],
) -> list[str]:
    source_ids: list[str] = []
    for claim_id in claim_ids:
        claim = claims_by_id.get(claim_id)
        if claim is not None:
            source_ids.extend(
                claim_source_ids(claim.supporting_citations, claim.supporting_source_ids)
            )
            source_ids.extend(
                claim_source_ids(claim.contradicting_citations, claim.contradicting_source_ids)
            )
    return labels_for_sources(source_ids, source_labels)


def claim_source_ids(citations: list[CaseSourceCitation], named: list[str]) -> list[str]:
    return [citation.source_id for citation in citations] or named


def report_findings(
    claims: list[CaseAnalysisClaim],
    labels: dict[str, str],
) -> tuple[list[ReportFinding], dict[str, int]]:
    by_text: dict[str, int] = {}
    ordinals: dict[str, int] = {}
    findings: list[ReportFinding] = []
    for claim in claims:
        text = claim.text.strip()
        if text in by_text:
            ordinals[claim.claim_id] = by_text[text]
            continue
        ordinal = len(findings) + 1
        by_text[text] = ordinals[claim.claim_id] = ordinal
        findings.append(
            ReportFinding(
                ordinal=ordinal,
                text=claim.text,
                status=EPISTEMIC_STATUS_LABELS.get(claim.epistemic_status, "ไม่ระบุสถานะ"),
                is_inference=claim.claim_type == "analytical_inference",
                source_labels=labels_for_sources(
                    claim_source_ids(claim.supporting_citations, claim.supporting_source_ids),
                    labels,
                ),
                contradicting_source_labels=labels_for_sources(
                    claim_source_ids(claim.contradicting_citations, claim.contradicting_source_ids),
                    labels,
                ),
                supporting_quotes=quotes(claim.supporting_citations),
                contradicting_quotes=quotes(claim.contradicting_citations),
                supporting_contexts=quote_contexts(claim.supporting_citations),
                contradicting_contexts=quote_contexts(claim.contradicting_citations),
                supporting_tolerated=tolerated_places(claim.supporting_citations),
                contradicting_tolerated=tolerated_places(claim.contradicting_citations),
                supporting_marked=marked_places(claim.supporting_citations),
                contradicting_marked=marked_places(claim.contradicting_citations),
                unverified_quotes=unverified_quotes(claim),
                reasoning_summary=claim.reasoning_summary,
            )
        )
    return findings, ordinals


def quotes(citations: list[CaseSourceCitation]) -> list[str]:
    return [citation.exact_quote for citation in citations if citation.exact_quote.strip()]


def unverified_quotes(claim: CaseAnalysisClaim) -> list[ReportUnverifiedQuote]:
    return [
        ReportUnverifiedQuote(
            written_quote=item.written_quote,
            evidence_unit_id=item.evidence_unit_id,
            places=[
                ReportPlace(written=difference.written, source=difference.source)
                for difference in (item.near_passage.differences if item.near_passage else [])
            ],
            meaning_passage=(
                item.meaning_passage.source_text
                if item.meaning_passage and claim.epistemic_status == "not_confirmed"
                else None
            ),
        )
        for item in claim.unverified_citations
    ]


def tolerated_places(citations: list[CaseSourceCitation]) -> list[list[ReportPlace]]:
    return [
        [
            ReportPlace(written=difference.written, source=difference.source)
            for difference in citation.tolerated_differences
        ]
        for citation in citations
        if citation.exact_quote.strip()
    ]


def marked_places(citations: list[CaseSourceCitation]) -> list[list[ReportMark]]:
    return [
        [
            ReportMark(marks=" ".join(words[:-1]), place=words[-1])
            for words in (flag.detail.split() for flag in citation.review_flags)
            if len(words) > 1 and words[-1] in ("ignored", "edge")
        ]
        for citation in citations
        if citation.exact_quote.strip()
    ]


def quote_contexts(citations: list[CaseSourceCitation]) -> list[ReportQuoteContext | None]:
    return [
        ReportQuoteContext(**citation.context.model_dump()) if citation.context else None
        for citation in citations
        if citation.exact_quote.strip()
    ]
