from __future__ import annotations

import textwrap

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table

from app.services.reports.pdf_chrome import table_style
from app.services.reports.pdf_design import paragraph_text
from app.services.reports.report_view_model_contracts import ReportViewModel


def build_evidence_story(
    view_model: ReportViewModel,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    i18n = view_model.i18n
    story: list[object] = [
        Paragraph(paragraph_text(i18n.get("sec_3", i18n["sec_5_3"])), styles["section_heading"]),
        Spacer(1, 2 * mm),
        Paragraph(f"<b>{paragraph_text(i18n['sub_evidence_reg'])}</b>", styles["subheading"]),
        Spacer(1, 2 * mm),
    ]
    if view_model.evidence_rows:
        table_data = [[
            Paragraph(f"<b>{paragraph_text(i18n['col_item'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_description'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_type'])}</b>", styles["table_header"]),
            Paragraph(f"<b>{paragraph_text(i18n['col_source'])}</b>", styles["table_header"]),
        ]]
        for evidence in view_model.evidence_rows:
            chunks = textwrap.wrap(
                evidence.description,
                width=1200,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]
            for chunk_index, chunk in enumerate(chunks):
                first_chunk = chunk_index == 0
                table_data.append([
                    Paragraph(
                        f"<b>{paragraph_text(evidence.item_id if first_chunk else '')}</b>",
                        styles["table_cell_small"],
                    ),
                    Paragraph(paragraph_text(chunk), styles["table_cell"]),
                    Paragraph(
                        paragraph_text(evidence.artifact_type if first_chunk else ""),
                        styles["table_cell_small"],
                    ),
                    Paragraph(
                        paragraph_text(evidence.source_type if first_chunk else ""),
                        styles["table_cell_small"],
                    ),
                ])
        table = Table(table_data, colWidths=(18 * mm, 102 * mm, 27 * mm, 31 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)
    else:
        story.append(Paragraph(paragraph_text(i18n["empty_evidence"]), styles["body_muted"]))

    if view_model.has_indicators:
        story.extend(
            [
                Spacer(1, 2 * mm),
                Paragraph(f"<b>{paragraph_text(i18n['sub_iocs'])}</b>", styles["subheading"]),
                Spacer(1, 1.5 * mm),
            ]
        )
        table_data = [
            [
                Paragraph(f"<b>{paragraph_text(i18n['col_ioc_type'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{paragraph_text(i18n['col_ioc_value'])}</b>", styles["table_header"]),
                Paragraph(f"<b>{paragraph_text(i18n['col_ioc_note'])}</b>", styles["table_header"]),
            ]
        ]
        for indicator in view_model.indicator_rows:
            table_data.append(
                [
                    Paragraph(f"<b>{paragraph_text(indicator.indicator_type)}</b>", styles["table_cell_small"]),
                    Paragraph(f"<font name=\"Courier\" size=\"7.5\">{paragraph_text(indicator.value)}</font>", styles["table_cell_code"]),
                    Paragraph(paragraph_text(indicator.note), styles["table_cell_small"]),
                ]
            )
        table = Table(table_data, colWidths=(36 * mm, 82 * mm, 60 * mm), repeatRows=1)
        table.setStyle(table_style())
        story.append(table)

    story.append(Spacer(1, 4 * mm))
    return story


__all__ = ["build_evidence_story"]
