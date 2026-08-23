from __future__ import annotations

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


def parse_report_items(
    sections_by_id: dict[str, ReportSection],
    *,
    language: ReportLanguage,
) -> ParsedReportItems:
    evidence_rows: list[EvidenceViewRow] = []
    indicator_rows: list[IndicatorViewRow] = []
    seen: set[str] = set()
    for section_id in ("indicators_found",):
        section = sections_by_id.get(section_id)
        if section is None:
            continue
        for item in section.items:
            if item.startswith("No "):
                continue
            evidence_rows.append(
                EvidenceViewRow(
                    item_id="-",
                    title=item,
                    artifact_type="User message",
                    description=item,
                    source_type="User reported",
                    confidence="reported",
                )
            )
            indicator_rows.extend(
                _extract_indicators_from_text(item, note="User-authored evidence", seen=seen)
            )
    timeline_rows: list[TimelineViewRow] = []
    return ParsedReportItems(
        evidence_rows=evidence_rows,
        indicator_rows=indicator_rows,
        timeline_rows=timeline_rows,
        has_indicators=bool(indicator_rows),
    )


__all__ = ["ParsedReportItems", "parse_report_items"]
