"""Scores, binder part: the binder sensitivity and audit of section 5.4.2.

The binder is the pinned one (pinned/1e29bd3), imported, not rewritten.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

from scores_common import HERE, quotes_of, row, v0_words

sys.path.insert(0, str(HERE / "pinned" / "1e29bd3" / "backend"))

from app.trace.quotes import (  # noqa: E402
    MAX_QUOTE_CHARS,
    expand_unique_ellipsis_quote,
    find_aligned_quote,
    find_folded_quote,
    quote_occurrences,
    without_edge_ellipses,
)

# ================================================================================================= RULES

ELLIPSIS = re.compile(r"(?:\.{3,}|…+)")
MIDDLE_ELLIPSIS = re.compile(r"\S\s*(?:\.{3,}|…+)\s*\S")


def stitched(text: str, written: dict) -> set[str]:
    """Spans the binder kept only by expanding a middle ellipsis over source text the model left out."""
    out = set()
    for quote in (without_edge_ellipses(q) for claim in written["claims"] for q in quotes_of(claim)):
        if MIDDLE_ELLIPSIS.search(quote) and not quote_occurrences(text, quote) and not find_folded_quote(text, quote):
            if (expanded := expand_unique_ellipsis_quote(text, quote)) is not None:
                out.add(expanded)
    return out


def in_order(source: list[str], pieces: list[list[str]]) -> bool:
    """Each piece's words occur as a run in the source, the pieces one after another."""
    at = 0
    for piece in pieces:
        hit = next((i for i in range(at, len(source) - len(piece) + 1) if source[i:i + len(piece)] == piece), None)
        if hit is None:
            return False
        at = hit + len(piece)
    return True


def dropped_because(text: str, quote: str) -> str | None:
    """None when the pinned binder keeps a written quote; otherwise why it dropped it (the audit's three piles)."""
    quote = without_edge_ellipses(quote)
    found = quote if quote_occurrences(text, quote) else find_aligned_quote(text, quote)
    if found is not None:
        return None if len(found) <= MAX_QUOTE_CHARS else "longer than the limit"
    pieces = [v0_words(piece).split() for piece in ELLIPSIS.split(quote)]
    kept_in_order = in_order(v0_words(text).split(), [p for p in pieces if p])
    return "every word kept, in order" if kept_in_order else "words changed"


# ================================================================================================= DATA


def binder(views: dict) -> None:
    views = views["two calls"]
    piles, by_case = Counter(), Counter()
    for c, v in views.items():
        if v["done"]:
            for claim in v["written"]["claims"]:
                for quote in quotes_of(claim):
                    if why := dropped_because(v["case"]["text"], quote):
                        piles[why] += 1
                        by_case[c] += why == "every word kept, in order"
    row("5.4.2 binder", "quotes the binder dropped, cases 51-150", sum(piles.values()), "22")
    row("5.4.2 binder", "of them, every word kept in order", piles["every word kept, in order"], "19")
    row("5.4.2 binder", "of those, in case 1271", by_case["1271"], "14")
    trace, written = views["1271"]["trace"], {c["claim_id"]: c for c in views["1271"]["written"]["claims"]}
    demoted = [c["claim_id"] for c in trace["claims"] if c["epistemic_status"] == "not_confirmed"]
    wrapped = [cid for cid in demoted if all(q.strip().startswith(('"', "“")) for q in quotes_of(written[cid]))]
    row("5.4.2 binder", "1271: claims demoted (every quote wrapped in quotation marks)",
        f"{len(demoted)} ({len(wrapped)})",
        "14 (14)")
    case = views["10086"]
    [quote] = [q for c in case["written"]["claims"] if c["claim_id"] == "A-05" for q in quotes_of(c)
               if MIDDLE_ELLIPSIS.search(without_edge_ellipses(q))]
    kept = expand_unique_ellipsis_quote(case["case"]["text"], without_edge_ellipses(quote))
    row("5.4.2 binder", "10086 A-05: characters written, characters kept", f"{len(quote)} -> {len(kept)}", "207 -> 719")
