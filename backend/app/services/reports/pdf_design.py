from __future__ import annotations

import os
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        "body": ParagraphStyle("ReportBody", parent=base["Normal"], fontName=regular, fontSize=8.5, leading=12.2, textColor=INK),
        "body_indent": ParagraphStyle("ReportBodyIndent", parent=base["Normal"], fontName=regular, fontSize=8.5, leading=12.2, textColor=INK, firstLineIndent=14),
        "body_small": ParagraphStyle("ReportBodySmall", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK),
        "body_muted": ParagraphStyle("ReportBodyMuted", parent=base["Normal"], fontName=regular, fontSize=8, leading=11, textColor=MUTED),
        "table_header": ParagraphStyle("ReportTableHeader", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=9.5, textColor=INK),
        "table_header_center": ParagraphStyle("ReportTableHeaderCenter", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=9.5, textColor=INK, alignment=TA_CENTER),
        "table_cell": ParagraphStyle("ReportTableCell", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK),
        "table_cell_center": ParagraphStyle("ReportTableCellCenter", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=10, textColor=INK, alignment=TA_CENTER),
        "table_cell_small": ParagraphStyle("ReportTableCellSmall", parent=base["Normal"], fontName=regular, fontSize=7.5, leading=9.5, textColor=INK),
        "table_cell_code": ParagraphStyle("ReportTableCellCode", parent=base["Normal"], fontName="Courier", fontSize=7, leading=9.5, textColor=INK),
        "end_note": ParagraphStyle("ReportEndNote", parent=base["Normal"], fontName=bold, fontSize=7.5, leading=10, textColor=MUTED, alignment=TA_CENTER),
    }


import re


def formatted_text(value: object) -> str:
    """Format markdown text (bold, italic, code, line breaks) into safe ReportLab HTML."""
    raw = plain_text(value)
    # Remove markdown header artifacts
    raw = re.sub(r"^###+\s*[^\n]+\n?", "", raw, flags=re.MULTILINE)
    # Escape HTML special characters
    escaped = escape(raw)
    # Convert bold **text** -> <b>text</b>
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    # Convert italic *text* -> <i>text</i>
    escaped = re.sub(r"\*([^\*]+?)\*", r"<i>\1</i>", escaped)
    # Convert inline code `code` -> <font name="Courier" size="7.5">\1</font>
    escaped = re.sub(r"`([^`]+?)`", r'<font name="Courier" size="7.5">\1</font>', escaped)
    # Convert newlines to <br/>
    escaped = escaped.replace("\n", "<br/>")
    return escaped


def paragraph_text(value: object) -> str:
    return formatted_text(value)


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

