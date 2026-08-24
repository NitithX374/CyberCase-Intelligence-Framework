from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate

from app.schemas.reports import ChatReportRead
from app.services.reports.pdf_chrome import draw_page_chrome
from app.services.reports.pdf_design import (
    build_report_styles,
    plain_text,
    register_report_fonts,
)
from app.services.reports.report_pdf_story import build_formal_report_story
from app.services.reports.report_view_model_builder import build_report_view_model
from app.services.reports.report_view_model_contracts import ReportLanguage


def render_chat_report_pdf(
    report: ChatReportRead,
    *,
    thread_title: str,
    language: ReportLanguage = "th",
) -> bytes:
    if report.report is None:
        raise ValueError("a structured report is required for PDF rendering")

    view_model = build_report_view_model(report, thread_title=thread_title, language=language)
    font_names = register_report_fonts()
    styles = build_report_styles(font_names)
    buffer = BytesIO()
    doc_title = plain_text(report.report.title) if report.report.title else plain_text(view_model.case_title)
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
    story = build_formal_report_story(view_model, report=report, styles=styles)
    document.build(
        story,
        onFirstPage=lambda canvas, doc: draw_page_chrome(
            canvas,
            doc,
            font_names=font_names,
            report_id=view_model.report_id,
            view_model=view_model,
        ),
        onLaterPages=lambda canvas, doc: draw_page_chrome(
            canvas,
            doc,
            font_names=font_names,
            report_id=view_model.report_id,
            view_model=view_model,
        ),
    )
    return buffer.getvalue()


__all__ = ["render_chat_report_pdf"]
