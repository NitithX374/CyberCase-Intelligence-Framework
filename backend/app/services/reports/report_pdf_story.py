from __future__ import annotations

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, Spacer, Table

from app.schemas.reports import ChatReportRead
from app.services.reports.pdf_chrome import header_meta_table, table_style
from app.services.reports.report_pdf_provenance import build_provenance_story
from app.services.reports.pdf_design import DARK_RULE, PAGE_WIDTH, RULE, paragraph_text
from app.services.reports.report_view_model import ReportViewModel


def build_formal_report_story(
    view_model: ReportViewModel,
    *,
    report: ChatReportRead,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    content_width = PAGE_WIDTH - 32 * mm
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n["org_header"]), styles["eyebrow"]),
        Spacer(1, 2 * mm),
        Paragraph(paragraph_text(i18n["doc_title"]), styles["doc_title"]),
        Spacer(1, 3 * mm),
        header_meta_table(view_model, styles=styles, width=content_width),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1.2, color=DARK_RULE),
        Spacer(1, 5 * mm),
    ]
    story.extend(_summary_story(view_model, styles))
    story.extend(_timeline_story(view_model, styles))
    story.extend(_evidence_story(view_model, styles))
    story.extend(_mitre_story(view_model, styles))
    story.extend(_gap_story(view_model, styles))
    story.extend(build_provenance_story(view_model, styles))
    return story


def _summary_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n["sec_5_1"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    for paragraph in view_model.summary_paragraphs:
        story.extend([
            Paragraph(paragraph_text(paragraph), styles["body_indent"]),
            Spacer(1, 1.5 * mm),
        ])
    story.append(Spacer(1, 4 * mm))
    return story


def _timeline_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n["sec_5_2"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    if not view_model.timeline_rows:
        story.append(Paragraph(paragraph_text(i18n["empty_timeline"]), styles["body_muted"]))
        story.append(Spacer(1, 4 * mm))
        return story
    if any(len(row.event) > 600 for row in view_model.timeline_rows):
        story.extend(_long_timeline_story(view_model, styles))
    else:
        table_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_order'])}</b>", styles["table_header_center"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_time'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_event'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_source_evidence'])}</b>", styles["table_header"]),
        ]]
        for row in view_model.timeline_rows:
            event_text = paragraph_text(row.event)
            if row.actors and row.actors != "-":
                event_text += f"<br/><font color=\"#6B7280\" size=\"7.5\">{paragraph_text(i18n['actor_prefix'])}: {paragraph_text(row.actors)}</font>"
            table_data.append([
                Paragraph(str(row.order), styles["table_cell_center"]),
                Paragraph(f"<b>{paragraph_text(row.time_display)}</b>", styles["table_cell_small"]),
                Paragraph(event_text, styles["table_cell"]),
                Paragraph(paragraph_text(row.source_evidence), styles["table_cell_small"]),
            ])
        table = Table(table_data, colWidths=(14 * mm, 34 * mm, 86 * mm, 44 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)
    story.append(Spacer(1, 4 * mm))
    return story


def _long_timeline_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = []
    for row in view_model.timeline_rows:
        header_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_order'])} {row.order}</b>", styles["table_header_center"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_time'])}: {paragraph_text(row.time_display)}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_source_evidence'])}: {paragraph_text(row.source_evidence)}</b>", styles["table_header"]),
        ]]
        table = Table(header_data, colWidths=(22 * mm, 60 * mm, 96 * mm))
        table.setStyle(table_style())
        story.extend([
            table,
            Spacer(1, 1.5 * mm),
        ])
        event_body = paragraph_text(row.event)
        if row.actors and row.actors != "-":
            event_body += f"<br/><font color=\"#6B7280\" size=\"7.5\">{paragraph_text(i18n['actor_prefix'])}: {paragraph_text(row.actors)}</font>"
        story.extend([
            Paragraph(event_body, styles["body"]),
            Spacer(1, 3 * mm),
        ])
    return story


def _evidence_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n["sec_5_3"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_evidence_reg'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    if view_model.evidence_rows:
        table_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_item'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_type'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_description'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_source'])}</b>", styles["table_header"]),
        ]]
        for evidence in view_model.evidence_rows:
            table_data.append([
                Paragraph(f"<b>{paragraph_text(evidence.title)}</b><br/><font color=\"#6B7280\" size=\"7\">ID: {paragraph_text(evidence.item_id)}</font>", styles["table_cell"]),
                Paragraph(paragraph_text(evidence.artifact_type), styles["table_cell_small"]),
                Paragraph(paragraph_text(evidence.description), styles["table_cell"]),
                Paragraph(paragraph_text(evidence.source_type), styles["table_cell_small"]),
            ])
        table = Table(table_data, colWidths=(44 * mm, 32 * mm, 68 * mm, 34 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)
    else:
        story.append(Paragraph(paragraph_text(i18n["empty_evidence"]), styles["body_muted"]))

    if view_model.has_indicators:
        story.extend([
            Spacer(1, 3 * mm),
            Paragraph(f"<b>{paragraph_text(i18n['sub_iocs'])}</b>", styles["subheading"]),
            Spacer(1, 1.5 * mm),
        ])
        table_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_ioc_type'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_ioc_value'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_ioc_note'])}</b>", styles["table_header"]),
        ]]
        for indicator in view_model.indicator_rows:
            table_data.append([
                Paragraph(f"<b>{paragraph_text(indicator.indicator_type)}</b>", styles["table_cell_small"]),
                Paragraph(f"<font name=\"Courier\" size=\"7.5\">{paragraph_text(indicator.value)}</font>", styles["table_cell_code"]),
                Paragraph(paragraph_text(indicator.note), styles["table_cell_small"]),
            ])
        table = Table(table_data, colWidths=(38 * mm, 80 * mm, 60 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)
    story.append(Spacer(1, 4 * mm))
    return story


def _mitre_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n["sec_5_5"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    if view_model.has_mitre_mappings:
        story.extend([
            Paragraph(paragraph_text(i18n["sub_mitre_intro"]), styles["body"]),
            Spacer(1, 1.5 * mm),
        ])
        table_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_finding'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_case_support'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_mitre'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_mapping_status'])}</b>", styles["table_header"]),
        ]]
        for mapping in view_model.mitre_rows:
            technique = f"<b>{paragraph_text(mapping.technique_id)}</b><br/><font color=\"#4B5563\" size=\"7.5\">{paragraph_text(mapping.technique_name)}</font>"
            status = f"{paragraph_text(mapping.status_display)}<br/><font color=\"#6B7280\" size=\"7\">{paragraph_text(i18n['retrieval_source'])}: {paragraph_text(mapping.source)}</font>"
            table_data.append([
                Paragraph(f"<b>{paragraph_text(mapping.finding)}</b>", styles["table_cell"]),
                Paragraph(paragraph_text(mapping.case_evidence_support), styles["table_cell"]),
                Paragraph(technique, styles["table_cell_small"]),
                Paragraph(status, styles["table_cell_small"]),
            ])
        table = Table(table_data, colWidths=(44 * mm, 60 * mm, 44 * mm, 30 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)
    else:
        story.append(Paragraph(paragraph_text(i18n["empty_mitre"]), styles["body_muted"]))
    story.append(Spacer(1, 4 * mm))
    return story


def _gap_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    content: list[object] = [
        Paragraph(paragraph_text(i18n["sec_5_6"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_unresolved'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    for issue in view_model.unresolved_issues:
        issue_text = f"• <b>{paragraph_text(issue.description)}</b>"
        if issue.reason and issue.reason != "-":
            issue_text += f"<br/><font color=\"#6B7280\" size=\"7.5\">&nbsp;&nbsp;{paragraph_text(issue.reason)}</font>"
        content.extend([Paragraph(issue_text, styles["body"]), Spacer(1, 1.5 * mm)])
    content.extend([
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_next_steps'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ])
    for action in view_model.verification_actions:
        content.extend([
            Paragraph(f"{action.order}. {paragraph_text(action.action)}", styles["body"]),
            Spacer(1, 1.5 * mm),
        ])
    return [KeepTogether(content), Spacer(1, 4 * mm)]
