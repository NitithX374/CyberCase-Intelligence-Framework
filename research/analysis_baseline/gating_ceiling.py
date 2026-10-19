from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import binding_downstream as bd
from scores_common import CASES, lead, mean_difference, signed, v0_words
from summary_measures import matcher

HERE = Path(__file__).resolve().parent
BACKEND = "F:/cc-worktrees/measure-e35e558/backend"
POLICIES = {"LABEL": None, "GATE-production": "production", "GATE-exact": "exact only",
            "GATE-sim0.80": "similarity >= 0.80", "GATE-sim0.98": "similarity >= 0.98"}
CONTRASTS = (("LABEL", "GATE-production"), ("LABEL", "GATE-exact"), ("GATE-production", "GATE-exact"),
             ("LABEL", "GATE-sim0.98"), ("LABEL", "GATE-sim0.80"))
NL = chr(10)


def visible(policy: str, checks: dict, text: str, reading: dict) -> tuple[list[str], int]:
    name = POLICIES[policy] or "production"
    check = checks[name]
    status = bd.bound_claims(check, text, reading) if POLICIES[policy] else {}
    carried, removed = [], 0
    for claim in reading.get("claims", []):
        if status.get(claim["claim_id"]) == "demoted":
            removed += 1
            continue
        quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        located = [q for q in quotes if check(text, q)]
        carried.append(" ".join([claim.get("text", ""), *located]))
    return carried, removed


def share(texts: list[str], facts: list[dict], mentioned) -> float:
    return sum(any(mentioned(t, f) for t in texts) for f in facts) / len(facts) if facts else 0.0


def shown(r) -> str:
    return f"{signed(r[0])} [{signed(r[1])}, {signed(r[2])}]"


def verdict(r) -> str:
    return "excludes 0" if r[1] > 0 or r[2] < 0 else "includes 0"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default=BACKEND)
    args = parser.parse_args()
    located_quote, quotes = bd.binder(args.backend)
    checks = bd.checkers(located_quote, quotes)
    mentioned = matcher(v0_words, stemmed=True)
    data = bd.readings()

    report: dict = {"sets": {}}
    md = ["# What gating would cost: information left for the judgement (ceiling, not summary coverage)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          "Stemmed matcher; book_scores bootstrap (2,000 case resamples, seed 2026). No model call.", ""]
    for name, items in data.items():
        english = name.startswith("English")
        ids = [case for case, _, _ in items]
        values = {p: {"all": {}, "lead": {}, "floor": {}} for p in POLICIES}
        counts = {p: {"removed": 0, "cases_touched": 0, "claims": 0} for p in POLICIES}
        for i, (case, text, reading) in enumerate(items):
            for policy in POLICIES:
                carried, removed = visible(policy, checks, text, reading)
                counts[policy]["removed"] += removed
                counts[policy]["cases_touched"] += int(removed > 0)
                counts[policy]["claims"] += len(reading.get("claims", []))
                if english:
                    gold = CASES[case]
                    nxt = CASES[ids[(i + 1) % len(ids)]]
                    values[policy]["all"][case] = share(carried, gold["gold"], mentioned)
                    values[policy]["lead"][case] = share(carried, lead(gold), mentioned)
                    values[policy]["floor"][case] = share(carried, nxt["gold"], mentioned)
        entry: dict = {"cases": len(items), "counts": counts}
        md += [f"## {name} ({len(items)} cases)", "", "| Policy | Claims removed | Cases with a claim removed | "
               + ("Ceiling, all facts | Ceiling, main event | Floor |" if english else ""),
               "|---|---|---|" + ("---|---|---|" if english else "")]
        for policy in POLICIES:
            c = counts[policy]
            row = f"| {policy} | {c['removed']} of {c['claims']} | {c['cases_touched']} |"
            if english:
                row += (f" {np.mean(list(values[policy]['all'].values())):.3f} |"
                        f" {np.mean(list(values[policy]['lead'].values())):.3f} |"
                        f" {np.mean(list(values[policy]['floor'].values())):.3f} |")
            md.append(row)
        if english:
            rows = []
            md += ["", "| Contrast | Ceiling, all facts | Interval | Main event | Floor difference |", "|---|---|---|---|---|"]
            for left, right in CONTRASTS:
                r_all = mean_difference(values[right]["all"], values[left]["all"], ids)
                r_lead = mean_difference(values[right]["lead"], values[left]["lead"], ids)
                r_floor = mean_difference(values[right]["floor"], values[left]["floor"], ids)
                rows.append({"contrast": f"{left} − {right}", "all": list(r_all), "lead": list(r_lead),
                             "floor": list(r_floor)})
                md.append(f"| {left} − {right} | {shown(r_all)} | {verdict(r_all)} | {shown(r_lead)} | "
                          f"{shown(r_floor)} |")
            entry["contrasts"] = rows
            entry["means"] = {p: {k: float(np.mean(list(v.values()))) for k, v in values[p].items()}
                              for p in POLICIES}
        md.append("")
        report["sets"][name] = entry
    (HERE / "results" / "gating_ceiling.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (HERE / "results" / "gating_ceiling.md").write_text(NL.join(md) + NL, encoding="utf-8")
    print(NL.join(md))


if __name__ == "__main__":
    main()
