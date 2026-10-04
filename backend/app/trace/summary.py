from __future__ import annotations

import re

from app.trace.claims import normalize_identifier

SUMMARY_CLAIM_IDS = re.compile(r"\[\s*(A-\d{2,}(?:\s*,\s*A-\d{2,})*)\s*\]")
UNIT_SEPARATORS = " \t\r\n.,;:!?…。、！？；：，．"


def summary_pieces(summary: str) -> list[tuple[str, list[str]]]:
    pieces: list[tuple[str, list[str]]] = []
    start = 0
    for match in SUMMARY_CLAIM_IDS.finditer(summary):
        text = summary[start : match.start()]
        text = (text.lstrip(UNIT_SEPARATORS) if start else text.lstrip()).rstrip()
        start = match.end()
        claim_ids = written_ids(match.group(1))
        if text:
            pieces.append((text, claim_ids))
        elif pieces:
            previous_text, previous_ids = pieces[-1]
            pieces[-1] = (previous_text, list(dict.fromkeys([*previous_ids, *claim_ids])))
    tail = summary[start:].lstrip(UNIT_SEPARATORS).rstrip() if start else summary.strip()
    if tail:
        pieces.append((tail, []))
    return pieces


def written_ids(bracket: str) -> list[str]:
    ids = [normalize_identifier(part.strip(), "A", "A|claim|c") for part in bracket.split(",")]
    return list(dict.fromkeys(str(claim_id) for claim_id in ids))


__all__ = ["SUMMARY_CLAIM_IDS", "summary_pieces"]
