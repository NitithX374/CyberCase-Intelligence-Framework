from __future__ import annotations

from reportlab.platypus import Paragraph, Spacer

from app.services.reports.case_report_pdf_formatting import paragraph_text
from app.services.reports.case_report_rendering import (
    ReportDisplayClaim,
    ReportDisplaySource,
)


def build_indicator_story(
    claims: tuple[ReportDisplayClaim, ...],
    styles: dict[str, object],
) -> list[object]:
    story: list[object] = []
    for claim in claims:
        references = ", ".join(claim.source_labels) or "ไม่มีการอ้างอิงโดยตรง"
        story.extend(
            [
                Paragraph(
                    f"<b>{paragraph_text(f'ตัวบ่งชี้ {claim.ordinal} · {claim.epistemic_label}')}</b>",
                    styles["subheading"],
                ),
                Paragraph(paragraph_text(claim.text), styles["body"]),
                Paragraph(
                    paragraph_text(f"{claim.support_label} · อ้างอิง: {references}"),
                    styles["body_small"],
                ),
            ]
        )
        for quote in claim.supporting_quotes:
            story.append(
                Paragraph(
                    paragraph_text(f"ข้อความจากหลักฐาน: “{quote}”"),
                    styles["body_muted"],
                )
            )
        for quote in claim.contradicting_quotes:
            story.append(
                Paragraph(
                    paragraph_text(f"ข้อความที่ขัดแย้ง: “{quote}”"),
                    styles["body_muted"],
                )
            )
        if claim.reasoning_summary:
            story.append(
                Paragraph(
                    paragraph_text(f"เหตุผลเชิงวิเคราะห์: {claim.reasoning_summary}"),
                    styles["body_muted"],
                )
            )
        story.append(Spacer(1, 2.2))
    return story


def build_source_register_story(
    sources: tuple[ReportDisplaySource, ...],
    styles: dict[str, object],
) -> list[object]:
    story: list[object] = [
        Paragraph("เอกสาร/หลักฐานอ้างอิง", styles["section_heading"]),
        Spacer(1, 2),
        Paragraph(
            "รายการนี้เป็นดัชนีอ้างอิงของหลักฐานที่ใช้ประกอบรายงาน รายละเอียดข้อความจะแสดงเฉพาะส่วนที่ถูกอ้างในตัวบ่งชี้",
            styles["body_muted"],
        ),
    ]
    for source in sources:
        story.extend(
            [
                Paragraph(
                    paragraph_text(f"{source.label} · {source.filename}"),
                    styles["body"],
                ),
                Spacer(1, 1.2),
            ]
        )
    return story


__all__ = ["build_indicator_story", "build_source_register_story"]
