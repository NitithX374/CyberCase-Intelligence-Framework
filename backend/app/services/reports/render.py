from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.reports import StructuredReport
from app.services.reports.contracts import CaseReportInput
from app.services.reports.display import ReportIssue, build_case_report_display

REFERENCE_SUFFIXES = (
    re.compile(r"\s*[·•]\s*อ้างอิง\s*:\s*.*$"),
    re.compile(r"\s*\(อ้างอิง\s*:\s*.*\)$"),
    re.compile(r"\s*\[อ้างอิง\s*:\s*.*\]$"),
)
HEADING_MARKER = re.compile(r"^#{1,6}\s*", flags=re.MULTILINE)


def clean_report_text(value: object) -> str:
    text = HEADING_MARKER.sub("", str(value))
    return text.replace("**", "").replace("`", "")


def strip_reference_text(value: object) -> str:
    text = clean_report_text(value)
    for pattern in REFERENCE_SUFFIXES:
        text = pattern.sub("", text)
    return text.strip()


TEMPLATE_DIRECTORY = Path(__file__).with_name("templates")
REPORT_TEMPLATE_NAME = "case_report.html.j2"


def render_case_report_html(
    report_input: CaseReportInput,
    report: StructuredReport,
    issue: ReportIssue | None = None,
) -> str:
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIRECTORY)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "j2", "xml"),
            default_for_string=True,
        ),
    )
    environment.filters["clean_report_text"] = clean_report_text
    environment.filters["strip_reference_text"] = strip_reference_text
    template = environment.get_template(REPORT_TEMPLATE_NAME)
    return template.render(
        report=report,
        display=build_case_report_display(report_input, report, issue),
    )


def render_case_report_pdf(
    report_input: CaseReportInput,
    report: StructuredReport,
    issue: ReportIssue | None = None,
) -> bytes:
    from weasyprint import HTML

    return HTML(string=render_case_report_html(report_input, report, issue)).write_pdf()


__all__ = [
    "REPORT_TEMPLATE_NAME",
    "clean_report_text",
    "render_case_report_html",
    "render_case_report_pdf",
    "strip_reference_text",
]
