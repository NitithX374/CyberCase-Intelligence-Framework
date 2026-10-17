from __future__ import annotations

from collections.abc import Mapping

MAX_SUPPORTED_DOCUMENT_PAGES = 500
MAX_PAGE_SPANS_PER_QUOTE = 8
MAX_QUOTE_CHARS = 2_000


def find_document_locator(
    document: Mapping[str, object],
    content: str,
    occurrences: list[int],
    quote_length: int,
) -> tuple[str, str, tuple[int, ...]] | None:
    document_id = document.get("document_id")
    filename = document.get("filename")
    if not isinstance(document_id, str) or not isinstance(filename, str):
        return None
    spans = validate_page_spans(document.get("page_spans"), content)
    occurrence_pages: list[tuple[int, ...]] = []
    for start in occurrences:
        end = start + quote_length
        pages = tuple(span[0] for span in spans if span[1] < end and span[2] > start)
        if (
            not pages
            or len(pages) > MAX_PAGE_SPANS_PER_QUOTE
            or not any(span[1] <= start < span[2] for span in spans)
            or not any(span[1] < end <= span[2] for span in spans)
        ):
            return None
        occurrence_pages.append(pages)
    if not occurrence_pages:
        return None
    unique_pages = set(occurrence_pages)
    if len(unique_pages) != 1:
        return None
    return document_id, filename, unique_pages.pop()


def validate_page_spans(value: object, content: str) -> list[tuple[int, int, int]]:
    if not isinstance(value, list):
        return []
    spans: list[tuple[int, int, int]] = []
    seen_pages: set[int] = set()
    previous_end = 0
    for item in value:
        if not isinstance(item, Mapping):
            break
        page = item.get("page_number")
        start = item.get("start_offset")
        end = item.get("end_offset")
        if isinstance(page, int) and start is None and end is None:
            continue
        if not all(isinstance(part, int) for part in (page, start, end)):
            break
        if (
            start < 0
            or end > len(content)
            or start >= end
            or page < 1
            or page > MAX_SUPPORTED_DOCUMENT_PAGES
        ):
            break
        if page in seen_pages or start < previous_end:
            break
        seen_pages.add(page)
        previous_end = end
        spans.append((page, start, end))
    return spans


__all__ = [
    "MAX_PAGE_SPANS_PER_QUOTE",
    "MAX_QUOTE_CHARS",
    "MAX_SUPPORTED_DOCUMENT_PAGES",
    "find_document_locator",
    "validate_page_spans",
]
