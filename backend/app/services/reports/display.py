from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.schemas.reports import ReportClaim, ReportSection, StructuredReport
from app.services.analysis.contracts import CaseAnalysisClaim, CaseAnalysisTrace
from app.services.reports.content import (
    EPISTEMIC_STATUS_LABELS,
    GAP_STATUS_LABELS,
    PRIORITY_LABELS,
    SUPPORT_TYPE_LABELS,
    labels_for_sources,
    reference_labels,
    source_labels_for_report,
)
from app.services.reports.contracts import CaseReportInput

SECTION_TITLES = {
    "case_summary": "สรุปข้อเท็จจริงของคดี",
    "case_evidence": "ข้อเท็จจริงและตัวบ่งชี้ที่ตรวจพบ",
    "mitre_attack_mapping": "การจำแนกพฤติกรรมตามกรอบ MITRE ATT&CK",
    "mapping_rationale": "เหตุผลประกอบการจำแนกพฤติกรรม",
    "evidence_to_examine": "ประเด็นที่ต้องตรวจสอบเพิ่มเติม",
    "preliminary_recommendations": "ข้อเสนอแนะเบื้องต้น",
    "system_limitations": "ข้อจำกัดและข้อสงวนของรายงาน",
}

UNTITLED = {"new case", "cybercase investigation"}

THAI_MONTHS = (
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
)
BANGKOK = timezone(timedelta(hours=7))


def thai_date(moment: datetime, *, with_time: bool = False) -> str:
    local = moment.astimezone(BANGKOK)
    date = f"{local.day} {THAI_MONTHS[local.month - 1]} {local.year + 543}"
    return f"{date} เวลา {local:%H.%M} น." if with_time else date


@dataclass(frozen=True)
class ReportIssue:
    version_number: int
    created_at: datetime


@dataclass(frozen=True)
class ReportDisplaySource:
    label: str
    kind: str
    detail: str


@dataclass(frozen=True)
class ReportDisplayClaim:
    ordinal: int
    claim_id: str
    text: str
    support_label: str
    epistemic_label: str
    is_inference: bool
    source_labels: tuple[str, ...]
    contradicting_source_labels: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    contradicting_quotes: tuple[str, ...]
    reasoning_summary: str | None


@dataclass(frozen=True)
class ReportDisplayParty:
    name: str
    role: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class ReportDisplayEvent:
    time: str
    event: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class ReportDisplayImpact:
    description: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class ReportDisplayTechnique:
    technique_id: str
    name: str
    tactic: str
    meaning: str
    reason: str
    findings: tuple[int, ...]
    references: tuple[str, ...]


@dataclass(frozen=True)
class ReportDisplayGap:
    topic: str
    priority: str
    status: str
    description: str
    reason: str


@dataclass(frozen=True)
class CaseReportDisplay:
    subject: str
    issue: ReportIssue | None
    issued: str | None
    analysed: str | None
    summary: str
    parties: tuple[ReportDisplayParty, ...]
    timeline: tuple[ReportDisplayEvent, ...]
    impacts: tuple[ReportDisplayImpact, ...]
    claims: tuple[ReportDisplayClaim, ...]
    techniques: tuple[ReportDisplayTechnique, ...]
    techniques_matched: bool
    gaps: tuple[ReportDisplayGap, ...]
    sources: tuple[ReportDisplaySource, ...]
    sections: dict[str, ReportSection]
    titles: dict[str, str]


def build_case_report_display(
    report_input: CaseReportInput,
    report: StructuredReport,
    issue: ReportIssue | None = None,
) -> CaseReportDisplay:
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    labels = source_labels_for_report(report_input)
    trace_claims = {claim.claim_id: claim for claim in trace.claims}

    def references(claim_ids: list[str]) -> tuple[str, ...]:
        return reference_labels(claim_ids, trace_claims, labels)

    claims, ordinals = display_claims(report.claims, trace_claims, labels)
    techniques, matched = display_techniques(report_input, trace, ordinals, references)
    return CaseReportDisplay(
        subject=subject(report.title),
        issue=issue,
        issued=thai_date(issue.created_at, with_time=True) if issue else None,
        analysed=(
            thai_date(report_input.analysis_created_at)
            if report_input.analysis_created_at
            else None
        ),
        summary=report_input.analysis_summary,
        parties=tuple(
            ReportDisplayParty(party.name, party.role, references(party.claim_ids))
            for party in trace.involved_parties
        ),
        timeline=tuple(
            ReportDisplayEvent(event.time, event.event, references(event.claim_ids))
            for event in trace.timeline
        ),
        impacts=tuple(
            ReportDisplayImpact(impact.description, references(impact.claim_ids))
            for impact in trace.impacts
        ),
        claims=claims,
        techniques=techniques,
        techniques_matched=matched,
        gaps=tuple(
            ReportDisplayGap(
                topic=gap.topic,
                priority=PRIORITY_LABELS[gap.priority],
                status=GAP_STATUS_LABELS[gap.status],
                description=gap.description,
                reason=gap.reason,
            )
            for gap in trace.gaps
        ),
        sources=evidence_register(report_input, labels),
        sections={section.section_id: section for section in report.sections},
        titles=SECTION_TITLES,
    )


def subject(title: str) -> str:
    cleaned = title.strip()
    if not cleaned or cleaned.casefold() in UNTITLED:
        return "ไม่ได้ระบุชื่อเรื่อง"
    return cleaned


def display_claims(
    report_claims: list[ReportClaim],
    trace_claims: dict[str, CaseAnalysisClaim],
    labels: dict[str, str],
) -> tuple[tuple[ReportDisplayClaim, ...], dict[str, int]]:
    by_text: dict[str, int] = {}
    ordinals: dict[str, int] = {}
    claims: list[ReportDisplayClaim] = []
    for claim in report_claims:
        text = claim.text.strip()
        if text in by_text:
            ordinals[claim.claim_id] = by_text[text]
            continue
        ordinal = len(claims) + 1
        by_text[text] = ordinals[claim.claim_id] = ordinal
        claims.append(display_claim(ordinal, claim, trace_claims.get(claim.claim_id), labels))
    return tuple(claims), ordinals


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
    return ReportDisplayClaim(
        ordinal=ordinal,
        claim_id=report_claim.claim_id,
        text=report_claim.text,
        support_label=SUPPORT_TYPE_LABELS[report_claim.support_type],
        epistemic_label=EPISTEMIC_STATUS_LABELS.get(
            getattr(trace_claim, "epistemic_status", "unknown"),
            "ไม่ระบุสถานะ",
        ),
        is_inference=report_claim.support_type == "analytical_inference",
        source_labels=labels_for_sources(supporting_source_ids, source_labels),
        contradicting_source_labels=labels_for_sources(
            getattr(trace_claim, "contradicting_source_ids", []),
            source_labels,
        ),
        supporting_quotes=quotes_from_citations(getattr(trace_claim, "supporting_citations", [])),
        contradicting_quotes=quotes_from_citations(
            getattr(trace_claim, "contradicting_citations", [])
        ),
        reasoning_summary=getattr(trace_claim, "reasoning_summary", None),
    )


def display_techniques(
    report_input: CaseReportInput,
    trace: CaseAnalysisTrace,
    ordinals: dict[str, int],
    references: Callable[[list[str]], tuple[str, ...]],
) -> tuple[tuple[ReportDisplayTechnique, ...], bool]:
    augmentation = report_input.technical_augmentation
    if augmentation is None:
        return (), False
    rows = {
        str(row.get("technique_id")): row
        for row in augmentation.mitre_table
        if isinstance(row, dict) and row.get("technique_id")
    }
    if augmentation.status == "retrieved_with_matches":
        return (
            tuple(
                ReportDisplayTechnique(
                    technique_id=association.technique_id,
                    name=row_text(rows.get(association.technique_id), "name"),
                    tactic=row_text(rows.get(association.technique_id), "tactic"),
                    meaning=association.plain_meaning.strip(),
                    reason=association.reason,
                    findings=tuple(
                        sorted(
                            {
                                ordinals[claim_id]
                                for claim_id in association.claim_ids
                                if claim_id in ordinals
                            }
                        )
                    ),
                    references=references(association.claim_ids),
                )
                for association in trace.mitre_associations
            ),
            True,
        )
    if augmentation.status == "retrieved_from_rag":
        return (
            tuple(
                ReportDisplayTechnique(
                    technique_id=str(row.get("technique_id") or row.get("name") or "-"),
                    name=row_text(row, "name"),
                    tactic=row_text(row, "tactic"),
                    meaning="",
                    reason="",
                    findings=(),
                    references=(),
                )
                for row in augmentation.mitre_table
                if isinstance(row, dict)
            ),
            False,
        )
    return (), False


def row_text(row: dict[str, object] | None, key: str) -> str:
    value = (row or {}).get(key)
    return value.strip() if isinstance(value, str) else ""


def evidence_register(
    report_input: CaseReportInput, labels: dict[str, str]
) -> tuple[ReportDisplaySource, ...]:
    register = [
        ReportDisplaySource(
            label=labels[source.source_id],
            kind=SOURCE_KINDS.get(source.source_kind, "ข้อมูลประกอบคดี"),
            detail=(
                source.filename or "เอกสารที่ไม่ได้ระบุชื่อ"
                if source.source_kind == "document"
                else excerpt(source.text)
            ),
        )
        for source in report_input.source_bundle.sources
    ]
    register.extend(
        ReportDisplaySource(
            label=labels[item.qa_id],
            kind="คำตอบติดตามผล",
            detail=f"คำถาม: {item.question}",
        )
        for item in report_input.followup_history
        if item.is_answered and item.qa_id in labels
    )
    return tuple(register)


SOURCE_KINDS = {
    "document": "เอกสาร",
    "narrative": "คำบรรยายเหตุการณ์",
    "followup_answer": "คำตอบติดตามผล",
}


def excerpt(text: str, limit: int = 120) -> str:
    line = " ".join(text.split())
    return f"{line[:limit].rstrip()}…" if len(line) > limit else line


def quotes_from_citations(citations: list[object]) -> tuple[str, ...]:
    return tuple(
        citation.exact_quote
        for citation in citations
        if isinstance(getattr(citation, "exact_quote", None), str) and citation.exact_quote.strip()
    )


__all__ = [
    "SECTION_TITLES",
    "CaseReportDisplay",
    "ReportDisplayClaim",
    "ReportDisplaySource",
    "ReportIssue",
    "build_case_report_display",
    "thai_date",
]
