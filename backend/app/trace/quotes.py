import difflib
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cached_property
from typing import Literal

from pythainlp.tokenize import word_tokenize
from rapidfuzz import fuzz

MAX_SUPPORTED_DOCUMENT_PAGES = 500
MAX_PAGE_SPANS_PER_QUOTE = 8
MAX_QUOTE_CHARS = 2_000
MAX_POINTER_PLACES = 3
MAX_TOLERATED_DIFFERENCES = 8
CONTEXT_WORDS = 3
WORD = re.compile(r"[A-Za-z]+(?:-\d+)+|\d+(?:[.,:/-]\d+)+|\w+(?:['’]\w+)*|\s+|[^\w\s]")
HAS_WORD = re.compile(r"\w")
THAI = re.compile(r"[฀-๿]")
MASK = "\0"
EDGE_ELLIPSIS = re.compile(r"^\s*[\[(]?(?:\.{3,}|…+)[\])]?\s*|\s*[\[(]?(?:\.{3,}|…+)[\])]?\s*$")
QUOTE_MARK = "[\"'“”‘’]"
OCR_TAG = r"(?:<page_number>[^<]*</page_number>|</?[A-Za-z][^<>]*>)"
FORMAT_QUOTE_MARKS = frozenset("\"'“”‘’«»„‚`´")
FORMAT_DASHES = frozenset("‐‑‒–—―−")
FORMAT_PUNCTUATION = frozenset(".,;:!?()[]{}-/…*_#~")
EDGE_MARKS = frozenset(".,;:!?()[]{}…") | FORMAT_QUOTE_MARKS
MIN_FORMAT_FORM_CHARS = 8
MEANING_MARKS = frozenset("?~≈±%<>")
EDGE_REACH = 2
OCR_TAG_PATTERN = re.compile(OCR_TAG)
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
BOUNDARY = " "
MARKUP = r"[*_#`~]"
TIGHT_JOIN = rf"(?:(?:\s*(?:{MARKUP}|{OCR_TAG}))+\s*)?"
LOOSE_JOIN = rf"{MARKUP}*\s*(?:{OCR_TAG}\s*)*"
BOUNDARY_GAP = rf"(?:{MARKUP}|\s|{OCR_TAG})+"
LOOSE_GAP = rf"(?:{MARKUP}|\s|{OCR_TAG})*"

QuoteTier = Literal["exact", "folded", "ellipsis", "relaxed", "format"]


def folded(text: str) -> tuple[str, list[int]]:
    pieces: list[str] = []
    index: list[int] = []
    for position, character in enumerate(text):
        for piece in unicodedata.normalize("NFKC", character):
            pieces.append(piece)
            index.append(position)
    return "".join(pieces), index


@dataclass(frozen=True)
class FormatForm:
    text: str
    index: list[int]


def solid(character: str) -> bool:
    return character.isalnum() and THAI.match(character) is None


def kept_dash(before: str, after: str) -> bool:
    if before.isdigit() and after.isdigit():
        return True
    return after.isdigit() and not before.isalnum()


def thousands_comma(units: list[tuple[str, int]], at: int) -> bool:
    digits = 0
    while at + 1 + digits < len(units) and units[at + 1 + digits][0].isdigit():
        digits += 1
    return digits == 3


def format_form(text: str) -> FormatForm:
    units = [
        (piece, position)
        for position, character in enumerate(text)
        for piece in unicodedata.normalize("NFKC", character)
    ]
    pieces: list[str] = []
    index: list[int] = []
    boundary_at: int | None = None
    after_solid = False
    for at, (piece, position) in enumerate(units):
        if piece in FORMAT_DASHES:
            piece = "-"
        before = units[at - 1][0] if at else ""
        after = units[at + 1][0] if at + 1 < len(units) else ""
        if piece.isspace():
            boundary_at = position if boundary_at is None else boundary_at
            continue
        if piece in FORMAT_QUOTE_MARKS:
            continue
        if piece == "-":
            kept = kept_dash(before, after)
        elif piece in FORMAT_PUNCTUATION:
            kept = (
                before.isdigit()
                and after.isdigit()
                and not (piece == "," and thousands_comma(units, at))
            )
        else:
            kept = True
        if not kept:
            continue
        word = solid(piece)
        if boundary_at is not None:
            if after_solid and word:
                pieces.append(BOUNDARY)
                index.append(boundary_at)
            boundary_at = None
        for letter in piece.translate(THAI_DIGITS).casefold():
            pieces.append(letter)
            index.append(position)
        after_solid = word
    return FormatForm("".join(pieces), index)


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
    def format_form(self) -> FormatForm:
        return format_form(self.text)

    @cached_property
    def tag_spans(self) -> list[tuple[int, int]]:
        return [match.span() for match in OCR_TAG_PATTERN.finditer(self.text)]


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
    anchors = [
        at
        for at, (tag, i1, i2, _, _) in enumerate(opcodes)
        if tag == "equal" and word_count(written[i1:i2])
    ]
    if not anchors:
        return None
    first_anchor, last_anchor = anchors[0], anchors[-1]
    written_head, original_head = opcodes[first_anchor][1], opcodes[first_anchor][3]
    written_tail, original_tail = opcodes[last_anchor][2], opcodes[last_anchor][4]
    thai = bool(THAI.search(quote) or THAI.search("".join(original)))
    head = nearest_words(
        original,
        list(range(original_head)),
        len(word_groups(written[:written_head], thai)),
        reverse=True,
        thai=thai,
    )
    tail = nearest_words(
        original,
        list(range(original_tail, len(original))),
        len(word_groups(written[written_tail:], thai)),
        reverse=False,
        thai=thai,
    )
    kept = [*head, *tail]
    places = diff_places(written[:written_head], [original[j] for j in head])
    for tag, i1, i2, j1, j2 in opcodes[first_anchor : last_anchor + 1]:
        kept.extend(range(j1, j2))
        if tag != "equal":
            add_place(places, "".join(written[i1:i2]), "".join(original[j1:j2]))
    for written_text, source_text in diff_places(
        written[written_tail:], [original[j] for j in tail]
    ):
        add_place(places, written_text, source_text)
    span_start, span_end = window[min(kept)][0], window[max(kept)][1]
    piece = content[span_start:span_end]
    span_start += len(piece) - len(piece.lstrip())
    span_end -= len(piece) - len(piece.rstrip())
    return (span_start, span_end), places


def word_count(tokens: list[str]) -> int:
    return sum(1 for token in tokens if HAS_WORD.search(token))


def word_groups(tokens: list[str], thai: bool, offset: int = 0) -> list[tuple[int, int]]:
    if thai:
        return [
            (at + offset, at + offset) for at, token in enumerate(tokens) if HAS_WORD.search(token)
        ]
    groups: list[tuple[int, int]] = []
    first: int | None = None
    last: int | None = None
    for at, token in enumerate(tokens):
        if not token.strip():
            if first is not None and last is not None:
                groups.append((first + offset, last + offset))
            first = last = None
        elif HAS_WORD.search(token):
            first = at if first is None else first
            last = at
    if first is not None and last is not None:
        groups.append((first + offset, last + offset))
    return groups


def add_place(places: list[tuple[str, str]], written: str, source: str) -> None:
    place = (written.strip(), source.strip())
    if place[0] != place[1] and place not in places:
        places.append(place)


def diff_places(written: list[str], original: list[str]) -> list[tuple[str, str]]:
    places: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, written, original, autojunk=False
    ).get_opcodes():
        if tag != "equal":
            add_place(places, "".join(written[i1:i2]), "".join(original[j1:j2]))
    return places


def text_places(written: str, located: str) -> list[tuple[str, str]]:
    return diff_places(
        [written[a:b] for a, b in token_spans(written)],
        [located[a:b] for a, b in token_spans(located)],
    )


def tolerated_differences(quote: str, located: str) -> tuple[tuple[str, str], ...]:
    kept = [
        (written, source)
        for written, source in text_places(
            without_edge_marks(without_edge_ellipses(quote)), without_edge_marks(located)
        )
        if without_quote_marks(written) != without_quote_marks(source)
    ]
    return tuple(kept[:MAX_TOLERATED_DIFFERENCES])


def meaning_marks(text: str) -> list[str]:
    plain = unicodedata.normalize("NFKC", OCR_TAG_PATTERN.sub("", text))
    return [mark for mark in dict.fromkeys(plain) if mark in MEANING_MARKS]


def ignored_marks(differences: Iterable[tuple[str, str]]) -> list[str]:
    ignored: list[str] = []
    for written, source in differences:
        in_written, in_source = meaning_marks(written), meaning_marks(source)
        for mark in dict.fromkeys([*in_written, *in_source]):
            if (mark in in_written) != (mark in in_source) and mark not in ignored:
                ignored.append(mark)
    return ignored


def reached_mark(source: IndexedText, positions: range) -> str | None:
    for position in positions:
        character = source.text[position]
        if character in "\r\n":
            return None
        if character.isspace():
            continue
        mark = unicodedata.normalize("NFKC", character)
        covered = any(start <= position < end for start, end in source.tag_spans)
        return mark if mark in MEANING_MARKS and not covered else None
    return None


def edge_marks(source: IndexedText, start: int, end: int) -> list[str]:
    after = reached_mark(source, range(end, min(len(source.text), end + EDGE_REACH)))
    before = reached_mark(source, range(start - 1, max(-1, start - 1 - EDGE_REACH), -1))
    return list(dict.fromkeys(mark for mark in (before, after) if mark))


def without_quote_marks(text: str) -> str:
    return "".join(character for character in text if character not in FORMAT_QUOTE_MARKS).strip()


def without_edge_marks(text: str) -> str:
    start, end = 0, len(text)
    while start < end and (text[start].isspace() or text[start] in EDGE_MARKS):
        start += 1
    while end > start and (text[end - 1].isspace() or text[end - 1] in EDGE_MARKS):
        end -= 1
    return text[start:end]


def context_edge(words: list[tuple[int, int]], content: str, at: int, direction: int) -> int:
    counted = 0
    while 0 <= at + direction < len(words) and counted < CONTEXT_WORDS:
        at += direction
        if content[words[at][0] : words[at][1]].strip():
            counted += 1
    return at


def nearest_words(
    original: list[str], sources: list[int], wanted: int, *, reverse: bool, thai: bool
) -> list[int]:
    if not wanted or not sources:
        return []
    groups = word_groups(original[sources[0] : sources[-1] + 1], thai, sources[0])
    chosen = groups[-wanted:] if reverse else groups[:wanted]
    if not chosen:
        return []
    return list(range(chosen[0][0], chosen[-1][1] + 1))


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


@dataclass(frozen=True)
class LocatedQuote:
    spans: list[tuple[int, int]]
    tier: QuoteTier


def locate_quote(source: str | IndexedText, quote: str) -> LocatedQuote | None:
    source = indexed(source)
    content = source.text
    quote = without_edge_ellipses(quote)
    occurrences = quote_occurrences(content, quote)
    if len(occurrences) == 1:
        return LocatedQuote([(occurrences[0], occurrences[0] + len(quote))], "exact")
    if len(occurrences) > 1:
        return None

    compatibility_aligned = find_folded_quote(source, quote)
    if compatibility_aligned is not None:
        return LocatedQuote([compatibility_aligned], "folded")

    ellipsis_aligned = unique_ellipsis_pieces(content, quote)
    if ellipsis_aligned is not None:
        return LocatedQuote(ellipsis_aligned, "ellipsis")

    relaxed = find_relaxed_quote(content, quote)
    if relaxed is not None:
        return LocatedQuote([relaxed], "relaxed")

    format_only = find_format_only_quote(source, quote)
    return LocatedQuote([format_only], "format") if format_only is not None else None


def find_aligned_quote(source: str | IndexedText, quote: str) -> list[tuple[int, int]] | None:
    located = locate_quote(source, quote)
    return located.spans if located is not None else None


def relaxed_word(word: str) -> str:
    pieces = [QUOTE_MARK if character == '"' else re.escape(character) for character in word]
    joined = [pieces[0]]
    for before, after, piece in zip(word, word[1:], pieces[1:], strict=False):
        joined.append(TIGHT_JOIN if solid(before) and solid(after) else LOOSE_JOIN)
        joined.append(piece)
    return "".join(joined)


def relaxed_words(words: list[str]) -> str:
    pieces: list[str] = []
    for number, word in enumerate(words):
        if number:
            solid_gap = solid(words[number - 1][-1]) and solid(word[0])
            pieces.append(BOUNDARY_GAP if solid_gap else LOOSE_GAP)
        pieces.append(relaxed_word(word))
    return "".join(pieces)


def find_relaxed_quote(content: str, quote: str) -> tuple[int, int] | None:
    clean_quote = re.sub(r"[*_#`~]", "", quote)
    clean_quote = re.sub(QUOTE_MARK, '"', clean_quote)
    words = clean_quote.split()
    if not words:
        return None

    pattern_str = rf"{MARKUP}*" + relaxed_words(words) + rf"{MARKUP}*"

    try:
        matches = list(re.finditer(pattern_str, content))
    except re.error:
        return None

    return matches[0].span() if len(matches) == 1 else None


def find_format_only_quote(source: str | IndexedText, quote: str) -> tuple[int, int] | None:
    source = indexed(source)
    form = source.format_form
    wanted = format_form(without_edge_ellipses(quote))
    if len(wanted.text) - wanted.text.count(BOUNDARY) < MIN_FORMAT_FORM_CHARS:
        return None
    spans = [
        (form.index[start], form.index[start + len(wanted.text) - 1] + 1)
        for start in quote_occurrences(form.text, wanted.text)
    ]
    if len(spans) == 1 or len({source.text[a:b] for a, b in spans}) == 1:
        return spans[0]
    return None


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
    "MAX_TOLERATED_DIFFERENCES",
    "LocatedQuote",
    "NearPassage",
    "QuoteTier",
    "edge_marks",
    "extract_documents_for_source",
    "find_document_locator",
    "find_aligned_quote",
    "find_format_only_quote",
    "ignored_marks",
    "locate_quote",
    "nearest_passage",
    "quote_occurrences",
    "resolve_document_locator",
    "tolerated_differences",
    "validate_page_spans",
    "without_edge_ellipses",
]
