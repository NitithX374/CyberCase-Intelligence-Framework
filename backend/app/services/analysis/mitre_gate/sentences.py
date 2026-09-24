from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from pythainlp.tokenize import sent_tokenize

from app.services.sources.case_source_bundle import CaseSourceItem

MIN_SENTENCE_CHARS = 25


@dataclass(frozen=True)
class Sentence:
    source_id: str
    text: str


def split_text(text: str) -> list[str]:
    sentences: list[str] = []
    for line in text.splitlines():
        if line.strip():
            sentences.extend(joined_fragments(sent_tokenize(line, engine="crfcut")))
    return sentences


def joined_fragments(pieces: Sequence[str]) -> list[str]:
    sentences: list[str] = []
    held = ""
    for piece in pieces:
        held += piece
        if len(held.strip()) >= MIN_SENTENCE_CHARS:
            sentences.append(held)
            held = ""
    if held.strip():
        if sentences:
            sentences[-1] += held
        else:
            sentences.append(held)
    return [sentence.strip() for sentence in sentences]


def split_sources(sources: Sequence[CaseSourceItem]) -> list[Sentence]:
    return [
        Sentence(source_id=source.source_id, text=text)
        for source in sources
        for text in split_text(source.text)
    ]


__all__ = ["MIN_SENTENCE_CHARS", "Sentence", "split_sources", "split_text"]
