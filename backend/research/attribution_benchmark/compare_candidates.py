import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from candidate_reports import write_json
from data import LABELS, sha256
from metrics import BOOTSTRAP_REPLICATES, SEED, f1_from_counts


def read_scores(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def paired_intervals(runs, split):
    random = np.random.default_rng(SEED)
    model_keys = list(runs)
    base = runs["mdeberta"]
    base_rows = read_scores(base["path"] / f"scores_{split}.jsonl")
    identity = [(row["id"], row["gold"], row["cluster"], row["src_dataset"]) for row in base_rows]
    counts = {}
    for key, run in runs.items():
        rows = read_scores(run["path"] / f"scores_{split}.jsonl")
        if [(row["id"], row["gold"], row["cluster"], row["src_dataset"]) for row in rows] != identity:
            raise ValueError(f"Unmatched evaluation units: {key}:{split}")
        by_source = defaultdict(lambda: defaultdict(lambda: np.zeros(4, dtype=np.float64)))
        threshold = run["summary"]["selection"]["threshold"]
        for row in rows:
            prediction = "attributable" if row["p_supported"] >= threshold else "not attributable"
            cell = 2 * LABELS.index(row["gold"]) + LABELS.index(prediction)
            by_source[row["src_dataset"]][row["cluster"]][cell] += 1
        counts[key] = by_source
    draws = {key: [] for key in model_keys}
    for source in sorted(counts["mdeberta"]):
        clusters = list(counts["mdeberta"][source])
        weights = random.multinomial(len(clusters), np.repeat(1 / len(clusters), len(clusters)), size=BOOTSTRAP_REPLICATES)
        for key in model_keys:
            values = np.asarray([counts[key][source][cluster] for cluster in clusters])
            draws[key].append(f1_from_counts(weights @ values))
    means = {key: np.mean(values, axis=0) for key, values in draws.items()}
    baseline = means["mdeberta"]
    return {
        key: {
            "delta_mean_source_macro_f1": run["summary"]["results"][split]["mean_source_macro_f1"] - base["summary"]["results"][split]["mean_source_macro_f1"],
            "delta_ci95": np.quantile(means[key] - baseline, [0.025, 0.975]).tolist(),
            "unit": "paired source-stratified question+response clusters", "replicates": BOOTSTRAP_REPLICATES, "seed": SEED,
        } for key, run in runs.items()
    }


def compare(suite):
    manifest = json.loads((suite / "suite_manifest.json").read_text(encoding="utf-8"))
    runs = {}
    rows = []
    for outcome in manifest["outcomes"]:
        if outcome["status"] != "complete":
            rows.append({"model": outcome["model"], "status": outcome["status"], "failure": outcome.get("failure")})
            continue
        path = Path(outcome["output"])
        summary = json.loads((path / "summary.json").read_text(encoding="utf-8"))
        verification = json.loads((path / "verification.json").read_text(encoding="utf-8"))
        if verification["status"] != "passed" or sha256(path / "summary.json") != verification["summary_sha256"]:
            raise ValueError(f"Unverified comparison input: {outcome['model']}")
        runs[outcome["model"]] = {"path": path, "summary": summary}
        row = {
            "model": outcome["model"], "checkpoint": summary["model"]["model"], "revision": summary["model"]["revision"],
            "status": "complete", "device": summary["model"]["device"], "dtype": summary["model"]["dtype"],
            "batch_size": summary["model"]["batch_size"], "threshold": summary["selection"]["threshold"],
            "dev_mean_source_macro_f1": summary["selection"]["dev_mean_source_macro_f1"],
            "runner_seconds": summary["timing"]["runner_wall_seconds"], "load_seconds": summary["timing"]["model_load_seconds"],
            "unit_latency_p50_p95_seconds": summary["timing"]["amortized_unit_p50_p95_seconds"],
            "resources": summary["resources"], "report": str(path / "report.md"),
            "summary_sha256": verification["summary_sha256"],
            "previous_attempts": outcome.get("previous_attempts", []),
        }
        for split in ("test", "test_ood"):
            result = summary["results"][split]
            row[split] = {"mean_source_macro_f1": result["mean_source_macro_f1"], "ci95": result["bootstrap"]["mean_source_macro_f1_ci95"],
                          "pooled_macro_f1": result["pooled"]["macro_f1"], "false_acceptance": result["pooled"]["false_acceptance"],
                          "false_warning": result["pooled"]["false_warning"], "truncated_units": result["pooled"]["truncated_units"],
                          "per_source": {source: cell["macro_f1"] for source, cell in result["source_subsets"].items()}}
        rows.append(row)
    paired = {split: paired_intervals(runs, split) for split in ("test", "test_ood")} if "mdeberta" in runs else {}
    result = {"created_at": datetime.now(timezone.utc).isoformat(), "suite_status": manifest["status"],
              "models": rows, "paired_vs_mdeberta": paired,
              "selection_note": "Thresholds use EN dev only. Test model rankings are descriptive, not winner selection.",
              "translation": "none; English-only checkpoint screening"}
    write_json(suite / "comparison.json", result)
    lines = ["# AttributionBench: local candidate comparison", "", f"Created {result['created_at']}.", "",
             "All attempted models use the same 1,198 EN dev / 1,610 ID / 1,686 OOD rows, 512-token cap, complete claims and ordered cited references.",
             "No training, Thai translation, application integration or external inference API calls. Downloads are recorded separately.",
             "Primary: unweighted mean source-subset Macro-F1, dev-selected thresholds. Test ordering is descriptive.",
             "", "| Model | ID Macro-F1 | OOD Macro-F1 | Dev Macro-F1 | Threshold | ID false acceptance | OOD false acceptance | Minutes | Peak allocated GiB |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        if row["status"] != "complete":
            lines.append(f"| {row['model']} ({row['status']}) | — | — | — | — | — | — | — | — |")
            continue
        peak = row["resources"]["cuda_peak_allocated_bytes"]
        memory = f"{peak / 2**30:.2f}" if peak is not None else "CPU"
        report = Path(row["report"]).relative_to(suite).as_posix()
        lines.append(f"| [{row['model']}]({report}) | {100 * row['test']['mean_source_macro_f1']:.2f} | "
                     f"{100 * row['test_ood']['mean_source_macro_f1']:.2f} | {100 * row['dev_mean_source_macro_f1']:.2f} | "
                     f"{row['threshold']:.2f} | {100 * row['test']['false_acceptance']['rate']:.2f} | "
                     f"{100 * row['test_ood']['false_acceptance']['rate']:.2f} | {row['runner_seconds'] / 60:.2f} | {memory} |")
    lines += ["", "## Paired differences from matched mDeBERTa", "",
              "Differences and CIs are percentage points. The same cluster resamples are applied to both compared models.", "",
              "| Model | ID difference [95% CI] | OOD difference [95% CI] |", "|---|---|---|"]
    for key in runs:
        if not paired:
            break
        values = []
        for split in ("test", "test_ood"):
            cell = paired[split][key]
            lo, hi = cell["delta_ci95"]
            values.append(f"{100 * cell['delta_mean_source_macro_f1']:+.2f} [{100 * lo:+.2f}, {100 * hi:+.2f}]")
        lines.append(f"| {key} | {values[0]} | {values[1]} |")
    lines += ["", "## Interpretation limits", "",
              "- MiniCheck uses its binary classifier directly; its native evidence-chunk/max wrapper is deliberately absent from this fixed-context comparison.",
              "- AttrScore uses normalized complete label-sequence likelihoods and its author prompt, not greedy generation. Prompt tokens reduce its evidence budget.",
              "- Tokenizers and required input formats differ. A shared 512-token cap is not identical evidence coverage; each report counts truncation and discarded tokens.",
              "- These are checkpoint/adapter comparisons. Different architectures, training corpora and input formats prevent attributing a score change to training objective alone.",
              "- ID/OOD name the official AttributionBench splits. Earlier training-data overlap for each downloaded checkpoint has not been audited.",
              "- Library load diagnostics remain in run.log. XLM-R's two extra pooler tensors are unused by the installed classifier path; the AttrScore loader leaves differing tied-weight values untied.",
              "- Runtime includes loading, input inspection, inference and metrics; download time is excluded. Peak allocated CUDA memory excludes driver/other-process memory.",
              "- DeBERTa-small and mDeBERTa execution partly overlapped checkpoint downloads. Timing is descriptive, not an isolated speed comparison.",
              "- Each row is one frozen execution. Native Thai case-domain generalization and fine-tuning are unmeasured.",
              "- The earlier batch-2 mDeBERTa run is preserved separately; this comparison uses the new matched batch-1 run.", ""]
    recovered = [row for row in rows if row.get("previous_attempts")]
    if recovered:
        lines += ["## Earlier attempts", "", "Successful retries preserve the original failures and their execution-source snapshots.", ""]
        for row in recovered:
            for attempt in row["previous_attempts"]:
                failure = attempt.get("failure", {})
                lines.append(f"- {row['model']}: {failure.get('type', attempt['status'])}: {failure.get('message', '')}; `{attempt['output']}`.")
    failures = [row for row in rows if row["status"] != "complete"]
    if failures:
        lines += ["## Recorded failures", ""]
        for row in failures:
            failure = row["failure"]
            lines.append(f"- {row['model']}: {failure['type']}: {failure['message']}" if failure else f"- {row['model']}: {row['status']}")
    (suite / "comparison.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"comparison": str(suite / "comparison.md"), "complete_models": list(runs)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    compare(parser.parse_args().suite.resolve())
