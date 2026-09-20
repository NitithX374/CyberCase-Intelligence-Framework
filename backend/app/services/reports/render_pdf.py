from __future__ import annotations

import os
import re
from html import escape
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
from app.services.reports.contracts import CaseReportInput
from app.services.reports.display import (
    CaseReportDisplay,
    ReportDisplayClaim,
    ReportDisplaySource,
    build_case_report_display,
)
from app.services.reports.text import plain_text, strip_reference_text

INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#4B5563")
RULE = colors.HexColor("#D1D5DB")
DARK_RULE = colors.HexColor("#1E293B")
ACCENT = colors.HexColor("#1E293B")
PANEL = colors.HexColor("#F3F4F6")
PAGE_WIDTH = A4[0]


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
        "eyebrow": ParagraphStyle(
            "ReportEyebrow",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=10,
            textColor=MUTED,
            textTransform="uppercase",
            spaceAfter=1,
        ),
        "doc_title": ParagraphStyle(
            "ReportDocTitle",
            parent=base["Normal"],
            fontName=bold,
            fontSize=15,
            leading=20,
            textColor=ACCENT,
            spaceAfter=2,
        ),
        "doc_subtitle": ParagraphStyle(
            "ReportDocSubtitle",
            parent=base["Normal"],
            fontName=bold,
            fontSize=10,
            leading=14,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "section_heading": ParagraphStyle(
            "ReportSectionHeading",
            parent=base["Normal"],
            fontName=bold,
            fontSize=10.5,
            leading=14,
            textColor=ACCENT,
            backColor=PANEL,
            borderColor=RULE,
            borderWidth=0.5,
            borderPadding=(2, 5, 2, 5),
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "subheading": ParagraphStyle(
            "ReportSubheading",
            parent=base["Normal"],
            fontName=bold,
            fontSize=9,
            leading=13,
            textColor=ACCENT,
            spaceBefore=3,
            spaceAfter=1.5,
            keepWithNext=True,
        ),
        "meta_label": ParagraphStyle(
            "ReportMetaLabel",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=11,
            textColor=MUTED,
        ),
        "meta_value": ParagraphStyle(
            "ReportMetaValue",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=11,
            textColor=INK,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["Normal"],
            fontName=regular,
            fontSize=9,
            leading=14,
            textColor=INK,
        ),
        "body_indent": ParagraphStyle(
            "ReportBodyIndent",
            parent=base["Normal"],
            fontName=regular,
            fontSize=9,
            leading=14,
            textColor=INK,
            firstLineIndent=14,
        ),
        "body_small": ParagraphStyle(
            "ReportBodySmall",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8,
            leading=11,
            textColor=INK,
        ),
        "body_muted": ParagraphStyle(
            "ReportBodyMuted",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.5,
            leading=12.5,
            textColor=MUTED,
        ),
        "quote": ParagraphStyle(
            "ReportQuote",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.5,
            leading=12.5,
            textColor=MUTED,
            leftIndent=14,
        ),
        "reasoning": ParagraphStyle(
            "ReportReasoning",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor("#1E3A8A"),
            leftIndent=14,
        ),
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=9.5,
            textColor=INK,
        ),
        "table_header_center": ParagraphStyle(
            "ReportTableHeaderCenter",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=9.5,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "ReportTableCell",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=10,
            textColor=INK,
        ),
        "table_cell_center": ParagraphStyle(
            "ReportTableCellCenter",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=10,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "table_cell_small": ParagraphStyle(
            "ReportTableCellSmall",
            parent=base["Normal"],
            fontName=regular,
            fontSize=7.5,
            leading=9.5,
            textColor=INK,
        ),
        "table_cell_code": ParagraphStyle(
            "ReportTableCellCode",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=7,
            leading=9.5,
            textColor=INK,
        ),
        "end_note": ParagraphStyle(
            "ReportEndNote",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8.5,
            leading=11.5,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def formatted_text(value: object) -> str:
    raw = plain_text(value)
    raw = re.sub(r"^#{1,6}\s*", "", raw, flags=re.MULTILINE)
    escaped = escape(raw)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*([^\*]+?)\*", r"<i>\1</i>", escaped)
    escaped = re.sub(r"`([^`]+?)`", r'<font name="Courier" size="7.5">\1</font>', escaped)
    return escaped.replace("\n", "<br/>")


def paragraph_text(value: object) -> str:
    return formatted_text(value)


def build_indicator_story(
    claims: tuple[ReportDisplayClaim, ...],
    styles: dict[str, object],
) -> list[object]:
    story: list[object] = []
    for claim in claims:
        epistemic_note = ""
        if claim.epistemic_label not in ("ปรากฏในหลักฐาน", "reported"):
            epistemic_note = f" <i>({claim.epistemic_label})</i>"

        story.append(
            Paragraph(f"<b>ตัวบ่งชี้ที่ {claim.ordinal}:</b>{epistemic_note}", styles["subheading"])
        )
        story.append(Paragraph(paragraph_text(claim.text), styles["body"]))

        for quote in claim.supporting_quotes:
            story.append(
                Paragraph(f"<i>ข้อความจากหลักฐาน: “{paragraph_text(quote)}”</i>", styles["quote"])
            )
        for quote in claim.contradicting_quotes:
            story.append(
                Paragraph(f"<i>ข้อความที่ขัดแย้ง: “{paragraph_text(quote)}”</i>", styles["quote"])
            )
        if claim.reasoning_summary:
            story.append(
                Paragraph(
                    f"<i>เหตุผลเชิงวิเคราะห์: {paragraph_text(claim.reasoning_summary)}</i>",
                    styles["reasoning"],
                )
            )
        story.append(Spacer(1, 2 * mm))
    return story


def build_source_register_story(
    sources: tuple[ReportDisplaySource, ...],
    styles: dict[str, object],
) -> list[object]:
    story: list[object] = [
        Paragraph("เอกสารที่ใช้ประกอบการวิเคราะห์", styles["section_heading"]),
        Spacer(1, 1.5 * mm),
        Paragraph(
            "รายงานฉบับนี้จัดทำขึ้นจากการประมวลผลเอกสารหลักฐานในสำนวนคดีดังต่อไปนี้:",
            styles["body_muted"],
        ),
        Spacer(1, 1 * mm),
    ]
    for source in sources:
        story.append(
            Paragraph(
                paragraph_text(f"• {source.filename}"),
                styles["body"],
            )
        )
    return story


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
    story = build_report_story(report_input, report, styles)
    document.build(
        story,
        onFirstPage=lambda canvas, doc: draw_page_chrome(canvas, doc, report_id),
        onLaterPages=lambda canvas, doc: draw_page_chrome(canvas, doc, report_id),
    )
    return buffer.getvalue()


def build_report_story(
    report_input: CaseReportInput,
    report: StructuredReport,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    display = build_case_report_display(report_input, report)
    story: list[object] = [
        Paragraph("CYBERCASE INTELLIGENCE FRAMEWORK", styles["eyebrow"]),
        Spacer(1, 1.5 * mm),
        Paragraph("รายงานสรุปผลการวิเคราะห์คดีเบื้องต้น", styles["doc_title"]),
        Paragraph(f"เรื่อง: {paragraph_text(report.title)}", styles["doc_subtitle"]),
        Spacer(1, 1 * mm),
        build_metadata_table(display, styles),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1, color=DARK_RULE),
        Spacer(1, 3 * mm),
    ]
    for section in report.sections:
        story.append(Paragraph(paragraph_text(section.heading), styles["section_heading"]))
        story.append(Spacer(1, 1.5 * mm))

        if section.section_id == "case_summary":
            for paragraph in section.paragraphs:
                cleaned = strip_reference_text(paragraph)
                if cleaned.startswith("วัตถุประสงค์ของรายงาน:"):
                    story.append(
                        Paragraph(
                            f"<b>วัตถุประสงค์:</b> {paragraph_text(cleaned.replace('วัตถุประสงค์ของรายงาน:', '').strip())}",
                            styles["body"],
                        )
                    )
                    story.append(Spacer(1, 1 * mm))
                elif cleaned.startswith("สรุปจากผลวิเคราะห์:"):
                    story.append(
                        Paragraph("<b>สรุปภาพรวมจากผลการวิเคราะห์:</b>", styles["subheading"])
                    )
                    story.append(
                        Paragraph(
                            paragraph_text(cleaned.replace("สรุปจากผลวิเคราะห์:", "").strip()),
                            styles["body_indent"],
                        )
                    )
                    story.append(Spacer(1, 1 * mm))
                elif cleaned.startswith("ข้อสรุปเบื้องต้น:"):
                    story.append(Paragraph("<b>ข้อสรุปเบื้องต้น:</b>", styles["subheading"]))
                    story.append(
                        Paragraph(
                            paragraph_text(cleaned.replace("ข้อสรุปเบื้องต้น:", "").strip()),
                            styles["body_indent"],
                        )
                    )
                    story.append(Spacer(1, 1 * mm))
                else:
                    story.append(Paragraph(paragraph_text(cleaned), styles["body_indent"]))

            parties = []
            timeline = []
            impacts = []
            others = []

            for item in section.items:
                cleaned = strip_reference_text(item)
                if cleaned.startswith("ผู้เกี่ยวข้อง:"):
                    parties.append(cleaned.replace("ผู้เกี่ยวข้อง:", "").strip())
                elif cleaned.startswith("ลำดับเหตุการณ์:"):
                    timeline.append(cleaned.replace("ลำดับเหตุการณ์:", "").strip())
                elif cleaned.startswith("ผลกระทบที่ปรากฏ:"):
                    impacts.append(cleaned.replace("ผลกระทบที่ปรากฏ:", "").strip())
                else:
                    others.append(cleaned)

            if parties:
                story.append(Paragraph("<b>ผู้เกี่ยวข้องในคดี:</b>", styles["subheading"]))
                for p in parties:
                    match = re.match(r"^([^\(]+)\s*\((.+)\)$", p)
                    if match:
                        name, role = match.group(1).strip(), match.group(2).strip()
                        story.append(
                            Paragraph(
                                f"• <b>{paragraph_text(name)}</b> — {paragraph_text(role)}",
                                styles["body"],
                            )
                        )
                    else:
                        story.append(Paragraph(f"• {paragraph_text(p)}", styles["body"]))
                story.append(Spacer(1, 1.5 * mm))

            if timeline:
                story.append(Paragraph("<b>ลำดับเหตุการณ์สำคัญ:</b>", styles["subheading"]))
                for t in timeline:
                    if "—" in t:
                        time_part, event_part = t.split("—", 1)
                        story.append(
                            Paragraph(
                                f"• <b>{paragraph_text(time_part.strip())}</b>: {paragraph_text(event_part.strip())}",
                                styles["body"],
                            )
                        )
                    elif " - " in t:
                        time_part, event_part = t.split(" - ", 1)
                        story.append(
                            Paragraph(
                                f"• <b>{paragraph_text(time_part.strip())}</b>: {paragraph_text(event_part.strip())}",
                                styles["body"],
                            )
                        )
                    else:
                        story.append(Paragraph(f"• {paragraph_text(t)}", styles["body"]))
                story.append(Spacer(1, 1.5 * mm))

            if impacts:
                story.append(Paragraph("<b>ความเสียหายและผลกระทบที่ปรากฏ:</b>", styles["subheading"]))
                for imp in impacts:
                    story.append(Paragraph(f"• {paragraph_text(imp)}", styles["body"]))
                story.append(Spacer(1, 1.5 * mm))

            if others:
                for o in others:
                    story.append(Paragraph(f"• {paragraph_text(o)}", styles["body"]))

        elif section.section_id == "case_evidence":
            story.extend(build_indicator_story(display.claims, styles))

        elif section.section_id == "evidence_to_examine":
            for paragraph in section.paragraphs:
                story.append(Paragraph(paragraph_text(paragraph), styles["body"]))
                story.append(Spacer(1, 1 * mm))

            for item in section.items:
                cleaned = strip_reference_text(item)
                parts = [p.strip() for p in cleaned.split("·")]
                if len(parts) >= 3:
                    topic = parts[0]
                    prio = parts[1].replace("ระดับความสำคัญ:", "").strip()
                    status_part = parts[2].replace("สถานะ:", "").strip()
                    rest = " · ".join(parts[3:]) if len(parts) > 3 else ""

                    desc = rest
                    reason = ""
                    if "เหตุผล:" in rest:
                        desc, reason = rest.split("เหตุผล:", 1)
                    elif "เหตุผลเชิงวิเคราะห์:" in rest:
                        desc, reason = rest.split("เหตุผลเชิงวิเคราะห์:", 1)

                    story.append(
                        Paragraph(
                            f"• <b>{paragraph_text(topic)}</b> (ความสำคัญ: {paragraph_text(prio)} | สถานะ: {paragraph_text(status_part)})",
                            styles["body"],
                        )
                    )
                    if desc.strip():
                        story.append(
                            Paragraph(f"รายละเอียด: {paragraph_text(desc.strip())}", styles["quote"])
                        )
                    if reason.strip():
                        story.append(
                            Paragraph(
                                f"<i>เหตุผลที่ควรตรวจสอบ: {paragraph_text(reason.strip())}</i>",
                                styles["reasoning"],
                            )
                        )
                    story.append(Spacer(1, 1.5 * mm))
                else:
                    story.append(Paragraph(f"• {paragraph_text(cleaned)}", styles["body"]))

        elif section.section_id == "preliminary_recommendations":
            for paragraph in section.paragraphs:
                story.append(Paragraph(paragraph_text(paragraph), styles["body"]))
                story.append(Spacer(1, 1 * mm))

            specific_recs = []
            general_recs = []
            for item in section.items:
                cleaned = strip_reference_text(item)
                if cleaned.startswith("ตรวจสอบเพิ่มเติมในประเด็น"):
                    specific_recs.append(cleaned.replace("ตรวจสอบเพิ่มเติมในประเด็น", "").strip())
                else:
                    general_recs.append(cleaned)

            if specific_recs:
                story.append(
                    Paragraph("<b>ประเด็นสำคัญที่ควรดำเนินการตรวจสอบเพิ่มเติม:</b>", styles["subheading"])
                )
                for rec in specific_recs:
                    if ":" in rec:
                        topic, desc = rec.split(":", 1)
                        story.append(
                            Paragraph(
                                f"• <b>{paragraph_text(topic.strip())}</b>: {paragraph_text(desc.strip())}",
                                styles["body"],
                            )
                        )
                    else:
                        story.append(Paragraph(f"• {paragraph_text(rec)}", styles["body"]))
                story.append(Spacer(1, 1.5 * mm))

            if general_recs:
                story.append(
                    Paragraph("<b>แนวทางการปฏิบัติในการรวบรวมพยานหลักฐาน:</b>", styles["subheading"])
                )
                for rec in general_recs:
                    story.append(Paragraph(f"• {paragraph_text(rec)}", styles["body"]))
                story.append(Spacer(1, 1.5 * mm))

        else:
            for paragraph in section.paragraphs:
                story.append(Paragraph(paragraph_text(paragraph), styles["body"]))
                story.append(Spacer(1, 1 * mm))
            for item in section.items:
                cleaned = strip_reference_text(item)
                story.append(Paragraph(f"• {paragraph_text(cleaned)}", styles["body"]))
                story.append(Spacer(1, 1 * mm))

        story.append(Spacer(1, 2.5 * mm))

    story.extend(build_source_register_story(display.sources, styles))
    return story


def build_metadata_table(
    display: CaseReportDisplay,
    styles: dict[str, ParagraphStyle],
) -> Table:
    rows = [
        [
            Paragraph("<b>ประเภทเอกสาร:</b> รายงานสรุปผลการวิเคราะห์เบื้องต้น", styles["meta_value"]),
            Paragraph("<b>สถานะ:</b> เบื้องต้น / ยังไม่ยืนยัน", styles["meta_value"]),
        ],
        [
            Paragraph(f"<b>เอกสารที่นำเข้า:</b> {len(display.sources)} รายการ", styles["meta_value"]),
            Paragraph("<b>วัตถุประสงค์:</b> สำหรับการตรวจสำนวนภายใน", styles["meta_value"]),
        ],
    ]
    table = Table(
        rows,
        colWidths=(89 * mm, 89 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ]
        )
    )
    return table


def draw_page_chrome(canvas, document, report_id: UUID) -> None:
    canvas.saveState()
    canvas.setStrokeColor(DARK_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(document.leftMargin, 11 * mm, PAGE_WIDTH - document.rightMargin, 11 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.drawString(document.leftMargin, 7 * mm, "CyberCase · Preliminary analysis")
    canvas.drawRightString(PAGE_WIDTH - document.rightMargin, 7 * mm, f"Page {document.page}")
    canvas.restoreState()


__all__ = [
    "ACCENT",
    "DARK_RULE",
    "INK",
    "MUTED",
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
