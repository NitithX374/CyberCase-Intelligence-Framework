from __future__ import annotations

import logging
import threading
from bisect import bisect_right
from functools import cache, cached_property
from importlib.metadata import version
from typing import Any

from pythainlp.tokenize import sent_tokenize

from app.trace.citations import MAX_CONTEXT_CHARS, CaseQuoteContext

MIN_SENTENCE_CHARS = 25
SAT_MODEL = "sat-3l-sm"
SAT_REVISION = "137da054051ad9f1eac42025f758db4ac9f22535"
SAT_THRESHOLD = 0.025

logger = logging.getLogger(__name__)

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

                    _sat_model = SaT(SAT_MODEL, from_pretrained_kwargs={"revision": SAT_REVISION})
                except Exception:
                    logger.warning(
                        "SaT %s@%s could not be loaded; sentences are split with PyThaiNLP crfcut",
                        SAT_MODEL,
                        SAT_REVISION,
                        exc_info=True,
                    )
                    _sat_model = False
    return _sat_model if _sat_model is not False else None


@cache
def package_version(name: str) -> str:
    return version(name)


def segmenter_identity() -> str:
    if get_sat_segmenter() is not None:
        return (
            f"sat:{SAT_MODEL}@{SAT_REVISION}:threshold={SAT_THRESHOLD}"
            f":wtpsplit={package_version('wtpsplit')}"
        )
    return f"crfcut:pythainlp={package_version('pythainlp')}"


def tokenize_sentences(segment_text: str) -> list[str]:
    segmenter = get_sat_segmenter()
    if segmenter is None:
        return sent_tokenize(segment_text, engine="crfcut")
    return segmenter.split(segment_text, threshold=SAT_THRESHOLD)


def sentence_spans(text: str) -> list[tuple[int, int]]:
    return SentenceIndex(text).spans(0, len(text))


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


class SentenceIndex:
    def __init__(self, text: str) -> None:
        self.text = text
        self.split: dict[str, list[tuple[int, int]]] = {}

    @cached_property
    def lines(self) -> list[tuple[int, int]]:
        return line_spans(self.text)

    def line_of(self, position: int) -> int:
        return bisect_right([start for start, _ in self.lines], position) - 1

    def spans(self, start: int, end: int) -> list[tuple[int, int]]:
        return [
            span
            for line_start, line_end in line_spans(self.text[start:end])
            for span in self.sentences_in(start + line_start, start + line_end)
        ]

    def sentences_in(self, start: int, end: int) -> list[tuple[int, int]]:
        line = self.text[start:end]
        if line not in self.split:
            self.split[line] = line_sentences(line, 0, len(line))
        return [(start + span_start, start + span_end) for span_start, span_end in self.split[line]]

    def sentences(self, line: int) -> list[tuple[int, int]]:
        return self.sentences_in(*self.lines[line])

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
    "SentenceIndex",
    "get_sat_segmenter",
    "quote_context",
    "segmenter_identity",
    "sentence_spans",
    "tokenize_sentences",
]
