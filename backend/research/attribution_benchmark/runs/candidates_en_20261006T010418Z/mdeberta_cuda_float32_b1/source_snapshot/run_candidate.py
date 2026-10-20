import argparse
import json
import platform
import shutil
import sys
import time
import traceback
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from candidate_inference import CandidateRunner
from candidate_models import MODELS, metric_rows
from candidate_reports import write_json, write_report
from data import ROOT, read_split, sha256, verify_manifest
from metrics import argmax_reference, bootstrap, choose_threshold, grouped


SOURCE_FILES = (
    "data.py", "metrics.py", "candidate_models.py", "candidate_adapters.py", "candidate_inference.py",
    "candidate_reports.py", "run_candidate.py", "verify_candidate.py",
)


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


def execute(args, output, configuration):
    started = time.perf_counter()
    manifest = verify_manifest()
    configuration["dataset"] = manifest
    splits = {split: read_split(split) for split in ("dev", "test", "test_ood")}
    spec = MODELS[args.model]
    runner = CandidateRunner(spec, args.device, args.batch_size, args.precision)
    prepared = {split: runner.inspect_inputs(rows) for split, rows in splits.items()}
    configuration.update(
        model=runner.signature, model_artifact_sha256=runner.artifact_hashes(),
        inputs={split: {"units": len(rows), "truncated": sum(row["truncated"] for row in rows),
                        "max_claim_tokens": max(row["claim_tokens"] for row in rows),
                        "max_prompt_tokens": max(row["prompt_tokens"] for row in rows)}
                for split, (_, rows) in prepared.items()},
    )
    write_json(output / "run_manifest.json", configuration)
    print(json.dumps({"preflight": configuration["inputs"]}), flush=True)
    scores = {"dev": runner.score(splits["dev"], "dev", output / "scores_dev.jsonl", *prepared["dev"])}
    selection = choose_threshold(metric_rows(scores["dev"], spec.labels[spec.supported_index]))
    selection.update(selected_at=datetime.now(timezone.utc).isoformat(), dev_scores_sha256=sha256(output / "scores_dev.jsonl"))
    write_json(output / "selection.json", selection)
    print(json.dumps({"frozen_threshold": selection["threshold"], "dev_mean_source_macro_f1": selection["dev_mean_source_macro_f1"]}), flush=True)
    for split in ("test", "test_ood"):
        scores[split] = runner.score(splits[split], split, output / f"scores_{split}.jsonl", *prepared[split])
    converted = {split: metric_rows(rows, spec.labels[spec.supported_index]) for split, rows in scores.items()}
    results = {split: grouped(rows, selection["threshold"]) for split, rows in converted.items()}
    for split in ("test", "test_ood"):
        results[split]["bootstrap"] = bootstrap(converted[split], selection["threshold"])
    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(), "dataset": manifest, "model": runner.signature,
        "selection": selection, "results": results,
        "argmax_reference": {split: argmax_reference(converted[split]) for split in ("test", "test_ood")},
        "score_sha256": {split: sha256(output / f"scores_{split}.jsonl") for split in scores},
        "resources": runner.resource_usage(),
        "timing": {
            "attempted_units": sum(len(rows) for rows in splits.values()), "completed_units": runner.computed,
            "failures": 0, "runner_wall_seconds": time.perf_counter() - started, "model_load_seconds": runner.load_seconds,
            "batch_latency_p50_p95_seconds": np.quantile(runner.batch_times, [0.5, 0.95]).tolist(),
            "amortized_unit_p50_p95_seconds": np.quantile(runner.unit_times, [0.5, 0.95]).tolist(),
        },
        "command": configuration["command"],
    }
    write_json(output / "summary.json", summary)
    write_report(output, summary)
    configuration.update(status="complete", finished_at=summary["finished_at"], summary_sha256=sha256(output / "summary.json"))
    write_json(output / "run_manifest.json", configuration)
    print(json.dumps({"complete": str(output), "primary": {split: results[split]["mean_source_macro_f1"] for split in ("test", "test_ood")}}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=tuple(MODELS))
    parser.add_argument("--device", required=True, choices=("cpu", "cuda"))
    parser.add_argument("--precision", default="float32", choices=("float32", "float16"))
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source_snapshot = output / "source_snapshot"
    source_snapshot.mkdir()
    for filename in SOURCE_FILES:
        shutil.copyfile(ROOT / filename, source_snapshot / filename)
    configuration = {
        "schema_version": 2, "status": "running", "started_at": datetime.now(timezone.utc).isoformat(),
        "requested_model": args.model, "requested_device": args.device, "requested_precision": args.precision,
        "requested_batch_size": args.batch_size, "source_snapshot": "source_snapshot",
        "source_sha256": {filename: sha256(source_snapshot / filename) for filename in SOURCE_FILES},
        "platform": platform.platform(), "python": sys.version,
        "command": f"& '.\\env_mitre\\Scripts\\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model {args.model} --device {args.device} --precision {args.precision} --batch-size {args.batch_size} --output '{output}'",
    }
    write_json(output / "run_manifest.json", configuration)
    with (output / "run.log").open("x", encoding="utf-8") as logfile, redirect_stdout(Tee(logfile)):
        print(f"Run directory: {output}", flush=True)
        try:
            execute(args, output, configuration)
        except Exception as error:
            failure = {"type": type(error).__name__, "message": str(error), "at": datetime.now(timezone.utc).isoformat(),
                       "traceback": traceback.format_exc()}
            write_json(output / "failure.json", failure)
            configuration.update(status="failed", failure=failure)
            write_json(output / "run_manifest.json", configuration)
            raise


if __name__ == "__main__":
    main()
