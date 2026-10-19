"""The schema-fix test of README.md (cases 151-250), read from its saved run. No model is called.

  python slimfix_analysis.py main_YYYYMMDD_HHMMSS [--sample main|pilot]
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

import robustness as rb

HERE = Path(__file__).resolve().parent
RUN = sys.argv[1]
SAMPLE = sys.argv[sys.argv.index("--sample") + 1] if "--sample" in sys.argv else "main"
RAW = HERE / "results" / f"raw_{RUN}"
ARMS = ("single", "cybercase", "cybercase_slim")
TRACED = ARMS
CAP = 40_800
DESCRIPTIVE = (("cybercase_slim", "cybercase"), ("cybercase", "single"))
PREVIOUSLY_USED = {"1917", "1811"}

records = [json.loads(line) for line in (HERE / "results" / f"{RUN}.jsonl").read_text(encoding="utf-8").splitlines()]
by = {(r["case"], r["arm"]): r for r in records}
ran = {key: r for key, r in by.items() if r.get("error_kind") not in ("budget", "harness")}
stopped = sorted(f"{c}/{a} ({r['error_kind']})" for (c, a), r in by.items() if r.get("error_kind") in ("budget", "harness"))
main_rows = [c["id"] for c in rb.cases.values() if c["sample"] == SAMPLE]
order = main_rows[150:250] if SAMPLE == "main" else main_rows
ids = [c for c in order if all((c, arm) in ran for arm in ARMS)]


def runaway(call: dict) -> bool:
    return (call.get("output_tokens") or 0) >= CAP or call.get("stop_reason") in ("max_tokens", "length")


def first_reading(record: dict | None) -> dict | None:
    if record is None:
        return None
    return next((c for c in record["calls"] if c["stage"] == "case_reading" and c.get("output_tokens") is not None), None)


def bound(case_id: str, arm: str) -> dict | None:
    if "error" in ran[(case_id, arm)]:
        return None
    return json.loads((RAW / f"{case_id}_{arm}_1.json").read_text(encoding="utf-8"))["bound"]


for c in ids:
    for arm in ARMS:
        trace = bound(c, arm)
        rb.TEXTS[(c, arm)] = rb.own_text(trace) if trace is not None else None


def share(r: dict, field: str, gold: str) -> float:
    return 0.0 if "error" in r else len(r[field]) / r[gold]


def per_case(arm: str, subset: list[str], field: str = "stated_lead", gold: str = "gold_lead") -> dict[str, float]:
    return {c: share(ran[(c, arm)], field, gold) for c in subset}


def sign_flip(d: np.ndarray) -> float:
    rng = np.random.default_rng(rb.SEED)
    flips = rng.choice([-1.0, 1.0], size=(10000, len(d)))
    return (1 + int((np.abs((flips * d).mean(axis=1)) >= abs(d.mean())).sum())) / 10001


def paired_bootstrap(values: dict[str, float], subset: list[str]) -> tuple[float, float, float]:
    return rb.bootstrap(values, subset)


lines = [f"# Schema-fix test, cases 151-250 ({RUN})", "",
         f"Cases with all three arms run: {len(ids)} of {len(order)}. Budget or harness stops: {', '.join(stopped) or 'none'}.",
         ""]
report: dict = {"run": RUN, "cases": len(ids), "stopped": stopped}

pairs = [c for c in order if first_reading(ran.get((c, "cybercase"))) and first_reading(ran.get((c, "cybercase_slim")))]
excluded = [c for c in order if c not in pairs]
table = Counter((runaway(first_reading(ran[(c, "cybercase")])), runaway(first_reading(ran[(c, "cybercase_slim")])))
                for c in pairs)
b, c_ = table[(True, False)], table[(False, True)]
p_mech = stats.binomtest(b, b + c_, 0.5).pvalue if b + c_ else 1.0
rate_old = sum(runaway(first_reading(ran[(c, "cybercase")])) for c in pairs) / len(pairs) if pairs else float("nan")
rate_new = sum(runaway(first_reading(ran[(c, "cybercase_slim")])) for c in pairs) / len(pairs) if pairs else float("nan")
rng = np.random.default_rng(rb.SEED)
diffs = []
for _ in range(2000):
    draw = [pairs[i] for i in rng.integers(0, len(pairs), len(pairs))]
    diffs.append(np.mean([runaway(first_reading(ran[(c, "cybercase")])) - runaway(first_reading(ran[(c, "cybercase_slim")]))
                          for c in draw]))
rd_low, rd_high = np.percentile(diffs, [2.5, 97.5]) if pairs else (float("nan"), float("nan"))

recall = {arm: per_case(arm, ids) for arm in ARMS}
d_claim = {c: recall["cybercase_slim"][c] - recall["single"][c] for c in ids}
point, low, high = paired_bootstrap(d_claim, ids)
p_claim = sign_flip(np.array([d_claim[c] for c in ids]))
holm_sorted = sorted((("mechanism", p_mech), ("claim", p_claim)), key=lambda kv: kv[1])
holm, running = {}, 0.0
for rank, (name, p) in enumerate(holm_sorted):
    running = max(running, min(1.0, p * (2 - rank)))
    holm[name] = running
report["mechanism"] = {"pairs": len(pairs), "excluded": excluded, "only_cybercase": b, "only_slim": c_,
                       "both": table[(True, True)], "neither": table[(False, False)], "rate_cybercase": rate_old,
                       "rate_slim": rate_new, "risk_difference_ci": [float(rd_low), float(rd_high)],
                       "mcnemar_p": p_mech, "holm_p": holm["mechanism"]}
report["claim"] = {"diff": point, "ci": [low, high], "sign_flip_p": p_claim, "holm_p": holm["claim"]}
lines += ["## Confirmatory (Holm across the two)", "",
          f"1. First reading attempt ran away: cybercase {rate_old:.2f}, cybercase_slim {rate_new:.2f} on {len(pairs)} paired "
          f"cases (excluded: {', '.join(excluded) or 'none'}). Only cybercase {b}, only slim {c_}, both {table[(True, True)]}, "
          f"neither {table[(False, False)]}. Risk difference {rate_old - rate_new:+.2f} [{rd_low:+.2f}, {rd_high:+.2f}]. "
          f"Exact McNemar p = {p_mech:.4g}, Holm p = {holm['mechanism']:.4g}.",
          f"2. Mention recall, main event, failures 0: cybercase_slim − single {rb.fmt(point, low, high)}, sign-flip "
          f"p = {p_claim:.4g}, Holm p = {holm['claim']:.4g}.", "",
          "## Arms", "", "| Arm | Completed | Failures | Recall | Runaway attempts / reading or single calls | Calls | USD | USD per case | Model s median |",
          "|---|---|---|---|---|---|---|---|---|"]
for arm in ARMS:
    rows = [ran[(c, arm)] for c in ids]
    calls = [call for r in rows for call in r["calls"]]
    heavy = [call for call in calls if call["stage"] in ("case_reading", "case_direct")]
    fails = Counter(r["error"] for r in rows if "error" in r)
    seconds = [sum(call["ms"] for call in r["calls"]) / 1000 for r in rows]
    usd = sum(call["usd"] for call in calls)
    lines.append(f"| {arm} | {sum('error' not in r for r in rows)} | {dict(fails) or '—'} | "
                 f"{np.mean(list(recall[arm].values())):.3f} | {sum(runaway(x) for x in heavy)}/{len(heavy)} | {len(calls)} | "
                 f"{usd:.4f} | {usd / max(1, len(rows)):.5f} | {np.median(seconds):.0f} |")
    report[f"arm_{arm}"] = {"failures": dict(fails), "usd": usd, "runaways": sum(runaway(x) for x in heavy),
                            "heavy_calls": len(heavy)}

lines += ["", "## Descriptive", ""]
for a, b2 in DESCRIPTIVE:
    lines.append(f"- {a} − {b2}, mention recall: {rb.fmt(*paired_bootstrap({c: recall[a][c] - recall[b2][c] for c in ids}, ids))}")
both = {arm: [c for c in ids if "error" not in ran[(c, arm)]] for arm in ARMS}
for a, b2 in (("cybercase_slim", "single"), *DESCRIPTIVE):
    subset = [c for c in ids if c in both[a] and c in both[b2]]
    lines.append(f"- completed only, {a} − {b2} ({len(subset)} cases): "
                 f"{rb.fmt(*paired_bootstrap({c: recall[a][c] - recall[b2][c] for c in subset}, subset))}")
    n_words = {c: min(len(rb.TEXTS[(c, a)].split()), len(rb.TEXTS[(c, b2)].split())) for c in subset}
    cut = {c: rb.recall(c, a, "V0", True, text=" ".join(rb.TEXTS[(c, a)].split()[:n_words[c]]))
           - rb.recall(c, b2, "V0", True, text=" ".join(rb.TEXTS[(c, b2)].split()[:n_words[c]])) for c in subset}
    lines.append(f"- matched length, {a} − {b2}: {rb.fmt(*paired_bootstrap(cut, subset))}")
for variant in ("V1", "V3", "V6"):
    values = {arm: {c: rb.recall(c, arm, variant, True) for c in ids} for arm in ARMS}
    lines.append(f"- {variant}, cybercase_slim − single: "
                 f"{rb.fmt(*paired_bootstrap({c: values['cybercase_slim'][c] - values['single'][c] for c in ids}, ids))}")
sensitivity = [c for c in ids if c not in PREVIOUSLY_USED]
lines.append(f"- without the two previously used cases ({len(sensitivity)} cases), cybercase_slim − single: "
             f"{rb.fmt(*paired_bootstrap({c: d_claim[c] for c in sensitivity}, sensitivity))}")
counts = {}
for arm in ("cybercase", "cybercase_slim"):
    traces = {c: bound(c, arm) for c in both[arm]}
    counts[arm] = {c: (len(t["claims"]), sum(len(x["supporting_citations"]) + len(x["contradicting_citations"])
                                              for x in t["claims"])) for c, t in traces.items()}
common = [c for c in counts["cybercase"] if c in counts["cybercase_slim"]]
for index, label in ((0, "claims"), (1, "quotes")):
    old = np.mean([counts["cybercase"][c][index] for c in common]) if common else float("nan")
    new = np.mean([counts["cybercase_slim"][c][index] for c in common]) if common else float("nan")
    ci = paired_bootstrap({c: counts["cybercase_slim"][c][index] - counts["cybercase"][c][index] for c in common}, common)
    caveat = new < 0.9 * old and ci[2] < 0
    report[f"{label}_per_case"] = {"cybercase": old, "cybercase_slim": new, "diff_ci": list(ci), "caveat": bool(caveat)}
    lines.append(f"- {label} per completed case: cybercase {old:.1f}, slim {new:.1f}, slim − cybercase {rb.fmt(*ci)}"
                 f"{' — caveat applies (more than 10% fewer and CI below 0)' if caveat else ''}")
for arm in TRACED:
    done = [ran[(c, arm)] for c in ids if "error" not in ran[(c, arm)]]
    claimed = sum((r.get("grounding") or {}).get("citations_claimed", 0) for r in done)
    verified = sum((r.get("grounding") or {}).get("citations_verified", 0) for r in done)
    written = sum(r["identifiers"]["written"] for r in done)
    supported = sum(r["identifiers"]["supported"] for r in done)
    coverage = np.mean([share(ran[(c, arm)], "grounded_lead", "gold_lead") for c in ids])
    cited = np.mean([0.0 if "error" in ran[(c, arm)] else len(set(ran[(c, arm)]["stated_lead"]) & set(ran[(c, arm)]["grounded_lead"]))
                     / ran[(c, arm)]["gold_lead"] for c in ids])
    lines.append(f"- {arm}: verbatim {verified}/{claimed}, identifier precision {supported}/{written}, gold-span citation "
                 f"coverage {coverage:.3f}, stated-and-cited {cited:.3f}")
provider = Counter()
for arm in ("cybercase", "cybercase_slim"):
    for c in pairs:
        call = first_reading(ran[(c, arm)])
        provider[(arm, call.get("provider") or "?", runaway(call))] += 1
lines.append("- first reading attempt by provider (arm, provider, ran away): "
             + "; ".join(f"{k[0]} {k[1]} {'yes' if k[2] else 'no'} {n}" for k, n in sorted(provider.items())))

(HERE / "results" / f"{RUN}_slimfix.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
(HERE / "results" / f"{RUN}_slimfix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
