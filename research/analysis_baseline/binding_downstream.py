from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
THAI_RUN = "20261001_223057"
ENGLISH = {"confirmation": "main_20261001_021428", "development": "main_20260930_193646"}
THAI_ARMS = {"development": ("clean",), "confirmation": ("targeted", "realistic")}
ARM = "cybercase_nogrammar"
TIERS = ("find_folded_quote", "unique_ellipsis_pieces", "find_relaxed_quote", "find_format_only_quote")
SEED, RESAMPLES = 2026, 2000


def binder(backend: str):
    sys.path.insert(0, backend)
    import app.trace.bind as bind
    import app.trace.quotes as quotes

    if not Path(bind.__file__).resolve().is_relative_to(Path(backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    return bind.located_quote, quotes


def checkers(located_quote, quotes) -> dict:
    from rapidfuzz import fuzz

    kept = {name: getattr(quotes, name) for name in TIERS}

    def exact_only(text: str, quote: str) -> bool:
        for name in TIERS:
            setattr(quotes, name, lambda *args: None)
        try:
            return located_quote(text, quote) is not None
        finally:
            for name, function in kept.items():
                setattr(quotes, name, function)

    def folded(text: str) -> str:
        return re.sub(r"\s+", " ", text.casefold()).strip()

    return {
        "exact only": exact_only,
        "production": lambda text, quote: located_quote(text, quote) is not None,
        "similarity >= 0.80": lambda text, quote: fuzz.partial_ratio(quote, text) / 100 >= 0.80,
        "similarity >= 0.98": lambda text, quote: fuzz.partial_ratio(quote, text) / 100 >= 0.98,
        "similarity, case-folded >= 0.98": lambda text, quote: fuzz.partial_ratio(folded(quote), folded(text)) / 100 >= 0.98,
    }


def readings() -> dict[str, list[tuple[str, str, dict]]]:
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    out: dict[str, list[tuple[str, str, dict]]] = {}
    for split, run in ENGLISH.items():
        for path in sorted((HERE / "results" / f"raw_{run}").glob(f"*_{ARM}_1.json")):
            written = json.loads(path.read_text(encoding="utf-8")).get("written")
            if written:
                case = path.name.split("_")[0]
                out.setdefault(f"English {split}", []).append((case, cases[case]["text"], written))
    articles = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            articles[record["id"]] = record
    for split, arms in THAI_ARMS.items():
        for arm in arms:
            for path in sorted((THAI / "results" / f"raw_{THAI_RUN}").glob(f"*_{arm}.json")):
                reading = json.loads(path.read_text(encoding="utf-8"))["reading"]
                if reading:
                    article = path.name.split("_")[0]
                    out.setdefault(f"Thai {split}", []).append((f"{arm}:{article}", articles[article][arm], reading))
    return out


def bound_claims(check, text: str, reading: dict) -> dict[str, str]:
    status = {}
    for claim in reading.get("claims", []):
        quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        located = any(check(text, q) for q in quotes)
        reported = claim.get("epistemic_status") == "reported"
        status[claim["claim_id"]] = "bound" if located else ("demoted" if reported else "other")
    return status


def leak(status: dict[str, str], reading: dict) -> Counter:
    groups: Counter = Counter()
    for kind in ("involved_parties", "timeline", "impacts"):
        for item in reading.get(kind, []):
            known = [status[i] for i in item.get("claim_ids", []) if i in status]
            if not known:
                group = "no known claim"
            elif all(s == "bound" for s in known):
                group = "all bound"
            elif "bound" in known:
                group = "mixed"
            elif all(s == "demoted" for s in known):
                group = "only demoted"
            else:
                group = "only other, none located"
            groups[f"{kind}: {group}"] += 1
            groups[f"all items: {group}"] += 1
            groups["all items"] += 1
    return groups


def bootstrap(pairs: list[tuple[int, int]]) -> list:
    counts = np.array(pairs, dtype=float)
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    hits, total = int(counts[:, 0].sum()), int(counts[:, 1].sum())
    return [hits, total, round(hits / total, 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4)]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    located_quote, quotes = binder(args.backend)
    checks = checkers(located_quote, quotes)
    data = readings()
    report: dict = {"M1/M3": {}, "leak": {}}
    md = ["# Binding and downstream status", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          "No model call.", "", "## M1 and M3 by checker", "",
          "| Data | Checker | M1 reported claims bound | Demoted | M3 cases fully bound |", "|---|---|---|---|---|"]
    for name, items in data.items():
        for label, check in checks.items():
            m1, m3 = [], []
            for _, text, reading in items:
                status = bound_claims(check, text, reading)
                reported = [s for s in status.values() if s != "other"]
                m1.append((sum(s == "bound" for s in reported), len(reported)))
                m3.append((int(all(s == "bound" for s in reported)), 1))
            a, b = bootstrap(m1), bootstrap(m3)
            report["M1/M3"][f"{name} | {label}"] = {"M1": a, "M3": b, "demoted": a[1] - a[0]}
            md.append(f"| {name} | {label} | {a[2]:.4f} [{a[3]:.4f}, {a[4]:.4f}] | {a[1] - a[0]} | "
                      f"{b[0]}/{b[1]} = {b[2]:.3f} [{b[3]:.3f}, {b[4]:.3f}] |")
    md += ["", "## Status leak, production checker", "",
           "| Data | Items | All bound | Mixed | Only demoted | Only other, none located | No known claim |",
           "|---|---|---|---|---|---|---|"]
    for name, items in data.items():
        total: Counter = Counter()
        for _, text, reading in items:
            total += leak(bound_claims(checks["production"], text, reading), reading)
        report["leak"][name] = dict(total)
        cells = [total[f"all items: {g}"] for g in ("all bound", "mixed", "only demoted", "only other, none located",
                                                    "no known claim")]
        md.append(f"| {name} | {total['all items']} | " + " | ".join(str(c) for c in cells) + " |")
    (HERE / "results" / "binding_downstream.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "binding_downstream.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
