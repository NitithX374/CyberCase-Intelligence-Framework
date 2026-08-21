"""Deterministic Jinja2 HTML rendering for CyberCase incident analysis reports."""

from __future__ import annotations

from pathlib import Path
from typing import Literal
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.reports import ChatReportRead
from app.services.reports.report_view_model import (
    ReportLanguage,
    ReportViewModel,
    build_report_view_model,
)

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
_CSS_PATH = _TEMPLATES_DIR / "report.css"

_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_report_css() -> str:
    """Return the embedded CSS stylesheet for HTML/PDF rendering."""
    if _CSS_PATH.is_file():
        return _CSS_PATH.read_text(encoding="utf-8")
    return ""


def render_chat_report_html_from_view_model(view_model: ReportViewModel) -> str:
    """Render HTML string deterministically from a ReportViewModel."""
    template = _jinja_env.get_template("report.html.j2")
    css_content = get_report_css()
    return template.render(
        report=view_model,
        css_content=css_content,
    )


def render_chat_report_html(
    report: ChatReportRead,
    *,
    thread_title: str = "CyberCase Investigation",
    language: ReportLanguage = "th",
) -> str:
    """Build the view model and render formal report HTML in Thai or English."""
    view_model = build_report_view_model(
        report,
        thread_title=thread_title,
        language=language,
    )
    return render_chat_report_html_from_view_model(view_model)


__all__ = [
    "get_report_css",
    "render_chat_report_html",
    "render_chat_report_html_from_view_model",
]
