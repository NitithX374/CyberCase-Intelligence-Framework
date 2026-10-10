from __future__ import annotations

import threading
from bisect import bisect_right
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from pythainlp.tokenize import sent_tokenize

from app.sources.bundle import CaseSourceItem
from app.trace.citations import MAX_CONTEXT_CHARS, CaseQuoteContext

MIN_SENTENCE_CHARS = 25
SAT_THRESHOLD = 0.05

_sat_model: Any = None
_sat_lock = threading.Lock()


def get_sat_segmenter() -> Any:
    global _sat_model
    if _sat_model is None:
        with _sat_lock:
            if _sat_model is None:
                try:
                    import warnings

                    warnings.filterwarnings("ignore", message=".*XLMRobertaTokenizerFast.*")
                    from wtpsplit import SaT

                    _sat_model = SaT("sat-3l-sm")
                except Exception:
                    _sat_model = False
    return _sat_model if _sat_model is not False else None


def tokenize_sentences(segment_text: str) -> list[str]:
    segmenter = get_sat_segmenter()
    if segmenter is not None:
        try:
            return segmenter.split(segment_text, threshold=SAT_THRESHOLD)
        except Exception:
            pass
    return sent_tokenize(segment_text, engine="crfcut")


@dataclass(frozen=True)
class Sentence:
    source_id: str
    text: str


def split_text(text: str) -> list[str]:
    return [text[start:end] for start, end in sentence_spans(text)]


def sentence_spans(text: str) -> list[tuple[int, int]]:
    return [span for start, end in line_spans(text) for span in line_sentences(text, start, end)]


def line_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    for line in text.splitlines(keepends=True):
        content = line.splitlines()[0] if line.splitlines() else ""
        if content.strip():
            spans.append((start, start + len(content)))
        start += len(line)
    return spans


def line_sentences(text: str, start: int, end: int) -> list[tuple[int, int]]:
    segment_text = text[start:end]
    pieces = tokenize_sentences(segment_text)
    if "".join(pieces) != segment_text:
        return [stripped(text, start, end)]
    spans: list[tuple[int, int]] = []
    held_start, at = start, start
    for piece in pieces:
        at += len(piece)
        if len(text[held_start:at].strip()) >= MIN_SENTENCE_CHARS:
            spans.append((held_start, at))
            held_start = at
    if text[held_start:at].strip():
        if spans:
            spans[-1] = (spans[-1][0], at)
        else:
            spans.append((held_start, at))
    return [stripped(text, span_start, span_end) for span_start, span_end in spans]


def stripped(text: str, start: int, end: int) -> tuple[int, int]:
    piece = text[start:end]
    return start + len(piece) - len(piece.lstrip()), end - len(piece) + len(piece.rstrip())


def split_sources(sources: Sequence[CaseSourceItem]) -> list[Sentence]:
    return [
        Sentence(source_id=source.source_id, text=text)
        for source in sources
        for text in split_text(source.text)
    ]


class SentenceIndex:
    def __init__(self, text: str) -> None:
        self.text = text
        self.split: dict[int, list[tuple[int, int]]] = {}

    @cached_property
    def lines(self) -> list[tuple[int, int]]:
        return line_spans(self.text)

    def line_of(self, position: int) -> int:
        return bisect_right([start for start, _ in self.lines], position) - 1

    def sentences(self, line: int) -> list[tuple[int, int]]:
        if line not in self.split:
            self.split[line] = line_sentences(self.text, *self.lines[line])
        return self.split[line]

    def previous(self, line: int, sentence: tuple[int, int]) -> tuple[int, int] | None:
        same_line = self.sentences(line)
        position = same_line.index(sentence)
        if position > 0:
            return same_line[position - 1]
        return self.sentences(line - 1)[-1] if line > 0 else None


def quote_context(index: SentenceIndex, quote: str) -> CaseQuoteContext | None:
    text = index.text
    start = text.find(quote) if quote else -1
    if start < 0 or text.find(quote, start + 1) >= 0:
        return None
    end = start + len(quote)
    first_line, last_line = index.line_of(start), index.line_of(end - 1)
    touching = [
        span
        for line in range(first_line, last_line + 1)
        for span in index.sentences(line)
        if span[1] > start and span[0] < end
    ]
    if not touching:
        return None
    previous = index.previous(first_line, touching[0])
    before = text[(previous or touching[0])[0] : start]
    after = text[end : touching[-1][1]]
    if previous is not None and len(before) + len(after) > MAX_CONTEXT_CHARS:
        before = text[touching[0][0] : start]
    keep_before = min(len(before), max(MAX_CONTEXT_CHARS // 2, MAX_CONTEXT_CHARS - len(after)))
    keep_after = min(len(after), MAX_CONTEXT_CHARS - keep_before)
    return CaseQuoteContext(
        before=before[len(before) - keep_before :],
        after=after[:keep_after],
        cut_before=keep_before < len(before),
        cut_after=keep_after < len(after),
    )


__all__ = [
    "MIN_SENTENCE_CHARS",
    "SAT_THRESHOLD",
    "Sentence",
    "SentenceIndex",
    "get_sat_segmenter",
    "quote_context",
    "sentence_spans",
    "split_sources",
    "split_text",
    "tokenize_sentences",
]
