from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


_NO_SPACE_BEFORE = frozenset(",.;:!?%)]}")
_NO_SPACE_AFTER = frozenset("([{\\")


@dataclass(frozen=True)
class NormalizedText:
    text: str
    source_ranges: tuple[tuple[int, int], ...]


def _unicode_items(value: str) -> list[tuple[str, int, int]]:
    items: list[tuple[str, int, int]] = []
    for index, character in enumerate(value):
        normalized = unicodedata.normalize("NFKC", character)
        items.extend((item, index, index + 1) for item in normalized)
    return items


def normalize_with_mapping(value: str) -> NormalizedText:
    items = _unicode_items(value)
    while items and items[0][0].isspace():
        items.pop(0)
    while items and items[-1][0].isspace():
        items.pop()

    compacted: list[tuple[str, int, int]] = []
    whitespace_pending = False
    for item in items:
        if item[0].isspace():
            whitespace_pending = True
            continue
        if whitespace_pending and compacted:
            compacted.append((" ", compacted[-1][2], item[1]))
        compacted.append(item)
        whitespace_pending = False

    normalized: list[tuple[str, int, int]] = []
    for item in compacted:
        character = item[0]
        if character in _NO_SPACE_BEFORE and normalized and normalized[-1][0] == " ":
            normalized.pop()
        if character == " " and normalized and normalized[-1][0] in _NO_SPACE_AFTER:
            continue
        normalized.append(item)

    return NormalizedText(
        text="".join(item[0] for item in normalized),
        source_ranges=tuple((item[1], item[2]) for item in normalized),
    )


def normalize_text(value: str) -> str:
    return normalize_with_mapping(value).text


def diagnostic_punctuation_text(value: str) -> str:
    normalized = normalize_text(value)
    without_punctuation = re.sub(r"[^\w\s]", "", normalized, flags=re.UNICODE)
    return re.sub(r"\s+", " ", without_punctuation).strip()


def diagnostic_quote_text(value: str) -> str:
    normalized = normalize_text(value)
    return normalized.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))
