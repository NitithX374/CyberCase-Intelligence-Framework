from app.services.reports.report_view_model_contracts import (
    ReportLanguage,
    UnresolvedIssueViewRow,
    VerificationActionViewRow,
)
from app.services.reports.report_view_model_text import I18N_STRINGS


def project_review_actions(
    unresolved_issues: list[UnresolvedIssueViewRow],
    *,
    lang: ReportLanguage,
    has_mitre_mappings: bool,
) -> tuple[list[VerificationActionViewRow], list[str]]:
    i18n = I18N_STRINGS[lang]
    verification_actions: list[VerificationActionViewRow] = []
    action_order = 1

    real_gaps = [g for g in unresolved_issues if g.description != i18n["empty_gaps"]]
    for gap in real_gaps:
        action_text = (
            f"ควรตรวจสอบเอกสาร พยานบุคคล หรือข้อมูลต้นทางเพิ่มเติมเพื่อยืนยันประเด็น: {gap.description}"
            if lang == "th"
            else f"Review source records, witness accounts, or other primary material to verify: {gap.description}"
        )
        verification_actions.append(
            VerificationActionViewRow(order=action_order, action=action_text)
        )
        action_order += 1

    if lang == "th":
        baseline_actions = [
            "ตรวจสอบวันเวลา จำนวนเงิน บุคคล สถานที่ และเลขอ้างอิงกับเอกสารต้นฉบับหรือข้อมูลจากหน่วยงานที่เกี่ยวข้อง",
            "ตรวจสอบความสอดคล้องระหว่างคำให้การ เอกสาร และลำดับเหตุการณ์ก่อนใช้ประกอบข้อสรุป",
            "เก็บรักษาเอกสารและข้อมูลต้นทางพร้อมบันทึกที่มาเพื่อให้ตรวจสอบย้อนกลับได้",
        ]
    else:
        baseline_actions = [
            "Verify dates, amounts, persons, locations, and reference numbers against original records or relevant authorities.",
            "Reconcile statements, documents, and chronology before relying on them in a conclusion.",
            "Preserve source records with provenance sufficient for later review.",
        ]

    for base_action in baseline_actions:
        if not any(base_action[:30] in act.action for act in verification_actions):
            verification_actions.append(
                VerificationActionViewRow(order=action_order, action=base_action)
            )
            action_order += 1

    if lang == "th":
        limitations = [
            "รายงานนี้เป็นสรุปผลการวิเคราะห์เบื้องต้นสำหรับการทบทวนและการสืบสวนเพิ่มเติม",
            "ข้อมูลอ้างอิงจากเนื้อหาที่ผู้ใช้ส่งเข้าสู่ระบบและยังไม่ได้รับการยืนยันโดยอิสระกับเอกสารหรือพยานหลักฐานต้นฉบับ",
            "สถานะและข้อสังเกตในรายงานเป็นผลการวิเคราะห์ ไม่ใช่ข้อวินิจฉัยทางกฎหมายหรือคำพิพากษา",
        ]
    else:
        limitations = [
            "This report is a preliminary analytical summary for review and further investigation.",
            "Information originates from user-submitted material and has not been independently verified against primary records or evidence.",
            "Analytical statuses and observations are not legal findings or judicial determinations.",
        ]
    if has_mitre_mappings:
        limitations.append(
            "MITRE ATT&CK เป็นบริบททางเทคนิคภายนอกและไม่ใช่หลักฐานยืนยันข้อเท็จจริงในคดี"
            if lang == "th"
            else "MITRE ATT&CK is external technical context and does not prove case facts."
        )

    return verification_actions, limitations
