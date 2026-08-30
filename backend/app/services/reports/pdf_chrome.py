from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle

from app.services.reports.pdf_design import (
    DARK_RULE,
    INK,
    MUTED,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    PANEL,
    RULE,
    paragraph_text,
    plain_text,
)
from app.services.reports.report_view_model_contracts import ReportViewModel


def header_meta_table(
    view_model: ReportViewModel,
    *,
    styles: dict[str, object],
    width: float,
) -> Table:
    i18n = view_model.i18n
    data = [
        [
            Paragraph(f"<b>{paragraph_text(i18n['lbl_case_title'])}</b>", styles["meta_label"]),
            Paragraph(f"<b>{paragraph_text(view_model.case_title)}</b>", styles["meta_value"]),
        ],
        [
            Paragraph(f"<b>{paragraph_text(i18n['lbl_generated_date'])}</b>", styles["meta_label"]),
            Paragraph(paragraph_text(view_model.generated_date), styles["meta_value"]),
        ],
        [
            Paragraph(f"<b>{paragraph_text(i18n['lbl_report_status'])}</b>", styles["meta_label"]),
            Paragraph(f"<b>{paragraph_text(view_model.report_status)}</b>", styles["meta_value"]),
        ],
    ]
    table = Table(data, colWidths=(35 * mm, width - 35 * mm))
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
    ]))
    return table


def table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.0 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.0 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.0 * mm),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("LINEABOVE", (0, 0), (-1, 0), 1.0, DARK_RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, DARK_RULE),
    ])


def draw_page_chrome(
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
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(document.leftMargin, PAGE_HEIGHT - 12 * mm, PAGE_WIDTH - document.rightMargin, PAGE_HEIGHT - 12 * mm)
    canvas.line(document.leftMargin, 12 * mm, PAGE_WIDTH - document.rightMargin, 12 * mm)
    canvas.setFont(bold, 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(document.leftMargin, PAGE_HEIGHT - 10 * mm, "CYBERCASE INTELLIGENCE FRAMEWORK")
    canvas.drawRightString(PAGE_WIDTH - document.rightMargin, PAGE_HEIGHT - 10 * mm, plain_text(i18n["running_header"]))
    canvas.setFont(regular, 6.5)
    canvas.drawString(document.leftMargin, 8 * mm, f"Report ID: {report_id}")
    canvas.drawRightString(PAGE_WIDTH - document.rightMargin, 8 * mm, f"{plain_text(i18n['page_label'])} {document.page}")
    canvas.restoreState()
