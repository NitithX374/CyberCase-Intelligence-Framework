"""Design × decoding grid (README.md, 2026-10-02): contrasts (1)-(3) by book_scores.py's rules. No model call.

  python gptoss_grid.py                       Gemma's four stored arms only (post hoc)
  python gptoss_grid.py --run main_<stamp>    gpt-oss's four arms from one run, the rerun check, and Gemma beside them

Writes results/gptoss_grid_<stamp>.md and .json (gptoss_grid_gemma_posthoc.* without --run).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import numpy as np

import book_scores as bs
from single_nogrammar import asks, shown, verdict

CELLS = ("one call, grammar", "two calls, grammar", "one call, no grammar", "two calls, no grammar")
ARM_NAMES = dict(zip(CELLS, ("single", "cybercase", "single_nogrammar", "cybercase_nogrammar")))
GEMMA = {"one call, grammar": (bs.SHIPPED, "single"), "two calls, grammar": (bs.SHIPPED, "cybercase"),
         "one call, no grammar": ("main_20261001_202601", "single_nogrammar"),
         "two calls, no grammar": (bs.FINAL, "cybercase_nogrammar")}
GPTOSS_STORED = "main_20261001_061433"
METRICS = (("M1", "m1"), ("M2", "m2"), ("M4", "m4"), ("M4b", "m4b"), ("M5 V0", "m5"), ("M5-std", "m5std"))
PAIRS = (("1", "design, grammar", "one call, grammar", "two calls, grammar"),
         ("1", "design, no grammar", "one call, no grammar", "two calls, no grammar"),
         ("2", "decoding, one call", "one call, grammar", "one call, no grammar"),
         ("2", "decoding, two calls", "two calls, grammar", "two calls, no grammar"))


def completed(views: dict, labels: tuple[str, ...]) -> tuple[list[str], list[str]]:
    every = sorted(set.intersection(*(set(views[label]) for label in labels)))
    return every, [c for c in every if all(views[label][c]["done"] for label in labels)]


def interaction(s: dict, labels: tuple[str, ...], key: str, cases: list[str]) -> tuple[float, float, float]:
    """(one call no grammar − one call grammar) − (two calls no grammar − two calls grammar), resampled by case."""
    sg, cg, sn, cn = (s[label][key] for label in labels)
    if key in ("m1", "m2"):
        parts = [(np.array([x[c][0] for c in cases]), np.array([x[c][1] for c in cases])) for x in (sg, cg, sn, cn)]
        ratio = lambda part, i: part[0][i].sum() / part[1][i].sum()  # noqa: E731
        statistic = lambda i: (ratio(parts[2], i) - ratio(parts[0], i)) - (ratio(parts[3], i) - ratio(parts[1], i))  # noqa: E731
        return (float(statistic(np.arange(len(cases)))), *bs.bootstrap(len(cases), statistic))
    d = np.array([(sn[c] - sg[c]) - (cn[c] - cg[c]) for c in cases])
    return (float(d.mean()), *bs.bootstrap(len(d), lambda i: d[i].mean()))


def describe(views: dict, scores: dict, label: str, run: str, arm: str) -> dict:
    x, records = scores[label], [v["record"] for v in views[label].values()]
    counted = [asks(r) for r in records]
    return {"run": run, "arm": arm, "cases": x["cases"], "completed": len(x["done"]),
            "m1": list(bs.pooled(x["m1"])), "m2": list(bs.pooled(x["m2"])), "m4": bs.average(x["m4"]),
            "m4b": bs.average(x["m4b"]), "m5_v0": bs.average(x["m5"]), "m5_std": bs.average(x["m5std"]),
            "failed": x["failed"], "capped": x["capped"], "invalid_replies": sum(i for _, i in counted),
            "reasks": sum(r for r, _ in counted), "median_model_seconds": x["seconds"], "usd_per_case": x["usd"],
            "failures": dict(Counter(r["error"].removeprefix("CaseAnalysisFailure: ") for r in records if "error" in r))}


def grid(model: str, configured: dict[str, tuple[str, str]], posthoc: bool) -> dict:
    views, scores = bs.analysis(configured, CELLS)
    arms = {label: describe(views, scores, label, *configured[label]) for label in CELLS}
    contrasts = []
    for number, name, a_label, b_label in PAIRS:
        every, both = completed(views, (a_label, b_label))
        for metric, key in METRICS:
            a, b = scores[a_label][key], scores[b_label][key]
            primary = None if key in ("m1", "m2") else bs.mean_difference(a, b, every)
            secondary = bs.pooled_difference(a, b, both) if key in ("m1", "m2") else bs.mean_difference(a, b, both)
            contrasts.append({"model": model, "contrast": number, "name": name, "metric": metric,
                              "difference": f"{b_label} − {a_label}", "cases": len(every),
                              "completed_in_both": len(both), "failures_0": list(primary) if primary else None,
                              "completed": list(secondary), "verdict": verdict(primary or secondary),
                              "post_hoc": posthoc})
    every, all_four = completed(views, CELLS)
    for metric, key in METRICS:
        primary = None if key in ("m1", "m2") else interaction(scores, CELLS, key, every)
        secondary = interaction(scores, CELLS, key, all_four)
        contrasts.append({"model": model, "contrast": "3", "name": "interaction", "metric": metric,
                          "difference": "(one-call decoding effect) − (two-call decoding effect)",
                          "cases": len(every), "completed_in_both": len(all_four),
                          "failures_0": list(primary) if primary else None, "completed": list(secondary),
                          "verdict": verdict(primary or secondary), "post_hoc": True if model == "Gemma" else posthoc})
    return {"arms": arms, "contrasts": contrasts}


def rerun_check(run: str) -> list[dict]:
    labels = ("one call, grammar", "two calls, grammar", "two calls, no grammar")
    configured = {**{f"{label} (stored)": (GPTOSS_STORED, ARM_NAMES[label]) for label in labels},
                  **{label: (run, ARM_NAMES[label]) for label in labels}}
    views, scores = bs.analysis(configured, tuple(configured))
    rows = []
    for label in labels:
        old, new = f"{label} (stored)", label
        every, both = completed(views, (old, new))
        for metric, key in METRICS:
            a, b = scores[old][key], scores[new][key]
            primary = None if key in ("m1", "m2") else bs.mean_difference(a, b, every)
            secondary = bs.pooled_difference(a, b, both) if key in ("m1", "m2") else bs.mean_difference(a, b, both)
            rows.append({"arm": label, "metric": metric, "failures_0": list(primary) if primary else None,
                         "completed": list(secondary), "cases": len(every), "completed_in_both": len(both),
                         "stored_completed": len(scores[old]["done"]), "rerun_completed": len(scores[new]["done"])})
    return rows


def arm_table(title: str, arms: dict) -> list[str]:
    md = [f"### {title}", "",
          "| Arm | Run | Completed | M1 | M2 | M4 | M4b | M5 V0 | M5-std | Failed (by kind) | Calls to cap | Invalid "
          "replies | Re-asks | Median model s | USD per case |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, a in arms.items():
        kinds = ", ".join(f"{k} {n}" for k, n in sorted(a["failures"].items())) or "none"
        md.append(f"| {label} | `{a['run']}` | {a['completed']}/{a['cases']} | {bs.frac(*a['m1'])} | "
                  f"{bs.frac(*a['m2'])} | {a['m4']:.3f} | {a['m4b']:.3f} | {a['m5_v0']:.3f} | {a['m5_std']:.3f} | "
                  f"{a['failed']} ({kinds}) | {a['capped']} | {a['invalid_replies']} | {a['reasks']} | "
                  f"{a['median_model_seconds']:.0f} | {a['usd_per_case']:.4f} |")
    return md + [""]


def contrast_table(title: str, rows: list[dict]) -> list[str]:
    md = [f"### {title}", "", "| # | Contrast | Metric | Failures 0 (primary) | Completed (secondary) | Interval |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        primary = shown(r["failures_0"]) + f" (n {r['cases']})" if r["failures_0"] else "-"
        label = r["name"] + (" (post hoc)" if r["post_hoc"] else "")
        md.append(f"| {r['contrast']} | {label} | {r['metric']} | {primary} | {shown(r['completed'])} "
                  f"(n {r['completed_in_both']}) | {r['verdict']} |")
    return md + [""]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=None)
    args = parser.parse_args()
    out = {"gemma": grid("Gemma", GEMMA, posthoc=True)}
    if args.run:
        out["run"] = args.run
        out["gptoss"] = grid("gpt-oss", {label: (args.run, ARM_NAMES[label]) for label in CELLS}, posthoc=False)
        out["rerun_check"] = rerun_check(args.run)
    stem = f"gptoss_grid_{args.run.removeprefix('main_')}" if args.run else "gptoss_grid_gemma_posthoc"

    md = [f"# Design × decoding grid{f' ({args.run})' if args.run else ': Gemma, post hoc'}", ""]
    if args.run:
        md += arm_table("gpt-oss-120b, one run", out["gptoss"]["arms"])
        md += contrast_table("gpt-oss-120b contrasts", out["gptoss"]["contrasts"])
        md += ["### Rerun check against `main_20261001_061433` (descriptive): rerun − stored", "",
               "| Arm | Metric | Failures 0 | Completed in both | Completed stored / rerun |", "|---|---|---|---|---|"]
        md += [f"| {r['arm']} | {r['metric']} | {shown(r['failures_0']) if r['failures_0'] else '-'} | "
               f"{shown(r['completed'])} (n {r['completed_in_both']}) | {r['stored_completed']} / {r['rerun_completed']} |"
               for r in out["rerun_check"]] + [""]
    md += arm_table("Gemma 4 26B, stored arms (three runs, two dates)", out["gemma"]["arms"])
    md += contrast_table("Gemma contrasts (stored runs; the interaction is post hoc)", out["gemma"]["contrasts"])
    (bs.HERE / "results" / f"{stem}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (bs.HERE / "results" / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
