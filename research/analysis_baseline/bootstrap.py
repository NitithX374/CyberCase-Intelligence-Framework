"""Case-level bootstrap intervals for a run.py run. Added after the main run; the frozen protocol names no interval.
Failed runs score 0, as the main-run decisions in README.md fix it.

  python bootstrap.py results/main_20260928_081639.jsonl
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARMS = ("prose", "cybercase", "single")
records = [json.loads(line) for line in (HERE / sys.argv[1]).read_text(encoding="utf-8").splitlines()]
by = {(r["case"], r["arm"]): r for r in records if r.get("error_kind") not in ("budget", "harness")}
ids = sorted(c for c in {r["case"] for r in records} if all((c, arm) in by for arm in ARMS))


def share(r: dict, field: str, gold: str) -> float:
    return 0.0 if "error" in r else len(r[field]) / r[gold]


def value(arm: str, metric: str, cases: list[str]) -> float:
    rows = [by[(c, arm)] for c in cases]
    if metric == "identifier_precision":
        done = [r for r in rows if "error" not in r]
        written = sum(r["identifiers"]["written"] for r in done)
        return sum(r["identifiers"]["supported"] for r in done) / written if written else np.nan
    field, gold = {"recall_lead": ("stated_lead", "gold_lead"), "recall_all": ("stated", "gold"),
                   "grounded_recall_lead": ("grounded_lead", "gold_lead"),
                   "grounded_recall_all": ("grounded", "gold")}[metric]
    return float(np.mean([share(r, field, gold) for r in rows]))


COMPARISONS = [
    ("recall_lead", "cybercase", "prose"), ("recall_lead", "cybercase", "single"), ("recall_lead", "single", "prose"),
    ("recall_all", "cybercase", "prose"), ("recall_all", "cybercase", "single"),
    ("grounded_recall_lead", "cybercase", "single"), ("grounded_recall_all", "cybercase", "single"),
    ("identifier_precision", "cybercase", "prose"), ("identifier_precision", "cybercase", "single"),
    ("identifier_precision", "single", "prose"),
]
rng = np.random.default_rng(2026)
samples = [list(rng.choice(ids, size=len(ids), replace=True)) for _ in range(2000)]
print(f"{len(ids)} cases with every arm")
for metric, a, b in COMPARISONS:
    point = value(a, metric, ids) - value(b, metric, ids)
    draws = np.array([value(a, metric, s) - value(b, metric, s) for s in samples])
    draws = draws[~np.isnan(draws)]
    print(f"{metric:22s} {a:9s} - {b:6s} {point:+.3f} [{np.percentile(draws, 2.5):+.3f}, {np.percentile(draws, 97.5):+.3f}]")

for arm in ARMS:
    rows = [by[(c, arm)] for c in ids]
    seconds = [sum(call["ms"] for call in r["calls"]) / 1000 for r in rows]
    retried = sum(max(Counter(call["stage"] for call in r["calls"]).values(), default=0) > 1 for r in rows)
    print(f"{arm:9s} model seconds per run: median {np.median(seconds):.0f}, p90 {np.percentile(seconds, 90):.0f}, "
          f"max {max(seconds):.0f}; runs with a retried stage {retried}; "
          f"failed {sum('error' in r for r in rows)}")
