from __future__ import annotations

from app.schemas.reports import (
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    ReportClaim,
    ReportSection,
)
from app.services.case_analysis.contracts import CaseAnalysisClaim, CaseAnalysisTrace
from app.services.reports.case_report_contracts import CaseReportInput


SUPPORT_TYPE_LABELS = {
    "user_reported": "ข้อเท็จจริงที่ปรากฏในหลักฐาน",
    "analytical_inference": "ข้อสันนิษฐานเชิงวิเคราะห์",
    "unknown": "ยังไม่ทราบจากหลักฐานที่มี",
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


def build_case_report_claims(
    report_input: CaseReportInput,
    trace: CaseAnalysisTrace,
) -> list[ReportClaim]:
    association_by_claim: dict[str, list[str]] = {}
    for association in trace.mitre_associations:
        for claim_id in association.claim_ids:
            association_by_claim.setdefault(claim_id, []).append(association.technique_id)
    return [
        ReportClaim(
            claim_id=claim.claim_id,
            section_id="case_evidence",
            text=claim.text,
            support_type=support_type(claim.claim_type),
            source_evidence_ids=list(dict.fromkeys(claim.supporting_source_ids + claim.contradicting_source_ids)),
            mitre_technique_ids=list(dict.fromkeys(association_by_claim.get(claim.claim_id, []))),
        )
        for claim in trace.claims
    ]


def build_case_report_sections(
    report_input: CaseReportInput,
    trace: CaseAnalysisTrace,
) -> list[ReportSection]:
    source_labels = source_labels_for_report(report_input)
    claims_by_id = {claim.claim_id: claim for claim in trace.claims}
    return [
        ReportSection(
            section_id="case_summary",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["case_summary"],
            paragraphs=summary_paragraphs(report_input),
            items=summary_items(trace, claims_by_id, source_labels),
        ),
        ReportSection(
            section_id="case_evidence",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["case_evidence"],
            paragraphs=["แสดงข้อเท็จจริงและสัญญาณที่ปรากฏในหลักฐาน พร้อมสถานะการยืนยันและแหล่งอ้างอิง"],
            items=[] if trace.claims else ["ยังไม่พบตัวบ่งชี้ที่ผ่านการตรวจสอบจากผลวิเคราะห์"],
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["mitre_attack_mapping"],
            paragraphs=["MITRE ATT&CK เป็นข้อมูลภายนอกเพื่อช่วยจัดหมวดพฤติกรรมทางเทคนิค ไม่ใช่หลักฐานของคดี"],
            items=technical_items(report_input, trace),
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["mapping_rationale"],
            paragraphs=["เหตุผลต่อไปนี้อธิบายการเชื่อมโยงเชิงเทคนิคกับตัวบ่งชี้ของคดี ไม่ใช่การยืนยันว่ามีการใช้เทคนิคนั้นจริง"],
            items=technical_rationale(report_input, trace, claims_by_id, source_labels),
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["evidence_to_examine"],
            paragraphs=["รายการนี้สรุปช่องว่างหรือความขัดแย้งที่ควรตรวจสอบเพิ่มเติมก่อนใช้ประกอบการพิจารณาคดี"],
            items=gap_items(trace),
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["preliminary_recommendations"],
            paragraphs=["คำแนะนำมุ่งที่การยืนยันข้อเท็จจริง การรักษาหลักฐาน และการลดความไม่แน่นอนของคดี"],
            items=recommendation_items(trace),
        ),
        ReportSection(
            section_id="system_limitations",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["system_limitations"],
            items=build_case_report_limitations(report_input),
        ),
    ]


def build_case_report_limitations(report_input: CaseReportInput) -> list[str]:
    limitations = [
        "รายงานนี้เป็นการวิเคราะห์เบื้องต้นจากหลักฐานที่ถูกนำเข้าสู่ Case และยังต้องตรวจสอบโดยผู้ปฏิบัติงาน",
        "ข้อเท็จจริงและตัวบ่งชี้อ้างอิงเฉพาะหลักฐานของคดี ไม่รวมคำตอบจาก Chat หรือข้อมูลภายนอก",
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
        limitations.append("ระบบยอมรับรายการ MITRE ทั้งหมดจาก RAG service เป็นบริบททางเทคนิคภายนอก โดยไม่ถือเป็นหลักฐานของคดีหรือการเชื่อมโยงกับ claim")
    elif augmentation.status == "retrieved_without_supported_match":
        limitations.append("พบข้อมูล MITRE ภายนอก แต่ยังไม่มี mapping ที่เชื่อมโยงกับหลักฐานของคดีได้")
    elif augmentation.status == "failed":
        limitations.append("การเสริมข้อมูล MITRE ขัดข้อง จึงไม่ควรใช้ส่วน mapping เป็นข้อสรุปของคดี")
    else:
        limitations.append("MITRE ATT&CK ในรายงานเป็นบริบทภายนอกเพื่อช่วยจัดหมวดพฤติกรรม ไม่ใช่หลักฐานของคดี")
    return limitations


def summary_paragraphs(report_input: CaseReportInput) -> list[str]:
    paragraphs = [
        "วัตถุประสงค์ของรายงาน: ช่วยให้ผู้ตรวจสอบเห็นภาพรวมของคดี ประเด็นสำคัญ และหลักฐานที่ควรตรวจสอบต่อ โดยไม่ใช่คำวินิจฉัยทางกฎหมาย",
        f"สรุปจากผลวิเคราะห์: {report_input.analysis_summary}",
    ]
    if report_input.analysis_answer.strip() != report_input.analysis_summary.strip():
        paragraphs.append(f"ข้อสรุปเบื้องต้น: {report_input.analysis_answer}")
    return paragraphs


def summary_items(
    trace: CaseAnalysisTrace,
    claims_by_id: dict[str, CaseAnalysisClaim],
    source_labels: dict[str, str],
) -> list[str]:
    items = [
        f"ผู้เกี่ยวข้อง: {party.name} ({party.role}) · {claim_references(party.claim_ids, claims_by_id, source_labels)}"
        for party in trace.involved_parties
    ]
    items.extend(
        f"ลำดับเหตุการณ์: {event.time} — {event.event} · {claim_references(event.claim_ids, claims_by_id, source_labels)}"
        for event in trace.timeline
    )
    items.extend(
        f"ผลกระทบที่ปรากฏ: {impact.description} · {claim_references(impact.claim_ids, claims_by_id, source_labels)}"
        for impact in trace.impacts
    )
    return items or ["ผลวิเคราะห์ยังไม่มีข้อมูลผู้เกี่ยวข้อง ลำดับเหตุการณ์ หรือผลกระทบที่สกัดได้"]


def claim_references(
    claim_ids: list[str],
    claims_by_id: dict[str, CaseAnalysisClaim],
    source_labels: dict[str, str],
) -> str:
    source_ids: list[str] = []
    for claim_id in claim_ids:
        claim = claims_by_id.get(claim_id)
        if claim is not None:
            source_ids.extend(claim.supporting_source_ids)
            source_ids.extend(claim.contradicting_source_ids)
    labels = list(dict.fromkeys(source_labels[source_id] for source_id in source_ids if source_id in source_labels))
    return f"อ้างอิง: {', '.join(labels)}" if labels else "อ้างอิง: ไม่มีหลักฐานโดยตรง"


def source_labels_for_report(report_input: CaseReportInput) -> dict[str, str]:
    return {
        source.source_id: f"E-{index:02d}"
        for index, source in enumerate(report_input.source_bundle.sources, 1)
    }


def support_type(claim_type: str) -> str:
    return {
        "reported": "user_reported",
        "analytical_inference": "analytical_inference",
        "unknown": "unknown",
    }[claim_type]


def technical_items(
    report_input: CaseReportInput,
    trace: CaseAnalysisTrace,
) -> list[str]:
    augmentation = report_input.technical_augmentation
    if augmentation is None:
        return ["ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้สำหรับผลวิเคราะห์นี้"]
    if augmentation.status == "not_applicable":
        return ["ไม่พบเงื่อนไขที่จำเป็นต้องใช้ MITRE ATT&CK กับคดีนี้"]
    if augmentation.status == "insufficient_context":
        return ["มีการร้องขอ MITRE ATT&CK แต่ข้อมูลทางเทคนิคภายนอกไม่เพียงพอ"]
    if augmentation.status == "retrieved_from_rag":
        items = []
        for row in augmentation.mitre_table:
            identifier = row.get("technique_id") or row.get("name") or "RAG technical reference"
            name = row.get("name")
            description = row.get("description")
            label = str(identifier)
            if isinstance(name, str) and name.strip() and name.strip() != label:
                label += f" — {name.strip()}"
            if isinstance(description, str) and description.strip():
                label += f" · {description.strip()}"
            items.append(f"{label} · ยอมรับจาก RAG service เป็นบริบททางเทคนิคภายนอก ไม่ใช่หลักฐานของคดี")
        return items or ["RAG service ไม่ได้ส่งรายการ MITRE ที่ใช้แสดงผล"]
    if augmentation.status == "retrieved_without_supported_match":
        return ["พบข้อมูล MITRE ATT&CK ภายนอก แต่ยังไม่มี mapping ที่เชื่อมโยงกับหลักฐานของคดีได้"]
    if augmentation.status == "failed":
        return [f"การเสริมข้อมูล MITRE ATT&CK ไม่สำเร็จ จึงไม่แสดง mapping เป็นข้อสรุปของคดี ({augmentation.failure_code})"]
    rows_by_id = {
        str(row.get("technique_id")): row
        for row in augmentation.mitre_table
        if isinstance(row, dict) and row.get("technique_id")
    }
    items = []
    for association in trace.mitre_associations:
        row = rows_by_id.get(association.technique_id, {})
        name = row.get("name")
        description = row.get("description")
        label = f"{association.technique_id}{f' — {name}' if isinstance(name, str) and name.strip() else ''}"
        if isinstance(description, str) and description.strip():
            label += f" · {description.strip()}"
        items.append(f"{label} · บริบททางเทคนิคภายนอก ไม่ใช่หลักฐานของคดี")
    return items or ["ไม่พบ mapping ที่ผ่านการตรวจสอบ"]


def technical_rationale(
    report_input: CaseReportInput,
    trace: CaseAnalysisTrace,
    claims_by_id: dict[str, CaseAnalysisClaim],
    source_labels: dict[str, str],
) -> list[str]:
    augmentation = report_input.technical_augmentation
    if augmentation is not None and augmentation.status == "retrieved_with_matches":
        return [
            f"{association.technique_id}: {association.reason} · {claim_references(association.claim_ids, claims_by_id, source_labels)} · ใช้เพื่อจัดหมวดพฤติกรรม ไม่ได้ยืนยันการเกิดเหตุ"
            for association in trace.mitre_associations
        ] or ["ไม่พบเหตุผลของ mapping ที่บันทึกไว้"]
    if augmentation is not None and augmentation.status == "failed":
        return [f"ยังไม่สามารถอธิบาย mapping ได้ เนื่องจากการเสริมข้อมูล MITRE ขัดข้อง ({augmentation.failure_code})"]
    if augmentation is not None and augmentation.status == "retrieved_without_supported_match":
        return ["ข้อมูล MITRE ที่ค้นพบยังเป็นข้อมูลภายนอก เพราะไม่ผ่านการเชื่อมโยงกับหลักฐานของคดี"]
    if augmentation is not None and augmentation.status == "insufficient_context":
        return ["ยังไม่มีบริบททางเทคนิคเพียงพอสำหรับการให้เหตุผลของ mapping"]
    if augmentation is not None and augmentation.status == "retrieved_from_rag":
        return [
            f"{row.get('technique_id') or row.get('name') or 'RAG technical reference'}: รายการนี้รับโดยตรงจาก RAG service เพื่อจัดหมวดบริบททางเทคนิค ไม่ได้สร้าง claim association และไม่ยืนยันการเกิดเหตุ"
            for row in augmentation.mitre_table
        ] or ["ไม่มีรายการจาก RAG service ให้เหตุผลเพิ่มเติม"]
    if augmentation is not None and augmentation.status == "not_applicable":
        return ["ระบบข้ามการค้นหา MITRE ตามเกณฑ์ความเกี่ยวข้องของคดี"]
    return ["ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้ จึงไม่มีการอนุมาน mapping จาก metadata"]


def gap_items(trace: CaseAnalysisTrace) -> list[str]:
    if not trace.gaps:
        return ["ไม่พบช่องว่างสำคัญที่ต้องตรวจสอบเพิ่มเติมจากผลวิเคราะห์นี้"]
    return [
        f"{gap.gap_id} · {gap.topic} · ระดับความสำคัญ: {PRIORITY_LABELS[gap.priority]} · สถานะ: {GAP_STATUS_LABELS[gap.status]} · {gap.description} เหตุผล: {gap.reason}"
        for gap in trace.gaps
    ]


def recommendation_items(trace: CaseAnalysisTrace) -> list[str]:
    items = [
        f"ตรวจสอบเพิ่มเติมในประเด็น {gap.topic}: {gap.description}"
        for gap in trace.gaps
    ]
    items.extend(
        [
            "ตรวจสอบเอกสารต้นฉบับและความสอดคล้องของข้อมูลก่อนใช้เป็นข้อเท็จจริง",
            "เปรียบเทียบข้อมูลจากหลายแหล่งและบันทึกผลที่ยืนยันได้แยกจากข้อสันนิษฐาน",
            "รักษาข้อมูลต้นฉบับและบริบทที่เกี่ยวข้องไว้เพื่อให้ตรวจสอบย้อนกลับได้",
        ]
    )
    return list(dict.fromkeys(items))


__all__ = [
    "EPISTEMIC_STATUS_LABELS",
    "GAP_STATUS_LABELS",
    "PRIORITY_LABELS",
    "SUPPORT_TYPE_LABELS",
    "build_case_report_claims",
    "build_case_report_limitations",
    "build_case_report_sections",
]
