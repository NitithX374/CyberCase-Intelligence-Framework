import difflib
import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cached_property

from pythainlp.tokenize import word_tokenize
from rapidfuzz import fuzz

MAX_SUPPORTED_DOCUMENT_PAGES = 500
MAX_PAGE_SPANS_PER_QUOTE = 8
MAX_QUOTE_CHARS = 2_000
MAX_POINTER_PLACES = 3
CONTEXT_WORDS = 3
WORD = re.compile(r"\w+(?:['’]\w+)*|\s+|[^\w\s]")
THAI = re.compile(r"[฀-๿]")
MASK = "\0"
EDGE_ELLIPSIS = re.compile(r"^\s*[\[(]?(?:\.{3,}|…+)[\])]?\s*|\s*[\[(]?(?:\.{3,}|…+)[\])]?\s*$")
QUOTE_MARK = "[\"'“”‘’]"
OCR_TAG = r"(?:<page_number>[^<]*</page_number>|</?[A-Za-z][^<>]*>)"
FORMAT_QUOTE_MARKS = frozenset("\"'“”‘’«»„‚`´")
FORMAT_DASHES = frozenset("‐‑‒–—―−")
FORMAT_PUNCTUATION = frozenset(".,;:!?()[]{}-/…*_#~")
MIN_FORMAT_FORM_CHARS = 8


def folded(text: str) -> tuple[str, list[int]]:
    pieces: list[str] = []
    index: list[int] = []
    for position, character in enumerate(text):
        for piece in unicodedata.normalize("NFKC", character):
            pieces.append(piece)
            index.append(position)
    return "".join(pieces), index


def format_form(text: str) -> tuple[str, list[int]]:
    pieces: list[str] = []
    index: list[int] = []
    for position, character in enumerate(text):
        between_digits = (
            0 < position < len(text) - 1
            and text[position - 1].isdigit()
            and text[position + 1].isdigit()
        )
        for piece in unicodedata.normalize("NFKC", character):
            if piece in FORMAT_DASHES:
                piece = "-"
            if piece.isspace() or piece in FORMAT_QUOTE_MARKS:
                continue
            if piece in FORMAT_PUNCTUATION and not between_digits:
                continue
            for letter in piece.casefold():
                pieces.append(letter)
                index.append(position)
    return "".join(pieces), index


@dataclass(frozen=True)
class NearPassage:
    source_text: str
    differences: tuple[tuple[str, str], ...]
    occurrences: int = 1


@dataclass(frozen=True)
class Alignment:
    start: int
    end: int
    edits: int


class IndexedText:
    def __init__(self, text: str) -> None:
        self.text = text

    @cached_property
    def folded(self) -> tuple[str, list[int]]:
        return folded(self.text)

    @cached_property
    def format_form(self) -> tuple[str, list[int]]:
        return format_form(self.text)


def indexed(content: str | IndexedText) -> IndexedText:
    return content if isinstance(content, IndexedText) else IndexedText(content)


def nearest_passage(source: str | IndexedText, quote: str) -> NearPassage | None:
    content = indexed(source).text
    quote = without_edge_ellipses(quote)
    if not quote or not content or any(mark in quote.strip(" .…")[1:-1] for mark in ("...", "…")):
        return None
    best = aligned_candidate(content, quote)
    if best is None:
        return None
    second = aligned_candidate(masked_everywhere(content, content[best.start : best.end]), quote)
    second_edits = second.edits if second is not None else len(quote)
    if second_edits < best.edits + max(3, len(quote) // 10) or best.edits > len(quote) / 3:
        return None
    worded = word_places(quote, content, best.start, best.end)
    if worded is None:
        return None
    (start, end), places = worded
    passage = content[start:end]
    if not passage or len(places) > MAX_POINTER_PLACES:
        return None
    return NearPassage(
        source_text=passage,
        differences=tuple(places),
        occurrences=len(quote_occurrences(content, passage)),
    )


def masked_everywhere(content: str, text: str) -> str:
    characters = list(content)
    for start in quote_occurrences(content, text):
        characters[start : start + len(text)] = MASK * len(text)
    return "".join(characters)


def aligned_candidate(content: str, quote: str) -> Alignment | None:
    window = fuzz.partial_ratio_alignment(quote, content)
    if window is None:
        return None
    low = max(0, window.dest_start - len(quote))
    high = min(len(content), window.dest_end + len(quote))
    if low >= high:
        return None
    alignment = infix_alignment(quote, content[low:high])
    return Alignment(start=alignment.start + low, end=alignment.end + low, edits=alignment.edits)


def infix_alignment(quote: str, text: str) -> Alignment:
    width = len(text)
    previous = [0] * (width + 1)
    moves: list[bytearray] = []
    for row_at, character in enumerate(quote, 1):
        row = [row_at] + [0] * width
        move = bytearray(width + 1)
        move[0] = 1
        for column in range(1, width + 1):
            diagonal = previous[column - 1] + (character != text[column - 1])
            up = previous[column] + 1
            left = row[column - 1] + 1
            if diagonal <= up and diagonal <= left:
                row[column] = diagonal
            elif up <= left:
                row[column] = up
                move[column] = 1
            else:
                row[column] = left
                move[column] = 2
        moves.append(move)
        previous = row
    end = min(range(width + 1), key=previous.__getitem__)
    quote_at, column = len(quote), end
    while quote_at > 0:
        step = moves[quote_at - 1][column]
        if step != 2:
            quote_at -= 1
        if step != 1:
            column -= 1
    return Alignment(start=column, end=end, edits=previous[end])


def token_spans(text: str, offset: int = 0) -> list[tuple[int, int]]:
    if THAI.search(text):
        tokens = word_tokenize(text, engine="newmm", keep_whitespace=True)
        if "".join(tokens) == text:
            spans: list[tuple[int, int]] = []
            at = offset
            for token in tokens:
                spans.append((at, at + len(token)))
                at += len(token)
            return spans
    return [
        (start + offset, end + offset) for start, end in (m.span() for m in WORD.finditer(text))
    ]


def word_places(
    quote: str, content: str, start: int, end: int
) -> tuple[tuple[int, int], list[tuple[str, str]]] | None:
    margin = max(len(quote), 100)
    low, high = max(0, start - margin), min(len(content), end + margin)
    source_words = token_spans(content[low:high], low)
    inside = [at for at, (a, b) in enumerate(source_words) if b > start and a < end]
    if not inside:
        return None
    first = context_edge(source_words, content, inside[0], -1)
    last = context_edge(source_words, content, inside[-1], 1)
    window = source_words[first : last + 1]
    written = [quote[a:b] for a, b in token_spans(quote)]
    original = [content[a:b] for a, b in window]
    opcodes = difflib.SequenceMatcher(None, written, original, autojunk=False).get_opcodes()
    equal = [at for at, opcode in enumerate(opcodes) if opcode[0] == "equal"]
    head, tail = (equal[0], equal[-1]) if equal else (len(opcodes), -1)
    kept: list[int] = []
    places: list[tuple[str, str]] = []
    for at, (tag, i1, i2, j1, j2) in enumerate(opcodes):
        sources = list(range(j1, j2))
        written_words = sum(1 for word in written[i1:i2] if word.strip())
        if at < head:
            sources = nearest_words(original, sources, written_words, reverse=True)
        elif at > tail:
            sources = nearest_words(original, sources, written_words, reverse=False)
        kept.extend(sources)
        if tag == "equal":
            continue
        place = ("".join(written[i1:i2]).strip(), "".join(original[j] for j in sources).strip())
        if place[0] != place[1] and place not in places:
            places.append(place)
    if not kept:
        return None
    span_start, span_end = window[min(kept)][0], window[max(kept)][1]
    piece = content[span_start:span_end]
    span_start += len(piece) - len(piece.lstrip())
    span_end -= len(piece) - len(piece.rstrip())
    return (span_start, span_end), places


def context_edge(words: list[tuple[int, int]], content: str, at: int, direction: int) -> int:
    counted = 0
    while 0 <= at + direction < len(words) and counted < CONTEXT_WORDS:
        at += direction
        if content[words[at][0] : words[at][1]].strip():
            counted += 1
    return at


def nearest_words(
    original: list[str], sources: list[int], wanted: int, *, reverse: bool
) -> list[int]:
    picked: list[int] = []
    counted = 0
    for at in reversed(sources) if reverse else sources:
        if counted == wanted:
            break
        picked.append(at)
        if original[at].strip():
            counted += 1
    return sorted(picked)


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


def without_edge_ellipses(quote: str) -> str:
    trimmed = EDGE_ELLIPSIS.sub("", quote)
    return trimmed if len(trimmed) >= 2 else quote


def find_aligned_quote(source: str | IndexedText, quote: str) -> list[tuple[int, int]] | None:
    source = indexed(source)
    content = source.text
    quote = without_edge_ellipses(quote)
    occurrences = quote_occurrences(content, quote)
    if len(occurrences) == 1:
        return [(occurrences[0], occurrences[0] + len(quote))]
    if len(occurrences) > 1:
        return None

    compatibility_aligned = find_folded_quote(source, quote)
    if compatibility_aligned is not None:
        return [compatibility_aligned]

    ellipsis_aligned = unique_ellipsis_pieces(content, quote)
    if ellipsis_aligned is not None:
        return ellipsis_aligned

    relaxed = find_relaxed_quote(content, quote)
    if relaxed is not None:
        return [relaxed]

    format_only = find_format_only_quote(source, quote)
    return [format_only] if format_only is not None else None


def find_relaxed_quote(content: str, quote: str) -> tuple[int, int] | None:
    clean_quote = re.sub(r"[*_#`~]", "", quote)
    clean_quote = re.sub(QUOTE_MARK, '"', clean_quote)
    words = clean_quote.split()
    if not words:
        return None

    def word_to_pattern(w: str) -> str:
        parts: list[str] = []
        for ch in w:
            if ch == '"':
                parts.append(QUOTE_MARK)
            else:
                parts.append(re.escape(ch))
        return rf"[*_#`~]*\s*(?:{OCR_TAG}\s*)*".join(parts)

    word_patterns = [word_to_pattern(w) for w in words]
    pattern_str = r"[*_#`~]*" + rf"(?:[*_#`~\s]|{OCR_TAG})*".join(word_patterns) + r"[*_#`~]*"

    try:
        matches = list(re.finditer(pattern_str, content))
    except re.error:
        return None

    return matches[0].span() if len(matches) == 1 else None


def find_format_only_quote(source: str | IndexedText, quote: str) -> tuple[int, int] | None:
    source = indexed(source)
    source_form, index = source.format_form
    quote_form, _ = format_form(without_edge_ellipses(quote))
    if len(quote_form) < MIN_FORMAT_FORM_CHARS:
        return None
    positions = quote_occurrences(source_form, quote_form)
    if len(positions) != 1:
        return None
    return index[positions[0]], index[positions[0] + len(quote_form) - 1] + 1


def find_folded_quote(source: str | IndexedText, quote: str) -> tuple[int, int] | None:
    source = indexed(source)
    folded_content, index = source.folded
    folded_quote, _ = folded(quote)
    if not folded_quote:
        return None
    positions = quote_occurrences(folded_content, folded_quote)
    if len(positions) != 1:
        return None
    end_piece = positions[0] + len(folded_quote) - 1
    return index[positions[0]], index[end_piece] + 1


def unique_ellipsis_pieces(content: str, quote: str) -> list[tuple[int, int]] | None:
    parts = [part.strip() for part in re.split(r"(?:\.{3,}|…+)", quote)]
    if len(parts) < 2 or any(len(part) < 2 for part in parts):
        return None
    candidates: list[list[tuple[int, int]]] = []

    def collect(part_index: int, search_from: int, placed: list[tuple[int, int]]) -> None:
        if len(candidates) > 1:
            return
        if part_index == len(parts):
            candidates.append(placed)
            return
        part = parts[part_index]
        start = content.find(part, search_from)
        while start >= 0:
            collect(part_index + 1, start + len(part), [*placed, (start, start + len(part))])
            if len(candidates) > 1:
                return
            start = content.find(part, start + 1)

    collect(0, 0, [])
    return candidates[0] if len(candidates) == 1 else None


__all__ = [
    "IndexedText",
    "MAX_PAGE_SPANS_PER_QUOTE",
    "MAX_QUOTE_CHARS",
    "MAX_SUPPORTED_DOCUMENT_PAGES",
    "NearPassage",
    "extract_documents_for_source",
    "find_document_locator",
    "find_aligned_quote",
    "find_format_only_quote",
    "nearest_passage",
    "quote_occurrences",
    "resolve_document_locator",
    "validate_page_spans",
    "without_edge_ellipses",
]
