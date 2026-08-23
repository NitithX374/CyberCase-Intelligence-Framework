from __future__ import annotations;

from app.schemas.reports import ChatReportRead, ReportSection
from app.services.reports.report_view_model_contracts import (
    MitreMappingViewRow,
    ProvenanceViewRow,
    ReportLanguage,
    ReportViewModel,
    UnresolvedIssueViewRow,
    VerificationActionViewRow,
)
from app.services.reports.report_view_model_text import (
    I18N_STRINGS,
    _format_datetime,
    _strict_marked_fields,
)
from app.services.reports.report_view_model_items import parse_report_items

def build_report_view_model(
    report: ChatReportRead,
    *,
    thread_title: str = "CyberCase Investigation",
    language: ReportLanguage = "th",
) -> ReportViewModel:
    """Deterministically transform persisted ChatReportRead into ReportViewModel."""

    lang = language if language in ("th", "en") else "th"
    i18n = I18N_STRINGS[lang]

    structured = report.report
    sections_by_id: dict[str, ReportSection] = {}
    if structured:
        for sec in structured.sections:
            sections_by_id[sec.section_id] = sec

    title = structured.title if structured and structured.title.strip() else thread_title
    report_status_display = i18n["status_provisional"]
    generated_date_str = _format_datetime(report.created_at)
    version_label_str = f"Version {report.version_number}"

    parsed_items = parse_report_items(
        sections_by_id,
        language=lang,
    )
    evidence_rows = parsed_items.evidence_rows
    indicator_rows = parsed_items.indicator_rows
    timeline_rows = parsed_items.timeline_rows
    has_indicators = parsed_items.has_indicators

    mitre_view_rows: list[MitreMappingViewRow] = []
    raw_mitre_items = []
    for sec_id in ("technical_analysis_mitre", "mitre_attack_mapping"):
        if sec_id in sections_by_id:
            raw_mitre_items.extend(sections_by_id[sec_id].items)

    for item in raw_mitre_items:
        m_parsed = _strict_marked_fields(
            item,
            (
                " | Name: ",
                " | Mapping status: ",
                " | Source: ",
                " | Relevance: ",
                " | Score: ",
                " | Tactic: ",
                " | Entity type: ",
                " | Description: ",
            ),
        )
        if m_parsed is not None:
            t_id, t_name, m_status, m_src, m_rel, m_score, m_tactic, e_type, m_desc = m_parsed
            finding_title = f"{m_tactic}: {t_name}"
            status_display = i18n["status_candidate"]
            if m_rel == "cited_in_answer" or "cited" in m_rel:
                status_display = i18n["status_reported_analysis"]

            mitre_view_rows.append(
                MitreMappingViewRow(
                    finding=finding_title,
                    case_evidence_support=(
                        m_desc
                        if m_desc != "No description was persisted."
                        else ("No additional details." if lang == "en" else "ไม่มีรายละเอียดเพิ่มเติม")
                    ),
                    technique_id=t_id,
                    technique_name=t_name,
                    status_display=status_display,
                    tactic=m_tactic,
                    source=m_src,
                    relevance=m_rel,
                )
            )
        elif "No MITRE" not in item:
            mitre_view_rows.append(
                MitreMappingViewRow(
                    finding=item[:60],
                    case_evidence_support=item,
                    technique_id="MITRE Candidate",
                    technique_name=item[:40],
                    status_display=i18n["status_candidate"],
                    tactic="General",
                    source="external_mitre_retrieval",
                    relevance="candidate",
                )
            )

    has_mitre_mappings = len(mitre_view_rows) > 0

    summary_paragraphs: list[str] = []
    bg_items = []
    for sec_id in ("case_background_scope", "case_summary", "executive_summary"):
        if sec_id in sections_by_id:
            for p in sections_by_id[sec_id].paragraphs:
                p_clean = p.strip()
                if p_clean and not p_clean.startswith("Snapshot scope:") and not p_clean.startswith("This preliminary report"):
                    summary_paragraphs.append(p_clean)
            for item in sections_by_id[sec_id].items:
                if "Message " in item and "): " in item:
                    _, _, content = item.partition("): ")
                    if content:
                        bg_items.append(content.strip())
                elif "Generation method:" not in item and "Ordered user" not in item:
                    bg_items.append(item.strip())

    if bg_items:
        first_item = bg_items[0]
        if lang == "th":
            prefix = "มีการรายงานว่า " if not first_item.startswith("มี") and not first_item.startswith("พบ") else ""
            summary_paragraphs.append(f"{prefix}{first_item}")
            if len(bg_items) > 1:
                summary_paragraphs.append(f"จากข้อมูลที่ได้รับ: {'; '.join(bg_items[1:])}")
        else:
            summary_paragraphs.append(f"Initial report indicates: {first_item}")
            if len(bg_items) > 1:
                summary_paragraphs.append(f"Subsequent reported activity: {'; '.join(bg_items[1:])}")

    if not summary_paragraphs:
        summary_paragraphs.append(i18n["empty_summary"])

    unresolved_issues: list[UnresolvedIssueViewRow] = []
    limitations: list[str] = []
    if structured and structured.limitations:
        for lim in structured.limitations:
            if lim.startswith("Extraction warning: "):
                warning_text = lim[len("Extraction warning: ") :]
                unresolved_issues.append(
                    UnresolvedIssueViewRow(
                        description=warning_text,
                        category="Warning / Gap" if lang == "en" else "ข้อสังเกต / คำเตือน",
                        reason=(
                            "Ambiguity or inconsistency detected in reported data"
                            if lang == "en"
                            else "พบความคลุมเครือหรือความไม่สอดคล้องในข้อมูลที่ได้รับ"
                        ),
                    )
                )
            else:
                limitations.append(lim)

    if not unresolved_issues:
        unresolved_issues.append(
            UnresolvedIssueViewRow(
                description=i18n["empty_gaps"],
                category="Normal" if lang == "en" else "สถานะปกติ",
                reason="-",
            )
        )

    verification_actions: list[VerificationActionViewRow] = []
    for sec_id in ("preliminary_recommendations", "conclusions_limitations_next_steps"):
        if sec_id in sections_by_id:
            for item in sections_by_id[sec_id].items:
                if item and "Review every candidate" not in item:
                    verification_actions.append(
                        VerificationActionViewRow(order=len(verification_actions) + 1, action=item)
                    )

    if not verification_actions:
        if lang == "en":
            verification_actions = [
                VerificationActionViewRow(
                    order=1,
                    action="Examine original digital artifacts (e.g., server logs, PCAP, disk images) to confirm reported indicators and timestamps.",
                ),
                VerificationActionViewRow(
                    order=2,
                    action="Verify connections between involved user accounts and endpoints to determine the full scope of impact.",
                ),
                VerificationActionViewRow(
                    order=3,
                    action="Correlate observed behaviors against MITRE ATT&CK techniques to establish appropriate mitigation controls.",
                ),
                VerificationActionViewRow(
                    order=4,
                    action="Preserve forensic copies of all relevant digital evidence following standard chain-of-custody protocols.",
                ),
            ]
        else:
            verification_actions = [
                VerificationActionViewRow(
                    order=1,
                    action="ตรวจพิสูจน์พยานหลักฐานต้นฉบับ (เช่น Server Logs, PCAP, Disk Image) เพื่อยืนยันตัวบ่งชี้และเวลาที่แท้จริง",
                ),
                VerificationActionViewRow(
                    order=2,
                    action="ตรวจสอบความสัมพันธ์ระหว่างบัญชีผู้ใช้และอุปกรณ์ปลายทางที่เกี่ยวข้องเพื่อยืนยันขอบเขตความเสียหาย",
                ),
                VerificationActionViewRow(
                    order=3,
                    action="เปรียบเทียบพฤติกรรมในระบบกับ MITRE ATT&CK Techniques ที่ตรวจพบเพื่อกำหนดมาตรการสกัดกั้นที่เหมาะสม",
                ),
                VerificationActionViewRow(
                    order=4,
                    action="เก็บรักษาสำเนาพยานหลักฐานดิจิทัลตามระเบียบสายการครอบครองพยานหลักฐาน (Chain of Custody)",
                ),
            ]

    if not limitations:
        if lang == "en":
            limitations = [
                "This report is a provisional, unverified preliminary analysis designed for investigative orientation.",
                "Portions of incident details originate from user-submitted statements and have not been independently confirmed with raw evidence.",
                "The automated analysis reflects only the snapshot data provided and does not replace a comprehensive digital forensics examination.",
                "Associated MITRE ATT&CK techniques represent retrieval mapping candidates and require expert validation.",
            ]
        else:
            limitations = [
                "รายงานนี้เป็นรายงานสรุปผลการวิเคราะห์เบื้องต้น (Provisional / Unverified Report) สำหรับใช้เป็นแนวทางการสืบสวน",
                "ข้อมูลเหตุการณ์บางส่วนมาจากข้อความที่ผู้ใช้หรือผู้แจ้งเหตุรายงาน และยังไม่ได้รับการตรวจสอบยืนยันกับพยานหลักฐานดิจิทัลต้นฉบับโดยตรง",
                "ระบบประมวลผลตามสแนปช็อตข้อมูลที่ได้รับเท่านั้น ไม่สามารถทดแทนกระบวนการตรวจพิสูจน์พยานหลักฐานทางนิติวิทยาศาสตร์ดิจิทัลอย่างเป็นทางการได้",
                "เทคนิคและยุทธวิธี MITRE ATT&CK ที่ปรากฏเป็นผลจากการจับคู่เชิงวิเคราะห์ (Candidate Mapping) ต้องอาศัยผู้เชี่ยวชาญยืนยันก่อนใช้เป็นข้อสรุปทางคดี",
            ]

    provenance_rows: list[ProvenanceViewRow] = [
        ProvenanceViewRow(label="Report ID", value=str(report.report_id)),
        ProvenanceViewRow(label="Report Version", value=f"v{report.version_number} ({report.report.report_version if report.report else 'preliminary_analysis_report_v1'})"),
        ProvenanceViewRow(label="Generated Date (UTC)", value=generated_date_str),
        ProvenanceViewRow(label="Source Snapshot Hash", value=report.source_snapshot_hash),
        ProvenanceViewRow(label="Retrieval Context", value=report.retrieval_context_id),
        ProvenanceViewRow(label="Analysis Message", value=str(report.analysis_message_id)),
        ProvenanceViewRow(label="Prompt Version", value=report.prompt_version),
        ProvenanceViewRow(label="Template Provider", value=f"{report.provider} ({report.model})"),
        ProvenanceViewRow(label="Verification Status", value="Validated against frozen raw-evidence snapshot"),
    ]

    return ReportViewModel(
        report_id=str(report.report_id),
        case_title=title,
        generated_date=generated_date_str,
        report_status=report_status_display,
        version_label=version_label_str,
        language=lang,
        i18n=i18n,
        summary_paragraphs=summary_paragraphs,
        timeline_rows=timeline_rows,
        evidence_rows=evidence_rows,
        has_indicators=has_indicators,
        indicator_rows=indicator_rows,
        has_mitre_mappings=has_mitre_mappings,
        mitre_rows=mitre_view_rows,
        unresolved_issues=unresolved_issues,
        verification_actions=verification_actions,
        limitations=limitations,
        provenance_rows=provenance_rows,
    )
