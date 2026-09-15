from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.reports import StructuredReport
from app.services.reports.case_report_contracts import CaseReportInput
from app.services.reports.case_report_rendering import build_case_report_display


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
    template = environment.get_template(REPORT_TEMPLATE_NAME)
    return template.render(
        report=report,
        display=build_case_report_display(report_input, report),
    )


def clean_report_text(value: object) -> str:
    text = str(value)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    return text.replace("**", "").replace("`", "")


__all__ = ["REPORT_TEMPLATE_NAME", "clean_report_text", "render_case_report_html"]
