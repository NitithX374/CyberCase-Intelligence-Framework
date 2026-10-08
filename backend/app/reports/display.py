from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.reports.contracts import CaseReportInput
from app.reports.findings import (
    EPISTEMIC_STATUS_LABELS,
    reference_labels,
    report_findings,
    source_labels_for_report,
)
from app.reports.limitations import clarification_limitation, report_limitations
from app.reports.schemas import (
    CaseReportContent,
    ReportEvent,
    ReportGap,
    ReportImpact,
    ReportParty,
    ReportSource,
    ReportSummaryUnit,
)
from app.reports.technical import augmentation_notes, report_techniques
from app.trace.claims import CaseAnalysisGap
from app.trace.trace import CaseAnalysisTrace

CHECKLIST_TOPICS = {
    "who_affected": "ผู้ได้รับผลกระทบ",
    "who_responsible": "ผู้กระทำ",
    "what": "สิ่งที่เกิดขึ้น",
    "when": "เวลาที่เกิดเหตุ",
    "where": "สถานที่เกิดเหตุ",
    "why": "มูลเหตุจูงใจ",
    "how": "วิธีการที่ใช้",
    "how_much": "ขอบเขตความเสียหาย",
}

GAP_STATUS_LABELS = {
    "NOT_PROVIDED": "ยังไม่มีข้อมูล",
    "EXPLICITLY_UNKNOWN": "ระบุว่ายังไม่ทราบ",
    "AMBIGUOUS": "ข้อมูลกำกวม",
    "CONFLICTING": "ข้อมูลขัดแย้งกัน",
}

PRIORITY_LABELS = {
    "high": "สูง",
    "medium": "กลาง",
    "low": "ต่ำ",
}

SOURCE_KINDS = {
    "document": "เอกสาร",
    "narrative": "คำบรรยายเหตุการณ์",
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


def build_case_report_content(report_input: CaseReportInput) -> CaseReportContent:
    trace = report_input.analysis_trace
    augmentation = report_input.technical_augmentation
    labels = source_labels_for_report(report_input)
    claims_by_id = {claim.claim_id: claim for claim in trace.claims}

    def references(claim_ids: list[str]) -> list[str]:
        return reference_labels(claim_ids, claims_by_id, labels)

    findings, ordinals = report_findings(trace.claims, labels)
    techniques, matched = report_techniques(augmentation, trace, ordinals, references)
    mapping_note, rationale_note = augmentation_notes(augmentation)
    return CaseReportContent(
        title=subject(report_input.case_title),
        analysed=(
            thai_date(report_input.analysis_created_at)
            if report_input.analysis_created_at
            else None
        ),
        summary=report_input.analysis_summary,
        views_derived_from_claims=trace.view_extraction is not None,
        summary_units=[
            ReportSummaryUnit(
                text=unit.text,
                references=sorted(
                    {ordinals[claim_id] for claim_id in unit.claim_ids if claim_id in ordinals}
                ),
                support=unit.support,
            )
            for unit in trace.summary_units
        ],
        parties=[
            ReportParty(
                name=party.name,
                role=party.role,
                claim_context=[
                    claims_by_id[claim_id].text
                    for claim_id in party.claim_ids
                    if trace.view_extraction is not None and claim_id in claims_by_id
                ],
                references=references(party.claim_ids),
                support=party.support,
                projection_grounding=party.projection_grounding,
            )
            for party in trace.involved_parties
        ],
        timeline=[
            ReportEvent(
                time=event.time,
                event=event.event,
                references=references(event.claim_ids),
                support=event.support,
                projection_grounding=event.projection_grounding,
            )
            for event in trace.timeline
        ],
        impacts=[
            ReportImpact(
                description=impact.description,
                references=references(impact.claim_ids),
                support=impact.support,
                projection_grounding=impact.projection_grounding,
            )
            for impact in trace.impacts
        ],
        findings=findings,
        techniques=techniques,
        techniques_matched=matched,
        mapping_note=mapping_note,
        rationale_note=rationale_note,
        gaps=[
            ReportGap(
                topic=gap_topic(gap),
                priority=PRIORITY_LABELS[gap.priority],
                status=GAP_STATUS_LABELS[gap.status],
                description=gap.description,
                reason=gap.reason,
            )
            for gap in trace.gaps
        ],
        recommendations=recommendation_items(trace),
        limitations=report_limitations(report_input),
        sources=source_register(report_input, labels),
    )


def subject(title: str) -> str:
    cleaned = title.strip()
    if not cleaned or cleaned.casefold() in UNTITLED:
        return "ไม่ได้ระบุชื่อเรื่อง"
    return cleaned


def gap_topic(gap: CaseAnalysisGap) -> str:
    if gap.topic != gap.gap_key:
        return gap.topic
    return CHECKLIST_TOPICS.get(gap.gap_key, gap.gap_key.replace("_", " "))


def recommendation_items(trace: CaseAnalysisTrace) -> list[str]:
    items = [
        f"ตรวจสอบเพิ่มเติมในประเด็น {gap_topic(gap)}: ดำเนินการสืบสวน/สอบสวนเพื่อคลี่คลายข้อเท็จจริง ({PRIORITY_LABELS[gap.priority]})"
        for gap in trace.gaps
    ]
    items.extend(
        [
            "ตรวจสอบเอกสารต้นฉบับและความสอดคล้องของข้อมูลก่อนใช้เป็นข้อเท็จจริง",
            "เปรียบเทียบข้อมูลจากหลายแหล่งและบันทึกผลที่ยืนยันได้แยกจากข้อสันนิษฐาน",
            "รักษาข้อมูลต้นฉบับและบันทึก Chain of Custody ไว้เพื่อให้ตรวจสอบย้อนกลับได้",
        ]
    )
    return list(dict.fromkeys(items))


def source_register(report_input: CaseReportInput, labels: dict[str, str]) -> list[ReportSource]:
    register = [
        ReportSource(
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
        ReportSource(
            label=labels[item.qa_id], kind="คำตอบติดตามผล", detail=f"คำถาม: {item.question}"
        )
        for item in report_input.followup_history
        if item.is_answered and item.qa_id in labels
    )
    return register


def excerpt(text: str, limit: int = 120) -> str:
    line = " ".join(text.split())
    return f"{line[:limit].rstrip()}…" if len(line) > limit else line


__all__ = [
    "EPISTEMIC_STATUS_LABELS",
    "GAP_STATUS_LABELS",
    "PRIORITY_LABELS",
    "build_case_report_content",
    "clarification_limitation",
    "recommendation_items",
    "report_limitations",
    "thai_date",
]
