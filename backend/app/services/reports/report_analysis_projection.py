from __future__ import annotations

import re
from collections.abc import Iterable

from app.schemas.reports import StructuredReport
from app.services.reports.report_contracts import ReportInputSnapshot
from app.services.reports.report_view_model_contracts import (
    ReportLanguage,
    TimelineViewRow,
)


_HEADING_RE = re.compile(r"(?m)^#{1,6}\s*(?:\d+(?:\.\d+)*\.?\s*)?(.+?)\s*$")
_LIST_PREFIX_RE = re.compile(r"^(?:[-*•]|\d+[.)])\s+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_DATE_SEPARATOR_RE = re.compile(r"\s+(?:—|–|-)\s+", re.UNICODE)
_THAI_MONTHS = (
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
)


def formal_case_title(value: str) -> str:
    if value.count("\n") > 1 or len(value) > 180:
        return "เรื่องร้องทุกข์ตามข้อมูลสำนวนที่ส่งเข้าสู่ระบบ"
    for raw_line in value.splitlines():
        clean_line = _clean_inline(raw_line)
        if clean_line:
            return _bounded(clean_line, 110)
    return "กรณีที่ผู้ใช้ส่งเข้าสู่ระบบ"


def project_summary_paragraphs(
    structured: StructuredReport | None,
    snapshot: ReportInputSnapshot | None,
    *,
    language: ReportLanguage,
) -> list[str]:
    analysis_text = _analysis_text(snapshot)
    tokens = (
        ("ภาพรวมคดี", "ภาพรวมเหตุการณ์")
        if language == "th"
        else ("overall case", "incident summary", "case overview")
    )
    overview = _section_body(analysis_text, tokens)
    if overview:
        paragraphs = [_clean_inline(item) for item in re.split(r"\n\s*\n", overview)]
        return [item for item in paragraphs if item]
    trace_summary = _trace_summary(snapshot)
    if trace_summary:
        return [_clean_inline(trace_summary)]
    if structured:
        section = next(
            (item for item in structured.sections if item.section_id == "case_summary"),
            None,
        )
        if section:
            cleaned = [_clean_inline(item) for item in section.paragraphs]
            return [item for item in cleaned if item][:2]
    return []


def project_timeline_rows(
    structured: StructuredReport | None,
    snapshot: ReportInputSnapshot | None,
    *,
    language: ReportLanguage,
) -> list[TimelineViewRow]:
    analysis_text = _analysis_text(snapshot)
    tokens = (
        ("ลำดับเหตุการณ์สำคัญ", "ลำดับเหตุการณ์")
        if language == "th"
        else ("key sequence", "timeline", "incident progression")
    )
    timeline_body = _section_body(analysis_text, tokens)
    items = _list_items(timeline_body)
    if not items:
        return []
    source_label = _source_label(_source_ids(structured, snapshot), snapshot, language)
    rows: list[TimelineViewRow] = []
    for item in items:
        time_display, event = _split_timeline_item(item, language)
        if not event:
            continue
        rows.append(
            TimelineViewRow(
                order=len(rows) + 1,
                time_display=time_display,
                event=event,
                source_evidence=source_label,
                status="reported",
            )
        )
    return rows


def _analysis_text(snapshot: ReportInputSnapshot | None) -> str:
    return snapshot.analysis_answer if snapshot else ""


def _trace_summary(snapshot: ReportInputSnapshot | None) -> str:
    if snapshot and isinstance(snapshot.analysis_trace, dict):
        summary = snapshot.analysis_trace.get("summary")
        if isinstance(summary, str):
            return summary.strip()
    return ""


def _section_body(text: str, tokens: tuple[str, ...]) -> str:
    matches = list(_HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        heading = _clean_inline(match.group(1)).lower()
        if not any(token.lower() in heading for token in tokens):
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.end() : end].strip()
    return ""


def _list_items(body: str) -> list[str]:
    items: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not _LIST_PREFIX_RE.match(line):
            continue
        clean = _clean_inline(_LIST_PREFIX_RE.sub("", line, count=1))
        if clean:
            items.append(clean)
    return items


def _split_timeline_item(item: str, language: ReportLanguage) -> tuple[str, str]:
    parts = _DATE_SEPARATOR_RE.split(item, maxsplit=1)
    if len(parts) == 2 and _looks_like_time(parts[0]):
        return _plain_text(parts[0]).strip(), _clean_inline(parts[1])
    unspecified = "ไม่ระบุวันเวลา" if language == "th" else "Date not specified"
    return unspecified, _clean_inline(item)


def _looks_like_time(value: str) -> bool:
    compact = value.strip().lower()
    return (
        len(compact) <= 80
        and (
            any(month in compact for month in _THAI_MONTHS)
            or bool(re.search(r"\b(?:19|20|25)\d{2}\b", compact))
            or any(token in compact for token in ("เวลา", "ช่วง", "date", "time"))
        )
    )


def _trace_claims(snapshot: ReportInputSnapshot | None) -> list[dict[str, object]]:
    if snapshot is None or not isinstance(snapshot.analysis_trace, dict):
        return []
    claims = snapshot.analysis_trace.get("claims")
    if not isinstance(claims, list):
        return []
    return [claim for claim in claims if isinstance(claim, dict)]


def _claim_source_ids(claim: dict[str, object]) -> list[str]:
    raw_ids = claim.get("supporting_source_message_ids") or claim.get("source_message_ids")
    if not isinstance(raw_ids, list):
        return []
    return [str(item) for item in raw_ids if str(item).strip()]


def _source_ids(
    structured: StructuredReport | None,
    snapshot: ReportInputSnapshot | None,
) -> list[str]:
    ids = [source_id for claim in _trace_claims(snapshot) for source_id in _claim_source_ids(claim)]
    if not ids and structured:
        ids = [source_id for claim in structured.claims for source_id in claim.source_message_ids]
    if not ids and snapshot:
        ids = [str(message.message_id) for message in snapshot.source_messages]
    return list(dict.fromkeys(ids))


def _source_label(
    source_ids: Iterable[str],
    snapshot: ReportInputSnapshot | None,
    language: ReportLanguage,
) -> str:
    ordinal_by_id = {
        str(message.message_id): message.ordinal
        for message in snapshot.source_messages
    } if snapshot else {}
    ordinals = sorted({ordinal_by_id[source_id] for source_id in source_ids if source_id in ordinal_by_id})
    if not ordinals:
        return "ข้อมูลจากสำนวนที่ผู้ใช้ส่ง" if language == "th" else "User-submitted case material"
    prefix = "ข้อความ" if language == "th" else "Message"
    return f"{prefix} " + ", ".join(f"#{ordinal}" for ordinal in ordinals)


def _clean_inline(value: object) -> str:
    text = _plain_text(value)
    text = _HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _bounded(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _plain_text(value: object) -> str:
    return (
        str(value)
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


__all__ = [
    "formal_case_title",
    "project_summary_paragraphs",
    "project_timeline_rows",
]
