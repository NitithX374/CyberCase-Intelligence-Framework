from __future__ import annotations

from io import BytesIO
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.reports import StructuredReport
from app.services.reports.case_report_contracts import CaseReportInputSnapshot
from app.services.reports.pdf_design import (
    DARK_RULE,
    PANEL,
    RULE,
    build_report_styles,
    paragraph_text,
    plain_text,
    register_report_fonts,
)


def render_case_report_pdf(
    snapshot: CaseReportInputSnapshot,
    report: StructuredReport,
    report_id: UUID,
) -> bytes:
    fonts = register_report_fonts()
    styles = build_report_styles(fonts)
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=plain_text(report.title),
        author="CyberCase Intelligence Framework",
        subject="Case evidence-bound analysis report",
    )
    story = _story(snapshot, report, styles)
    document.build(
        story,
        onFirstPage=lambda canvas, doc: _page_chrome(canvas, doc, report_id),
        onLaterPages=lambda canvas, doc: _page_chrome(canvas, doc, report_id),
    )
    return buffer.getvalue()


def _story(
    snapshot: CaseReportInputSnapshot,
    report: StructuredReport,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    story: list[object] = [
        Paragraph("CYBERCASE INTELLIGENCE FRAMEWORK", styles["eyebrow"]),
        Spacer(1, 2 * mm),
        Paragraph(paragraph_text(report.title), styles["doc_title"]),
        Spacer(1, 3 * mm),
        _metadata_table(snapshot, styles),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1.2, color=DARK_RULE),
        Spacer(1, 5 * mm),
    ]
    for section in report.sections:
        story.extend(
            [
                Paragraph(paragraph_text(section.heading), styles["section_heading"]),
                Spacer(1, 2 * mm),
            ]
        )
        story.extend(Paragraph(paragraph_text(text), styles["body"]) for text in section.paragraphs)
        for item in section.items:
            story.extend(
                [
                    Paragraph(f"• {paragraph_text(item)}", styles["body"]),
                    Spacer(1, 1.2 * mm),
                ]
            )
        story.append(Spacer(1, 3 * mm))
    story.extend(_claim_story(report, styles))
    story.extend(_source_story(snapshot, styles))
    return story


def _metadata_table(
    snapshot: CaseReportInputSnapshot,
    styles: dict[str, ParagraphStyle],
) -> Table:
    rows = [
        ("Case", str(snapshot.case_id)),
        ("Analysis result", str(snapshot.analysis_result_id)),
        ("Evidence snapshot", f"{snapshot.evidence_snapshot_id} · revision {snapshot.evidence_revision}"),
        ("Evidence text SHA-256", snapshot.evidence_sha256),
        ("Evidence manifest SHA-256", snapshot.manifest_sha256),
    ]
    table = Table(
        [[Paragraph(paragraph_text(label), styles["meta_label"]), Paragraph(paragraph_text(value), styles["meta_value"])] for label, value in rows],
        colWidths=(45 * mm, 133 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7DEE7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ]
        )
    )
    return table


def _claim_story(
    report: StructuredReport,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    if not report.claims:
        return []
    story: list[object] = [
        Paragraph("Claim source bindings", styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    for claim in report.claims:
        sources = ", ".join(claim.source_evidence_ids) or "No source binding"
        story.extend(
            [
                Paragraph(f"<b>{paragraph_text(claim.claim_id)}</b>: {paragraph_text(claim.text)}", styles["body"]),
                Paragraph(f"Evidence source IDs: {paragraph_text(sources)}", styles["body_small"]),
                Spacer(1, 2 * mm),
            ]
        )
    return story


def _source_story(
    snapshot: CaseReportInputSnapshot,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    story: list[object] = [
        Paragraph("Evidence snapshot sources", styles["section_heading"]),
        Spacer(1, 2 * mm),
    ]
    for source in snapshot.sources:
        label = f"{source.source_id} · revision {source.revision}"
        if source.filename:
            label += f" · {source.filename}"
        story.extend(
            [
                Paragraph(f"<b>{paragraph_text(label)}</b>", styles["subheading"]),
                Paragraph(paragraph_text(source.exact_text), styles["body"]),
                Spacer(1, 2 * mm),
            ]
        )
    return story


def _page_chrome(canvas, document, report_id: UUID) -> None:
    canvas.saveState()
    canvas.setStrokeColor(DARK_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(document.leftMargin, 11 * mm, A4[0] - document.rightMargin, 11 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.drawString(document.leftMargin, 7 * mm, f"Report {report_id}")
    canvas.drawRightString(A4[0] - document.rightMargin, 7 * mm, f"Page {document.page}")
    canvas.restoreState()


__all__ = ["render_case_report_pdf"]
