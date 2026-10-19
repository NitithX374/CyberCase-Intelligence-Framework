from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RUNS = {"confirmation": "main_20261001_021428", "development": "main_20260930_193646"}
ARM = "cybercase_nogrammar"
SEED, RESAMPLES = 2026, 2000


def load(backend: str):
    sys.path.insert(0, backend)
    sys.path.insert(0, str(HERE))
    import app.trace.bind as bind
    from scores_common import lead, v0_words

    if not Path(bind.__file__).resolve().is_relative_to(Path(backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    return bind.located_quote, lead, v0_words


def mentioned(v0_words, text: str, fact: dict) -> bool:
    return f" {fact['text']} " in f" {v0_words(text)} "


def per_case(located_quote, lead, v0_words, case: dict, written: dict) -> dict:
    text = case["text"]
    checked, unchecked = [], []
    for claim in written["claims"]:
        quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        found = [q for q in quotes if located_quote(text, q) is not None]
        (checked if found else unchecked).append(" ".join([claim.get("text", ""), *found]))
    summary = written.get("summary", "")
    row = {"facts": 0, "summary": 0, "claims": 0, "checked": 0, "dropped": 0, "traceable": 0, "unchecked_only": 0,
           "untraceable": 0, "summary_words": len(summary.split())}
    for fact in lead(case):
        in_summary = mentioned(v0_words, summary, fact)
        in_checked = any(mentioned(v0_words, t, fact) for t in checked)
        in_unchecked = any(mentioned(v0_words, t, fact) for t in unchecked)
        row["facts"] += 1
        row["summary"] += in_summary
        row["claims"] += in_checked or in_unchecked
        row["checked"] += in_checked
        row["dropped"] += in_checked and not in_summary
        if in_summary:
            key = "traceable" if in_checked else "unchecked_only" if in_unchecked else "untraceable"
            row[key] += 1
    return row


def ratio(rows: list[dict], top: str, bottom: str) -> list:
    counts = np.array([[r[top], r[bottom]] for r in rows if r[bottom]], dtype=float)
    hits, total = int(counts[:, 0].sum()), int(counts[:, 1].sum())
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    return [hits, total, round(hits / total, 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4)]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    located_quote, lead, v0_words = load(args.backend)
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    report, md = {}, ["# Fact preservation into the summary (Q1-Q3)", "",
                      f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend "
                      f"`{args.backend}`. No model call.", "",
                      "| Split | Cases | Q1 summary coverage | claims coverage | Q2 dropped | Q3 traceable | "
                      "Q3 unchecked only | Q3 untraceable | mean summary words |", "|---|---|---|---|---|---|---|---|---|"]
    for split, run in RUNS.items():
        rows = []
        for path in sorted((HERE / "results" / f"raw_{run}").glob(f"*_{ARM}_1.json")):
            written = json.loads(path.read_text(encoding="utf-8")).get("written")
            if written:
                rows.append(per_case(located_quote, lead, v0_words, cases[path.name.split("_")[0]], written))
        cell = {"cases": len(rows), "Q1": ratio(rows, "summary", "facts"), "claims": ratio(rows, "claims", "facts"),
                "Q2": ratio(rows, "dropped", "checked"), "traceable": ratio(rows, "traceable", "summary"),
                "unchecked_only": ratio(rows, "unchecked_only", "summary"),
                "untraceable": ratio(rows, "untraceable", "summary"),
                "summary_words": round(sum(r["summary_words"] for r in rows) / len(rows), 1)}
        report[split] = cell
        shown = lambda c: f"{c[2]:.3f} [{c[3]:.3f}, {c[4]:.3f}] ({c[0]}/{c[1]})"
        md.append(f"| {split} | {cell['cases']} | {shown(cell['Q1'])} | {shown(cell['claims'])} | {shown(cell['Q2'])} | "
                  f"{shown(cell['traceable'])} | {shown(cell['unchecked_only'])} | {shown(cell['untraceable'])} | "
                  f"{cell['summary_words']} |")
    (HERE / "results" / "summary_preservation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "summary_preservation.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
