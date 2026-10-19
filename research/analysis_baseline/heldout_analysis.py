"""The held-out replication of README.md (cases 51-150), read from its saved run. No model is called.

  python heldout_analysis.py main_YYYYMMDD_HHMMSS
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

import robustness as rb

HERE = Path(__file__).resolve().parent
RUN = sys.argv[1]
RAW = HERE / "results" / f"raw_{RUN}"
ARMS = ("prose", "single", "single_late", "cybercase")
PRIMARY = ("cybercase", "single")
SECONDARY = (("cybercase", "prose"), ("cybercase", "single_late"), ("single_late", "single"))
TRACED = ("single", "single_late", "cybercase")
ATTACKER_WORDS = {"attacker", "hacker", "perpetrator", "criminal"}
VICTIM_WORDS = {"victim", "target", "affected"}

records = [json.loads(line) for line in (HERE / "results" / f"{RUN}.jsonl").read_text(encoding="utf-8").splitlines()]
by = {(r["case"], r["arm"]): r for r in records}
ran = {key: r for key, r in by.items() if r.get("error_kind") not in ("budget", "harness")}
stopped = sorted(f"{c}/{a} ({r['error_kind']})" for (c, a), r in by.items() if r.get("error_kind") in ("budget", "harness"))
order = [c["id"] for c in rb.cases.values() if c["sample"] == "main"][50:150]
ids = [c for c in order if all((c, arm) in ran for arm in ARMS)]


def bound(case_id: str, arm: str) -> dict | None:
    if "error" in ran[(case_id, arm)]:
        return None
    return json.loads((RAW / f"{case_id}_{arm}_1.json").read_text(encoding="utf-8"))["bound"]


def text_of(case_id: str, arm: str) -> str | None:
    if "error" in ran[(case_id, arm)]:
        return None
    if arm == "prose":
        return (RAW / f"{case_id}_prose_1.txt").read_text(encoding="utf-8")
    return rb.own_text(bound(case_id, arm))


for c in ids:
    for arm in ARMS:
        rb.TEXTS[(c, arm)] = text_of(c, arm)


def share(r: dict, field: str, gold: str) -> float:
    return 0.0 if "error" in r else len(r[field]) / r[gold]


def per_case(arm: str, field: str = "stated_lead", gold: str = "gold_lead") -> dict[str, float]:
    return {c: share(ran[(c, arm)], field, gold) for c in ids}


def stated_and_cited(arm: str) -> dict[str, float]:
    out = {}
    for c in ids:
        r = ran[(c, arm)]
        out[c] = 0.0 if "error" in r else len(set(r["stated_lead"]) & set(r["grounded_lead"])) / r["gold_lead"]
    return out


def sign_flip(d: np.ndarray) -> float:
    rng = np.random.default_rng(rb.SEED)
    flips = rng.choice([-1.0, 1.0], size=(10000, len(d)))
    return (1 + int((np.abs((flips * d).mean(axis=1)) >= abs(d.mean())).sum())) / 10001


def diff(values: dict[str, dict[str, float]], a: str, b: str, subset: list[str]) -> dict[str, float]:
    return {c: values[a][c] - values[b][c] for c in subset}


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    out, running = {}, 0.0
    ranked = sorted(pvalues.items(), key=lambda kv: kv[1])
    for rank, (name, p) in enumerate(ranked):
        running = max(running, min(1.0, p * (len(ranked) - rank)))
        out[name] = running
    return out


def matched_length(a: str, b: str) -> tuple[dict[str, float], list[str]]:
    both = [c for c in ids if rb.TEXTS[(c, a)] and rb.TEXTS[(c, b)]]
    cut = {}
    for c in both:
        ta, tb = rb.TEXTS[(c, a)], rb.TEXTS[(c, b)]
        n = min(len(ta.split()), len(tb.split()))
        cut[c] = (rb.recall(c, a, "V0", True, text=" ".join(ta.split()[:n]))
                  - rb.recall(c, b, "V0", True, text=" ".join(tb.split()[:n])))
    return cut, both


def role_inversions(arm: str) -> tuple[int, int]:
    checked = inverted = 0
    for c in ids:
        trace = bound(c, arm)
        if trace is None:
            continue
        for fact in (f for f in rb.cases[c]["gold"] if f["role"] in ("Victim", "Attacker")):
            for party in trace["involved_parties"]:
                if not rb.contains(rb.norm(party["name"]), fact["text"]):
                    continue
                words = {w.rstrip("s") for w in rb.norm(party["role"]).split()}
                checked += 1
                if fact["role"] == "Victim" and words & ATTACKER_WORDS and not words & VICTIM_WORDS:
                    inverted += 1
                if fact["role"] == "Attacker" and words & VICTIM_WORDS and not words & ATTACKER_WORDS:
                    inverted += 1
    return inverted, checked


report: dict = {"run": RUN, "cases_in_order": len(order), "cases_scored": len(ids), "stopped_runs": stopped}
lines = [f"# Held-out replication, cases 51-150 ({RUN})", "",
         f"Cases scored: {len(ids)} of {len(order)}. Runs stopped by budget or harness: {', '.join(stopped) or 'none'}.", ""]

lines += ["## Failures, cost and time per arm", "", "| Arm | Completed | Failures | Calls | USD | Model s (median per run) |",
          "|---|---|---|---|---|---|"]
for arm in ARMS:
    rows = [ran[(c, arm)] for c in ids]
    calls = [call for r in rows for call in r["calls"]]
    failures = Counter(r["error"] for r in rows if "error" in r)
    seconds = [sum(call["ms"] for call in r["calls"]) / 1000 for r in rows]
    lines.append(f"| {arm} | {sum('error' not in r for r in rows)} | {dict(failures) or '—'} | {len(calls)} | "
                 f"{sum(call['usd'] for call in calls):.4f} | {np.median(seconds):.0f} |")
    report[f"cost_{arm}"] = {"calls": len(calls), "usd": sum(call["usd"] for call in calls),
                             "failures": dict(failures), "runaway_calls": sum(
                                 (call.get("output_tokens") or 0) >= 40000 for call in calls)}

recall = {arm: per_case(arm) for arm in ARMS}
lines += ["", "## Annotated-argument mention recall, main event (frozen V0 scorer, failures scored 0)", "",
          "| Arm | Mean |", "|---|---|"]
lines += [f"| {arm} | {np.mean(list(recall[arm].values())):.3f} |" for arm in ARMS]

a, b = PRIMARY
d = diff(recall, a, b, ids)
point, low, high = rb.bootstrap(d, ids)
p = sign_flip(np.array([d[c] for c in ids]))
report["primary"] = {"comparison": f"{a}-{b}", "diff": point, "ci": [low, high], "sign_flip_p": p}
lines += ["", "## Primary (fixed before the run)", "", f"- {a} − {b}: {rb.fmt(point, low, high)}, sign-flip p = {p:.4f}"]

secondary = {}
for a2, b2 in SECONDARY:
    dd = diff(recall, a2, b2, ids)
    pt, lo, hi = rb.bootstrap(dd, ids)
    secondary[f"{a2}-{b2}"] = {"diff": pt, "ci": [lo, hi], "sign_flip_p": sign_flip(np.array([dd[c] for c in ids]))}
for name, adjusted in holm({k: v["sign_flip_p"] for k, v in secondary.items()}).items():
    secondary[name]["holm_p"] = adjusted
report["secondary"] = secondary
lines += ["", "## Secondary (Holm across the three)", "", "| Comparison | Difference | 95% CI | Sign-flip p | Holm p |",
          "|---|---|---|---|---|"]
for name, r in secondary.items():
    lines.append(f"| {name.replace('-', ' − ', 1)} | {r['diff']:+.3f} | [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | "
                 f"{r['sign_flip_p']:.4f} | {r['holm_p']:.4f} |")

pairs = (PRIMARY, *SECONDARY)
lines += ["", "## Descriptive", ""]
for a2, b2 in pairs:
    cut, both = matched_length(a2, b2)
    lines.append(f"- matched length, {a2} − {b2} ({len(both)} cases): {rb.fmt(*rb.bootstrap(cut, both))}")
for variant in ("V1", "V3", "V6"):
    values = {arm: {c: rb.recall(c, arm, variant, True) for c in ids} for arm in ARMS}
    lines.append(f"- {variant}, main event: " + "; ".join(
        f"{a2} − {b2} {rb.fmt(*rb.bootstrap(diff(values, a2, b2, ids), ids))}" for a2, b2 in pairs))
all_events = {arm: per_case(arm, "stated", "gold") for arm in ARMS}
lines.append("- all-event mention recall: " + ", ".join(f"{arm} {np.mean(list(all_events[arm].values())):.3f}"
                                                      for arm in ARMS)
             + "; " + "; ".join(f"{a2} − {b2} {rb.fmt(*rb.bootstrap(diff(all_events, a2, b2, ids), ids))}"
                                for a2, b2 in pairs))
coverage = {arm: per_case(arm, "grounded_lead", "gold_lead") for arm in TRACED}
lines.append("- gold-span citation coverage, main event: " + ", ".join(
    f"{arm} {np.mean(list(coverage[arm].values())):.3f}" for arm in TRACED)
             + f"; cybercase − single {rb.fmt(*rb.bootstrap(diff(coverage, 'cybercase', 'single', ids), ids))}")
cited = {arm: stated_and_cited(arm) for arm in TRACED}
lines.append("- stated-and-cited recall, main event: " + ", ".join(
    f"{arm} {np.mean(list(cited[arm].values())):.3f}" for arm in TRACED)
             + f"; cybercase − single {rb.fmt(*rb.bootstrap(diff(cited, 'cybercase', 'single', ids), ids))}")
for arm in TRACED:
    inverted, checked = role_inversions(arm)
    report[f"role_{arm}"] = [inverted, checked]
lines.append("- role inversion (Victim/Attacker argument in a party worded as the other role, strict lexicon): "
             + ", ".join(f"{arm} {report[f'role_{arm}'][0]}/{report[f'role_{arm}'][1]}" for arm in TRACED))
for arm in ARMS:
    done = [ran[(c, arm)] for c in ids if "error" not in ran[(c, arm)]]
    written = sum(r["identifiers"]["written"] for r in done)
    supported = sum(r["identifiers"]["supported"] for r in done)
    claimed = sum((r.get("grounding") or {}).get("citations_claimed", 0) for r in done)
    verified = sum((r.get("grounding") or {}).get("citations_verified", 0) for r in done)
    lines.append(f"- {arm}: identifier precision {supported}/{written}"
                 + (f", verbatim {verified}/{claimed}" if claimed else "")
                 + f", words per completed run {np.mean([len(rb.TEXTS[(c, arm)].split()) for c in ids if rb.TEXTS[(c, arm)]]):.0f}")

dev_ids = rb.ids
dev = {arm: {c: rb.recall(c, arm, "V0", True) for c in dev_ids} for arm in ("prose", "single", "cybercase")}
held = {arm: {c: rb.recall(c, arm, "V0", True) for c in ids} for arm in ("prose", "single", "cybercase")}
for a2, b2 in (("cybercase", "single"), ("cybercase", "prose")):
    pooled = {**diff(dev, a2, b2, dev_ids), **diff(held, a2, b2, ids)}
    subset = list(pooled)
    lines.append(f"- pooled 1-150 (descriptive, two dates), {a2} − {b2} ({len(subset)} cases): "
                 f"{rb.fmt(*rb.bootstrap(pooled, subset))}")

(HERE / "results" / f"{RUN}_heldout.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(HERE / "results" / f"{RUN}_heldout.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
