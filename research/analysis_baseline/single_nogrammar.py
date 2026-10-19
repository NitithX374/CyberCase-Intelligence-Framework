"""One call without the grammar, cases 151-250 (README.md, 2026-10-02): the fixed comparisons, by book_scores.py's
rules. No model call.

  python single_nogrammar.py --run main_<stamp>

Writes results/single_nogrammar_<stamp>.md and .json.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import numpy as np

import book_scores as bs

LABELS = ("one call, grammar", "two calls, grammar", "two calls, no grammar", "one call, no grammar")
METRICS = (("M1", "m1"), ("M2", "m2"), ("M4", "m4"), ("M4b", "m4b"), ("M5 V0", "m5"), ("M5-std", "m5std"))
FIXED = (("1", "one call, no grammar", "two calls, no grammar"), ("2", "one call, grammar", "one call, no grammar"))


def cases(views: dict, x: str, y: str, completed: bool = False) -> list[str]:
    ids = sorted(set(views[x]) & set(views[y]))
    return [c for c in ids if views[x][c]["done"] and views[y][c]["done"]] if completed else ids


def verdict(result: tuple[float, float, float]) -> str:
    _, low, high = result
    return "excludes 0" if low > 0 or high < 0 else "includes 0"


def shown(result: tuple[float, float, float]) -> str:
    return f"{bs.signed(result[0])} [{bs.signed(result[1])}, {bs.signed(result[2])}]"


def asks(record: dict) -> tuple[int, int]:
    """Re-asks and invalid replies of one case, from its call records.

    A re-ask is every call of a stage after its first. An invalid reply is a call that ended before the token cap and
    was not the reply the stage kept; a stage kept its last reply unless the case failed on that stage.
    """
    failed = record.get("error", "").removeprefix("CaseAnalysisFailure: ")
    reasks = invalid = 0
    for stage, n in Counter(call["stage"] for call in record["calls"]).items():
        reasks += n - 1
        ended = sum(not bs.capped(call) for call in record["calls"] if call["stage"] == stage)
        invalid += ended - (0 if failed.startswith(f"{stage}_") else 1 if ended else 0)
    return reasks, invalid


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    configured = {"one call, grammar": (bs.SHIPPED, "single"), "two calls, grammar": (bs.SHIPPED, "cybercase"),
                  "two calls, no grammar": (bs.FINAL, "cybercase_nogrammar"),
                  "one call, no grammar": (args.run, "single_nogrammar")}
    views, scores = bs.analysis(configured, LABELS)

    arms = {}
    for label in LABELS:
        x, records = scores[label], [v["record"] for v in views[label].values()]
        counted = [asks(r) for r in records]
        n1, d1 = bs.pooled(x["m1"])
        n2, d2 = bs.pooled(x["m2"])
        arms[label] = {
            "run": configured[label][0], "arm": configured[label][1], "cases": x["cases"],
            "completed": len(x["done"]), "m1": [n1, d1], "m2": [n2, d2], "m4": bs.average(x["m4"]),
            "m4b": bs.average(x["m4b"]), "m5_v0": bs.average(x["m5"]), "m5_std": bs.average(x["m5std"]),
            "floor": float(np.mean(x["floor"])), "failed": x["failed"], "capped": x["capped"],
            "invalid_replies": sum(i for _, i in counted), "reasks": sum(r for r, _ in counted),
            "recorded_invalid": sum(p.startswith("invalid") for r in records for p in r.get("problems", [])),
            "median_model_seconds": x["seconds"], "usd_per_case": x["usd"],
            "failures": dict(Counter(r["error"] for r in records if "error" in r)),
        }

    rows = []
    for number, a_label, b_label in FIXED:
        every, both = cases(views, a_label, b_label), cases(views, a_label, b_label, True)
        for name, key in METRICS:
            a, b = scores[a_label][key], scores[b_label][key]
            if key in ("m1", "m2"):
                primary, secondary = None, bs.pooled_difference(a, b, both)
            else:
                primary, secondary = bs.mean_difference(a, b, every), bs.mean_difference(a, b, both)
            rows.append({"comparison": number, "metric": name, "minuend": b_label, "subtrahend": a_label,
                         "cases": len(every), "completed_in_both": len(both),
                         "failures_0": list(primary) if primary else None, "completed": list(secondary),
                         "verdict": verdict(primary or secondary)})

    ids = {label: sorted(views[label]) for label in LABELS}
    stamp = args.run.removeprefix("main_")
    out = {"run": args.run, "same_cases": all(v == ids[LABELS[0]] for v in ids.values()),
           "arms": arms, "comparisons": rows,
           "spent_usd": arms["one call, no grammar"]["usd_per_case"] * arms["one call, no grammar"]["cases"]}
    (bs.HERE / "results" / f"single_nogrammar_{stamp}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    md = [f"# One call without the grammar, cases 151-250 ({args.run})", "",
          f"Same cases in every arm: {out['same_cases']}. Spent USD {out['spent_usd']:.4f}.", "",
          "| Arm | Run | Completed | M1 | M2 | M4 | M4b | M5 V0 | M5-std | Floor | Failed | Calls to cap | Invalid "
          "replies | Re-asks | Median model s | USD per case |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, a in arms.items():
        md.append(f"| {label} | `{a['run']}` | {a['completed']}/{a['cases']} | {bs.frac(*a['m1'])} | "
                  f"{bs.frac(*a['m2'])} | {a['m4']:.3f} | {a['m4b']:.3f} | {a['m5_v0']:.3f} | {a['m5_std']:.3f} | "
                  f"{a['floor']:.3f} | {a['failed']} | {a['capped']} | {a['invalid_replies']} | {a['reasks']} | "
                  f"{a['median_model_seconds']:.0f} | {a['usd_per_case']:.4f} |")
    md += ["", "| # | Metric | Difference | Failures 0 (primary) | Completed in both | Interval |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        primary = shown(r["failures_0"]) + f" (n {r['cases']})" if r["failures_0"] else "-"
        md.append(f"| {r['comparison']} | {r['metric']} | {r['minuend']} − {r['subtrahend']} | {primary} | "
                  f"{shown(r['completed'])} (n {r['completed_in_both']}) | {r['verdict']} |")
    md += ["", "Failures: " + "; ".join(f"{label}: {a['failures'] or 'none'}" for label, a in arms.items()),
           "Invalid replies recorded by the arm itself (problems): "
           + "; ".join(f"{label}: {a['recorded_invalid']}" for label, a in arms.items())]
    (bs.HERE / "results" / f"single_nogrammar_{stamp}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
