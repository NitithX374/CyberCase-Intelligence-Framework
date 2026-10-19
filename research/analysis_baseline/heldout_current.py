"""The current system on the held-out cases 51-150 (README.md, 2026-10-01): the fixed comparisons, by book_scores.py's
rules. No model call.

  python heldout_current.py [--run main_20261001_021428]

Writes results/heldout_current.md and .json.
"""
from __future__ import annotations

import argparse
import json

import numpy as np

import book_scores as bs

CURRENT = "main_20261001_021428"
LABELS = ("prose", "one call", "two calls", "current")


def cases(views: dict, x: str, y: str, completed: bool = False) -> list[str]:
    ids = sorted(set(views[x]) & set(views[y]))
    return [c for c in ids if views[x][c]["done"] and views[y][c]["done"]] if completed else ids


def verdict(result: tuple[float, float, float]) -> str:
    _, low, high = result
    return "excludes 0" if low > 0 or high < 0 else "includes 0"


def shown(result: tuple[float, float, float]) -> str:
    return f"{bs.signed(result[0])} [{bs.signed(result[1])}, {bs.signed(result[2])}]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=CURRENT)
    args = parser.parse_args()
    configured = {"prose": (bs.DESIGN, "prose"), "one call": (bs.DESIGN, "single"),
                  "two calls": (bs.DESIGN, "cybercase"), "current": (args.run, "cybercase_nogrammar")}
    traced = ("one call", "two calls", "current")
    views, scores = bs.analysis(configured, traced)

    arms = {}
    for label in LABELS:
        x = scores[label]
        arm = {"cases": x["cases"], "completed": len(x["done"]), "m5_v0": bs.average(x["m5"]),
               "m5_std": bs.average(x["m5std"]), "floor": float(np.mean(x["floor"]))}
        if label in traced:
            n1, d1 = bs.pooled(x["m1"])
            n2, d2 = bs.pooled(x["m2"])
            arm.update(m1=[n1, d1], m2=[n2, d2], m3=[x["m3"], len(x["done"])], m4=bs.average(x["m4"]),
                       m4b=bs.average(x["m4b"]), failed=x["failed"], capped=x["capped"],
                       median_model_seconds=x["seconds"], usd_per_case=x["usd"])
        arms[label] = arm

    fixed = (("1", "prose", (("M5 V0", "m5"), ("M5-std", "m5std"))),
             ("2", "one call", (("M4", "m4"), ("M4b", "m4b"), ("M5 V0", "m5"), ("M5-std", "m5std"))),
             ("3", "two calls", (("M1", "m1"), ("M4", "m4"), ("M4b", "m4b"), ("M5 V0", "m5"), ("M5-std", "m5std"))))
    rows = []
    for number, other, metrics in fixed:
        every, both = cases(views, other, "current"), cases(views, other, "current", True)
        for name, key in metrics:
            a, b = scores[other][key], scores["current"][key]
            if key == "m1":
                primary, secondary = None, bs.pooled_difference(a, b, both)
            else:
                primary, secondary = bs.mean_difference(a, b, every), bs.mean_difference(a, b, both)
            rows.append({"comparison": number, "metric": name, "against": other, "cases": len(every),
                         "completed_in_both": len(both),
                         "failures_0": list(primary) if primary else None,
                         "completed": list(secondary),
                         "verdict": verdict(primary or secondary)})

    design_ids = sorted(views["two calls"])
    current_ids = sorted(views["current"])
    out = {"run": args.run, "same_cases_as_design": design_ids == current_ids,
           "case_range": [current_ids[0], current_ids[-1]] if current_ids else None, "arms": arms, "comparisons": rows,
           "spent_usd": arms["current"]["usd_per_case"] * arms["current"]["cases"]}
    (bs.HERE / "results" / "heldout_current.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    md = [f"# Current system on the held-out cases 51-150 ({args.run})", "",
          f"Same cases as the design comparison: {out['same_cases_as_design']}. Spent USD {out['spent_usd']:.4f}.", "",
          "| Arm | Cases | Completed | M1 | M2 | M3 | M4 | M4b | M5 V0 | M5-std | Floor | Failed | Calls to cap "
          "| Median model s | USD per case |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, a in arms.items():
        has_trace = label in traced
        md.append(f"| {label} | {a['cases']} | {a['completed']} | "
                  + (f"{bs.frac(*a['m1'])} | {bs.frac(*a['m2'])} | {bs.frac(*a['m3'], False)} | {a['m4']:.3f} | "
                     f"{a['m4b']:.3f} | " if has_trace else "- | - | - | - | - | ")
                  + f"{a['m5_v0']:.3f} | {a['m5_std']:.3f} | {a['floor']:.3f} | "
                  + (f"{a['failed']} | {a['capped']} | {a['median_model_seconds']:.0f} | {a['usd_per_case']:.4f} |"
                     if has_trace else "- | - | - | - |"))
    md += ["", "| # | Metric | current − | Failures 0 (primary) | Completed in both | Interval |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        primary = shown(r["failures_0"]) + f" (n {r['cases']})" if r["failures_0"] else "-"
        md.append(f"| {r['comparison']} | {r['metric']} | {r['against']} | {primary} | "
                  f"{shown(r['completed'])} (n {r['completed_in_both']}) | {r['verdict']} |")
    (bs.HERE / "results" / "heldout_current.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
