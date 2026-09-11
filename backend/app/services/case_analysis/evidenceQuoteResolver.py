import hashlib
import re
from collections.abc import Mapping

MAX_SUPPORTED_DOCUMENT_PAGES = 500
MAX_PAGE_SPANS_PER_QUOTE = 8


def resolve_document_locator(
    source_id: str,
    quote: str,
    content: str,
    document_context: object,
    *,
    require_complete_coverage: bool = False,
) -> dict[str, object]:
    occurrences = quote_occurrences(content, quote)
    candidates: set[tuple[str, str, tuple[int, ...]]] = set()
    for document in extractDocumentsForSource(source_id, document_context):
        locator = findDocumentLocator(
            document, content, occurrences, len(quote), require_complete_coverage
        )
        if locator is not None:
            candidates.add(locator)
    if len(candidates) != 1:
        return {"document_id": None, "filename": None, "page_numbers": []}
    document_id, filename, page_numbers = candidates.pop()
    return {
        "document_id": document_id,
        "filename": filename,
        "page_numbers": list(page_numbers),
    }


def extractDocumentsForSource(
    source_id: str, context: object
) -> list[Mapping[str, object]]:
    if not isinstance(context, list):
        return []
    documents: list[Mapping[str, object]] = []
    for entry in context:
        if (
            not isinstance(entry, Mapping)
            or entry.get("source_message_id", entry.get("source_id")) != source_id
        ):
            continue
        raw_documents = entry.get("documents")
        if isinstance(raw_documents, list):
            documents.extend(
                value for value in raw_documents if isinstance(value, Mapping)
            )
    return documents


def findDocumentLocator(
    document: Mapping[str, object],
    content: str,
    occurrences: list[int],
    quote_length: int,
    require_complete_coverage: bool,
) -> tuple[str, str, tuple[int, ...]] | None:
    document_id = document.get("document_id")
    filename = document.get("filename")
    if not isinstance(document_id, str) or not isinstance(filename, str):
        return None
    spans = validatePageSpans(document.get("page_spans"), content)
    occurrence_pages: list[tuple[int, ...]] = []
    for start in occurrences:
        end = start + quote_length
        if require_complete_coverage and not verifyQuoteCoverage(spans, start, end):
            return None
        pages = tuple(span[0] for span in spans if span[1] < end and span[2] > start)
        if (
            not pages
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


def verifyQuoteCoverage(spans: list[tuple[int, int, int]], start: int, end: int) -> bool:
    cursor = start
    covered = 0
    for page, lower, upper in spans:
        if upper <= cursor:
            continue
        if type(page) is not int or not 1 <= page <= MAX_SUPPORTED_DOCUMENT_PAGES or lower > cursor:
            return False
        covered += 1
        cursor = upper
        if cursor >= end:
            return covered <= MAX_PAGE_SPANS_PER_QUOTE
    return False


def validatePageSpans(value: object, content: str) -> list[tuple[int, int, int]]:
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
        expected_hash = item.get("text_sha256")
        if not all(isinstance(part, int) for part in (page, start, end)):
            break
        if (
            not isinstance(expected_hash, str)
            or start < 0
            or end > len(content)
            or start >= end
        ):
            break
        if page in seen_pages or start < previous_end:
            break
        actual_hash = hashlib.sha256(content[start:end].encode("utf-8")).hexdigest()
        if actual_hash != expected_hash:
            break
        seen_pages.add(page)
        previous_end = end
        spans.append((page, start, end))
    return spans


def quote_occurrences(content: str, quote: str) -> list[int]:
    occurrences: list[int] = []
    start = content.find(quote)
    while start >= 0:
        occurrences.append(start)
        start = content.find(quote, start + 1)
    return occurrences


def find_aligned_quote(content: str, quote: str) -> str | None:
    occurrences = quote_occurrences(content, quote)
    if len(occurrences) == 1:
        return quote
    if len(occurrences) > 1:
        return None

    ellipsis_aligned = _expand_unique_ellipsis_quote(content, quote)
    if ellipsis_aligned is not None:
        return ellipsis_aligned

    clean_quote = re.sub(r"[*_#`~]", "", quote)
    clean_quote = re.sub(r'["“”]', '"', clean_quote)
    clean_quote = re.sub(r"['‘’]", "'", clean_quote)
    words = clean_quote.split()
    if not words:
        return None

    def word_to_pattern(w: str) -> str:
        parts: list[str] = []
        for ch in w:
            if ch == '"':
                parts.append(r'["“”]')
            elif ch == "'":
                parts.append(r"['‘’]")
            else:
                parts.append(re.escape(ch))
        return r"[*_#`~]*\s*".join(parts)

    word_patterns = [word_to_pattern(w) for w in words]
    pattern_str = r"[*_#`~]*" + r"[*_#`~\s]*".join(word_patterns) + r"[*_#`~]*"

    try:
        matches = list(re.finditer(pattern_str, content))
    except re.error:
        return None

    if len(matches) == 1:
        match = matches[0]
        return content[match.start() : match.end()]

    return None


def _expand_unique_ellipsis_quote(content: str, quote: str) -> str | None:
    parts = [part.strip() for part in re.split(r"(?:\.{3,}|…+)", quote)]
    if len(parts) < 2 or any(len(part) < 2 for part in parts):
        return None
    candidates: list[tuple[int, int]] = []

    def collect(part_index: int, search_from: int, span_start: int | None) -> None:
        if len(candidates) > 1:
            return
        if part_index == len(parts):
            if span_start is not None:
                candidates.append((span_start, search_from))
            return
        part = parts[part_index]
        start = content.find(part, search_from)
        while start >= 0:
            collect(
                part_index + 1,
                start + len(part),
                start if span_start is None else span_start,
            )
            if len(candidates) > 1:
                return
            start = content.find(part, start + 1)

    collect(0, 0, None)
    if len(candidates) != 1:
        return None
    lower, upper = candidates[0]
    return content[lower:upper]


__all__ = [
    "MAX_PAGE_SPANS_PER_QUOTE",
    "MAX_SUPPORTED_DOCUMENT_PAGES",
    "extractDocumentsForSource",
    "findDocumentLocator",
    "find_aligned_quote",
    "quote_occurrences",
    "resolve_document_locator",
    "validatePageSpans",
    "verifyQuoteCoverage",
]
