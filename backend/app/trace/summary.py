from __future__ import annotations

import re

from app.trace.claims import normalize_identifier

SUMMARY_CLAIM_IDS = re.compile(r"\[\s*(A-\d{2,}(?:\s*,\s*A-\d{2,})*)\s*\]")
UNIT_SEPARATORS = " \t\r\n.,;:!?…。、！？；：，．"
UNIT_PUNCTUATION = frozenset(".,;:!?…。、！？；：，．")


def scan_summary(summary: str) -> list[tuple[str, list[str], str]]:
    pieces: list[tuple[str, list[str], str]] = []
    start = 0
    for match in SUMMARY_CLAIM_IDS.finditer(summary):
        gap = summary[start : match.start()]
        text = gap.lstrip(UNIT_SEPARATORS) if start else gap.lstrip()
        if pieces and start:
            pieces[-1] = (*pieces[-1][:2], punctuation(gap[: len(gap) - len(text)]))
        text = text.rstrip()
        start = match.end()
        claim_ids = written_ids(match.group(1))
        if text:
            pieces.append((text, claim_ids, ""))
        elif pieces:
            previous_text, previous_ids, _ = pieces[-1]
            merged = list(dict.fromkeys([*previous_ids, *claim_ids]))
            pieces[-1] = (previous_text, merged, "")
    if not start:
        tail = summary.strip()
    else:
        rest = summary[start:]
        tail = rest.lstrip(UNIT_SEPARATORS)
        if pieces:
            pieces[-1] = (*pieces[-1][:2], punctuation(rest[: len(rest) - len(tail)]))
        tail = tail.rstrip()
    if tail:
        pieces.append((tail, [], ""))
    return pieces


def summary_pieces(summary: str) -> list[tuple[str, list[str]]]:
    return [(text, claim_ids) for text, claim_ids, _ in scan_summary(summary)]


def summary_closings(summary: str) -> list[str]:
    return [closing for _, _, closing in scan_summary(summary)]


def punctuation(run: str) -> str:
    return "".join(character for character in run if character in UNIT_PUNCTUATION)


def written_ids(bracket: str) -> list[str]:
    ids = [normalize_identifier(part.strip(), "A", "A|claim|c") for part in bracket.split(",")]
    return list(dict.fromkeys(str(claim_id) for claim_id in ids))


__all__ = ["SUMMARY_CLAIM_IDS", "scan_summary", "summary_closings", "summary_pieces"]
