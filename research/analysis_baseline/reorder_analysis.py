"""The reorder confirmation of README.md (cases 151-250 rerun), read from its saved run. No model is called.

  python reorder_analysis.py main_YYYYMMDD_HHMMSS
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

import robustness as rb

HERE = Path(__file__).resolve().parent
RUN = sys.argv[1]
RAW = HERE / "results" / f"raw_{RUN}"
ARMS = ("cybercase", "cybercase_reorder")
CAP = 40_800

records = [json.loads(line) for line in (HERE / "results" / f"{RUN}.jsonl").read_text(encoding="utf-8").splitlines()]
by = {(r["case"], r["arm"]): r for r in records}
ran = {key: r for key, r in by.items() if r.get("error_kind") not in ("budget", "harness")}
stopped = sorted(f"{c}/{a} ({r['error_kind']})" for (c, a), r in by.items() if r.get("error_kind") in ("budget", "harness"))
order = [c["id"] for c in rb.cases.values() if c["sample"] == "main"][150:250]
ids = [c for c in order if all((c, arm) in ran for arm in ARMS)]


def runaway(call: dict) -> bool:
    return (call.get("output_tokens") or 0) >= CAP or call.get("stop_reason") in ("max_tokens", "length")


def first_reading(record: dict | None) -> dict | None:
    if record is None:
        return None
    return next((c for c in record["calls"] if c["stage"] == "case_reading" and c.get("output_tokens") is not None), None)


def recall(arm: str) -> dict[str, float]:
    return {c: 0.0 if "error" in ran[(c, arm)] else len(ran[(c, arm)]["stated_lead"]) / ran[(c, arm)]["gold_lead"]
            for c in ids}


pairs = [c for c in order if first_reading(ran.get((c, "cybercase"))) and first_reading(ran.get((c, "cybercase_reorder")))]
table = Counter((runaway(first_reading(ran[(c, "cybercase")])), runaway(first_reading(ran[(c, "cybercase_reorder")])))
                for c in pairs)
b, c_ = table[(True, False)], table[(False, True)]
p = stats.binomtest(b, b + c_, 0.5).pvalue if b + c_ else 1.0
rng = np.random.default_rng(rb.SEED)
draws = [np.mean([runaway(first_reading(ran[(c, "cybercase")])) - runaway(first_reading(ran[(c, "cybercase_reorder")]))
                  for c in (pairs[i] for i in rng.integers(0, len(pairs), len(pairs)))]) for _ in range(2000)]
low, high = np.percentile(draws, [2.5, 97.5])
rate = {arm: sum(runaway(first_reading(ran[(c, arm)])) for c in pairs) / len(pairs) for arm in ARMS}
lines = [f"# Reorder confirmation, cases 151-250 rerun ({RUN})", "",
         f"Cases with both arms run: {len(ids)} of {len(order)}. Budget or harness stops: {', '.join(stopped) or 'none'}.", "",
         "## Primary", "",
         f"First reading attempt ran away: cybercase {rate['cybercase']:.2f}, cybercase_reorder {rate['cybercase_reorder']:.2f} "
         f"on {len(pairs)} paired cases. Only cybercase {b}, only reorder {c_}, both {table[(True, True)]}, neither "
         f"{table[(False, False)]}. Risk difference {rate['cybercase'] - rate['cybercase_reorder']:+.2f} [{low:+.2f}, {high:+.2f}]. "
         f"Exact McNemar p = {p:.4g}.", "", "## Descriptive", "",
         "| Arm | Completed | Failures | Runaway attempts / reading calls | USD | USD per case | Model s median |",
         "|---|---|---|---|---|---|---|"]
report = {"run": RUN, "pairs": len(pairs), "only_cybercase": b, "only_reorder": c_, "both": table[(True, True)],
          "neither": table[(False, False)], "rates": rate, "risk_difference_ci": [float(low), float(high)], "mcnemar_p": p}
for arm in ARMS:
    rows = [ran[(c, arm)] for c in ids]
    calls = [call for r in rows for call in r["calls"]]
    reading = [call for call in calls if call["stage"] == "case_reading"]
    fails = Counter(r["error"] for r in rows if "error" in r)
    usd = sum(call["usd"] for call in calls)
    seconds = [sum(call["ms"] for call in r["calls"]) / 1000 for r in rows]
    lines.append(f"| {arm} | {sum('error' not in r for r in rows)} | {dict(fails) or '—'} | "
                 f"{sum(runaway(x) for x in reading)}/{len(reading)} | {usd:.4f} | {usd / max(1, len(rows)):.5f} | "
                 f"{np.median(seconds):.0f} |")
    report[f"failures_{arm}"] = sum(fails.values())
fa, fb = report["failures_cybercase"], report["failures_cybercase_reorder"]
lines.append(f"\n- failures: Fisher exact p = {stats.fisher_exact([[fa, len(ids) - fa], [fb, len(ids) - fb]])[1]:.4g}")
rec = {arm: recall(arm) for arm in ARMS}
d = {c: rec["cybercase_reorder"][c] - rec["cybercase"][c] for c in ids}
lines.append(f"- mention recall, main event, failures 0: cybercase {np.mean(list(rec['cybercase'].values())):.3f}, reorder "
             f"{np.mean(list(rec['cybercase_reorder'].values())):.3f}; reorder − cybercase {rb.fmt(*rb.bootstrap(d, ids))}")
done = [c for c in ids if "error" not in ran[(c, "cybercase")] and "error" not in ran[(c, "cybercase_reorder")]]
lines.append(f"- completed only ({len(done)} cases): reorder − cybercase {rb.fmt(*rb.bootstrap({c: d[c] for c in done}, done))}")
for arm in ARMS:
    traces = {c: json.loads((RAW / f"{c}_{arm}_1.json").read_text(encoding="utf-8"))["bound"] for c in done}
    claims = np.mean([len(t["claims"]) for t in traces.values()])
    quotes = np.mean([sum(len(x["supporting_citations"]) + len(x["contradicting_citations"]) for x in t["claims"])
                      for t in traces.values()])
    summaries = np.mean([sum(bool(x.get("reasoning_summary")) for x in t["claims"]) / max(1, len(t["claims"]))
                         for t in traces.values()])
    lines.append(f"- {arm}: claims {claims:.1f}, quotes {quotes:.1f}, share of claims with a reasoning summary {summaries:.2f}"
                 f" (per completed case)")
gen_arm = {c["generation_id"]: r["arm"] for r in records for c in r["calls"] if c.get("generation_id")}
where = Counter()
for f in RAW.glob("max_tokens_*.txt"):
    gid = re.sub(r"^(case_reading|case_direct|case_judgement)_", "", f.name[len("max_tokens_"):]).rsplit(".txt", 1)[0]
    before = f.read_text(encoding="utf-8").split("--- before the trailing whitespace")[-1]
    keys = re.findall(r'"([a-z_]+)"\s*:', before)
    claim = re.findall(r'"claim_id":\s*"A-(\d+)"', before)
    where[(gen_arm.get(gid, "?"), keys[-1] if keys else "?", claim[-1] if claim else "?")] += 1
lines.append("- where runaways began (arm, last key, claim): " + "; ".join(f"{k} {n}" for k, n in where.most_common()))
provider = Counter()
for arm in ARMS:
    for c in pairs:
        call = first_reading(ran[(c, arm)])
        provider[(arm, call.get("provider") or "?", runaway(call))] += 1
lines.append("- first reading attempt by provider (arm, provider, ran away): "
             + "; ".join(f"{k[0]} {k[1]} {'yes' if k[2] else 'no'} {n}" for k, n in sorted(provider.items())))
(HERE / "results" / f"{RUN}_reorder.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
(HERE / "results" / f"{RUN}_reorder.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
