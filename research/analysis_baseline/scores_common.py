"""Scores, shared part: what every part of book_scores uses.

Rules: a case's main-event facts, shares, quote positions and the V0 word normalisation. Data: the paths, the case
file, the one bootstrap, the paired differences, number formatting, and the rows that set each number beside the value
the book prints.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import numpy as np

# ================================================================================================= RULES


def lead(case: dict) -> list[dict]:
    """The main-event gold facts of a case (CASIE's annotators, selected by cases.py)."""
    return [fact for fact in case["gold"] if fact["lead"]]


def share(flags) -> float:
    """The share of true values."""
    flags = list(flags)
    return sum(flags) / len(flags)


def positions(text: str, quote: str) -> list[tuple[int, int]]:
    """Every (start, end) at which the quote occurs in the text."""
    found, start = [], text.find(quote)
    while start >= 0:
        found.append((start, start + len(quote)))
        start = text.find(quote, start + 1)
    return found


def quotes_of(claim: dict) -> list[str]:
    """The quotes of one claim, supporting and contradicting."""
    return [citation["exact_quote"] for citation in claim["supporting_citations"] + claim["contradicting_citations"]]


def v0_words(text: str) -> str:
    """The frozen V0 normalisation: NFKC, lower case, letters and digits only, single spaces."""
    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


# ================================================================================================= DATA

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MINUS = "\u2212"
ROWS: list[dict] = []


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


CASES = {case["id"]: case for case in jsonl(HERE / "data" / "cases.jsonl")}


def bootstrap(n: int, statistic) -> tuple[float, float]:
    """The one interval routine: 95% percentile interval over 2,000 resamples of n paired units, default_rng(2026)."""
    rng = np.random.default_rng(2026)
    draws = [statistic(rng.integers(0, n, n)) for _ in range(2000)]
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def mean_difference(a: dict[str, float], b: dict[str, float], cases: list[str]) -> tuple[float, float, float]:
    """b − a of per-case values over the cases, resampled by case."""
    d = np.array([b[c] - a[c] for c in cases])
    return (float(d.mean()), *bootstrap(len(d), lambda i: d[i].mean()))


def pooled_difference(a: dict, b: dict, cases: list[str]) -> tuple[float, float, float]:
    """b − a of a ratio pooled over the cases (numerator, denominator per case), recomputed in each resample."""
    na, da, nb, db = (np.array([side[c][k] for c in cases]) for side, k in ((a, 0), (a, 1), (b, 0), (b, 1)))
    statistic = lambda i: nb[i].sum() / db[i].sum() - na[i].sum() / da[i].sum()  # noqa: E731
    return (float(statistic(np.arange(len(cases)))), *bootstrap(len(cases), statistic))


def average(values: dict[str, float]) -> float:
    return float(np.mean(list(values.values())))


def pooled(counts: dict[str, tuple[int, int]]) -> tuple[int, int]:
    return sum(n for n, _ in counts.values()), sum(d for _, d in counts.values())


def signed(x: float) -> str:
    return f"{x:+.3f}".replace("-", MINUS)


def frac(n: int, d: int, with_share: bool = True) -> str:
    return f"{n:,}/{d:,} = {n / d:.3f}" if with_share else f"{n:,}/{d:,}"


def row(table: str, item: str, ours: object, book: str, agrees: bool | None = None) -> None:
    """One book number: equal when the strings are equal, or when `agrees` says so for a number the book words."""
    ROWS.append({"table": table, "item": item, "book": book, "ours": str(ours),
                 "verdict": "yes" if (str(ours) == book if agrees is None else agrees) else "NO"})


def interval_row(table: str, item: str, result: tuple[float, float, float], book: str) -> None:
    """One book difference: the point must be equal; the interval may move; a verdict that flips stops the run."""
    point, low, high = result
    b_point, b_low, b_high = (float(x.replace(MINUS, "-")) for x in re.findall(rf"[+{MINUS}]\d\.\d{{3}}", book))
    moved = round(max(abs(round(low, 3) - b_low), abs(round(high, 3) - b_high)), 3)
    flipped = (low > 0 or high < 0) != (b_low > 0 or b_high < 0)
    verdict = ("VERDICT FLIPPED" if flipped else "NO" if signed(point) != signed(b_point) else "yes" if moved == 0
               else f"point equal, interval moved {moved:.3f}")
    ROWS.append({"table": table, "item": item, "book": book, "ours": f"{signed(point)} [{signed(low)}, {signed(high)}]",
                 "verdict": verdict, "moved": moved, "flipped": flipped})
