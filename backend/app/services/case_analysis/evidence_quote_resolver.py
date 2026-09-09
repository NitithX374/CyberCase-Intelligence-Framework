import hashlib
from collections.abc import Mapping


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
    for document in _documents_for_source(source_id, document_context):
        locator = _locator_for_document(
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


def _documents_for_source(
    source_id: str, context: object
) -> list[Mapping[str, object]]:
    if not isinstance(context, list):
        return []
    documents: list[Mapping[str, object]] = []
    for entry in context:
        if (
            not isinstance(entry, Mapping)
            or entry.get("source_message_id") != source_id
        ):
            continue
        raw_documents = entry.get("documents")
        if isinstance(raw_documents, list):
            documents.extend(
                value for value in raw_documents if isinstance(value, Mapping)
            )
    return documents


def _locator_for_document(
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
    spans = _valid_page_spans(document.get("page_spans"), content)
    occurrence_pages: list[tuple[int, ...]] = []
    for start in occurrences:
        end = start + quote_length
        if require_complete_coverage and not _covers_quote(spans, start, end):
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


def _covers_quote(spans: list[tuple[int, int, int]], start: int, end: int) -> bool:
    cursor = start
    covered = 0
    for page, lower, upper in spans:
        if upper <= cursor:
            continue
        if type(page) is not int or not 1 <= page <= 500 or lower > cursor:
            return False
        covered += 1
        cursor = upper
        if cursor >= end:
            return covered <= 8
    return False


def _valid_page_spans(value: object, content: str) -> list[tuple[int, int, int]]:
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
