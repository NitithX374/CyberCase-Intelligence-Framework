"""Deterministic PDF rendering for validated persisted chat reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from io import BytesIO
import os
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.reports import ChatReportRead, ReportClaim, ReportSection


_INK = colors.HexColor("#171717")
_MUTED = colors.HexColor("#6B6A66")
_RULE = colors.HexColor("#C9C7BF")
_PANEL = colors.HexColor("#F4F3EF")
_PANEL_ALT = colors.HexColor("#FAFAF8")
_ACCENT = colors.HexColor("#365A70")
_PAGE_WIDTH, _PAGE_HEIGHT = A4

_TEMPLATE_REPORT_METADATA = frozenset(
    {
        (
            "deterministic",
            "baseline_report_template_v1",
            "chat_report_template_v1",
        ),
        (
            "deterministic",
            "preliminary_analysis_template_v1",
            "chat_preliminary_analysis_template_v1",
        ),
    }
)
_PRELIMINARY_REPORT_VERSION = "preliminary_analysis_report_v1"


@dataclass(frozen=True)
class _BackgroundRecord:
    ordinal: str
    source_type: str
    content: str


@dataclass(frozen=True)
class _EvidenceRecord:
    evidence_id: str
    title: str
    description: str
    artifact_type: str
    status: str
    confidence: str
    source_type: str


@dataclass(frozen=True)
class _EntityRecord:
    name: str
    entity_type: str
    reported_role: str
    persisted_status: str
    confidence: str


@dataclass(frozen=True)
class _RelationshipRecord:
    subject: str
    predicate: str
    object_: str
    statement: str
    status: str
    confidence: str


@dataclass(frozen=True)
class _TimelineRecord:
    event_id: str
    time: str
    event: str
    actors: str
    linked_evidence: str
    status: str
    confidence: str


@dataclass(frozen=True)
class _MitreRecord:
    technique_id: str
    name: str
    mapping_status: str
    source: str
    relevance: str
    score: str
    tactic: str
    entity_type: str
    description: str


def render_chat_report_pdf(
    report: ChatReportRead,
    *,
    thread_title: str,
) -> bytes:
    """Render a completed persisted report without calling the model."""

    if report.report is None:
        raise ValueError("a structured report is required for PDF rendering")

    font_names = _register_fonts()
    styles = _build_styles(font_names)
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title=_plain(report.report.title),
        author="CyberCase Intelligence Framework",
        subject="Provisional unverified digital-forensics report",
    )

    story = _build_story(report, thread_title=thread_title, styles=styles)
    document.build(
        story,
        onFirstPage=lambda canvas, doc: _draw_page_chrome(
            canvas, doc, font_names=font_names
        ),
        onLaterPages=lambda canvas, doc: _draw_page_chrome(
            canvas, doc, font_names=font_names
        ),
    )
    return buffer.getvalue()


def _build_story(
    report: ChatReportRead,
    *,
    thread_title: str,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    assert report.report is not None
    structured_report = report.report
    table_aware = _is_template_report(report)
    story: list[object] = [
        Paragraph("CYBERCASE INTELLIGENCE FRAMEWORK", styles["eyebrow"]),
        Spacer(1, 8 * mm),
        Paragraph(_paragraph_text(structured_report.title), styles["title"]),
        Spacer(1, 3 * mm),
        Paragraph(
            "PROVISIONAL / UNVERIFIED REPORT",
            styles["status"],
        ),
        Spacer(1, 10 * mm),
        Paragraph(
            "This document is a formal presentation of one validated structured report version. "
            "It contains user-reported and extraction-derived candidates and is not confirmed forensic evidence.",
            styles["lead"],
        ),
        Spacer(1, 8 * mm),
        _metadata_table(report, thread_title=thread_title, styles=styles),
        Spacer(1, 10 * mm),
        HRFlowable(width="100%", thickness=0.8, color=_RULE),
        Spacer(1, 7 * mm),
        Paragraph(
            "Source and handling note",
            styles["subheading"],
        ),
        Paragraph(
            "The report was generated from the frozen server-side chat snapshot identified below. "
            "The PDF renderer does not add facts, references, or conclusions.",
            styles["body"],
        ),
        PageBreak(),
    ]

    for index, section in enumerate(structured_report.sections, start=1):
        story.extend(
            _section_story(
                section,
                claims=[
                    claim
                    for claim in structured_report.claims
                    if claim.section_id == section.section_id
                ],
                index=index,
                styles=styles,
                table_aware=table_aware,
                heading_is_numbered=(
                    structured_report.report_version == _PRELIMINARY_REPORT_VERSION
                ),
            )
        )

    if (
        structured_report.limitations
        and structured_report.report_version != _PRELIMINARY_REPORT_VERSION
    ):
        story.extend(
            [
                Spacer(1, 5 * mm),
                HRFlowable(width="100%", thickness=0.8, color=_RULE),
                Spacer(1, 5 * mm),
                Paragraph("Report limitations", styles["section_heading"]),
            ]
        )
        for limitation in structured_report.limitations:
            story.append(Paragraph(f"- {_paragraph_text(limitation)}", styles["body"]))
            story.append(Spacer(1, 1.5 * mm))

    story.extend(
        [
            Spacer(1, 7 * mm),
            HRFlowable(width="100%", thickness=0.8, color=_RULE),
            Spacer(1, 4 * mm),
            Paragraph(
                "End of report - provisional and unverified",
                styles["end_note"],
            ),
        ]
    )
    return story


def _section_story(
    section: ReportSection,
    *,
    claims: list[ReportClaim],
    index: int,
    styles: dict[str, ParagraphStyle],
    table_aware: bool,
    heading_is_numbered: bool,
) -> list[object]:
    display_heading = (
        section.heading if heading_is_numbered else f"{index:02d}  {section.heading}"
    )
    story: list[object] = [
        Spacer(1, 3 * mm),
        Paragraph(
            _paragraph_text(display_heading),
            styles["section_heading"],
        ),
        Spacer(1, 3 * mm),
    ]
    for paragraph in section.paragraphs:
        story.append(Paragraph(_paragraph_text(paragraph), styles["body"]))
        story.append(Spacer(1, 2.5 * mm))

    integrated_claim_indexes: set[int] = set()
    if table_aware:
        item_story, integrated_claim_indexes = _template_section_story(
            section,
            claims=claims,
            styles=styles,
        )
        story.extend(item_story)
    else:
        story.extend(_legacy_item_story(section.items, styles=styles))

    remaining_claims = [
        claim
        for claim_index, claim in enumerate(claims)
        if claim_index not in integrated_claim_indexes
    ]
    if remaining_claims:
        story.append(Spacer(1, 2 * mm))
        for claim_index, claim in enumerate(remaining_claims):
            claim_text = (
                f"<b>{_paragraph_text(claim.claim_id)}</b>  "
                f"<font color=\"#365A70\">"
                f"{_paragraph_text(claim.support_type.replace('_', ' '))}</font><br/>"
                f"{_paragraph_text(claim.text)}"
            )
            references = _claim_references(claim)
            if references:
                claim_text += (
                    f"<br/><font color=\"#6B6A66\">"
                    f"References: {_paragraph_text(references)}</font>"
                )
            claim_story: list[object] = []
            if claim_index == 0:
                claim_story.extend(
                    [
                        Paragraph("Structured claims", styles["subheading"]),
                        Spacer(1, 1.5 * mm),
                    ]
                )
            claim_story.extend(
                [
                    Paragraph(claim_text, styles["claim"]),
                    Spacer(1, 2 * mm),
                ]
            )
            story.append(KeepTogether(claim_story))
    return story


def _is_template_report(report: ChatReportRead) -> bool:
    return (
        report.provider,
        report.model,
        report.prompt_version,
    ) in _TEMPLATE_REPORT_METADATA


def _template_section_story(
    section: ReportSection,
    *,
    claims: list[ReportClaim],
    styles: dict[str, ParagraphStyle],
) -> tuple[list[object], set[int]]:
    if section.section_id in {"case_background_scope", "case_summary"}:
        return _background_story(section.items, styles=styles), set()
    if section.section_id in {"evidence_findings", "indicators_found"}:
        return _evidence_story(section.items, claims=claims, styles=styles)
    if section.section_id == "individuals_accounts_systems_roles":
        return _entity_relationship_story(section.items, styles=styles), set()
    if section.section_id == "chronological_timeline":
        return _timeline_story(section.items, claims=claims, styles=styles)
    if section.section_id in {"technical_analysis_mitre", "mitre_attack_mapping"}:
        return _mitre_story(section.items, styles=styles), set()
    if section.section_id == "evidence_to_examine":
        return _evidence_to_examine_story(
            section.items,
            claims=claims,
            styles=styles,
        )
    return _legacy_item_story(section.items, styles=styles), set()


def _legacy_item_story(
    items: list[str],
    *,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    story: list[object] = []
    for item in items:
        story.append(Paragraph(f"- {_paragraph_text(item)}", styles["body"]))
        story.append(Spacer(1, 1.5 * mm))
    return story


def _background_story(
    items: list[str],
    *,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    story: list[object] = []
    pending_rows: list[list[str]] = []

    def flush_rows() -> None:
        if not pending_rows:
            return
        story.append(
            _summary_table(
                ("Message / source", "Content"),
                pending_rows,
                col_widths=(42 * mm, 128 * mm),
                styles=styles,
            )
        )
        story.append(Spacer(1, 2.5 * mm))
        pending_rows.clear()

    for item in items:
        record = _parse_background(item)
        if record is None:
            flush_rows()
            story.extend(_legacy_item_story([item], styles=styles))
            continue
        pending_rows.append(
            [f"Message {record.ordinal}\n{record.source_type}", record.content]
        )
    flush_rows()
    return story


def _evidence_story(
    items: list[str],
    *,
    claims: list[ReportClaim],
    styles: dict[str, ParagraphStyle],
) -> tuple[list[object], set[int]]:
    story: list[object] = []
    integrated: set[int] = set()
    for item in items:
        record = _parse_evidence(item)
        claim_match = _next_exact_claim(item, claims=claims, consumed=integrated)
        if record is None or claim_match is None:
            story.extend(_legacy_item_story([item], styles=styles))
            continue
        claim_index, claim = claim_match
        story.extend(
            _record_flowables(
                ("Claim", "Evidence ID", "Support", "Status", "Confidence"),
                (
                    claim.claim_id,
                    record.evidence_id,
                    claim.support_type.replace("_", " "),
                    record.status,
                    record.confidence,
                ),
                details=(
                    ("Title", record.title),
                    ("Description", record.description),
                    (
                        "Artifact / source",
                        f"Artifact type: {record.artifact_type}\nSource type: {record.source_type}",
                    ),
                    ("References", _claim_references(claim) or "none persisted"),
                ),
                col_widths=(22 * mm, 25 * mm, 48 * mm, 40 * mm, 35 * mm),
                styles=styles,
            )
        )
        story.append(Spacer(1, 3 * mm))
        integrated.add(claim_index)
    return story, integrated


def _entity_relationship_story(
    items: list[str],
    *,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    story: list[object] = []
    for item in items:
        entity = _parse_entity(item)
        if entity is not None:
            story.extend(
                _record_flowables(
                    ("Name", "Type", "Reported role", "Confidence"),
                    (
                        entity.name,
                        entity.entity_type,
                        entity.reported_role,
                        entity.confidence,
                    ),
                    details=(("Persisted status", entity.persisted_status),),
                    col_widths=(45 * mm, 35 * mm, 55 * mm, 35 * mm),
                    styles=styles,
                )
            )
            story.append(Spacer(1, 3 * mm))
            continue

        relationship = _parse_relationship(item)
        if relationship is not None:
            story.extend(
                _record_flowables(
                    ("Subject", "Predicate", "Object"),
                    (
                        relationship.subject,
                        relationship.predicate,
                        relationship.object_,
                    ),
                    details=(
                        ("Statement", relationship.statement),
                        (
                            "Status / confidence",
                            f"Status: {relationship.status}\nConfidence: {relationship.confidence}",
                        ),
                    ),
                    col_widths=(55 * mm, 45 * mm, 70 * mm),
                    styles=styles,
                )
            )
            story.append(Spacer(1, 3 * mm))
            continue

        story.extend(_legacy_item_story([item], styles=styles))
    return story


def _timeline_story(
    items: list[str],
    *,
    claims: list[ReportClaim],
    styles: dict[str, ParagraphStyle],
) -> tuple[list[object], set[int]]:
    story: list[object] = []
    integrated: set[int] = set()
    for item in items:
        record = _parse_timeline(item)
        claim_match = _next_exact_claim(item, claims=claims, consumed=integrated)
        if record is None or claim_match is None:
            story.extend(_legacy_item_story([item], styles=styles))
            continue
        claim_index, claim = claim_match
        story.extend(_timeline_record_story(record, claim=claim, styles=styles))
        story.append(Spacer(1, 3 * mm))
        integrated.add(claim_index)
    return story, integrated


def _evidence_to_examine_story(
    items: list[str],
    *,
    claims: list[ReportClaim],
    styles: dict[str, ParagraphStyle],
) -> tuple[list[object], set[int]]:
    """Strictly dispatch mixed timeline/entity/relationship rows without loss."""

    story: list[object] = []
    integrated: set[int] = set()
    for item in items:
        timeline = _parse_timeline(item)
        if timeline is not None:
            claim_match = _next_exact_claim(item, claims=claims, consumed=integrated)
            if claim_match is None:
                story.extend(_legacy_item_story([item], styles=styles))
                continue
            claim_index, claim = claim_match
            story.extend(_timeline_record_story(timeline, claim=claim, styles=styles))
            story.append(Spacer(1, 3 * mm))
            integrated.add(claim_index)
            continue

        if _parse_entity(item) is not None or _parse_relationship(item) is not None:
            story.extend(_entity_relationship_story([item], styles=styles))
            continue

        story.extend(_legacy_item_story([item], styles=styles))
    return story, integrated


def _timeline_record_story(
    record: _TimelineRecord,
    *,
    claim: ReportClaim,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    return _record_flowables(
        ("Claim", "Event ID", "Time", "Status", "Confidence"),
        (
            claim.claim_id,
            record.event_id,
            record.time,
            record.status,
            record.confidence,
        ),
        details=(
            ("Event", record.event),
            ("Actors", record.actors),
            ("Evidence references", record.linked_evidence),
            ("Claim references", _claim_references(claim) or "none persisted"),
        ),
        col_widths=(22 * mm, 25 * mm, 58 * mm, 35 * mm, 30 * mm),
        styles=styles,
    )


def _mitre_story(
    items: list[str],
    *,
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    story: list[object] = []
    for item in items:
        record = _parse_mitre(item)
        if record is None:
            story.extend(_legacy_item_story([item], styles=styles))
            continue
        story.extend(
            _record_flowables(
                ("ID", "Name", "Source", "Relevance", "Score"),
                (
                    record.technique_id,
                    record.name,
                    record.source,
                    record.relevance,
                    record.score,
                ),
                details=(
                    (
                        "Candidate metadata",
                        f"Mapping status: {record.mapping_status}\nTactic: {record.tactic}\nEntity type: {record.entity_type}",
                    ),
                    ("Description", record.description),
                ),
                col_widths=(23 * mm, 50 * mm, 30 * mm, 40 * mm, 27 * mm),
                styles=styles,
            )
        )
        story.append(Spacer(1, 3 * mm))
    return story


def _next_exact_claim(
    item: str,
    *,
    claims: list[ReportClaim],
    consumed: set[int],
) -> tuple[int, ReportClaim] | None:
    for claim_index, claim in enumerate(claims):
        if claim_index not in consumed and claim.text == item:
            return claim_index, claim
    return None


def _summary_table(
    headers: tuple[str, ...],
    rows: list[list[str]],
    *,
    col_widths: tuple[float, ...],
    styles: dict[str, ParagraphStyle],
) -> Table:
    data = [
        [Paragraph(_paragraph_text(value), styles["table_header"]) for value in headers]
    ]
    data.extend(
        [Paragraph(_paragraph_text(value), styles["table_body"]) for value in row]
        for row in rows
    )
    table = Table(
        data,
        colWidths=list(col_widths),
        repeatRows=0,
        splitByRow=1,
        splitInRow=1,
        hAlign="LEFT",
    )
    commands: list[tuple[object, ...]] = _base_table_commands()
    for row_index in range(1, len(data)):
        commands.append(
            (
                "BACKGROUND",
                (0, row_index),
                (-1, row_index),
                _PANEL_ALT if row_index % 2 else _PANEL,
            )
        )
    table.setStyle(TableStyle(commands))
    return table


def _record_flowables(
    headers: tuple[str, ...],
    values: tuple[str, ...],
    *,
    details: tuple[tuple[str, str], ...],
    col_widths: tuple[float, ...],
    styles: dict[str, ParagraphStyle],
) -> list[object]:
    """Keep ordinary records tabular and let unusually long details flow cleanly."""

    if not any(len(value) > 1_200 for _, value in details):
        return [
            _record_table(
                headers,
                values,
                details=details,
                col_widths=col_widths,
                styles=styles,
            )
        ]

    flowables: list[object] = [
        _record_table(
            headers,
            values,
            details=(),
            col_widths=col_widths,
            styles=styles,
        )
    ]
    for label, value in details:
        flowables.append(
            Paragraph(
                f"<b>{_paragraph_text(label)}</b><br/>{_paragraph_text(value)}",
                styles["record_detail_flow"],
            )
        )
    return flowables


def _record_table(
    headers: tuple[str, ...],
    values: tuple[str, ...],
    *,
    details: tuple[tuple[str, str], ...],
    col_widths: tuple[float, ...],
    styles: dict[str, ParagraphStyle],
) -> Table:
    column_count = len(headers)
    data: list[list[Paragraph]] = [
        [Paragraph(_paragraph_text(value), styles["table_header"]) for value in headers],
        [Paragraph(_paragraph_text(value), styles["table_body"]) for value in values],
    ]
    for label, value in details:
        detail_text = (
            f"<b>{_paragraph_text(label)}</b><br/>"
            f"{_paragraph_text(value)}"
        )
        data.append(
            [Paragraph(detail_text, styles["table_detail"])]
            + [Paragraph("", styles["table_detail"]) for _ in range(column_count - 1)]
        )

    table = Table(
        data,
        colWidths=list(col_widths),
        repeatRows=1,
        splitByRow=1,
        splitInRow=1,
        hAlign="LEFT",
    )
    commands: list[tuple[object, ...]] = _base_table_commands()
    commands.append(("BACKGROUND", (0, 1), (-1, 1), _PANEL_ALT))
    for row_index in range(2, len(data)):
        commands.extend(
            [
                ("SPAN", (0, row_index), (-1, row_index)),
                (
                    "BACKGROUND",
                    (0, row_index),
                    (-1, row_index),
                    _PANEL if row_index % 2 == 0 else _PANEL_ALT,
                ),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def _base_table_commands() -> list[tuple[object, ...]]:
    return [
        ("BACKGROUND", (0, 0), (-1, 0), _ACCENT),
        ("BOX", (0, 0), (-1, -1), 0.65, _RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DEDCD5")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]


def _parse_background(value: str) -> _BackgroundRecord | None:
    if value.count("): ") != 1:
        return None
    match = re.fullmatch(r"Message ([0-9]+) \(([^()\n]+)\): (.+)", value, re.DOTALL)
    if match is None:
        return None
    return _BackgroundRecord(
        ordinal=match.group(1),
        source_type=match.group(2),
        content=match.group(3),
    )


def _parse_evidence(value: str) -> _EvidenceRecord | None:
    fields = _strict_marked_fields(
        value,
        (
            " | Title: ",
            " | Description: ",
            " | Artifact type: ",
            " | Status: ",
            " | Confidence: ",
            " | Source type: ",
        ),
        terminal_period=True,
    )
    if fields is None:
        return None
    return _EvidenceRecord(*fields)


def _parse_entity(value: str) -> _EntityRecord | None:
    fields = _strict_marked_fields(
        value,
        (
            "Entity | Name: ",
            " | Type: ",
            " | Reported role: ",
            " | Persisted status: ",
            " | Confidence: ",
        ),
        terminal_period=True,
        leading_empty=True,
    )
    if fields is None:
        return None
    return _EntityRecord(*fields)


def _parse_relationship(value: str) -> _RelationshipRecord | None:
    prefix = "Relationship | "
    if value.count(prefix) != 1 or not value.startswith(prefix):
        return None
    fields = _strict_marked_fields(
        value[len(prefix) :],
        (
            " | Statement: ",
            " | Status: ",
            " | Confidence: ",
        ),
        terminal_period=True,
    )
    if fields is None:
        return None
    relation, statement, status, confidence = fields
    if relation.count(" -> ") != 2:
        return None
    subject, predicate, object_ = relation.split(" -> ")
    if not subject or not predicate or not object_:
        return None
    return _RelationshipRecord(
        subject=subject,
        predicate=predicate,
        object_=object_,
        statement=statement,
        status=status,
        confidence=confidence,
    )


def _parse_timeline(value: str) -> _TimelineRecord | None:
    fields = _strict_marked_fields(
        value,
        (
            " | Time: ",
            " | Event: ",
            " | Actors: ",
            " | Linked evidence: ",
            " | Status: ",
            " | Confidence: ",
        ),
        terminal_period=True,
    )
    if fields is None:
        return None
    return _TimelineRecord(*fields)


def _parse_mitre(value: str) -> _MitreRecord | None:
    fields = _strict_marked_fields(
        value,
        (
            " | Name: ",
            " | Mapping status: ",
            " | Source: ",
            " | Relevance: ",
            " | Score: ",
            " | Tactic: ",
            " | Entity type: ",
            " | Description: ",
        ),
    )
    if fields is None:
        return None
    return _MitreRecord(*fields)


def _strict_marked_fields(
    value: str,
    markers: tuple[str, ...],
    *,
    terminal_period: bool = False,
    leading_empty: bool = False,
) -> tuple[str, ...] | None:
    if any(value.count(marker) != 1 for marker in markers):
        return None
    fields: list[str] = []
    remainder = value
    for marker in markers:
        field, separator, remainder = remainder.partition(marker)
        if not separator:
            return None
        fields.append(field)
    if terminal_period:
        if not remainder.endswith("."):
            return None
        remainder = remainder[:-1]
    fields.append(remainder)
    if leading_empty:
        if fields[0] != "":
            return None
        fields = fields[1:]
    if not fields or any(field == "" for field in fields):
        return None
    return tuple(fields)


def _metadata_table(
    report: ChatReportRead,
    *,
    thread_title: str,
    styles: dict[str, ParagraphStyle],
) -> Table:
    rows = [
        ("Case / thread", thread_title),
        (
            "Report version",
            f"Version {report.version_number} / {report.report.report_version}",
        ),
        ("Report ID", str(report.report_id)),
        ("Generated", _format_datetime(report.finished_at or report.created_at)),
        ("Extraction", report.extraction_version),
        ("Validation", report.validation_status),
        ("Provider / model", f"{report.provider} / {report.model}"),
        ("Prompt version", report.prompt_version),
        ("Source snapshot", report.source_snapshot_hash),
    ]
    table = Table(
        [
            [
                Paragraph(_paragraph_text(label), styles["metadata_label"]),
                Paragraph(_paragraph_text(value), styles["metadata_value"]),
            ]
            for label, value in rows
        ],
        colWidths=[38 * mm, 118 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _PANEL),
                ("BOX", (0, 0), (-1, -1), 0.7, _RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DEDCD5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _build_styles(font_names: tuple[str, str]) -> dict[str, ParagraphStyle]:
    regular, bold = font_names
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle(
            "ReportEyebrow",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=10,
            textColor=_ACCENT,
            alignment=TA_LEFT,
            spaceAfter=0,
        ),
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName=bold,
            fontSize=23,
            leading=28,
            textColor=_INK,
            alignment=TA_LEFT,
            spaceAfter=0,
        ),
        "status": ParagraphStyle(
            "ReportStatus",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=11,
            textColor=_MUTED,
            alignment=TA_LEFT,
            spaceAfter=0,
        ),
        "lead": ParagraphStyle(
            "ReportLead",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=10.5,
            leading=16,
            textColor=_MUTED,
            alignment=TA_LEFT,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=9.5,
            leading=14,
            textColor=_INK,
            alignment=TA_LEFT,
            splitLongWords=1,
        ),
        "section_heading": ParagraphStyle(
            "ReportSectionHeading",
            parent=base["Heading2"],
            fontName=bold,
            fontSize=14,
            leading=18,
            textColor=_INK,
            alignment=TA_LEFT,
            spaceBefore=4 * mm,
            spaceAfter=0,
        ),
        "subheading": ParagraphStyle(
            "ReportSubheading",
            parent=base["Heading3"],
            fontName=bold,
            fontSize=9,
            leading=12,
            textColor=_ACCENT,
            alignment=TA_LEFT,
            spaceBefore=2 * mm,
            spaceAfter=2 * mm,
        ),
        "claim": ParagraphStyle(
            "ReportClaim",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=8.8,
            leading=13,
            textColor=_INK,
            backColor=colors.HexColor("#FAFAF8"),
            borderColor=colors.HexColor("#DEDCD5"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=0,
        ),
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.2,
            leading=9.5,
            textColor=colors.white,
            splitLongWords=1,
        ),
        "table_body": ParagraphStyle(
            "ReportTableBody",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=7.8,
            leading=10.5,
            textColor=_INK,
            splitLongWords=1,
        ),
        "table_detail": ParagraphStyle(
            "ReportTableDetail",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=8.2,
            leading=11.5,
            textColor=_INK,
            splitLongWords=1,
        ),
        "record_detail_flow": ParagraphStyle(
            "ReportRecordDetailFlow",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=8.2,
            leading=11.5,
            textColor=_INK,
            splitLongWords=1,
            leftIndent=6,
            rightIndent=6,
            spaceBefore=3,
            spaceAfter=5,
        ),
        "metadata_label": ParagraphStyle(
            "ReportMetadataLabel",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.8,
            leading=10,
            textColor=_MUTED,
        ),
        "metadata_value": ParagraphStyle(
            "ReportMetadataValue",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.2,
            leading=11,
            textColor=_INK,
        ),
        "end_note": ParagraphStyle(
            "ReportEndNote",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=11,
            textColor=_MUTED,
            alignment=TA_CENTER,
        ),
    }


def _draw_page_chrome(canvas, document, *, font_names: tuple[str, str]) -> None:
    regular, bold = font_names
    canvas.saveState()
    canvas.setStrokeColor(_RULE)
    canvas.setLineWidth(0.6)
    canvas.line(document.leftMargin, _PAGE_HEIGHT - 14 * mm, _PAGE_WIDTH - document.rightMargin, _PAGE_HEIGHT - 14 * mm)
    canvas.line(document.leftMargin, 13 * mm, _PAGE_WIDTH - document.rightMargin, 13 * mm)
    canvas.setFont(bold, 7)
    canvas.setFillColor(_MUTED)
    canvas.drawString(document.leftMargin, _PAGE_HEIGHT - 11 * mm, "CYBERCASE INTELLIGENCE FRAMEWORK")
    canvas.drawRightString(
        _PAGE_WIDTH - document.rightMargin,
        _PAGE_HEIGHT - 11 * mm,
        "PROVISIONAL / UNVERIFIED",
    )
    canvas.setFont(regular, 7)
    canvas.drawString(document.leftMargin, 8 * mm, "Formal report export - validate against the persisted report version")
    canvas.drawRightString(_PAGE_WIDTH - document.rightMargin, 8 * mm, f"Page {document.page}")
    canvas.restoreState()


def _claim_references(claim: ReportClaim) -> str:
    references: list[str] = []
    if claim.evidence_ids:
        references.append(f"evidence {', '.join(claim.evidence_ids)}")
    if claim.timeline_event_ids:
        references.append(f"timeline {', '.join(claim.timeline_event_ids)}")
    if claim.mitre_technique_ids:
        references.append(f"MITRE {', '.join(claim.mitre_technique_ids)}")
    return "; ".join(references)


def _format_datetime(value: datetime) -> str:
    normalized = value
    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=timezone.utc)
    return normalized.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _paragraph_text(value: object) -> str:
    text = _plain(value)
    return escape(text).replace("\n", "<br/>")


def _plain(value: object) -> str:
    return (
        str(value)
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def _register_fonts() -> tuple[str, str]:
    regular_path = _find_font(
        "CYBERCASE_PDF_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ),
    )
    bold_path = _find_font(
        "CYBERCASE_PDF_BOLD_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/tahomabd.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ),
    )
    if regular_path is None or bold_path is None:
        return "Helvetica", "Helvetica-Bold"

    pdfmetrics.registerFont(TTFont("CyberCaseSans", regular_path))
    pdfmetrics.registerFont(TTFont("CyberCaseSansBold", bold_path))
    return "CyberCaseSans", "CyberCaseSansBold"


def _find_font(environment_name: str, candidates: tuple[str, ...]) -> str | None:
    configured = Path(os.environ.get(environment_name, ""))
    if configured.is_file():
        return str(configured)
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return str(path)
    return None


__all__ = ["render_chat_report_pdf"]
