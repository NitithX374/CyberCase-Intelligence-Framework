"""The traceability framing of README.md (M1-M7), read from saved runs. No model is called.

  python traceability.py

Writes results/traceability.json and results/traceability.md.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "pinned" / "1e29bd3" / "backend"))

from app.trace.quotes import (  # noqa: E402
    expand_unique_ellipsis_quote,
    find_folded_quote,
    quote_occurrences,
    without_edge_ellipses,
)

SEED, DRAWS, CAP = 2026, 2000, 40_800
CASES = {r["id"]: r for r in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
MID_ELLIPSIS = re.compile(r"\S\s*(?:\.{3,}|…+)\s*\S")
DESIGN = ("main_20260930_020141", "single", "main_20260930_020141", "cybercase")
DECODING = ("main_20260930_062138", "cybercase", "main_20260930_193646", "cybercase_nogrammar")


def records(run: str, arm: str) -> dict[str, dict]:
    rows = [json.loads(line) for line in (HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines()]
    return {r["case"]: r for r in rows if r["arm"] == arm and r.get("run", 1) == 1
            and r.get("error_kind") not in ("budget", "harness")}


def saved(run: str, arm: str, case: str) -> dict:
    return json.loads((HERE / "results" / f"raw_{run}" / f"{case}_{arm}_1.json").read_text(encoding="utf-8"))


def stitched(text: str, written: dict | None) -> set[str]:
    if written is None:
        return set()
    out = set()
    for claim in written["claims"]:
        for citation in claim["supporting_citations"] + claim["contradicting_citations"]:
            quote = without_edge_ellipses(citation["exact_quote"])
            if not MID_ELLIPSIS.search(quote) or quote_occurrences(text, quote) or find_folded_quote(text, quote):
                continue
            expanded = expand_unique_ellipsis_quote(text, quote)
            if expanded is not None:
                out.add(expanded)
    return out


def case_view(run: str, arm: str, record: dict) -> dict:
    case = CASES[record["case"]]
    lead = [f for f in case["gold"] if f["lead"]]
    if "error" in record:
        return {"done": False, "m4": 0.0, "m4_unstitched": 0.0, "m5": 0.0, "lead": len(lead)}
    data = saved(run, arm, record["case"])
    bound, text = data["bound"], case["text"]
    leaky = stitched(text, data.get("written"))
    statuses = Counter(c["epistemic_status"] for c in bound["claims"])
    quotes = [q["exact_quote"] for c in bound["claims"] for q in c["supporting_citations"] + c["contradicting_citations"]]

    def spans(keep) -> list[tuple[int, int]]:
        found = []
        for quote in quotes:
            if not keep(quote):
                continue
            start = text.find(quote)
            while start >= 0:
                found.append((start, start + len(quote)))
                start = text.find(quote, start + 1)
        return found

    def cited(found) -> list[dict]:
        return [f for f in lead if any(a < e and b > s for s, e in f["spans"] for a, b in found)]

    every, clean = cited(spans(lambda q: True)), cited(spans(lambda q: q not in leaky))
    grounding = record["grounding"] or {}
    return {
        "done": True,
        "lead": len(lead),
        "reported": statuses["reported"],
        "not_confirmed": statuses["not_confirmed"],
        "claims": len(bound["claims"]),
        "quotes_claimed": grounding.get("citations_claimed", 0),
        "quotes_verified": grounding.get("citations_verified", 0),
        "m4": len(every) / len(lead),
        "m4_unstitched": len(clean) / len(lead),
        "m4_matches_record": len(every) == len(record.get("grounded_lead", [])),
        "stitched_quotes": len(leaky),
        "m5": len(record["stated_lead"]) / record["gold_lead"],
    }


def arm_summary(run: str, arm: str) -> tuple[dict, dict[str, dict]]:
    recs = records(run, arm)
    views = {c: case_view(run, arm, r) for c, r in recs.items()}
    done = [v for v in views.values() if v["done"]]
    calls = [call for r in recs.values() for call in r.get("calls", [])]
    capped = sum(c.get("stop_reason") in ("max_tokens", "length") or (c.get("output_tokens") or 0) >= CAP for c in calls)
    reported = sum(v["reported"] for v in done)
    demoted = sum(v["not_confirmed"] for v in done)
    summary = {
        "run": run, "arm": arm, "cases": len(recs), "completed": len(done),
        "M1": {"n": reported, "of": reported + demoted, "rate": reported / max(1, reported + demoted)},
        "M2": {"n": sum(v["quotes_verified"] for v in done), "of": sum(v["quotes_claimed"] for v in done)},
        "M3": {"n": sum(v["not_confirmed"] == 0 for v in done), "of": len(done)},
        "M4": float(np.mean([v["m4"] for v in views.values()])),
        "M4_completed": float(np.mean([v["m4"] for v in done])),
        "M4_unstitched": float(np.mean([v["m4_unstitched"] for v in views.values()])),
        "stitched_quotes": sum(v.get("stitched_quotes", 0) for v in done),
        "M4_recount_matches_record": all(v.get("m4_matches_record", True) for v in done),
        "M5": float(np.mean([v["m5"] for v in views.values()])),
        "M7": {"failed": len(recs) - len(done), "calls_to_cap": capped,
               "median_model_seconds": float(np.median([sum(c.get("ms") or 0 for c in r.get("calls", [])) / 1000
                                                        for r in recs.values()])),
               "usd_per_case": sum(c["usd"] for c in calls) / max(1, len(recs))},
        "claims": sum(v["claims"] for v in done),
    }
    summary["M2"]["rate"] = summary["M2"]["n"] / max(1, summary["M2"]["of"])
    return summary, views


def interval(values: list[float]) -> list[float]:
    return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]


def compare(a: dict[str, dict], b: dict[str, dict]) -> dict:
    ids = sorted(set(a) & set(b))
    both = [c for c in ids if a[c]["done"] and b[c]["done"]]
    rng = np.random.default_rng(SEED)

    def pooled(views, sample, n, d):
        top = sum(views[c][n] for c in sample)
        bottom = sum(views[c][d] for c in sample)
        return top / bottom if bottom else float("nan")

    def m1(views, sample):
        top = sum(views[c]["reported"] for c in sample)
        return top / max(1, top + sum(views[c]["not_confirmed"] for c in sample))

    m4 = np.array([b[c]["m4"] - a[c]["m4"] for c in ids])
    m4_both = np.array([b[c]["m4"] - a[c]["m4"] for c in both])
    draws = {"M1": [], "M2": [], "M4": [], "M4_completed": []}
    for _ in range(DRAWS):
        pick = [both[i] for i in rng.integers(0, len(both), len(both))]
        draws["M1"].append(m1(b, pick) - m1(a, pick))
        draws["M2"].append(pooled(b, pick, "quotes_verified", "quotes_claimed")
                           - pooled(a, pick, "quotes_verified", "quotes_claimed"))
        draws["M4"].append(m4[rng.integers(0, len(m4), len(m4))].mean())
        draws["M4_completed"].append(m4_both[rng.integers(0, len(m4_both), len(m4_both))].mean())
    return {
        "paired_cases": len(ids), "completed_in_both": len(both),
        "M1": {"difference": m1(b, both) - m1(a, both), "ci": interval(draws["M1"])},
        "M2": {"difference": pooled(b, both, "quotes_verified", "quotes_claimed")
               - pooled(a, both, "quotes_verified", "quotes_claimed"), "ci": interval(draws["M2"])},
        "M4": {"difference": float(m4.mean()), "ci": interval(draws["M4"])},
        "M4_completed": {"difference": float(m4_both.mean()), "ci": interval(draws["M4_completed"])},
    }


def word(interval_: list[float]) -> str:
    return "difference" if interval_[0] > 0 or interval_[1] < 0 else "not shown"


def lines_for(s: dict) -> str:
    return (f"| {s['arm']} ({s['run']}) | {s['completed']}/{s['cases']} | {s['M1']['n']}/{s['M1']['of']} = "
            f"{s['M1']['rate']:.3f} | {s['M2']['n']}/{s['M2']['of']} = {s['M2']['rate']:.3f} | "
            f"{s['M3']['n']}/{s['M3']['of']} | {s['M4']:.3f} ({s['M4_completed']:.3f}) | {s['M4_unstitched']:.3f} | "
            f"{s['M5']:.3f} | {s['M7']['failed']} | {s['M7']['calls_to_cap']} | {s['M7']['median_model_seconds']:.0f} | "
            f"{s['M7']['usd_per_case']:.4f} |")


def main() -> None:
    prose = records(DESIGN[0], "prose")
    prose_m5 = float(np.mean([0.0 if "error" in r else len(r["stated_lead"]) / r["gold_lead"] for r in prose.values()]))
    out, md = {"design": {}, "decoding": {}}, ["# Traceability framing (M1-M7)", "",
                                               "Read from saved runs; no model was called. Fixed in README.md "
                                               "(2026-10-01) before the intervals were computed.", ""]
    header = ["| Arm (run) | Completed | M1 traceable reported claims | M2 verified quotes | M3 fully traceable cases | "
              "M4 cited coverage, failures 0 (completed only) | M4 without stitched quotes | M5 mention (V0) | "
              "Failed | Calls to cap | Median model s | USD per case |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, (run_a, arm_a, run_b, arm_b) in (("design", DESIGN), ("decoding", DECODING)):
        sa, va = arm_summary(run_a, arm_a)
        sb, vb = arm_summary(run_b, arm_b)
        cmp = compare(va, vb)
        out[name] = {"a": sa, "b": sb, "comparison": cmp}
        md += [f"## {name.capitalize()}: {arm_b} − {arm_a}", ""] + header + [lines_for(sa), lines_for(sb)]
        if name == "design":
            md.append(f"| prose ({DESIGN[0]}) | {len(prose)}/{len(prose)} | — | — | — | — | — | {prose_m5:.3f} | "
                      f"0 | — | — | — |")
        md += ["", f"Paired cases {cmp['paired_cases']}, completed in both {cmp['completed_in_both']}.", ""]
        for key, label in (("M1", "M1 (pooled, completed in both)"), ("M2", "M2 (pooled, completed in both)"),
                           ("M4", "M4 (failures 0)"), ("M4_completed", "M4 (completed in both)")):
            d = cmp[key]
            md.append(f"- {label}: {d['difference']:+.3f} [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}] -> {word(d['ci'])}.")
        md += [f"- M4 recount equals the stored per-case figure: {sa['M4_recount_matches_record'] and sb['M4_recount_matches_record']}.",
               f"- Stitched quotes removed for the sensitivity: {arm_a} {sa['stitched_quotes']}, {arm_b} {sb['stitched_quotes']}"
               + (" (single saved no written trace, so none can be identified)" if arm_a == "single" else "") + ".", ""]
    out["prose_M5"] = prose_m5
    (HERE / "results" / "traceability.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (HERE / "results" / "traceability.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
