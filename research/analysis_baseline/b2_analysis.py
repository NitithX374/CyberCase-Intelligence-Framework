"""B2 of README.md: the single_late arm against the saved main-run arms. No model is called.

  python b2_analysis.py main_20260930_XXXXXX
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import robustness as rb

HERE = Path(__file__).resolve().parent
NEW = sys.argv[1]
new_records = {r["case"]: r for r in map(json.loads, (HERE / "results" / f"{NEW}.jsonl").read_text(
    encoding="utf-8").splitlines()) if r["arm"] == "single_late"}
ids = [c for c in rb.ids if c in new_records and new_records[c].get("error_kind") not in ("budget", "harness")]


def late_text(case_id: str) -> str | None:
    if "error" in new_records[case_id]:
        return None
    raw = HERE / "results" / f"raw_{NEW}" / f"{case_id}_single_late_1.json"
    return rb.own_text(json.loads(raw.read_text(encoding="utf-8"))["bound"])


for c in ids:
    rb.TEXTS[(c, "single_late")] = late_text(c)


def share(r: dict, field: str, gold: str) -> float:
    return 0.0 if "error" in r else len(r[field]) / r[gold]


def per_case(arm: str, field: str, gold: str) -> dict[str, float]:
    rows = new_records if arm == "single_late" else {c: rb.by[(c, arm)] for c in ids}
    return {c: share(rows[c], field, gold) for c in ids}


def sign_flip(d: np.ndarray) -> float:
    rng = np.random.default_rng(rb.SEED)
    flips = rng.choice([-1.0, 1.0], size=(10000, len(d)))
    return (1 + int((np.abs((flips * d).mean(axis=1)) >= abs(d.mean())).sum())) / 10001


lines = [f"# B2: single_late ({NEW}) against the saved main-run arms", "",
         f"Cases: {len(ids)}. single_late failures: "
         f"{sum('error' in new_records[c] for c in ids)} ({', '.join(new_records[c]['error'] for c in ids if 'error' in new_records[c]) or 'none'})",
         ""]
report: dict = {"run": NEW, "cases": len(ids)}

lines += ["## Primary: main-event recall, frozen scorer, failures scored 0", "",
          "| Arm | Recall |", "|---|---|"]
recall = {arm: per_case(arm, "stated_lead", "gold_lead") for arm in ("single", "single_late", "cybercase")}
for arm, values in recall.items():
    lines.append(f"| {arm} | {np.mean(list(values.values())):.3f} |")
comparisons = (("single_late", "single"), ("cybercase", "single_late"))
pvalues = {}
for a, b in comparisons:
    d = {c: recall[a][c] - recall[b][c] for c in ids}
    point, low, high = rb.bootstrap(d, ids)
    p = sign_flip(np.array([d[c] for c in ids]))
    pvalues[f"{a}-{b}"] = p
    report[f"{a}-{b}"] = {"diff": point, "ci": [low, high], "sign_flip_p": p}
holm = sorted(pvalues.items(), key=lambda kv: kv[1])
running = 0.0
for rank, (name, p) in enumerate(holm):
    running = max(running, min(1.0, p * (len(holm) - rank)))
    report[name]["holm_p"] = running
lines += ["", "| Comparison | Difference | 95% CI | Sign-flip p | Holm p |", "|---|---|---|---|---|"]
for a, b in comparisons:
    r = report[f"{a}-{b}"]
    lines.append(f"| {a} − {b} | {r['diff']:+.3f} | [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['sign_flip_p']:.4f} | "
                 f"{r['holm_p']:.4f} |")

lines += ["", "## Secondary", ""]
for label, field, gold in (("all-event recall", "stated", "gold"), ("grounded main-event recall", "grounded_lead", "gold_lead")):
    vals = {arm: per_case(arm, field, gold) for arm in ("single", "single_late", "cybercase")}
    means = ", ".join(f"{arm} {np.mean(list(v.values())):.3f}" for arm, v in vals.items())
    diffs = "; ".join(f"{a} − {b} {rb.fmt(*rb.bootstrap({c: vals[a][c] - vals[b][c] for c in ids}, ids))}"
                      for a, b in comparisons)
    lines.append(f"- {label}: {means}; {diffs}")

words = {arm: [len(rb.TEXTS[(c, arm)].split()) for c in ids if rb.TEXTS[(c, arm)]] for arm in ("single", "single_late", "cybercase")}
lines.append("- words written per completed run: " + ", ".join(f"{arm} {np.mean(w):.0f}" for arm, w in words.items()))

for variant in ("V1", "V3", "V6"):
    vals = {arm: {c: rb.recall(c, arm, variant, True) if rb.TEXTS[(c, arm)] else 0.0 for c in ids}
            for arm in ("single", "single_late", "cybercase")}
    lines.append(f"- {variant} main-event: " + "; ".join(
        f"{a} − {b} {rb.fmt(*rb.bootstrap({c: vals[a][c] - vals[b][c] for c in ids}, ids))}" for a, b in comparisons))

both = [c for c in ids if rb.TEXTS[(c, "single_late")] and rb.TEXTS[(c, "single")]]
cut = {}
for c in both:
    ta, tb = rb.TEXTS[(c, "single_late")], rb.TEXTS[(c, "single")]
    n = min(len(ta.split()), len(tb.split()))
    cut[c] = (rb.recall(c, "single_late", "V0", True, text=" ".join(ta.split()[:n]))
              - rb.recall(c, "single", "V0", True, text=" ".join(tb.split()[:n])))
lines.append(f"- matched length, single_late − single ({len(both)} cases): {rb.fmt(*rb.bootstrap(cut, both))}")

placement = {}
for arm in ("single", "single_late", "cybercase"):
    only_d = only_s = both_f = n = 0
    for c in ids:
        raw = (HERE / "results" / f"raw_{NEW}" / f"{c}_single_late_1.json" if arm == "single_late"
               else rb.RAW / f"{c}_{arm}_1.json")
        if not rb.TEXTS[(c, arm)] or not raw.exists():
            continue
        trace = json.loads(raw.read_text(encoding="utf-8"))["bound"]
        summary = rb.norm(trace["summary"])
        details = rb.norm(rb.own_text({**trace, "summary": ""}))
        n += 1
        for f in (f for f in rb.cases[c]["gold"] if f["lead"]):
            s, d = rb.contains(summary, f["text"]), rb.contains(details, f["text"])
            only_s += s and not d
            only_d += d and not s
            both_f += s and d
    placement[arm] = (only_d / n, both_f / n, only_s / n)
lines.append("- main-event facts per completed case, details only / both / summary only: " + "; ".join(
    f"{arm} {v[0]:.2f} / {v[1]:.2f} / {v[2]:.2f}" for arm, v in placement.items()))

calls = [call for c in ids for call in new_records[c]["calls"]]
seconds = [sum(call["ms"] for call in new_records[c]["calls"]) / 1000 for c in ids]
lines += ["", f"Cost USD {sum(call['usd'] for call in calls):.4f}; providers "
          f"{dict(__import__('collections').Counter(call.get('provider') for call in calls))}; model seconds per run median "
          f"{np.median(seconds):.0f}, p90 {np.percentile(seconds, 90):.0f}, max {max(seconds):.0f}"]

(HERE / "results" / f"{NEW}_b2.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(HERE / "results" / f"{NEW}_b2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
