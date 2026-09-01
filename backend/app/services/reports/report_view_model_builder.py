import re

from app.schemas.reports import ChatReportRead, ReportSection
from app.services.reports.report_analysis_projection import (
    formal_case_title,
    project_summary_paragraphs,
    project_timeline_rows,
)
from app.services.reports.report_contracts import ReportInputSnapshot
from app.services.reports.report_finding_projection import (
    project_finding_rows,
    project_unresolved_issues,
)
from app.services.reports.report_view_model_contracts import (
    MitreMappingViewRow,
    ProvenanceViewRow,
    ReportLanguage,
    ReportViewModel,
    UnresolvedIssueViewRow,
    VerificationActionViewRow,
)
from app.services.reports.report_view_model_items import parse_report_items
from app.services.reports.report_view_model_text import (
    I18N_STRINGS,
    _format_datetime,
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
    lang = language if language in ("th", "en") else "th"
    i18n = I18N_STRINGS[lang]

    structured = report.report
    sections_by_id: dict[str, ReportSection] = {}
    if structured:
        for sec in structured.sections:
            sections_by_id[sec.section_id] = sec

    title_source = structured.title if structured and structured.title.strip() else thread_title
    title = formal_case_title(title_source)
    report_status_display = i18n["status_provisional"]
    generated_date_str = _format_datetime(report.created_at)
    version_label_str = f"Version {report.version_number}"

    parsed_items = parse_report_items(
        sections_by_id,
        language=lang,
    )
    indicator_rows = parsed_items.indicator_rows
    has_indicators = parsed_items.has_indicators

    snapshot: ReportInputSnapshot | None = None
    if getattr(report, "source_snapshot", None):
        raw_snap = report.source_snapshot
        if isinstance(raw_snap, ReportInputSnapshot):
            snapshot = raw_snap
        elif isinstance(raw_snap, dict):
            try:
                snapshot = ReportInputSnapshot.model_validate(raw_snap)
            except Exception:
                snapshot = None

    evidence_rows = project_finding_rows(structured, snapshot, language=lang)
    timeline_rows = project_timeline_rows(structured, snapshot, language=lang)
    if not timeline_rows:
        timeline_rows = parsed_items.timeline_rows

    mitre_view_rows: list[MitreMappingViewRow] = []
    if snapshot and snapshot.mitre_rows:
        seen_techniques: set[str] = set()
        for row in snapshot.mitre_rows:
            t_id = row.technique_id
            if t_id in seen_techniques:
                continue
            seen_techniques.add(t_id)
            t_name = row.name.strip() or t_id
            t_tactic = row.tactic.strip() if row.tactic and row.tactic != "Adversary Tactic" else ""
            t_reason = row.reason.strip() or (
                "ข้อสันนิษฐานเชื่อมโยงจากฐานข้อมูล MITRE ATT&CK"
                if lang == "th"
                else "Analytical correlation from MITRE knowledge base"
            )
            finding_title = f"{t_tactic}: {t_name}" if t_tactic else t_name
            status_display = i18n["status_candidate"]

            mitre_view_rows.append(
                MitreMappingViewRow(
                    finding=finding_title,
                    case_evidence_support=t_reason,
                    technique_id=t_id,
                    technique_name=t_name,
                    status_display=status_display,
                    tactic=t_tactic or ("General" if lang == "en" else "ทั่วไป"),
                    source="MITRE ATT&CK Knowledge Base",
                    relevance="candidate",
                )
            )
    else:
        raw_mitre_items: list[str] = []
        for sec_id in ("technical_analysis_mitre", "mitre_attack_mapping", "mapping_rationale"):
            if sec_id in sections_by_id:
                raw_mitre_items.extend(sections_by_id[sec_id].items)

        seen_techniques = set()
        for item in raw_mitre_items:
            if not item or item.startswith("No ") or item.startswith("ไม่มี"):
                continue
            m_match = re.match(
                r"^(T\d+(?:\.\d+)?)\s*(?:[—:\-]\s*|\s+)(?:([^(:]+?)\s*(?:\(([^)]+)\))?\s*[:—\-]\s*)?(.*)$",
                item,
            )
            if m_match:
                t_id = m_match.group(1)
                if t_id in seen_techniques:
                    continue
                seen_techniques.add(t_id)
                t_name = (m_match.group(2) or "").strip() or t_id
                t_tactic = (m_match.group(3) or "").strip()
                t_rest = (m_match.group(4) or "").strip()
                finding_title = f"{t_tactic}: {t_name}" if t_tactic else t_name
                mitre_view_rows.append(
                    MitreMappingViewRow(
                        finding=finding_title,
                        case_evidence_support=t_rest or ("Analytical correlation from MITRE knowledge base" if lang == "en" else "ข้อสันนิษฐานเชื่อมโยงจากฐานข้อมูล MITRE ATT&CK"),
                        technique_id=t_id,
                        technique_name=t_name,
                        status_display=i18n["status_candidate"],
                        tactic=t_tactic or ("General" if lang == "en" else "ทั่วไป"),
                        source="MITRE ATT&CK Knowledge Base",
                        relevance="candidate",
                    )
                )

    has_mitre_mappings = len(mitre_view_rows) > 0

    summary_paragraphs = project_summary_paragraphs(structured, snapshot, language=lang)
    if not summary_paragraphs:
        summary_paragraphs.append(i18n["empty_summary"])

    unresolved_issues = project_unresolved_issues(snapshot, language=lang)
    evidence_to_examine = sections_by_id.get("evidence_to_examine")
    if not unresolved_issues and evidence_to_examine and evidence_to_examine.items:
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

    provenance_rows: list[ProvenanceViewRow] = [
        ProvenanceViewRow(label="Report ID", value=str(report.report_id)),
        ProvenanceViewRow(label="Report Version", value=f"v{report.version_number} ({report.report.report_version if report.report else 'preliminary_analysis_report_v1'})"),
        ProvenanceViewRow(label="Generated Date (UTC)", value=generated_date_str),
        ProvenanceViewRow(label="Source Snapshot Hash", value=report.source_snapshot_hash),
        ProvenanceViewRow(
            label="Retrieval Context ID",
            value=report.retrieval_context_id or ("ไม่เกี่ยวข้อง" if lang == "th" else "Not applicable"),
        ),
        ProvenanceViewRow(label="Analysis Message ID", value=str(report.analysis_message_id)),
        ProvenanceViewRow(label="Prompt Version", value=report.prompt_version),
        ProvenanceViewRow(label="Template Provider", value=f"{report.provider} ({report.model})"),
        ProvenanceViewRow(
            label="Verification Status",
            value=(
                "ตรวจสอบโครงสร้างและการอ้างอิงกับ snapshot แล้ว; ไม่ใช่การยืนยันข้อเท็จจริง"
                if lang == "th"
                else "Structure and references validated against the snapshot; facts not independently verified"
            ),
        ),
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
