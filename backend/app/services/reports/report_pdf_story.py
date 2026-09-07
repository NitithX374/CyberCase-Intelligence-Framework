from __future__ import annotations

import textwrap

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, Spacer, Table, TableStyle

from app.schemas.reports import ChatReportRead
from app.services.reports.pdf_chrome import header_meta_table, table_style
from app.services.reports.pdf_design import (
    DARK_RULE,
    PAGE_WIDTH,
    PANEL,
    RULE,
    paragraph_text,
)
from app.services.reports.report_view_model_contracts import ReportViewModel


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
    story.extend(build_evidence_story(view_model, styles))
    story.extend(_mitre_story(view_model, styles, content_width))
    story.extend(_gap_story(view_model, styles))
    story.extend(_next_steps_story(view_model, styles))
    story.extend(build_provenance_story(view_model, styles))
    return story


def _summary_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n.get("sec_1", i18n["sec_5_1"])), styles["section_heading"]),
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
        Paragraph(paragraph_text(i18n.get("sec_2", i18n["sec_5_2"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    if not view_model.timeline_rows:
        story.append(Paragraph(paragraph_text(i18n["empty_timeline"]), styles["body_muted"]))
        story.append(Spacer(1, 4 * mm))
        return story

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
    table = Table(table_data, colWidths=(10 * mm, 39 * mm, 91 * mm, 38 * mm), repeatRows=1)
    table.setStyle(table_style())
    story.append(table)
    story.append(Spacer(1, 4 * mm))
    return story


def build_evidence_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n.get("sec_3", i18n["sec_5_3"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_evidence_reg'])}</b>", styles["subheading"]),
        Spacer(1, 2 * mm),
    ]
    if view_model.evidence_rows:
        table_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_item'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_description'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_type'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_source'])}</b>", styles["table_header"]),
        ]]
        for evidence in view_model.evidence_rows:
            chunks = textwrap.wrap(
                evidence.description,
                width=1200,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]
            for chunk_index, chunk in enumerate(chunks):
                first_chunk = chunk_index == 0
                table_data.append([
                    Paragraph(
                        f"<b>{paragraph_text(evidence.item_id if first_chunk else '')}</b>",
                        styles["table_cell_small"],
                    ),
                    Paragraph(paragraph_text(chunk), styles["table_cell"]),
                    Paragraph(
                        paragraph_text(evidence.artifact_type if first_chunk else ""),
                        styles["table_cell_small"],
                    ),
                    Paragraph(
                        paragraph_text(evidence.source_type if first_chunk else ""),
                        styles["table_cell_small"],
                    ),
                ])
        table = Table(table_data, colWidths=(18 * mm, 102 * mm, 27 * mm, 31 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)
    else:
        story.append(Paragraph(paragraph_text(i18n["empty_evidence"]), styles["body_muted"]))

    if view_model.has_indicators:
        story.extend(
            [
                Spacer(1, 2 * mm),
                Paragraph(f"<b>{paragraph_text(i18n['sub_iocs'])}</b>", styles["subheading"]),
                Spacer(1, 1.5 * mm),
            ]
        )
        table_data = [
            [
                Paragraph(f"<b>{paragraph_text(i18n['col_ioc_type'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{paragraph_text(i18n['col_ioc_value'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{paragraph_text(i18n['col_ioc_note'])}</b>", styles["table_header"]),
            ]
        ]
        for indicator in view_model.indicator_rows:
            table_data.append(
                [
                    Paragraph(f"<b>{paragraph_text(indicator.indicator_type)}</b>", styles["table_cell_small"]),
                    Paragraph(f"<font name=\"Courier\" size=\"7.5\">{paragraph_text(indicator.value)}</font>", styles["table_cell_code"]),
                    Paragraph(paragraph_text(indicator.note), styles["table_cell_small"]),
                ]
            )
        table = Table(table_data, colWidths=(36 * mm, 82 * mm, 60 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)

    story.append(Spacer(1, 4 * mm))
    return story


def _mitre_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n.get("sec_4", i18n["sec_5_5"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    if view_model.has_mitre_mappings:
        story.extend([
            Paragraph(paragraph_text(i18n["sub_mitre_intro"]), styles["body_muted"]),
            Spacer(1, 2.5 * mm),
        ])
        for mapping in view_model.mitre_rows:
            tech_header = (
                f"<b>{paragraph_text(mapping.technique_id)} — {paragraph_text(mapping.technique_name)}</b>"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; <font color=\"#4B5563\" size=\"7.5\">Tactic: {paragraph_text(mapping.tactic)}</font>"
            )
            card_rows = [
                [Paragraph(tech_header, styles["table_header"])],
                [
                    Paragraph(
                        f"<b>{paragraph_text(i18n['col_case_support'])}:</b> {paragraph_text(mapping.case_evidence_support)}<br/>"
                        f"<font color=\"#4B5563\" size=\"7.5\"><b>{paragraph_text(i18n['col_mapping_status'])}:</b> {paragraph_text(mapping.status_display)}</font>",
                        styles["body"],
                    )
                ],
            ]
            tech_table = Table(card_rows, colWidths=[content_width])
            tech_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("TOPPADDING", (0, 0), (-1, 0), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 1.5 * mm),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 1), (-1, 1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 2.5 * mm),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, RULE),
            ]))
            story.append(KeepTogether([tech_table, Spacer(1, 2.5 * mm)]))
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
        Paragraph(paragraph_text(i18n.get("sec_5", i18n["sec_5_6"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_unresolved'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    for issue in view_model.unresolved_issues:
        issue_text = f"• <b>{paragraph_text(issue.description)}</b>"
        if issue.reason and issue.reason != "-":
            issue_text += f"<br/>&nbsp;&nbsp;<font color=\"#6B7280\" size=\"7.5\">{paragraph_text(issue.reason)}</font>"
        content.extend([Paragraph(issue_text, styles["body"]), Spacer(1, 1.5 * mm)])

    content.append(Spacer(1, 4 * mm))
    return content


def _next_steps_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    content: list[object] = [
        Paragraph(paragraph_text(i18n.get("sec_6", i18n["sec_5_6"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_next_steps'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    for action in view_model.verification_actions:
        content.extend([
            Paragraph(f"{action.order}. {paragraph_text(action.action)}", styles["body"]),
            Spacer(1, 1.5 * mm),
        ])

    content.append(Spacer(1, 4 * mm))
    return content


def build_provenance_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    content: list[object] = [
        Paragraph(paragraph_text(i18n.get("sec_7", i18n["sec_5_7"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    for limitation in view_model.limitations:
        content.extend([
            Paragraph(f"• {paragraph_text(limitation)}", styles["body_small"]),
            Spacer(1, 1.5 * mm),
        ])
    content.extend([
        Spacer(1, 4 * mm),
        PageBreak(),
        Paragraph(f"<b>{paragraph_text(i18n['sub_provenance'])}</b>", styles["subheading"]),
        Spacer(1, 2 * mm),
    ])
    table_data = [[
        Paragraph(f"<b>{paragraph_text(i18n['col_prov_item'])}</b>", styles["table_header"]),
        Paragraph(f"<b>{paragraph_text(i18n['col_prov_value'])}</b>", styles["table_header"]),
    ]]
    for row in view_model.provenance_rows:
        table_data.append([
            Paragraph(f"<b>{paragraph_text(row.label)}</b>", styles["table_cell_small"]),
            Paragraph(paragraph_text(row.value), styles["table_cell_small"]),
        ])
    table = Table(table_data, colWidths=(52 * mm, 126 * mm), repeatRows=1)
    table.setStyle(table_style())
    content.extend([
        table,
        Spacer(1, 5 * mm),
        HRFlowable(width="100%", thickness=0.8, color=RULE),
        Spacer(1, 3 * mm),
        Paragraph(paragraph_text(i18n["end_of_report"]), styles["end_note"]),
    ])
    return content


__all__ = [
    "build_evidence_story",
    "build_formal_report_story",
    "build_provenance_story",
]

