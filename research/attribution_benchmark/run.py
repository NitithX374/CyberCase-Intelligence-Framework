import argparse
import json
import platform
import shutil
import sys
import time
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from data import FILES, ROOT, read_split, sha256, verify_manifest
from inference import NliRunner
from metrics import argmax_reference, bootstrap, choose_threshold, grouped, predictions


class Tee:
    def __init__(self, logfile):
        self.logfile = logfile

    def write(self, text):
        self.logfile.write(text)
        sys.__stdout__.write(text)
        return len(text)

    def flush(self):
        self.logfile.flush()
        sys.__stdout__.flush()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def interval(values):
    return f"[{100 * values[0]:.2f}, {100 * values[1]:.2f}]"


def write_report(output, summary):
    model = summary["model"]
    threshold = summary["selection"]["threshold"]
    lines = [
        "# AttributionBench: local multilingual NLI baseline", "",
        f"Run completed {summary['finished_at']}. English original inputs; no translation or fine-tuning.", "",
        f"Model: `{model['model']}` @ `{model['revision']}`; {model['dtype']} on {model['device']} ({model['gpu']}).",
        f"Dataset: `{summary['dataset']['dataset']}` / subset_balanced @ `{summary['dataset']['revision']}`.", "",
        "Cited references are concatenated in their original order with two newlines as premise; the original claim is the hypothesis.",
        "The native 512-token input truncates only the premise from the right. The hypothesis is preserved. Empty cited-reference bundles remain in evaluation.",
        f"Predict attributable when p(entailment) >= {threshold:.2f}; threshold chosen solely on 1,198 EN development units.",
        "Selection maximizes mean source-subset Macro-F1 on a predeclared 0.01..0.99 grid; ties closest to 0.5 then lower threshold.", "",
        "## Primary results", "",
        "Scores are percentages. ID/OOD Avg is the unweighted mean of source-subset Macro-F1, matching the paper's aggregation.",
        "Pooled Macro-F1 is shown separately and weights subsets by their observed units. CI resamples question+response clusters within each source subset, 2,000 replicates, seed 20261006.", "",
        "| Test | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance rate | False warning rate |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for split, title in (("test", "ID"), ("test_ood", "OOD")):
        group = summary["results"][split]
        pooled = group["pooled"]
        lines.append(f"| {title} | {pooled['units']} | {100 * group['mean_source_macro_f1']:.2f} | "
                     f"{interval(group['bootstrap']['mean_source_macro_f1_ci95'])} | {100 * pooled['macro_f1']:.2f} | "
                     f"{100 * pooled['accuracy']:.2f} | {100 * pooled['false_acceptance']['rate']:.2f} | "
                     f"{100 * pooled['false_warning']['rate']:.2f} |")
    lines += ["", "False acceptance = gold not attributable predicted attributable / all gold not attributable. False warning = gold attributable predicted not attributable / all gold attributable.",
              "These class-conditional rates have different denominators from paper-style FP/FN percentages over all test units, which are also saved in summary.json.",
              "", "## Per-source results", "",
              "| Test | Source | Units | Macro-F1 | 95% CI | Accuracy | False acceptance | False warning | Truncated |",
              "|---|---|---:|---:|---|---:|---:|---:|---:|"]
    for split in ("test", "test_ood"):
        group = summary["results"][split]
        for source, cell in group["source_subsets"].items():
            ci = group["bootstrap"]["source_subsets"][source]["macro_f1_ci95"]
            lines.append(f"| {split} | {source} | {cell['units']} | {100 * cell['macro_f1']:.2f} | {interval(ci)} | "
                         f"{100 * cell['accuracy']:.2f} | {100 * cell['false_acceptance']['rate']:.2f} | "
                         f"{100 * cell['false_warning']['rate']:.2f} | {cell['truncated_units']} |")
    lines += ["", "## Class metrics and score ranking", "",
              "| Test | Gold class | Precision | Recall | F1 | Support |", "|---|---|---:|---:|---:|---:|"]
    for split in ("test", "test_ood"):
        pooled = summary["results"][split]["pooled"]
        for label, cell in pooled["per_class"].items():
            lines.append(f"| {split} | {label} | {100 * cell['precision']:.2f} | {100 * cell['recall']:.2f} | "
                         f"{100 * cell['f1-score']:.2f} | {int(cell['support'])} |")
    for split in ("test", "test_ood"):
        pooled = summary["results"][split]["pooled"]
        lines += [f"", f"{split} confusion rows/columns [not attributable, attributable]: `{pooled['confusion_matrix']}`.",
                  f"{split} score ranking, not attributable positive: AUROC={pooled['auroc_not_attributable']:.4f}, AP={pooled['ap_not_attributable']:.4f}."]
    lines += ["", "## Descriptive NLI argmax reference", "",
              "The same cached logits are mapped entailment -> attributable, neutral/contradiction -> not attributable; no second model inference or selection on test labels."]
    for split in ("test", "test_ood"):
        cell = summary["argmax_reference"][split]
        lines.append(f"- {split}: mean source Macro-F1 {100 * cell['mean_source_macro_f1']:.2f}, pooled Macro-F1 {100 * cell['pooled']['macro_f1']:.2f}.")
    timing = summary["timing"]
    lines += ["", "## Execution and limitations", "",
              f"- Valid outputs: {timing['completed_units']}/{timing['attempted_units']}; failures {timing['failures']}.",
              f"- Total dev+test runner wall time {timing['runner_wall_seconds']:.2f}s; model load {timing['model_load_seconds']:.2f}s.",
              f"- Batch latency p50/p95: {timing['batch_latency_p50_p95_seconds']}; amortized batch-time/unit p50/p95: {timing['amortized_unit_p50_p95_seconds']} seconds. Batch size {model['batch_size']}. This is amortized throughput timing, not single-request latency.",
              "- Local inference only; external model API calls/charges = 0. GPU/energy ownership cost is not monetized.",
              "- Full evidence beyond the native context window is discarded and counted. Scores measure the specified truncated-input NLI baseline, not full-document verification.",
              "- Binary not attributable combines partial, absent and contradictory support. Source support does not establish source truth.",
              "- No Thai inputs, native Thai case labels or downstream CyberCase report evaluation in this run.",
              "- This checkpoint is not one of AttributionBench's reported baselines; its results are a new measurement under the recorded input/decision protocol.",
              "", "## Reproduction", "", "```powershell", summary["command"], "```", "",
              "Dataset/model revisions, source and score hashes, package versions and input lengths are stored in the manifests and score JSONL. Threshold selection is recorded before test inference.",
              "", "Sources: [official dataset](https://huggingface.co/datasets/osunlp/AttributionBench), [AttributionBench paper](https://aclanthology.org/2024.findings-acl.886.pdf), [model card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7).", ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")


def execute(args, output):
    started = time.perf_counter()
    manifest = verify_manifest()
    splits = {split: read_split(split) for split in ("dev", "test", "test_ood")}
    runner = NliRunner(args.device, args.batch_size)
    lengths = {split: runner.inspect_inputs(rows) for split, rows in splits.items()}
    source_snapshot = output / "source_snapshot"
    source_snapshot.mkdir(exist_ok=False)
    source_files = ("data.py", "inference.py", "metrics.py", "run.py")
    for filename in source_files:
        shutil.copyfile(ROOT / filename, source_snapshot / filename)
    configuration = {
        "status": "running", "started_at": datetime.now(timezone.utc).isoformat(), "dataset": manifest,
        "model": runner.signature, "model_artifact_sha256": runner.artifact_hashes(),
        "source_sha256": {filename: sha256(source_snapshot / filename) for filename in source_files},
        "source_snapshot": "source_snapshot",
        "platform": platform.platform(), "python": sys.version,
        "inputs": {split: {"units": len(items), "truncated": sum(row['truncated'] for row in items),
                           "max_claim_tokens": max(row['claim_tokens'] for row in items)} for split, items in lengths.items()},
    }
    write_json(output / "run_manifest.json", configuration)
    print(json.dumps({"preflight": configuration["inputs"]}), flush=True)
    scores = {"dev": runner.score(splits["dev"], "dev", output / "scores_dev.jsonl", lengths["dev"])}
    selection = choose_threshold(scores["dev"])
    selection["selected_at"] = datetime.now(timezone.utc).isoformat()
    selection["dev_scores_sha256"] = sha256(output / "scores_dev.jsonl")
    write_json(output / "selection.json", selection)
    print(json.dumps({"frozen_threshold": selection['threshold'], "dev_mean_source_macro_f1": selection['dev_mean_source_macro_f1']}), flush=True)
    for split in ("test", "test_ood"):
        scores[split] = runner.score(splits[split], split, output / f"scores_{split}.jsonl", lengths[split])
    threshold = selection["threshold"]
    results = {split: grouped(rows, threshold) for split, rows in scores.items()}
    for split in ("test", "test_ood"):
        results[split]["bootstrap"] = bootstrap(scores[split], threshold)
    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(), "dataset": manifest, "model": runner.signature,
        "selection": selection, "results": results,
        "argmax_reference": {split: argmax_reference(scores[split]) for split in ("test", "test_ood")},
        "score_sha256": {split: sha256(output / f"scores_{split}.jsonl") for split in scores},
        "timing": {"attempted_units": sum(len(rows) for rows in splits.values()), "completed_units": runner.computed,
                   "failures": 0, "runner_wall_seconds": time.perf_counter() - started,
                   "model_load_seconds": runner.load_seconds,
                   "batch_latency_p50_p95_seconds": np.quantile(runner.batch_times, [0.5, 0.95]).tolist(),
                   "amortized_unit_p50_p95_seconds": np.quantile(runner.unit_times, [0.5, 0.95]).tolist()},
        "command": f"& '.\\env_mitre\\Scripts\\python.exe' -u 'research/attribution_benchmark/run.py' --device {args.device} --batch-size {args.batch_size}",
    }
    write_json(output / "summary.json", summary)
    write_report(output, summary)
    configuration.update(status="complete", finished_at=summary["finished_at"], summary_sha256=sha256(output / "summary.json"))
    write_json(output / "run_manifest.json", configuration)
    print(json.dumps({"complete": str(output), "primary": {split: results[split]["mean_source_macro_f1"] for split in ("test", "test_ood")}}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True, choices=("cpu", "cuda"))
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("nli_en_%Y%m%dT%H%M%SZ")
    output.mkdir(parents=True, exist_ok=False)
    with (output / "run.log").open("x", encoding="utf-8") as logfile, redirect_stdout(Tee(logfile)):
        print(f"Run directory: {output}", flush=True)
        try:
            execute(args, output)
        except Exception as error:
            write_json(output / "failure.json", {"type": type(error).__name__, "message": str(error), "at": datetime.now(timezone.utc).isoformat()})
            raise


if __name__ == "__main__":
    main()
