from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from itertools import chain, repeat
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from app.reports.display import thai_date
from app.reports.schemas import CaseReportContent, ReportQuoteContext
from app.trace.summary import summary_closings

HEADING_MARKER = re.compile(r"^#{1,6}\s*", flags=re.MULTILINE)
OCR_MARKUP = re.compile(
    r"<page_number>[^<]*</page_number>|</?(?:table|thead|tbody|tfoot|tr|th|td|caption|br)\b[^<>]*>",
    flags=re.IGNORECASE,
)
TEMPLATE_DIRECTORY = Path(__file__).with_name("templates")
REPORT_TEMPLATE_NAME = "case_report.html.j2"


@dataclass(frozen=True)
class ReportIssue:
    version_number: int
    created_at: datetime


def clean_report_text(value: object) -> str:
    text = HEADING_MARKER.sub("", str(value))
    return text.replace("**", "").replace("`", "")


def readable(text: str) -> str:
    return re.sub(r"\s+", " ", OCR_MARKUP.sub(" ", text))


def quoted(quotes: list[str], contexts: list[ReportQuoteContext | None]) -> list[Markup]:
    return [
        quote_in_context(quote, context)
        for quote, context in zip(quotes, chain(contexts, repeat(None)), strict=False)
    ]


def quote_in_context(quote: str, context: ReportQuoteContext | None) -> Markup:
    shown = readable(quote).strip()
    before = readable(context.before).lstrip() if context else ""
    after = readable(context.after).rstrip() if context else ""
    if context is None or not (before or after):
        return Markup("“{}”").format(shown)
    return Markup("“{}{}<strong>{}</strong>{}{}”").format(
        "… " if context.cut_before else "",
        before,
        shown,
        after,
        " …" if context.cut_after else "",
    )


def note_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("a") + remainder) + letters
    return letters


def closings_of(report: CaseReportContent) -> list[str]:
    closings = summary_closings(report.summary)
    return (
        closings if len(closings) == len(report.summary_units) else [""] * len(report.summary_units)
    )


def render_case_report_html(report: CaseReportContent, issue: ReportIssue | None = None) -> str:
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIRECTORY)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "j2", "xml"),
            default_for_string=True,
        ),
    )
    environment.filters["clean_report_text"] = clean_report_text
    environment.filters["quoted"] = quoted
    environment.filters["readable"] = readable
    environment.filters["note_letter"] = note_letter
    template = environment.get_template(REPORT_TEMPLATE_NAME)
    return template.render(
        report=report,
        summary_closings=closings_of(report),
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
    "note_letter",
    "quoted",
    "readable",
    "render_case_report_html",
    "render_case_report_pdf",
]
