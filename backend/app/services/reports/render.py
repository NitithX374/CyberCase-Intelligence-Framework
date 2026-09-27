from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.reports import CaseReportContent
from app.services.reports.display import thai_date

HEADING_MARKER = re.compile(r"^#{1,6}\s*", flags=re.MULTILINE)
TEMPLATE_DIRECTORY = Path(__file__).with_name("templates")
REPORT_TEMPLATE_NAME = "case_report.html.j2"


@dataclass(frozen=True)
class ReportIssue:
    version_number: int
    created_at: datetime


def clean_report_text(value: object) -> str:
    text = HEADING_MARKER.sub("", str(value))
    return text.replace("**", "").replace("`", "")


def render_case_report_html(report: CaseReportContent, issue: ReportIssue | None = None) -> str:
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIRECTORY)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "j2", "xml"),
            default_for_string=True,
        ),
    )
    environment.filters["clean_report_text"] = clean_report_text
    template = environment.get_template(REPORT_TEMPLATE_NAME)
    return template.render(
        report=report,
        issue=issue,
        issued=thai_date(issue.created_at, with_time=True) if issue else None,
    )


def render_case_report_pdf(report: CaseReportContent, issue: ReportIssue | None = None) -> bytes:
    from weasyprint import HTML

    return HTML(string=render_case_report_html(report, issue)).write_pdf()


__all__ = [
    "REPORT_TEMPLATE_NAME",
    "ReportIssue",
    "clean_report_text",
    "render_case_report_html",
    "render_case_report_pdf",
]
