"""Book scores: every number that chapters 5 and 6 of the thesis print, recounted from saved files.

  python book_scores.py          (on Windows, set PYTHONIOENCODING=utf-8 first: the output holds "−")

No model is called and nothing is trained. The rules live in files by responsibility, each with its rules first and
its data after:
  scores_common.py            what every part shares: loading, the one bootstrap, formatting, the rows
  scores_classifier.py        RQ1 and the datasets: Tables 5-1 to 5-3, 5-5 and 5-8 to 5-10
  scores_analysis.py          M1-M5, M4b, V0, V3 and M7, and every analysis arm scored case by case
  scores_analysis_checks.py   Tables 5-11, 5-12, 5-13, 5-15 and 5-16 and the comparisons of 5.4.2
  scores_binder.py            the binder sensitivity and audit, on the pinned binder
  scores_report.py            M6, report preservation: Table 5-14
This file runs them in the book's order and writes results/book_scores.md and results/book_scores.json. Every name the
parts define is reachable here as book_scores.<name>.
"""
from __future__ import annotations

import json
import re

import scores_analysis
from scores_analysis import (
    ARMS, DESIGN, FINAL, SHIPPED, TRACED, analysis, capped, citing, m1, m2, m3, m4, m4b, m5_std, m5_v0, mentions,
    model_seconds, normalize_answer, own_text, per_case, pointed_at, states, stating, unstitched, v3, v3_words,
)
from scores_analysis_checks import (
    comparisons, reliability, traceability_tables, worked_case,
)
from scores_binder import (
    MAX_QUOTE_CHARS, binder, dropped_because, expand_unique_ellipsis_quote, find_aligned_quote, find_folded_quote,
    in_order, quote_occurrences, stitched, without_edge_ellipses,
)
from scores_classifier import (
    CONFIGS, GATE, SEEDS, auroc, classifier, datasets, decisions, flag_every_f1, model_selection, prf,
)
from scores_common import (
    CASES, HERE, MINUS, ROOT, ROWS, average, bootstrap, frac, interval_row, jsonl, lead, mean_difference, pooled,
    pooled_difference, positions, quotes_of, row, share, signed, v0_words,
)
from scores_report import (
    RQ2, identical, kept_by_report, normalise, report_preservation, rows_by_claim, strings,
)

__all__ = [
    "ARMS", "CASES", "CONFIGS", "DESIGN", "FINAL", "GATE", "HERE", "MAX_QUOTE_CHARS", "MINUS", "ROOT", "ROWS",
    "RQ2", "SEEDS", "SHIPPED", "TRACED", "analysis", "arm", "auroc", "average", "binder", "bootstrap", "capped",
    "citing", "classifier", "comparisons", "datasets", "decisions", "dropped_because",
    "expand_unique_ellipsis_quote", "find_aligned_quote", "find_folded_quote", "flag_every_f1", "frac",
    "identical", "in_order", "interval_row", "jsonl", "kept_by_report", "lead", "m1", "m2", "m3", "m4", "m4b",
    "m5_std", "m5_v0", "mean_difference", "mentions", "model_seconds", "model_selection", "normalise",
    "normalize_answer", "own_text", "per_case", "pointed_at", "pooled", "pooled_difference", "positions", "prf",
    "quote_occurrences", "quotes_of", "reliability", "report_preservation", "row", "rows_by_claim", "share",
    "signed", "states", "stating", "stitched", "strings", "traceability_tables", "unstitched", "v0_words", "v3",
    "v3_words", "without_edge_ellipses", "worked_case",
]

ORDER = ["5-1", "5-2", "5-3", "5-5", "5.3.1", "5-8", "5-9", "5-10", "5-11", "5-12", "5.4.2 design", "5.4.2 prose",
         "5.4.2 binder", "5-13 decoding", "5-14", "5-15", "5-16", "6.1.2"]


def arm(label: str) -> dict[str, dict]:
    """The scored records of the arm with this label in ARMS, read here so that a script can add its own arm."""
    return scores_analysis.arm(*ARMS[label])


def write(classifier_cells: dict) -> None:
    md = ["# Book scores", "",
          "Every number chapters 5 and 6 print, recounted by `book_scores.py` from saved files. No model was called.",
          "Intervals: paired, 2,000 resamples, numpy default_rng(2026), 95% percentile, cases in id order.", ""]
    for table in sorted(dict.fromkeys(r["table"] for r in ROWS), key=ORDER.index):
        title = f"Table {table}" if re.match(r"\d-\d", table) else f"Section {table}"
        md += [f"## {title}", "", "| Item | Book | book_scores | Match |", "|---|---|---|---|"]
        md += [f"| {r['item']} | {r['book']} | {r['ours']} | {r['verdict']} |" for r in ROWS if r["table"] == table]
        md.append("")
    wrong = [r for r in ROWS if r["verdict"] == "NO"]
    moved = [r for r in ROWS if r.get("moved", 0) > 0.005]
    flipped = [r for r in ROWS if r.get("flipped")]
    def listed(rows: list[dict]) -> str:
        return "; ".join(f"{r['table']} {r['item']} (book {r['book']}, here {r['ours']})" for r in rows)

    md += ["## Reproduction check", "",
           f"- Numbers checked: {len(ROWS)}. Printed exactly as in the book: "
           f"{sum(r['ours'] == r['book'] for r in ROWS)}."
           f" Agreeing by the book's wording: {sum(r['verdict'] == 'yes' and r['ours'] != r['book'] for r in ROWS)}.",
           f"- Point estimates or counts that differ: {len(wrong)}" + (f": {listed(wrong)}" if wrong else "."),
           f"- Intervals that moved by more than 0.005: {len(moved)}" + (f": {listed(moved)}" if moved else "."),
           f"- Verdicts that flipped: {len(flipped)}" + (f": {listed(flipped)}" if flipped else "."), ""]
    (HERE / "results" / "book_scores.md").write_text("\n".join(md), encoding="utf-8")
    (HERE / "results" / "book_scores.json").write_text(json.dumps(
        {"rows": ROWS, "classifier_cells": {f"{t}|{r}": v for (t, r), v in classifier_cells.items()}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(md))
    if flipped:
        raise SystemExit("STOP: a verdict flipped; report it, do not adjust anything.")


def main() -> None:
    datasets()
    model_selection()
    cells = classifier()
    views, scores = analysis()
    traceability_tables(scores)
    comparisons(views, scores)
    reliability(scores)
    binder(views)
    report_preservation()
    worked_case(views)
    write(cells)


if __name__ == "__main__":
    main()
