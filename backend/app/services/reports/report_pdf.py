"""Deterministic PDF rendering for validated persisted CyberCase incident reports.

Supports both Thai ('th') and English ('en') formal investigative reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from io import BytesIO
import os
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.reports import ChatReportRead, ReportClaim, ReportSection
from app.services.reports.report_view_model import (
    ReportLanguage,
    ReportViewModel,
    TimelineViewRow,
    build_report_view_model,
)

_INK = colors.HexColor("#111827")
_MUTED = colors.HexColor("#4B5563")
_RULE = colors.HexColor("#E5E7EB")
_DARK_RULE = colors.HexColor("#111827")
_PANEL = colors.HexColor("#F3F4F6")
_PANEL_ALT = colors.HexColor("#FAFAFA")
_PAGE_WIDTH, _PAGE_HEIGHT = A4


def render_chat_report_pdf(
    report: ChatReportRead,
    *,
    thread_title: str,
    language: ReportLanguage = "th",
) -> bytes:
    """Render a completed persisted report deterministically as a formal PDF in Thai or English."""

    if report.report is None:
        raise ValueError("a structured report is required for PDF rendering")

    view_model = build_report_view_model(report, thread_title=thread_title, language=language)
    font_names = _register_fonts()
    styles = _build_styles(font_names)

    buffer = BytesIO()
    doc_title = _plain(report.report.title) if report.report.title else _plain(view_model.case_title)
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=doc_title,
        author="CyberCase Intelligence Framework",
        subject="Formal Provisional Incident Analysis Report",
    )

    story = _build_formal_story(view_model, report=report, styles=styles)
    document.build(
        story,
        onFirstPage=lambda canvas, doc: _draw_page_chrome(
            canvas, doc, font_names=font_names, report_id=view_model.report_id, view_model=view_model
        ),
        onLaterPages=lambda canvas, doc: _draw_page_chrome(
            canvas, doc, font_names=font_names, report_id=view_model.report_id, view_model=view_model
        ),
    )
    return buffer.getvalue()


def _build_formal_story(
    view_model: ReportViewModel,
    *,
    report: ChatReportRead,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    content_width = _PAGE_WIDTH - 32 * mm
    i18n = view_model.i18n
    story: list[object] = []

    # -------------------------------------------------------------------------
    # Document Header
    # -------------------------------------------------------------------------
    story.extend(
        [
            Paragraph(_paragraph_text(i18n["org_header"]), styles["eyebrow"]),
            Spacer(1, 2 * mm),
            Paragraph(_paragraph_text(i18n["doc_title"]), styles["doc_title"]),
            Spacer(1, 3 * mm),
            _header_meta_table(view_model, styles=styles, width=content_width),
            Spacer(1, 3 * mm),
            HRFlowable(width="100%", thickness=1.2, color=_DARK_RULE),
            Spacer(1, 5 * mm),
        ]
    )

    # -------------------------------------------------------------------------
    # 5.1 สรุปเหตุการณ์ / Incident Summary
    # -------------------------------------------------------------------------
    story.extend(
        [
            Paragraph(_paragraph_text(i18n["sec_5_1"]), styles["section_heading"]),
            Spacer(1, 2 * mm),
        ]
    )
    for p in view_model.summary_paragraphs:
        story.append(Paragraph(_paragraph_text(p), styles["body_indent"]))
        story.append(Spacer(1, 1.5 * mm))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------------------
    # 5.2 ลำดับเหตุการณ์ / Chronological Timeline
    # -------------------------------------------------------------------------
    story.extend(
        [
            Paragraph(_paragraph_text(i18n["sec_5_2"]), styles["section_heading"]),
            Spacer(1, 2 * mm),
        ]
    )
    if view_model.timeline_rows:
        has_very_long_events = any(len(r.event) > 600 for r in view_model.timeline_rows)
        if not has_very_long_events:
            timeline_table_data = [
                [
                    Paragraph(f"<b>{_paragraph_text(i18n['col_order'])}</b>", styles["table_header_center"]),
                    Paragraph(f"<b>{_paragraph_text(i18n['col_time'])}</b>", styles["table_header"]),
                    Paragraph(f"<b>{_paragraph_text(i18n['col_event'])}</b>", styles["table_header"]),
                    Paragraph(f"<b>{_paragraph_text(i18n['col_source_evidence'])}</b>", styles["table_header"]),
                ]
            ]
            for row in view_model.timeline_rows:
                event_text = _paragraph_text(row.event)
                if row.actors and row.actors != "-":
                    event_text += f"<br/><font color=\"#6B7280\" size=\"7.5\">{_paragraph_text(i18n['actor_prefix'])}: {_paragraph_text(row.actors)}</font>"
                timeline_table_data.append(
                    [
                        Paragraph(str(row.order), styles["table_cell_center"]),
                        Paragraph(f"<b>{_paragraph_text(row.time_display)}</b>", styles["table_cell_small"]),
                        Paragraph(event_text, styles["table_cell"]),
                        Paragraph(_paragraph_text(row.source_evidence), styles["table_cell_small"]),
                    ]
                )
            col_w = (14 * mm, 34 * mm, 86 * mm, 44 * mm)
            t = Table(timeline_table_data, colWidths=col_w, repeatRows=1)
            t.setStyle(_table_style())
            story.append(t)
        else:
            for row in view_model.timeline_rows:
                header_data = [
                    [
                        Paragraph(f"<b>{_paragraph_text(i18n['col_order'])} {row.order}</b>", styles["table_header_center"]),
                        Paragraph(f"<b>{_paragraph_text(i18n['col_time'])}: {_paragraph_text(row.time_display)}</b>", styles["table_header"]),
                        Paragraph(f"<b>{_paragraph_text(i18n['col_source_evidence'])}: {_paragraph_text(row.source_evidence)}</b>", styles["table_header"]),
                    ]
                ]
                t_head = Table(header_data, colWidths=(22 * mm, 60 * mm, 96 * mm))
                t_head.setStyle(_table_style())
                story.append(t_head)
                story.append(Spacer(1, 1.5 * mm))

                event_body = _paragraph_text(row.event)
                if row.actors and row.actors != "-":
                    event_body += f"<br/><font color=\"#6B7280\" size=\"7.5\">{_paragraph_text(i18n['actor_prefix'])}: {_paragraph_text(row.actors)}</font>"
                story.append(Paragraph(event_body, styles["body"]))
                story.append(Spacer(1, 3 * mm))
    else:
        story.append(Paragraph(_paragraph_text(i18n["empty_timeline"]), styles["body_muted"]))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------------------
    # 5.3 หลักฐานและตัวบ่งชี้สำคัญ / Evidence & Key Indicators
    # -------------------------------------------------------------------------
    story.extend(
        [
            Paragraph(_paragraph_text(i18n["sec_5_3"]), styles["section_heading"]),
            Spacer(1, 2 * mm),
            Paragraph(f"<b>{_paragraph_text(i18n['sub_evidence_reg'])}</b>", styles["subheading"]),
            Spacer(1, 1.5 * mm),
        ]
    )
    if view_model.evidence_rows:
        ev_table_data = [
            [
                Paragraph(f"<b>{_paragraph_text(i18n['col_item'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_type'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_description'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_source'])}</b>", styles["table_header"]),
            ]
        ]
        for ev in view_model.evidence_rows:
            ev_title = (
                f"<b>{_paragraph_text(ev.title)}</b>"
                f"<br/><font color=\"#6B7280\" size=\"7\">ID: {_paragraph_text(ev.item_id)}</font>"
            )
            ev_table_data.append(
                [
                    Paragraph(ev_title, styles["table_cell"]),
                    Paragraph(_paragraph_text(ev.artifact_type), styles["table_cell_small"]),
                    Paragraph(_paragraph_text(ev.description), styles["table_cell"]),
                    Paragraph(_paragraph_text(ev.source_type), styles["table_cell_small"]),
                ]
            )
        t_ev = Table(ev_table_data, colWidths=(44 * mm, 32 * mm, 68 * mm, 34 * mm), repeatRows=1)
        t_ev.setStyle(_table_style())
        story.append(t_ev)
    else:
        story.append(Paragraph(_paragraph_text(i18n["empty_evidence"]), styles["body_muted"]))

    if view_model.has_indicators:
        story.extend(
            [
                Spacer(1, 3 * mm),
                Paragraph(f"<b>{_paragraph_text(i18n['sub_iocs'])}</b>", styles["subheading"]),
                Spacer(1, 1.5 * mm),
            ]
        )
        ioc_table_data = [
            [
                Paragraph(f"<b>{_paragraph_text(i18n['col_ioc_type'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_ioc_value'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_ioc_note'])}</b>", styles["table_header"]),
            ]
        ]
        for ioc in view_model.indicator_rows:
            ioc_table_data.append(
                [
                    Paragraph(f"<b>{_paragraph_text(ioc.indicator_type)}</b>", styles["table_cell_small"]),
                    Paragraph(f"<font name=\"Courier\" size=\"7.5\">{_paragraph_text(ioc.value)}</font>", styles["table_cell_code"]),
                    Paragraph(_paragraph_text(ioc.note), styles["table_cell_small"]),
                ]
            )
        t_ioc = Table(ioc_table_data, colWidths=(38 * mm, 80 * mm, 60 * mm), repeatRows=1)
        t_ioc.setStyle(_table_style())
        story.append(t_ioc)
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------------------
    # 5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี / Relationships
    # -------------------------------------------------------------------------
    rel_story: list[object] = [
        Paragraph(_paragraph_text(i18n["sec_5_4"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    if view_model.has_relationships:
        rel_story.append(Paragraph(_paragraph_text(i18n["sub_relationships"]), styles["body"]))
        rel_story.append(Spacer(1, 1.5 * mm))
        for rel in view_model.relationship_rows:
            rel_text = (
                f"• <b>{_paragraph_text(rel.statement)}</b> "
                f"<font color=\"#6B7280\" size=\"7.5\">[{_paragraph_text(rel.status)} / {_paragraph_text(rel.confidence)}]</font>"
            )
            rel_story.append(Paragraph(rel_text, styles["relationship_item"]))
            rel_story.append(Spacer(1, 1.5 * mm))
    else:
        rel_story.append(Paragraph(_paragraph_text(i18n["empty_relationships"]), styles["body_muted"]))
    story.append(KeepTogether(rel_story))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------------------
    # 5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping
    # -------------------------------------------------------------------------
    story.extend(
        [
            Paragraph(_paragraph_text(i18n["sec_5_5"]), styles["section_heading"]),
            Spacer(1, 2 * mm),
        ]
    )
    if view_model.has_mitre_mappings:
        story.append(Paragraph(_paragraph_text(i18n["sub_mitre_intro"]), styles["body"]))
        story.append(Spacer(1, 1.5 * mm))
        mitre_table_data = [
            [
                Paragraph(f"<b>{_paragraph_text(i18n['col_finding'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_case_support'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_mitre'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{_paragraph_text(i18n['col_mapping_status'])}</b>", styles["table_header"]),
            ]
        ]
        for m in view_model.mitre_rows:
            tech_text = (
                f"<b>{_paragraph_text(m.technique_id)}</b>"
                f"<br/><font color=\"#4B5563\" size=\"7.5\">{_paragraph_text(m.technique_name)}</font>"
            )
            status_text = (
                f"{_paragraph_text(m.status_display)}"
                f"<br/><font color=\"#6B7280\" size=\"7\">{_paragraph_text(i18n['retrieval_source'])}: {_paragraph_text(m.source)}</font>"
            )
            mitre_table_data.append(
                [
                    Paragraph(f"<b>{_paragraph_text(m.finding)}</b>", styles["table_cell"]),
                    Paragraph(_paragraph_text(m.case_evidence_support), styles["table_cell"]),
                    Paragraph(tech_text, styles["table_cell_small"]),
                    Paragraph(status_text, styles["table_cell_small"]),
                ]
            )
        t_mitre = Table(mitre_table_data, colWidths=(44 * mm, 60 * mm, 44 * mm, 30 * mm), repeatRows=1)
        t_mitre.setStyle(_table_style())
        story.append(t_mitre)
    else:
        story.append(Paragraph(_paragraph_text(i18n["empty_mitre"]), styles["body_muted"]))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------------------
    # 5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม
    # -------------------------------------------------------------------------
    gaps_story: list[object] = [
        Paragraph(_paragraph_text(i18n["sec_5_6"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{_paragraph_text(i18n['sub_unresolved'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    for issue in view_model.unresolved_issues:
        issue_text = f"• <b>{_paragraph_text(issue.description)}</b>"
        if issue.reason and issue.reason != "-":
            issue_text += f"<br/><font color=\"#6B7280\" size=\"7.5\">&nbsp;&nbsp;{_paragraph_text(issue.reason)}</font>"
        gaps_story.append(Paragraph(issue_text, styles["body"]))
        gaps_story.append(Spacer(1, 1.5 * mm))

    gaps_story.extend(
        [
            Spacer(1, 2 * mm),
            Paragraph(f"<b>{_paragraph_text(i18n['sub_next_steps'])}</b>", styles["subheading"]),
            Spacer(1, 1.5 * mm),
        ]
    )
    for action in view_model.verification_actions:
        action_text = f"{action.order}. {_paragraph_text(action.action)}"
        gaps_story.append(Paragraph(action_text, styles["body"]))
        gaps_story.append(Spacer(1, 1.5 * mm))

    story.append(KeepTogether(gaps_story))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------------------
    # 5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ
    # -------------------------------------------------------------------------
    prov_story: list[object] = [
        Paragraph(_paragraph_text(i18n["sec_5_7"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{_paragraph_text(i18n['sub_limitations'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    for limit in view_model.limitations:
        prov_story.append(Paragraph(f"• {_paragraph_text(limit)}", styles["body_small"]))
        prov_story.append(Spacer(1, 1.2 * mm))

    prov_story.extend(
        [
            Spacer(1, 3 * mm),
            Paragraph(f"<b>{_paragraph_text(i18n['sub_provenance'])}</b>", styles["subheading"]),
            Spacer(1, 1.5 * mm),
        ]
    )
    prov_table_data = [
        [
            Paragraph(f"<b>{_paragraph_text(i18n['col_prov_item'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{_paragraph_text(i18n['col_prov_value'])}</b>", styles["table_header"]),
        ]
    ]
    for p_row in view_model.provenance_rows:
        prov_table_data.append(
            [
                Paragraph(f"<b>{_paragraph_text(p_row.label)}</b>", styles["table_cell_small"]),
                Paragraph(f"<font name=\"Courier\" size=\"7.5\">{_paragraph_text(p_row.value)}</font>", styles["table_cell_code"]),
            ]
        )
    t_prov = Table(prov_table_data, colWidths=(50 * mm, 128 * mm), repeatRows=1)
    t_prov.setStyle(_table_style())
    prov_story.append(t_prov)

    prov_story.extend(
        [
            Spacer(1, 5 * mm),
            HRFlowable(width="100%", thickness=0.8, color=_RULE),
            Spacer(1, 3 * mm),
            Paragraph(
                _paragraph_text(i18n["end_of_report"]),
                styles["end_note"],
            ),
        ]
    )
    story.append(KeepTogether(prov_story))
    return story


def _header_meta_table(
    view_model: ReportViewModel,
    *,
    styles: dict[str, ParagraphStyle],
    width: float,
) -> Table:
    i18n = view_model.i18n
    data = [
        [
            Paragraph(f"<b>{_paragraph_text(i18n['lbl_case_title'])}</b>", styles["meta_label"]),
            Paragraph(f"<b>{_paragraph_text(view_model.case_title)}</b>", styles["meta_value"]),
        ],
        [
            Paragraph(f"<b>{_paragraph_text(i18n['lbl_generated_date'])}</b>", styles["meta_label"]),
            Paragraph(_paragraph_text(view_model.generated_date), styles["meta_value"]),
        ],
        [
            Paragraph(f"<b>{_paragraph_text(i18n['lbl_report_status'])}</b>", styles["meta_label"]),
            Paragraph(f"<b>{_paragraph_text(view_model.report_status)}</b>", styles["meta_value"]),
        ],
    ]
    t = Table(data, colWidths=(35 * mm, width - 35 * mm))
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, _RULE),
            ]
        )
    )
    return t


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), _PANEL),
            ("TEXTCOLOR", (0, 0), (-1, 0), _INK),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2.0 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 2.0 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2.0 * mm),
            ("GRID", (0, 0), (-1, -1), 0.4, _RULE),
            ("LINEABOVE", (0, 0), (-1, 0), 1.0, _DARK_RULE),
            ("LINEBELOW", (0, 0), (-1, 0), 1.0, _DARK_RULE),
        ]
    )


def _draw_page_chrome(
    canvas,
    document,
    *,
    font_names: tuple[str, str],
    report_id: str,
    view_model: ReportViewModel,
) -> None:
    regular, bold = font_names
    i18n = view_model.i18n
    canvas.saveState()
    canvas.setStrokeColor(_RULE)
    canvas.setLineWidth(0.6)

    # Top running header line
    canvas.line(
        document.leftMargin,
        _PAGE_HEIGHT - 12 * mm,
        _PAGE_WIDTH - document.rightMargin,
        _PAGE_HEIGHT - 12 * mm,
    )
    # Bottom footer line
    canvas.line(
        document.leftMargin,
        12 * mm,
        _PAGE_WIDTH - document.rightMargin,
        12 * mm,
    )

    canvas.setFont(bold, 7)
    canvas.setFillColor(_MUTED)
    canvas.drawString(
        document.leftMargin,
        _PAGE_HEIGHT - 10 * mm,
        "CYBERCASE INTELLIGENCE FRAMEWORK",
    )
    canvas.drawRightString(
        _PAGE_WIDTH - document.rightMargin,
        _PAGE_HEIGHT - 10 * mm,
        _plain(i18n["running_header"]),
    )

    canvas.setFont(regular, 6.5)
    canvas.drawString(
        document.leftMargin,
        8 * mm,
        f"Report ID: {report_id}",
    )
    canvas.drawRightString(
        _PAGE_WIDTH - document.rightMargin,
        8 * mm,
        f"{_plain(i18n['page_label'])} {document.page}",
    )
    canvas.restoreState()


def _build_styles(font_names: tuple[str, str]) -> dict[str, ParagraphStyle]:
    regular, bold = font_names
    base = getSampleStyleSheet()

    return {
        "eyebrow": ParagraphStyle(
            "ReportEyebrow",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=10,
            textColor=_MUTED,
            textTransform="uppercase",
        ),
        "doc_title": ParagraphStyle(
            "ReportDocTitle",
            parent=base["Normal"],
            fontName=bold,
            fontSize=14,
            leading=18,
            textColor=_INK,
        ),
        "section_heading": ParagraphStyle(
            "ReportSectionHeading",
            parent=base["Normal"],
            fontName=bold,
            fontSize=10.5,
            leading=14,
            textColor=_INK,
            keepWithNext=True,
        ),
        "subheading": ParagraphStyle(
            "ReportSubheading",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8.5,
            leading=11.5,
            textColor=_INK,
            keepWithNext=True,
        ),
        "meta_label": ParagraphStyle(
            "ReportMetaLabel",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=10.5,
            textColor=_MUTED,
        ),
        "meta_value": ParagraphStyle(
            "ReportMetaValue",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=10.5,
            textColor=_INK,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=11.5,
            textColor=_INK,
        ),
        "body_indent": ParagraphStyle(
            "ReportBodyIndent",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=11.5,
            textColor=_INK,
            firstLineIndent=14,
        ),
        "body_small": ParagraphStyle(
            "ReportBodySmall",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=10,
            textColor=_INK,
        ),
        "body_muted": ParagraphStyle(
            "ReportBodyMuted",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=11,
            textColor=_MUTED,
        ),
        "relationship_item": ParagraphStyle(
            "ReportRelItem",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=11.5,
            textColor=_INK,
        ),
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=9.5,
            textColor=_INK,
        ),
        "table_header_center": ParagraphStyle(
            "ReportTableHeaderCenter",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=9.5,
            textColor=_INK,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "ReportTableCell",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=10,
            textColor=_INK,
        ),
        "table_cell_center": ParagraphStyle(
            "ReportTableCellCenter",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=10,
            textColor=_INK,
            alignment=TA_CENTER,
        ),
        "table_cell_small": ParagraphStyle(
            "ReportTableCellSmall",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=9.5,
            textColor=_INK,
        ),
        "table_cell_code": ParagraphStyle(
            "ReportTableCellCode",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=7,
            leading=9.5,
            textColor=_INK,
        ),
        "end_note": ParagraphStyle(
            "ReportEndNote",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=10,
            textColor=_MUTED,
            alignment=TA_CENTER,
        ),
    }


def _paragraph_text(value: object) -> str:
    text = _plain(value)
    return escape(text).replace("\n", "<br/>")


def _plain(value: object) -> str:
    return (
        str(value)
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def _register_fonts() -> tuple[str, str]:
    regular_path = _find_font(
        "CYBERCASE_PDF_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ),
    )
    bold_path = _find_font(
        "CYBERCASE_PDF_BOLD_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/tahomabd.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ),
    )
    if regular_path is None or bold_path is None:
        return "Helvetica", "Helvetica-Bold"

    try:
        pdfmetrics.registerFont(TTFont("CyberCaseSans", regular_path))
        pdfmetrics.registerFont(TTFont("CyberCaseSansBold", bold_path))
        return "CyberCaseSans", "CyberCaseSansBold"
    except Exception:
        return "Helvetica", "Helvetica-Bold"


def _find_font(environment_name: str, candidates: tuple[str, ...]) -> str | None:
    configured = Path(os.environ.get(environment_name, ""))
    if configured.is_file():
        return str(configured)
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return str(path)
    return None


__all__ = ["render_chat_report_pdf"]
