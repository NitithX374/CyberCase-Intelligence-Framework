from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from app.analysis.technical_context.contracts import CaseTechnicalAugmentation
from app.reports.contracts import CaseReportInput
from app.reports.schemas import (
    CaseReportContent,
    ReportEvent,
    ReportFinding,
    ReportGap,
    ReportImpact,
    ReportMark,
    ReportParty,
    ReportPlace,
    ReportQuoteContext,
    ReportSource,
    ReportSummaryUnit,
    ReportTechnique,
    ReportUnverifiedQuote,
)
from app.trace.claims import CaseAnalysisClaim, CaseAnalysisGap, CaseSourceCitation
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

EPISTEMIC_STATUS_LABELS = {
    "reported": "ปรากฏในหลักฐาน",
    "suspected": "อยู่ระหว่างตรวจสอบ",
    "contradicted": "มีข้อมูลขัดแย้ง",
    "not_established": "ยังไม่ยืนยัน",
    "unknown": "ไม่ทราบ",
    "not_confirmed": "ยังไม่ยืนยัน",
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

CLARIFICATION_LIMITATIONS = {
    "max_rounds_reached": (
        "ระบบใช้สิทธิ์ถามข้อมูลเพิ่มเติมจนครบจำนวนรอบที่กำหนดแล้ว "
        "ประเด็นที่ยังค้างอยู่ในหัวข้อข้อมูลที่ยังขาด จึงยังไม่ได้ถาม ไม่ใช่ว่าไม่จำเป็นต้องถาม"
    ),
    "gaps_exhausted": ("ระบบถามทุกประเด็นที่ถามได้แล้ว ประเด็นที่ยังค้างอยู่คือสิ่งที่ผู้ใช้ตอบไม่ได้ หรือหลักฐานที่มีตอบไม่ได้"),
    "no_eligible_gap": (
        "ประเด็นที่ยังค้างอยู่ไม่มีข้อใดที่การถามผู้ใช้จะช่วยได้ "
        "เพราะเป็นเรื่องที่ผู้ใช้ระบุว่าไม่ทราบ หรือต้องยืนยันจากหลักฐานเพิ่มเติมแทนการสอบถาม"
    ),
}

UNREACHABLE_SERVICE_CODES = {"rag_service_error", "rag_service_unavailable"}

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
    return CaseReportContent(
        title=subject(report_input.case_title),
        analysed=(
            thai_date(report_input.analysis_created_at)
            if report_input.analysis_created_at
            else None
        ),
        summary=report_input.analysis_summary,
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
                references=references(party.claim_ids),
                support=party.support,
            )
            for party in trace.involved_parties
        ],
        timeline=[
            ReportEvent(
                time=event.time,
                event=event.event,
                references=references(event.claim_ids),
                support=event.support,
            )
            for event in trace.timeline
        ],
        impacts=[
            ReportImpact(
                description=impact.description,
                references=references(impact.claim_ids),
                support=impact.support,
            )
            for impact in trace.impacts
        ],
        findings=findings,
        techniques=techniques,
        techniques_matched=matched,
        mapping_note=mapping_note(augmentation),
        rationale_note=rationale_note(augmentation),
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


def cited_source_ids(citations: list[CaseSourceCitation]) -> list[str]:
    return [citation.source_id for citation in citations]


def claim_source_ids(citations: list[CaseSourceCitation], named: list[str]) -> list[str]:
    return cited_source_ids(citations) or named


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
            places=[
                ReportPlace(written=difference.written, source=difference.source)
                for difference in (item.near_passage.differences if item.near_passage else [])
            ],
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


def report_techniques(
    augmentation: CaseTechnicalAugmentation | None,
    trace: CaseAnalysisTrace,
    ordinals: dict[str, int],
    references: Callable[[list[str]], list[str]],
) -> tuple[list[ReportTechnique], bool]:
    if augmentation is None:
        return [], False
    rows = {
        str(row["technique_id"]): row for row in augmentation.mitre_table if row.get("technique_id")
    }
    if augmentation.status == "retrieved_with_matches":
        return [
            ReportTechnique(
                technique_id=association.technique_id,
                name=row_text(rows.get(association.technique_id), "name"),
                tactic=row_text(rows.get(association.technique_id), "tactic"),
                meaning=association.plain_meaning.strip(),
                reason=association.reason,
                findings=sorted(
                    {
                        ordinals[claim_id]
                        for claim_id in association.claim_ids
                        if claim_id in ordinals
                    }
                ),
                references=references(association.claim_ids),
            )
            for association in trace.mitre_associations
        ], True
    if augmentation.status == "retrieved_from_rag":
        return [
            ReportTechnique(
                technique_id=str(row.get("technique_id") or row.get("name") or "-"),
                name=row_text(row, "name"),
                tactic=row_text(row, "tactic"),
                meaning="",
                reason="",
            )
            for row in augmentation.mitre_table
        ], False
    return [], False


def row_text(row: dict[str, object] | None, key: str) -> str:
    value = (row or {}).get(key)
    return value.strip() if isinstance(value, str) else ""


def failure_detail(augmentation: CaseTechnicalAugmentation) -> str:
    if augmentation.failure_code in UNREACHABLE_SERVICE_CODES:
        return "ไม่สามารถเชื่อมต่อกับบริการภายนอกได้ในขณะนี้"
    return f"ระบบภายนอกขัดข้อง ({augmentation.failure_code})"


def mapping_note(augmentation: CaseTechnicalAugmentation | None) -> str | None:
    if augmentation is None:
        return "ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้สำหรับผลวิเคราะห์นี้"
    if augmentation.status == "not_applicable":
        return "ไม่พบเงื่อนไขที่จำเป็นต้องใช้ MITRE ATT&CK กับคดีนี้"
    if augmentation.status == "insufficient_context":
        return "มีการร้องขอ MITRE ATT&CK แต่ข้อมูลทางเทคนิคภายนอกไม่เพียงพอ"
    if augmentation.status == "failed":
        return (
            f"การเสริมข้อมูล MITRE ATT&CK ไม่สำเร็จ: {failure_detail(augmentation)} "
            "จึงไม่แสดง mapping เป็นข้อสรุปของคดี"
        )
    return None


def rationale_note(augmentation: CaseTechnicalAugmentation | None) -> str | None:
    if augmentation is None:
        return "ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้ จึงไม่มีการอนุมาน mapping จาก metadata"
    if augmentation.status == "not_applicable":
        return "ระบบข้ามการค้นหา MITRE ตามเกณฑ์ความเกี่ยวข้องของคดี"
    if augmentation.status == "insufficient_context":
        return "ยังไม่มีบริบททางเทคนิคเพียงพอสำหรับการให้เหตุผลของ mapping"
    if augmentation.status == "failed":
        return f"ยังไม่สามารถอธิบาย mapping ได้ ({failure_detail(augmentation)})"
    return None


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


def clarification_limitation(trace: CaseAnalysisTrace) -> str | None:
    return CLARIFICATION_LIMITATIONS.get(trace.stop_reason or "")


def report_limitations(report_input: CaseReportInput) -> list[str]:
    limitations = [
        "รายงานนี้เป็นการวิเคราะห์เบื้องต้นจากหลักฐานที่ถูกนำเข้าสู่ Case และยังต้องตรวจสอบโดยผู้ปฏิบัติงาน",
        "ข้อเท็จจริงและตัวบ่งชี้อ้างอิงได้เฉพาะหลักฐานของคดีและคำตอบที่ผู้ใช้ให้ไว้ในคำถามติดตามผล "
        "คำตอบเหล่านั้นเป็นคำบอกเล่าของผู้ใช้ ยังไม่ได้ผ่านการตรวจสอบกับหลักฐาน "
        "และไม่รวมข้อมูลภายนอกอื่นใด",
        "ระบบไม่ใช่ผู้วินิจฉัยข้อเท็จจริงหรือข้อกฎหมาย และไม่ควรใช้รายงานนี้แทนการใช้ดุลยพินิจของพนักงานสอบสวนหรืออัยการ",
        "หากเอกสารต้นฉบับไม่ครบ อ่านไม่ชัด หรือมีข้อมูลขัดแย้ง รายงานอาจสะท้อนข้อจำกัดดังกล่าว",
    ]
    augmentation = report_input.technical_augmentation
    if augmentation is None:
        limitations.append("ผลการเสริมข้อมูล MITRE ไม่พร้อมใช้งาน จึงไม่มีการยืนยัน mapping จากข้อมูลภายนอก")
    elif augmentation.status == "not_applicable":
        limitations.append("ระบบไม่พบเงื่อนไขที่จำเป็นต้องใช้ MITRE ATT&CK กับคดีนี้")
    elif augmentation.status == "insufficient_context":
        limitations.append("ข้อมูลทางเทคนิคภายนอกไม่เพียงพอสำหรับการจัดทำ mapping")
    elif augmentation.status == "retrieved_from_rag":
        limitations.append(
            "ระบบยอมรับรายการ MITRE ทั้งหมดจาก RAG service เป็นบริบททางเทคนิคภายนอก โดยไม่ถือเป็นหลักฐานของคดีหรือการเชื่อมโยงกับ claim"
        )
    elif augmentation.status == "failed":
        limitations.append("การเสริมข้อมูล MITRE ขัดข้อง จึงไม่ควรใช้ส่วน mapping เป็นข้อสรุปของคดี")
    else:
        limitations.append("MITRE ATT&CK ในรายงานเป็นบริบทภายนอกเพื่อช่วยจัดหมวดพฤติกรรม ไม่ใช่หลักฐานของคดี")

    clarification = clarification_limitation(report_input.analysis_trace)
    if clarification is not None:
        limitations.append(clarification)
    return limitations


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
