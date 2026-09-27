import re
import unicodedata
from collections.abc import Mapping
from functools import cached_property

MAX_SUPPORTED_DOCUMENT_PAGES = 500
MAX_PAGE_SPANS_PER_QUOTE = 8
MAX_QUOTE_CHARS = 2_000
PARAPHRASE_TRIGRAM_SHARE = 0.6


def folded(text: str) -> tuple[str, list[int]]:
    pieces: list[str] = []
    index: list[int] = []
    for position, character in enumerate(text):
        for piece in unicodedata.normalize("NFKC", character):
            pieces.append(piece)
            index.append(position)
    return "".join(pieces), index


def trigrams(text: str) -> set[str]:
    stripped = "".join(text.split())
    return {stripped[i : i + 3] for i in range(len(stripped) - 2)}


class IndexedText:
    def __init__(self, text: str) -> None:
        self.text = text

    @cached_property
    def folded(self) -> tuple[str, list[int]]:
        return folded(self.text)

    @cached_property
    def trigrams(self) -> set[str]:
        return trigrams(self.text)


def indexed(content: str | IndexedText) -> IndexedText:
    return content if isinstance(content, IndexedText) else IndexedText(content)


def looks_like_a_paraphrase(content: str | IndexedText, quote: str) -> bool:
    wanted = trigrams(quote)
    if not wanted:
        return False
    return len(wanted & indexed(content).trigrams) / len(wanted) >= PARAPHRASE_TRIGRAM_SHARE


def resolve_document_locator(
    source_id: str,
    quote: str,
    content: str,
    document_context: object,
) -> dict[str, object]:
    occurrences = quote_occurrences(content, quote)
    candidates: set[tuple[str, str, tuple[int, ...]]] = set()
    for document in extract_documents_for_source(source_id, document_context):
        locator = find_document_locator(document, content, occurrences, len(quote))
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


def extract_documents_for_source(source_id: str, context: object) -> list[Mapping[str, object]]:
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
            documents.extend(value for value in raw_documents if isinstance(value, Mapping))
    return documents


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


def quote_occurrences(content: str, quote: str) -> list[int]:
    occurrences: list[int] = []
    start = content.find(quote)
    while start >= 0:
        occurrences.append(start)
        start = content.find(quote, start + 1)
    return occurrences


def find_aligned_quote(source: str | IndexedText, quote: str) -> str | None:
    source = indexed(source)
    content = source.text
    occurrences = quote_occurrences(content, quote)
    if len(occurrences) == 1:
        return quote
    if len(occurrences) > 1:
        return None

    compatibility_aligned = find_folded_quote(source, quote)
    if compatibility_aligned is not None:
        return compatibility_aligned

    ellipsis_aligned = expand_unique_ellipsis_quote(content, quote)
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


def find_folded_quote(source: str | IndexedText, quote: str) -> str | None:
    source = indexed(source)
    content = source.text
    folded_content, index = source.folded
    folded_quote, _ = folded(quote)
    if not folded_quote:
        return None
    positions = quote_occurrences(folded_content, folded_quote)
    if len(positions) != 1:
        return None
    start = index[positions[0]]
    end_piece = positions[0] + len(folded_quote) - 1
    return content[start : index[end_piece] + 1]


def expand_unique_ellipsis_quote(content: str, quote: str) -> str | None:
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
    "IndexedText",
    "MAX_PAGE_SPANS_PER_QUOTE",
    "MAX_QUOTE_CHARS",
    "looks_like_a_paraphrase",
    "MAX_SUPPORTED_DOCUMENT_PAGES",
    "extract_documents_for_source",
    "find_document_locator",
    "find_aligned_quote",
    "quote_occurrences",
    "resolve_document_locator",
    "validate_page_spans",
]
