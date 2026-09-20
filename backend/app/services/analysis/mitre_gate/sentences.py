"""Cutting case material into sentences, so the gate can judge one at a time.

A case source is a whole statement or a whole OCR'd report. Asked about all of
it at once, a gate can only answer whether the case as a whole is technical,
and the span it points at is whatever it chose to copy out. Asked about one
sentence, it answers about that sentence, and the span is the sentence.

Every sentence returned is an exact substring of its source, which is what lets
the gate's answer be checked against the material it came from.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from pythainlp.tokenize import sent_tokenize

from app.services.sources import CaseSourceItem

# Thai is written without spaces between words, so a sentence has to be found
# rather than split off. PyThaiNLP's crfcut is trained on Thai prose, and breaks
# at the dot in names like PowerShell.exe -- which would cut a technical phrase
# in half. A piece this short is the start of the sentence after it.
MIN_SENTENCE_CHARS = 25


@dataclass(frozen=True)
class Sentence:
    source_id: str
    text: str


def split_text(text: str) -> list[str]:
    """The sentences of one text, each an exact span of it.

    Lines are separated first: a report is full of headings, form fields and
    table rows that are each their own unit, and that a splitter trained on
    prose runs together into one long sentence.
    """

    sentences: list[str] = []
    for line in text.splitlines():
        if line.strip():
            sentences.extend(joined_fragments(sent_tokenize(line, engine="crfcut")))
    return sentences


def joined_fragments(pieces: Sequence[str]) -> list[str]:
    """Pieces of one line, with the too-short ones joined to a neighbour.

    A scrap left at the end of the line belongs to the sentence before it --
    on its own it is a word like "upload", which says nothing and would make a
    useless retrieval query out of a sentence that had plenty to say.

    Pieces are held unstripped so that what is joined stays contiguous, and
    each sentence is stripped once, at the end.
    """

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
