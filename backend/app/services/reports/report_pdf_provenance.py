from __future__ import annotations

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, Spacer, Table

from app.services.reports.pdf_chrome import table_style
from app.services.reports.pdf_styles import paragraph_text
from app.services.reports.pdf_theme import RULE
from app.services.reports.report_view_model import ReportViewModel


def build_provenance_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    content: list[object] = [
        Paragraph(paragraph_text(i18n["sec_5_7"]), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_limitations'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ]
    for limitation in view_model.limitations:
        content.extend([
            Paragraph(f"• {paragraph_text(limitation)}", styles["body_small"]),
            Spacer(1, 1.2 * mm),
        ])
    content.extend([
        Spacer(1, 3 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_provenance'])}</b>", styles["subheading"]),
        Spacer(1, 1.5 * mm),
    ])
    table_data = [[
        Paragraph(f"<b>{paragraph_text(i18n['col_prov_item'])}</b>", styles["table_header"]),
        Paragraph(f"<b>{paragraph_text(i18n['col_prov_value'])}</b>", styles["table_header"]),
    ]]
    for row in view_model.provenance_rows:
        table_data.append([
            Paragraph(f"<b>{paragraph_text(row.label)}</b>", styles["table_cell_small"]),
            Paragraph(f"<font name=\"Courier\" size=\"7.5\">{paragraph_text(row.value)}</font>", styles["table_cell_code"]),
        ])
    table = Table(table_data, colWidths=(50 * mm, 128 * mm), repeatRows=1)
    table.setStyle(table_style())
    content.extend([
        table,
        Spacer(1, 5 * mm),
        HRFlowable(width="100%", thickness=0.8, color=RULE),
        Spacer(1, 3 * mm),
        Paragraph(paragraph_text(i18n["end_of_report"]), styles["end_note"]),
    ])
    return [KeepTogether(content)]
