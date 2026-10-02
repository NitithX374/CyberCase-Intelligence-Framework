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


@dataclass(frozen=True)
class Alignment:
    start: int
    end: int
    edits: int
    path: tuple[tuple[str, int, int], ...]


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
    masked = content[: best.start] + MASK * (best.end - best.start) + content[best.end :]
    second = aligned_candidate(masked, quote)
    second_edits = second.edits if second is not None else len(quote)
    if second_edits < best.edits + max(3, len(quote) // 10) or best.edits > len(quote) / 2:
        return None
    passage = content[best.start : best.end]
    if not passage.strip() or len(quote_occurrences(content, passage)) != 1:
        return None
    places = quote_differences(quote, content, best.path)
    if len(places) > MAX_POINTER_PLACES:
        return None
    return NearPassage(source_text=passage, differences=tuple(places))


def aligned_candidate(content: str, quote: str) -> Alignment | None:
    window = fuzz.partial_ratio_alignment(quote, content)
    if window is None:
        return None
    low = max(0, window.dest_start - len(quote))
    high = min(len(content), window.dest_end + len(quote))
    if low >= high:
        return None
    alignment = infix_alignment(quote, content[low:high])
    return Alignment(
        start=alignment.start + low,
        end=alignment.end + low,
        edits=alignment.edits,
        path=tuple((op, quote_at, source_at + low) for op, quote_at, source_at in alignment.path),
    )


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
    path: list[tuple[str, int, int]] = []
    quote_at, column = len(quote), end
    while quote_at > 0:
        step = moves[quote_at - 1][column]
        if step == 0:
            same = quote[quote_at - 1] == text[column - 1]
            path.append(("=" if same else "~", quote_at - 1, column - 1))
            quote_at, column = quote_at - 1, column - 1
        elif step == 1:
            path.append(("+", quote_at - 1, column))
            quote_at -= 1
        else:
            path.append(("-", quote_at, column - 1))
            column -= 1
    path.reverse()
    return Alignment(start=column, end=end, edits=previous[end], path=tuple(path))


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


def widened(spans: list[tuple[int, int]], start: int, end: int) -> tuple[int, int]:
    hit = [span for span in spans if span[0] < max(end, start + 1) and span[1] > start]
    return min([start] + [span[0] for span in hit]), max([end] + [span[1] for span in hit])


def quote_differences(
    quote: str, content: str, path: tuple[tuple[str, int, int], ...]
) -> list[tuple[str, str]]:
    source_low = min(at for op, _, at in path)
    source_high = max(at for op, _, at in path) + 1
    window_low = max(0, source_low - len(quote))
    window_high = min(len(content), source_high + len(quote))
    quote_words = token_spans(quote)
    source_words = token_spans(content[window_low:window_high], window_low)
    quote_to_source: dict[int, int] = {}
    source_to_quote: dict[int, int] = {}
    for op, quote_at, source_at in path:
        if op != "-":
            quote_to_source.setdefault(quote_at, source_at)
        if op != "+":
            source_to_quote.setdefault(source_at, quote_at)
    runs: list[tuple[int, int, int, int]] = []
    current: tuple[int, int, int, int] | None = None
    for op, quote_at, source_at in path:
        if op == "=":
            if current is not None:
                runs.append(current)
                current = None
            continue
        quote_span = (quote_at, quote_at + 1) if op != "-" else (quote_at, quote_at)
        source_span = (source_at, source_at + 1) if op != "+" else (source_at, source_at)
        step = (*quote_span, *source_span)
        current = (
            step
            if current is None
            else (
                min(current[0], step[0]),
                max(current[1], step[1]),
                min(current[2], step[2]),
                max(current[3], step[3]),
            )
        )
    if current is not None:
        runs.append(current)
    regions: list[tuple[int, int, int, int]] = []
    for quote_start, quote_end, source_start, source_end in runs:
        for _ in range(6):
            new_quote = widened(quote_words, quote_start, quote_end)
            mapped = [quote_to_source[at] for at in range(*new_quote) if at in quote_to_source]
            new_source = widened(
                source_words,
                min([source_start, *mapped]),
                max([source_end, *(at + 1 for at in mapped)]),
            )
            back = [source_to_quote[at] for at in range(*new_source) if at in source_to_quote]
            grown = (
                min([new_quote[0], *back]),
                max([new_quote[1], *(at + 1 for at in back)]),
                *new_source,
            )
            if grown == (quote_start, quote_end, source_start, source_end):
                break
            quote_start, quote_end, source_start, source_end = grown
        if regions and (quote_start < regions[-1][1] or source_start < regions[-1][3]):
            last = regions.pop()
            quote_start, quote_end = min(quote_start, last[0]), max(quote_end, last[1])
            source_start, source_end = min(source_start, last[2]), max(source_end, last[3])
        regions.append((quote_start, quote_end, source_start, source_end))
    places: list[tuple[str, str]] = []
    for quote_start, quote_end, source_start, source_end in regions:
        written = [quote[a:b] for a, b in quote_words if a >= quote_start and b <= quote_end]
        original = [content[a:b] for a, b in source_words if a >= source_start and b <= source_end]
        matcher = difflib.SequenceMatcher(None, written, original, autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            place = ("".join(written[i1:i2]).strip(), "".join(original[j1:j2]).strip())
            if place[0] != place[1] and place not in places:
                places.append(place)
    return places


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
