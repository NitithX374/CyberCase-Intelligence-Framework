from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.reports import StructuredReport
from app.services.reports.case_report_contracts import CaseReportInput
from app.services.reports.case_report_pdf_formatting import formatted_text, paragraph_text, plain_text
from app.services.reports.case_report_pdf_sections import (
    build_indicator_story,
    build_source_register_story,
)
from app.services.reports.case_report_rendering import CaseReportDisplay, build_case_report_display


INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#4B5563")
RULE = colors.HexColor("#E5E7EB")
DARK_RULE = colors.HexColor("#243B53")
ACCENT = colors.HexColor("#243B53")
PANEL = colors.HexColor("#EAF0F6")
PAGE_WIDTH, PAGE_HEIGHT = A4


def register_report_fonts() -> tuple[str, str]:
    regular_path = find_report_font(
        "CYBERCASE_PDF_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ),
    )
    bold_path = find_report_font(
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


def find_report_font(
    environment_name: str,
    candidates: tuple[str, ...],
) -> str | None:
    configured = Path(os.environ.get(environment_name, ""))
    if configured.is_file():
        return str(configured)
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return str(path)
    return None


def build_report_styles(font_names: tuple[str, str]) -> dict[str, ParagraphStyle]:
    regular, bold = font_names
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle("ReportEyebrow", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=10, textColor=MUTED, textTransform="uppercase", spaceAfter=1),
        "doc_title": ParagraphStyle("ReportDocTitle", parent=base["Normal"], fontName=bold, fontSize=17, leading=22, textColor=ACCENT),
        "section_heading": ParagraphStyle("ReportSectionHeading", parent=base["Normal"], fontName=bold, fontSize=10.5, leading=14, textColor=ACCENT, backColor=PANEL, borderColor=RULE, borderWidth=0.4, borderPadding=(1.5, 5, 1.5, 5), keepWithNext=True),
        "subheading": ParagraphStyle("ReportSubheading", parent=base["Normal"], fontName=bold, fontSize=8.5, leading=11.5, textColor=INK, keepWithNext=True),
        "meta_label": ParagraphStyle("ReportMetaLabel", parent=base["Normal"], fontName=bold, fontSize=8, leading=10.5, textColor=MUTED),
        "meta_value": ParagraphStyle("ReportMetaValue", parent=base["Normal"], fontName=regular, fontSize=8, leading=10.5, textColor=INK),
        "body": ParagraphStyle("ReportBody", parent=base["Normal"], fontName=regular, fontSize=9.5, leading=13.8, textColor=INK),
        "body_indent": ParagraphStyle("ReportBodyIndent", parent=base["Normal"], fontName=regular, fontSize=9.5, leading=13.8, textColor=INK, firstLineIndent=14),
        "body_small": ParagraphStyle("ReportBodySmall", parent=base["Normal"], fontName=regular, fontSize=8.5, leading=11.5, textColor=INK),
        "body_muted": ParagraphStyle("ReportBodyMuted", parent=base["Normal"], fontName=regular, fontSize=8.5, leading=11.5, textColor=MUTED),
        "table_header": ParagraphStyle("ReportTableHeader", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=9.5, textColor=INK),
        "table_header_center": ParagraphStyle("ReportTableHeaderCenter", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=9.5, textColor=INK, alignment=TA_CENTER),
        "table_cell": ParagraphStyle("ReportTableCell", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK),
        "table_cell_center": ParagraphStyle("ReportTableCellCenter", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK, alignment=TA_CENTER),
        "table_cell_small": ParagraphStyle("ReportTableCellSmall", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=9.5, textColor=INK),
        "table_cell_code": ParagraphStyle("ReportTableCellCode", parent=base["Normal"], fontName="Courier", fontSize=7, leading=9.5, textColor=INK),
        "end_note": ParagraphStyle("ReportEndNote", parent=base["Normal"], fontName=bold, fontSize=8.5, leading=11.5, textColor=MUTED, alignment=TA_CENTER),
    }


def render_case_report_pdf(
    report_input: CaseReportInput,
    report: StructuredReport,
    report_id: UUID,
) -> bytes:
    fonts = register_report_fonts()
    styles = build_report_styles(fonts)
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=plain_text(report.title),
        author="CyberCase Intelligence Framework",
        subject="Preliminary case analysis report",
    )
    story = _story(report_input, report, styles)
    document.build(
        story,
        onFirstPage=lambda canvas, doc: _page_chrome(canvas, doc, report_id),
        onLaterPages=lambda canvas, doc: _page_chrome(canvas, doc, report_id),
    )
    return buffer.getvalue()


def _story(
    report_input: CaseReportInput,
    report: StructuredReport,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    display = build_case_report_display(report_input, report)
    story: list[object] = [
        Paragraph("CYBERCASE INTELLIGENCE FRAMEWORK", styles["eyebrow"]),
        Spacer(1, 2 * mm),
        Paragraph(paragraph_text(report.title), styles["doc_title"]),
        Spacer(1, 3 * mm),
        _metadata_table(display, styles),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1.2, color=DARK_RULE),
        Spacer(1, 5 * mm),
    ]
    for section in report.sections:
        story.extend(
            [
                Paragraph(paragraph_text(section.heading), styles["section_heading"]),
                Spacer(1, 2 * mm),
            ]
        )
        story.extend(Paragraph(paragraph_text(text), styles["body"]) for text in section.paragraphs)
        if section.section_id == "case_evidence":
            story.extend(build_indicator_story(display.claims, styles))
        else:
            for item in section.items:
                story.extend(
                    [
                        Paragraph(f"• {paragraph_text(item)}", styles["body"]),
                        Spacer(1, 1.2 * mm),
                    ]
                )
        story.append(Spacer(1, 3 * mm))
    story.extend(build_source_register_story(display.sources, styles))
    return story


def _metadata_table(
    display: CaseReportDisplay,
    styles: dict[str, ParagraphStyle],
) -> Table:
    rows = [
        ("ประเภทเอกสาร", "รายงานสรุปผลการวิเคราะห์คดีเบื้องต้น"),
        ("หลักฐานที่ใช้", f"{len(display.sources)} รายการ"),
        ("สถานะ", "เบื้องต้น / ยังไม่ยืนยัน"),
    ]
    table = Table(
        [[Paragraph(paragraph_text(label), styles["meta_label"]), Paragraph(paragraph_text(value), styles["meta_value"])] for label, value in rows],
        colWidths=(45 * mm, 133 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7DEE7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ]
        )
    )
    return table


def _page_chrome(canvas, document, _report_id: UUID) -> None:
    canvas.saveState()
    canvas.setStrokeColor(DARK_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(document.leftMargin, 11 * mm, A4[0] - document.rightMargin, 11 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.drawString(document.leftMargin, 7 * mm, "CyberCase · Preliminary analysis")
    canvas.drawRightString(A4[0] - document.rightMargin, 7 * mm, f"Page {document.page}")
    canvas.restoreState()


__all__ = [
    "ACCENT",
    "DARK_RULE",
    "INK",
    "MUTED",
    "PAGE_HEIGHT",
    "PAGE_WIDTH",
    "PANEL",
    "RULE",
    "build_report_styles",
    "find_report_font",
    "formatted_text",
    "paragraph_text",
    "plain_text",
    "register_report_fonts",
    "render_case_report_pdf",
]
