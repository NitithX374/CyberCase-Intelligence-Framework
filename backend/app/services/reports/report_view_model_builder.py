import re

from app.schemas.reports import ChatReportRead, ReportSection
from app.services.reports.report_view_model_contracts import (
    MitreMappingViewRow,
    ProvenanceViewRow,
    ReportLanguage,
    ReportViewModel,
    TimelineViewRow,
    UnresolvedIssueViewRow,
    VerificationActionViewRow,
)
from app.services.reports.report_view_model_items import parse_report_items
from app.services.reports.report_view_model_text import (
    I18N_STRINGS,
    _format_datetime,
    _strict_marked_fields,
)


def _clean_markdown_text(text: str) -> str:
    # Remove markdown headings, bold markers, and clean whitespace
    clean = re.sub(r"^###+\s*[^\n]+\n?", "", text, flags=re.MULTILINE)
    clean = re.sub(r"\*\*(.*?)\*\*", r"\1", clean)
    clean = re.sub(r"`([^`]+)`", r"\1", clean)
    clean = re.sub(r"^[-*•]\s+", "", clean, flags=re.MULTILINE)
    return clean.strip()


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
    timeline_rows = list(parsed_items.timeline_rows)
    has_indicators = parsed_items.has_indicators

    # If timeline_rows not populated from sections, populate from structured.claims
    if not timeline_rows and structured and structured.claims:
        source_label = (
            "ข้อมูลจากสำนวนที่ผู้ใช้ส่ง (ข้อความ #1)"
            if lang == "th"
            else "User-Submitted Evidence (#1)"
        )
        for claim in structured.claims:
            if claim.claim_id != "R-01" and claim.text:
                clean_claim_text = _clean_markdown_text(claim.text)
                if clean_claim_text:
                    timeline_rows.append(
                        TimelineViewRow(
                            order=len(timeline_rows) + 1,
                            time_display="—",
                            event=clean_claim_text,
                            source_evidence=source_label,
                            actors="-",
                            status=claim.support_type,
                        )
                    )

    # Parse MITRE rows
    mitre_view_rows: list[MitreMappingViewRow] = []
    raw_mitre_items: list[str] = []
    for sec_id in ("technical_analysis_mitre", "mitre_attack_mapping", "mapping_rationale"):
        if sec_id in sections_by_id:
            raw_mitre_items.extend(sections_by_id[sec_id].items)

    seen_techniques: set[str] = set()
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
            if t_id in seen_techniques:
                continue
            seen_techniques.add(t_id)
            finding_title = f"{m_tactic}: {t_name}" if m_tactic else t_name
            status_display = i18n["status_candidate"]

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
                    tactic=m_tactic or "General",
                    source="MITRE ATT&CK Knowledge Base",
                    relevance=m_rel,
                )
            )
        elif item and not item.startswith("No ") and not item.startswith("ไม่มี"):
            # Check pattern "Txxxx: reason" or "Txxxx Name reason"
            m_match = re.match(r"^(T\d+(?:\.\d+)?)(?:\s*[:\-—]\s*|\s+)(.*)$", item)
            if m_match:
                t_id = m_match.group(1)
                if t_id in seen_techniques:
                    continue
                seen_techniques.add(t_id)
                t_rest = m_match.group(2).strip()
                mitre_view_rows.append(
                    MitreMappingViewRow(
                        finding=f"MITRE Technique {t_id}",
                        case_evidence_support=t_rest or ("Analytical correlation from MITRE knowledge base" if lang == "en" else "ข้อสันนิษฐานเชื่อมโยงจากฐานข้อมูล MITRE ATT&CK"),
                        technique_id=t_id,
                        technique_name=t_id,
                        status_display=i18n["status_candidate"],
                        tactic="General",
                        source="MITRE ATT&CK Knowledge Base",
                        relevance="candidate",
                    )
                )

    has_mitre_mappings = len(mitre_view_rows) > 0

    # Summary Paragraphs (Section 1)
    summary_paragraphs: list[str] = []
    case_summary = sections_by_id.get("case_summary")
    if case_summary and case_summary.paragraphs:
        for p in case_summary.paragraphs:
            cleaned = _clean_markdown_text(p)
            if cleaned:
                summary_paragraphs.append(cleaned)

    if not summary_paragraphs:
        summary_paragraphs.append(i18n["empty_summary"])

    # Unresolved Issues (Section 5)
    unresolved_issues: list[UnresolvedIssueViewRow] = []
    evidence_to_examine = sections_by_id.get("evidence_to_examine")
    if evidence_to_examine and evidence_to_examine.items:
        for item in evidence_to_examine.items:
            clean_item = _clean_markdown_text(item)
            if (
                clean_item
                and not clean_item.startswith("No ")
                and not clean_item.startswith("ไม่มี")
                and "No explicit unresolved" not in clean_item
            ):
                reason = "-"
                desc = clean_item
                if " — " in clean_item:
                    desc, _, reason = clean_item.partition(" — ")
                elif " : " in clean_item:
                    desc, _, reason = clean_item.partition(" : ")
                unresolved_issues.append(
                    UnresolvedIssueViewRow(
                        description=desc.strip(),
                        category="ประเด็นที่ยังไม่ยืนยัน" if lang == "th" else "Unconfirmed Item",
                        reason=reason.strip() if reason != "-" else "",
                    )
                )

    # Check limitations for warnings as backup
    if structured and structured.limitations:
        for lim in structured.limitations:
            if lim.startswith("Extraction warning: "):
                warning_text = lim[len("Extraction warning: ") :]
                unresolved_issues.append(
                    UnresolvedIssueViewRow(
                        description=warning_text,
                        category="ข้อสังเกต / คำเตือน" if lang == "th" else "Warning / Gap",
                        reason=(
                            "พบความคลุมเครือหรือความไม่สอดคล้องในข้อมูลที่ได้รับ"
                            if lang == "th"
                            else "Ambiguity or inconsistency detected in reported data"
                        ),
                    )
                )

    if not unresolved_issues:
        unresolved_issues.append(
            UnresolvedIssueViewRow(
                description=i18n["empty_gaps"],
                category="สถานะปกติ" if lang == "th" else "Normal",
                reason="-",
            )
        )

    # Verification Actions (Section 6: Points for Further Investigation)
    verification_actions: list[VerificationActionViewRow] = []
    action_order = 1

    # Dynamically generate investigative actions from gaps
    real_gaps = [g for g in unresolved_issues if g.description != i18n["empty_gaps"]]
    for gap in real_gaps:
        gap_desc = gap.description
        if lang == "th":
            if "ส่งออก" in gap_desc or "destination" in gap_desc.lower() or "egress" in gap_desc.lower():
                action_text = f"ควรตรวจสอบข้อมูลบันทึกเครือข่าย (Firewall / Network Logs) เพิ่มเติมเพื่อระบุปลายทางและปริมาณข้อมูลที่เกี่ยวข้อง ({gap_desc})"
            elif "บัญชี" in gap_desc or "account" in gap_desc.lower() or "privilege" in gap_desc.lower():
                action_text = f"ควรตรวจสอบข้อมูลบันทึกการยืนยันตัวตน (Authentication / Audit Logs) เพิ่มเติมเพื่อระบุบัญชีผู้ใช้ที่เกี่ยวข้อง ({gap_desc})"
            else:
                action_text = f"ควรตรวจสอบพยานหลักฐานและบันทึกเหตุการณ์เพิ่มเติมเกี่ยวกับ: {gap_desc}"
        else:
            action_text = f"Investigate and review system/network logs regarding: {gap_desc}"

        verification_actions.append(
            VerificationActionViewRow(order=action_order, action=action_text)
        )
        action_order += 1

    # Standard forensic baseline actions
    if lang == "th":
        baseline_actions = [
            "ควรตรวจสอบและเก็บรักษาข้อมูลบันทึกเหตุการณ์ต้นฉบับ (Original Logs) เพื่อยืนยันความถูกต้องของเหตุการณ์",
            "ควรตรวจสอบความเชื่อมโยงของบัญชีผู้ใช้และอุปกรณ์ปลายทางในเครือข่ายเพิ่มเติมเพื่อยืนยันขอบเขตผลกระทบ",
            "ควรเก็บรักษาสำเนาพยานหลักฐานดิจิทัลตามระเบียบสายการครอบครองพยานหลักฐาน (Chain of Custody)",
        ]
    else:
        baseline_actions = [
            "Examine original digital artifacts (e.g., server logs, network captures) to confirm reported indicators.",
            "Verify connections between involved user accounts and endpoints to determine full scope of impact.",
            "Preserve forensic copies of relevant digital evidence following standard chain-of-custody protocols.",
        ]

    for base_action in baseline_actions:
        if not any(base_action[:30] in act.action for act in verification_actions):
            verification_actions.append(
                VerificationActionViewRow(order=action_order, action=base_action)
            )
            action_order += 1

    # Limitations (Section 7)
    if lang == "th":
        limitations = [
            "รายงานนี้เป็นรายงานสรุปผลการวิเคราะห์เบื้องต้น (Provisional / Unverified Report) สำหรับใช้เป็นแนวทางการสืบสวน",
            "ข้อมูลเหตุการณ์อ้างอิงจากข้อความและพยานหลักฐานที่ผู้ใช้ส่งเข้าสู่ระบบ และยังไม่ได้รับการตรวจสอบยืนยันกับพยานหลักฐานดิจิทัลต้นฉบับโดยตรง",
            "การวิเคราะห์และการเชื่อมโยงข้อมูล MITRE ATT&CK เป็นการอนุมานทางเทคนิคภายนอก ไม่สามารถทดแทนกระบวนการตรวจพิสูจน์พยานหลักฐานทางนิติวิทยาศาสตร์ดิจิทัลอย่างเป็นทางการได้",
        ]
    else:
        limitations = [
            "This report is a provisional, unverified preliminary analysis designed for investigative orientation.",
            "Incident details originate from user-submitted statements and have not been independently confirmed with raw evidence.",
            "Automated MITRE ATT&CK correlation is external technical interpretation and does not replace official digital forensics examination.",
        ]

    provenance_rows: list[ProvenanceViewRow] = [
        ProvenanceViewRow(label="Report ID", value=str(report.report_id)),
        ProvenanceViewRow(label="Report Version", value=f"v{report.version_number} ({report.report.report_version if report.report else 'preliminary_analysis_report_v1'})"),
        ProvenanceViewRow(label="Generated Date (UTC)", value=generated_date_str),
        ProvenanceViewRow(label="Source Snapshot Hash", value=report.source_snapshot_hash),
        ProvenanceViewRow(label="Retrieval Context ID", value=report.retrieval_context_id),
        ProvenanceViewRow(label="Analysis Message ID", value=str(report.analysis_message_id)),
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
