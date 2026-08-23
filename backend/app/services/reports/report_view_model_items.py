import re
from dataclasses import dataclass

from app.schemas.reports import ReportSection
from app.services.reports.report_view_model_contracts import (
    EvidenceViewRow,
    IndicatorViewRow,
    ReportLanguage,
    TimelineViewRow,
)
from app.services.reports.report_view_model_text import _extract_indicators_from_text


@dataclass(frozen=True)
class ParsedReportItems:
    evidence_rows: list[EvidenceViewRow]
    indicator_rows: list[IndicatorViewRow]
    timeline_rows: list[TimelineViewRow]
    has_indicators: bool


def _extract_timeline_from_text(
    text: str,
    *,
    language: ReportLanguage,
) -> list[TimelineViewRow]:
    rows: list[TimelineViewRow] = []
    if not text.strip():
        return rows

    # 1. Try finding Section 2 (Key Sequence / Progression) in markdown
    sec2_match = re.search(
        r"###\s*2\.\s*[^\n]+\n(.*?)(?=\n###\s*\d|\Z)",
        text,
        re.DOTALL,
    )
    raw_sequence = sec2_match.group(1).strip() if sec2_match else ""

    lines_to_parse: list[str] = []
    if raw_sequence:
        for line in raw_sequence.split("\n"):
            clean = line.strip()
            clean = re.sub(r"^[-*•]\s+", "", clean)
            clean = re.sub(r"^\d+\.\s+", "", clean)
            clean = clean.strip()
            if clean and len(clean) > 5 and not clean.startswith("#"):
                lines_to_parse.append(clean)

    # 2. Fallback: Check for numbered list in general text
    if not lines_to_parse:
        for line in text.split("\n"):
            m = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
            if m:
                clean = m.group(2).strip()
                if len(clean) > 5 and not clean.startswith("###"):
                    lines_to_parse.append(clean)

    source_label = (
        "ข้อมูลจากสำนวนที่ผู้ใช้ส่ง (ข้อความ #1)"
        if language == "th"
        else "User-Submitted Evidence (#1)"
    )

    for idx, item in enumerate(lines_to_parse):
        # Remove bold markers from event text
        clean_event = re.sub(r"\*\*(.*?)\*\*", r"\1", item).strip()
        rows.append(
            TimelineViewRow(
                order=idx + 1,
                time_display="—",
                event=clean_event,
                source_evidence=source_label,
                actors="-",
                status="reported",
            )
        )

    return rows


def parse_report_items(
    sections_by_id: dict[str, ReportSection],
    *,
    language: ReportLanguage,
) -> ParsedReportItems:
    evidence_rows: list[EvidenceViewRow] = []
    indicator_rows: list[IndicatorViewRow] = []
    seen: set[str] = set()

    # Parse Evidence Items from indicators_found section
    for section_id in ("indicators_found",):
        section = sections_by_id.get(section_id)
        if section is None:
            continue
        for idx, item in enumerate(section.items):
            if item.startswith("No ") or item.startswith("ไม่มี"):
                continue

            ordinal_match = re.match(r"^Message\s+(\d+):\s*(.*)$", item, re.DOTALL)
            if ordinal_match:
                ordinal = ordinal_match.group(1)
                content = ordinal_match.group(2).strip()
            else:
                ordinal = str(idx + 1)
                content = item.strip()

            title = (
                f"ข้อมูลจากสำนวนคดี (ข้อความ #{ordinal})"
                if language == "th"
                else f"Case Evidence (Message #{ordinal})"
            )
            art_type = (
                "ข้อมูลสำนวนที่ผู้ใช้ส่ง"
                if language == "th"
                else "User Statement"
            )
            src_type = (
                "ผู้ใช้ส่งเข้าสู่ระบบ"
                if language == "th"
                else "User Submission"
            )

            evidence_rows.append(
                EvidenceViewRow(
                    item_id=f"#{ordinal}",
                    title=title,
                    artifact_type=art_type,
                    description=content,
                    source_type=src_type,
                    confidence="reported",
                )
            )
            indicator_rows.extend(
                _extract_indicators_from_text(
                    content,
                    note="ข้อความจากสำนวนคดี" if language == "th" else "User-authored evidence",
                    seen=seen,
                )
            )

    # Parse Timeline Rows from case_summary paragraphs or raw markdown
    timeline_rows: list[TimelineViewRow] = []
    case_summary = sections_by_id.get("case_summary")
    if case_summary:
        full_summary_text = "\n\n".join(case_summary.paragraphs)
        timeline_rows = _extract_timeline_from_text(
            full_summary_text,
            language=language,
        )

    return ParsedReportItems(
        evidence_rows=evidence_rows,
        indicator_rows=indicator_rows,
        timeline_rows=timeline_rows,
        has_indicators=bool(indicator_rows),
    )


__all__ = ["ParsedReportItems", "parse_report_items"]
