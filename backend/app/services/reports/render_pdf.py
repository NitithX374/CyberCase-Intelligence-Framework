"""The PDF, printed from the same HTML the reader is shown.

There used to be two renderers for one report: a Jinja2 template for the HTML
export, and six hundred lines of reportlab for the PDF. Both read the same
`CaseReportDisplay`, but each took `content.py`'s joined strings apart again on
its own -- the template by prefix, the PDF by splitting on the separator and
indexing what fell out. So the two could disagree about the same report, and
the PDF broke whenever a separator moved: taking the gap id out of a bullet
shifted every positional index in it.

One renderer cannot disagree with itself. The page furniture the reportlab
canvas drew by hand -- the rule above the footer, the running title, the page
number -- is now `@page` margin boxes in the template's stylesheet, which is
where the A4 size and the margins already lived.

WeasyPrint lays text out through Pango and HarfBuzz, which break Thai lines
better than reportlab did; the Dockerfile installs those beside the Thai fonts,
and fontconfig finds the fonts from there without being told a path.
"""

from __future__ import annotations

from uuid import UUID

from app.schemas.reports import StructuredReport
from app.services.reports.contracts import CaseReportInput
from app.services.reports.render_html import render_case_report_html


def render_case_report_pdf(
    report_input: CaseReportInput,
    report: StructuredReport,
    report_id: UUID,
) -> bytes:
    """The stored report as a PDF: the HTML export, paginated.

    WeasyPrint is imported here rather than at the top of the file because it
    loads Pango and Cairo through ctypes the moment it is imported, and raises
    if they are missing. reportlab was pure Python and could not fail that way.
    At module level one absent system library would break every import of
    `app.services.reports` -- the whole package, for a JWT helper or a report
    contract -- which is the same failure the empty `services/__init__.py`
    exists to prevent. Here, only rendering a PDF needs the native stack.

    `report_id` is the report this was rendered from. Nothing in the document
    prints it -- the reportlab version took it too and never used it either --
    but the callers pass it and it says which report a file came from.
    """

    from weasyprint import HTML

    html = render_case_report_html(report_input, report)
    return HTML(string=html).write_pdf()


__all__ = ["render_case_report_pdf"]
