import re

from app.schemas.reports import ChatReportRead, ReportSection
from app.services.reports.report_analysis_projection import (
    formal_case_title,
    project_summary_paragraphs,
    project_timeline_rows,
)
from app.services.reports.report_contracts import read_render_snapshot
from app.services.reports.report_mitre_projection import project_mitre_rows
from app.services.reports.report_review_projection import project_review_actions
from app.services.reports.report_finding_projection import (
    project_finding_rows,
    project_unresolved_issues,
)
from app.services.reports.report_view_model_contracts import (
    ProvenanceViewRow,
    ReportLanguage,
    ReportViewModel,
    UnresolvedIssueViewRow,
)
from app.services.reports.report_view_model_items import parse_report_items
from app.services.reports.report_view_model_text import (
    I18N_STRINGS,
    _format_datetime,
)


def _clean_markdown_text(text: str) -> str:
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
    if report.report is None:
        raise ValueError("A structured report is required for rendering")
    if language not in ("th", "en"):
        raise ValueError("Report language must be th or en")
    lang = language
    i18n = I18N_STRINGS[lang]

    structured = report.report
    sections_by_id: dict[str, ReportSection] = {}
    if structured:
        for sec in structured.sections:
            sections_by_id[sec.section_id] = sec

    title_source = (
        structured.title if structured and structured.title.strip() else thread_title
    )
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

    snapshot = read_render_snapshot(report.source_snapshot)

    evidence_rows = project_finding_rows(structured, snapshot, language=lang)
    timeline_rows = project_timeline_rows(structured, snapshot, language=lang)
    if snapshot is None and not timeline_rows:
        timeline_rows = parsed_items.timeline_rows

    mitre_view_rows = project_mitre_rows(snapshot, sections_by_id, lang=lang)

    has_mitre_mappings = len(mitre_view_rows) > 0

    summary_paragraphs = project_summary_paragraphs(structured, snapshot, language=lang)
    if not summary_paragraphs:
        summary_paragraphs.append(i18n["empty_summary"])

    unresolved_issues = project_unresolved_issues(snapshot, language=lang)
    evidence_to_examine = sections_by_id.get("evidence_to_examine")
    if (
        snapshot is None
        and not unresolved_issues
        and evidence_to_examine
        and evidence_to_examine.items
    ):
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
                        category="ประเด็นที่ยังไม่ยืนยัน"
                        if lang == "th"
                        else "Unconfirmed Item",
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
                        category="ข้อสังเกต / คำเตือน"
                        if lang == "th"
                        else "Warning / Gap",
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

    verification_actions, limitations = project_review_actions(
        unresolved_issues, lang=lang, has_mitre_mappings=has_mitre_mappings
    )

    provenance_rows: list[ProvenanceViewRow] = [
        ProvenanceViewRow(label="Report ID", value=str(report.report_id)),
        ProvenanceViewRow(
            label="Report Version",
            value=f"v{report.version_number} ({report.report.report_version if report.report else 'preliminary_analysis_report_v1'})",
        ),
        ProvenanceViewRow(label="Generated Date (UTC)", value=generated_date_str),
        ProvenanceViewRow(
            label="Source Snapshot Hash", value=report.source_snapshot_hash
        ),
        ProvenanceViewRow(
            label="Retrieval Context ID",
            value=report.retrieval_context_id
            or ("ไม่เกี่ยวข้อง" if lang == "th" else "Not applicable"),
        ),
        ProvenanceViewRow(
            label="Analysis Message ID", value=str(report.analysis_message_id)
        ),
        ProvenanceViewRow(label="Prompt Version", value=report.prompt_version),
        ProvenanceViewRow(
            label="Template Provider", value=f"{report.provider} ({report.model})"
        ),
        ProvenanceViewRow(
            label="Verification Status",
            value=(
                "แสดงโครงสร้างรายงานที่บันทึกไว้; ไม่ใช่การยืนยันข้อเท็จจริง"
                if lang == "th"
                else "Saved report structure rendered; facts not independently verified"
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
