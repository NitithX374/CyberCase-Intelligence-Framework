from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.reports import StructuredReport
from app.services.reports.contracts import CaseReportInput
from app.services.reports.display import build_case_report_display
from app.services.reports.text import clean_report_text, strip_reference_text

TEMPLATE_DIRECTORY = Path(__file__).with_name("templates")
REPORT_TEMPLATE_NAME = "case_report.html.j2"


def render_case_report_html(
    report_input: CaseReportInput,
    report: StructuredReport,
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
        display=build_case_report_display(report_input, report),
    )


__all__ = ["REPORT_TEMPLATE_NAME", "render_case_report_html"]
