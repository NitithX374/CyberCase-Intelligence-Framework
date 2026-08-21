from __future__ import annotations

from html import escape

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from app.services.reports.pdf_theme import INK, MUTED


def build_report_styles(font_names: tuple[str, str]) -> dict[str, ParagraphStyle]:
    regular, bold = font_names
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle("ReportEyebrow", parent=base["Normal"], fontName=bold, fontSize=8, leading=10, textColor=MUTED, textTransform="uppercase"),
        "doc_title": ParagraphStyle("ReportDocTitle", parent=base["Normal"], fontName=bold, fontSize=14, leading=18, textColor=INK),
        "section_heading": ParagraphStyle("ReportSectionHeading", parent=base["Normal"], fontName=bold, fontSize=10.5, leading=14, textColor=INK, keepWithNext=True),
        "subheading": ParagraphStyle("ReportSubheading", parent=base["Normal"], fontName=bold, fontSize=8.5, leading=11.5, textColor=INK, keepWithNext=True),
        "meta_label": ParagraphStyle("ReportMetaLabel", parent=base["Normal"], fontName=bold, fontSize=8, leading=10.5, textColor=MUTED),
        "meta_value": ParagraphStyle("ReportMetaValue", parent=base["Normal"], fontName=regular, fontSize=8, leading=10.5, textColor=INK),
        "body": ParagraphStyle("ReportBody", parent=base["Normal"], fontName=regular, fontSize=8, leading=11.5, textColor=INK),
        "body_indent": ParagraphStyle("ReportBodyIndent", parent=base["Normal"], fontName=regular, fontSize=8, leading=11.5, textColor=INK, firstLineIndent=14),
        "body_small": ParagraphStyle("ReportBodySmall", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK),
        "body_muted": ParagraphStyle("ReportBodyMuted", parent=base["Normal"], fontName=regular, fontSize=8, leading=11, textColor=MUTED),
        "relationship_item": ParagraphStyle("ReportRelItem", parent=base["Normal"], fontName=regular, fontSize=8, leading=11.5, textColor=INK),
        "table_header": ParagraphStyle("ReportTableHeader", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=9.5, textColor=INK),
        "table_header_center": ParagraphStyle("ReportTableHeaderCenter", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=9.5, textColor=INK, alignment=TA_CENTER),
        "table_cell": ParagraphStyle("ReportTableCell", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK),
        "table_cell_center": ParagraphStyle("ReportTableCellCenter", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK, alignment=TA_CENTER),
        "table_cell_small": ParagraphStyle("ReportTableCellSmall", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=9.5, textColor=INK),
        "table_cell_code": ParagraphStyle("ReportTableCellCode", parent=base["Normal"], fontName="Courier", fontSize=7, leading=9.5, textColor=INK),
        "end_note": ParagraphStyle("ReportEndNote", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=10, textColor=MUTED, alignment=TA_CENTER),
    }


def paragraph_text(value: object) -> str:
    return escape(plain_text(value)).replace("\n", "<br/>")


def plain_text(value: object) -> str:
    return (
        str(value)
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )
