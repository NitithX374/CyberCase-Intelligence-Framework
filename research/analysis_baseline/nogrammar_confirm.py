"""The no-grammar confirmation of README.md, read from saved runs. No model is called.

  python nogrammar_confirm.py main_YYYYMMDD_HHMMSS
  python nogrammar_confirm.py pilot_YYYYMMDD_HHMMSS --control pilot_20260930_060711   (dry run)
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED, DRAWS = 2026, 2000
TREATMENT, CONTROL = "cybercase_nogrammar", "cybercase"
CAP = 40_800


def records(run: str, arm: str) -> dict[str, dict]:
    rows = [json.loads(line) for line in (HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines()]
    return {r["case"]: r for r in rows if r["arm"] == arm and r.get("run", 1) == 1
            and r.get("error_kind") not in ("budget", "harness")}


def recall(r: dict) -> float:
    return 0.0 if "error" in r else len(r["stated_lead"]) / r["gold_lead"]


def runaway(call: dict) -> bool:
    return call.get("stop_reason") in ("max_tokens", "length") or (call.get("output_tokens") or 0) >= CAP


def paired(diff: dict[str, float]) -> tuple[float, float, float]:
    ids = sorted(diff)
    values = np.array([diff[c] for c in ids])
    rng = np.random.default_rng(SEED)
    draws = [values[rng.integers(0, len(values), len(values))].mean() for _ in range(DRAWS)]
    return float(values.mean()), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def arm_lines(name: str, rows: list[dict]) -> list[str]:
    done = [r for r in rows if "error" not in r]
    reading = [next((c for c in r["calls"] if c["stage"] == "case_reading"), None) for r in rows]
    cited = sum((r["grounding"] or {}).get("citations_claimed", 0) for r in done)
    verified = sum((r["grounding"] or {}).get("citations_verified", 0) for r in done)
    written = sum(r["identifiers"]["written"] for r in done)
    return [f"- {name}: {len(rows)} cases, failed {len(rows) - len(done)} "
            f"({dict(Counter(r['error'][:60] for r in rows if 'error' in r)) or 'none'}); first reading attempt ran "
            f"away {sum(bool(c) and runaway(c) for c in reading)}; invalid replies "
            f"{sum(sum(p.startswith('invalid') for p in r.get('problems', [])) for r in rows)}; verified quotes "
            f"{verified}/{cited} = {verified / max(1, cited):.3f}; identifier precision "
            f"{sum(r['identifiers']['supported'] for r in done) / max(1, written):.3f}; claims per completed case "
            f"{np.mean([(r['grounding'] or {}).get('claims', 0) for r in done]) if done else 0:.1f}; USD "
            f"{sum(c['usd'] for r in rows for c in r['calls']):.4f}; median s "
            f"{np.median([r['seconds'] for r in rows]):.0f}"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("--control", default="main_20260930_062138")
    args = parser.parse_args()
    treated, control = records(args.run, TREATMENT), records(args.control, CONTROL)
    ids = sorted(set(treated) & set(control))
    failures = sum("error" in treated[c] for c in ids)
    diff = {c: recall(treated[c]) - recall(control[c]) for c in ids}
    done = [c for c in ids if "error" not in treated[c] and "error" not in control[c]]
    effect = paired(diff)
    completed = paired({c: diff[c] for c in done}) if done else (float("nan"),) * 3
    verified = sum((treated[c]["grounding"] or {}).get("citations_verified", 0) for c in ids if "error" not in treated[c])
    cited = sum((treated[c]["grounding"] or {}).get("citations_claimed", 0) for c in ids if "error" not in treated[c])
    share = verified / max(1, cited)
    reliability = failures <= 2 * len(ids) / 100
    quality = effect[1] > -0.05
    lines = [f"# No-grammar confirmation ({args.run}, control {args.control})", "",
             f"Paired cases: {len(ids)} (treatment {len(treated)}, control {len(control)}).", "",
             "## Primary", "",
             f"1. Reliability: {failures} of {len(ids)} cases without a completed trace "
             f"(limit {2 * len(ids) / 100:.1f}) -> {'pass' if reliability else 'fail'}.",
             f"2. Quality: main-event mention recall, failures 0, nogrammar - shipped "
             f"{effect[0]:+.3f} [{effect[1]:+.3f}, {effect[2]:+.3f}]; non-inferior if the lower bound > -0.05 -> "
             f"{'pass' if quality else 'fail'}.", "",
             "## Secondary and descriptive", "",
             f"- Completed in both ({len(done)} cases): {completed[0]:+.3f} [{completed[1]:+.3f}, {completed[2]:+.3f}].",
             f"- Verified quotes (treatment): {share:.3f}; required at least 0.95 -> {'pass' if share >= 0.95 else 'fail'}.",
             f"- Mean recall: nogrammar {np.mean([recall(treated[c]) for c in ids]):.3f}, shipped "
             f"{np.mean([recall(control[c]) for c in ids]):.3f}."]
    lines += arm_lines("nogrammar", [treated[c] for c in ids]) + arm_lines("shipped (stored)", [control[c] for c in ids])
    reading = ("Both primaries pass: propose the no-grammar reading for production." if reliability and quality else
               "Reliability passes, recall does not: the owner decides." if reliability else
               "Reliability fails: not adopted.")
    lines += ["", f"**Reading, as fixed: {reading}**"]
    report = {"run": args.run, "control": args.control, "pairs": len(ids), "failures": failures,
              "recall_difference": effect, "completed_difference": completed, "verified_share": share,
              "reliability_pass": reliability, "quality_pass": quality}
    (HERE / "results" / f"{args.run}_nogrammar.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (HERE / "results" / f"{args.run}_nogrammar.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
