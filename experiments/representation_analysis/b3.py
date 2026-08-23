from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from experiments.context_refinement.metrics import load_sbert_model, score_condition
from experiments.context_refinement.reproducibility import runtime_device_report, set_deterministic_seed
from research.sevenllm_preflight.run_openrouter_b0 import DEFAULT_BASE_URL

from .constants import DEFAULT_OUTPUT_DIR, DEFAULT_SBERT_MODEL, DOWNSTREAM_GENERATION_CONFIG, DOWNSTREAM_MODEL, SEED
from .dataset import DEFAULT_BENCHMARK, DEFAULT_SELECTION, gold_text, load_reused_subset, sha256_file
from .runner import ensure_analysis
from .serializers import estimate_tokens
from .storage import index_records, write_json, write_jsonl, write_or_validate_json


DEFAULT_SOURCE_DIR = DEFAULT_OUTPUT_DIR
DEFAULT_B3_OUTPUT_DIR = DEFAULT_OUTPUT_DIR.parent / "pilot_28_b3"


def build_augmented_context(raw: str, events: str) -> str:
    event_block = events if events else "(no atomic events extracted)"
    return f"Raw narrative:\n{raw}\n\nSource-grounded atomic events:\n{event_block}"


def validate_sources(rows: list[dict[str, Any]], source_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    b0 = {key[0]: value for key, value in index_records(source_dir / "b0_analysis.jsonl", ("sample_id",)).items()}
    b2 = {key[0]: value for key, value in index_records(source_dir / "b2_extractions.jsonl", ("sample_id",)).items()}
    expected = {str(row["id"]) for row in rows}
    if set(b0) != expected or set(b2) != expected:
        raise ValueError("B3 requires complete frozen-28 B0 analysis and B2 extraction artifacts")
    for row in rows:
        sample_id = str(row["id"])
        if b0[sample_id].get("requested_model") != DOWNSTREAM_MODEL or b0[sample_id].get("generation_config") != DOWNSTREAM_GENERATION_CONFIG:
            raise ValueError(f"B0 contract mismatch for {sample_id}")
        if not b2[sample_id].get("extraction_success") or b2[sample_id].get("source") != str(row["input"]):
            raise ValueError(f"B2 extraction contract mismatch for {sample_id}")
    return b0, b2


def metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    return {"count": len(records), "rouge_l_mean": round(mean(record[condition]["rouge_l"] for record in records), 6), "sbert_mean": round(mean(record[condition]["sbert"] for record in records), 6)}


def paired_stats(records: list[dict[str, Any]], left: str, right: str, metric: str) -> dict[str, Any]:
    deltas = [record[left][metric] - record[right][metric] for record in records]
    return {"count": len(deltas), "mean_delta": round(mean(deltas), 6), "median_delta": round(median(deltas), 6), "improved": sum(value > 1e-6 for value in deltas), "degraded": sum(value < -1e-6 for value in deltas), "unchanged": sum(abs(value) <= 1e-6 for value in deltas)}


def build_results(rows: list[dict[str, Any]], b0: dict[str, dict[str, Any]], b2: dict[str, dict[str, Any]], b3: dict[str, dict[str, Any]], source_dir: Path, model: Any) -> list[dict[str, Any]]:
    scores = {"B0": score_condition(rows, b0, "B0", model), "B3": score_condition(rows, b3, "B3", model)}
    source_detail = {str(record["sample_id"]): record for record in __import__("experiments.representation_analysis.storage", fromlist=["read_jsonl"]).read_jsonl(source_dir / "detailed_results.jsonl")}
    records: list[dict[str, Any]] = []
    for row in rows:
        sample_id, raw = str(row["id"]), str(row["input"])
        augmented = b3[sample_id]["input_context"]
        records.append({"sample_id": sample_id, "category": row["category"], "task": row["task"], "instruction": row["instruction"], "gold_output": gold_text(row), "B0": {"input_chars": len(raw), "estimated_input_tokens": estimate_tokens(raw), "output": b0[sample_id]["prediction_raw"], **scores["B0"][sample_id]}, "B2": source_detail[sample_id]["B2"], "B3": {"input_chars": len(augmented), "estimated_input_tokens": estimate_tokens(augmented), "event_count": b2[sample_id]["event_count"], "output": b3[sample_id]["prediction_raw"], "returned_model": b3[sample_id]["returned_model"], **scores["B3"][sample_id]}})
    return records


def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["category"]].append(record)
    return {"experiment": "B3 raw narrative plus GLiNER2 event scaffold", "sample_count": len(records), "config": config, "overall": {condition: metric_stats(records, condition) for condition in ("B0", "B2", "B3")}, "by_task": {task: {condition: metric_stats(group, condition) for condition in ("B0", "B2", "B3")} for task, group in sorted(grouped.items())}, "pairwise": {f"B3-{right}": {metric: paired_stats(records, "B3", right, metric) for metric in ("rouge_l", "sbert")} for right in ("B0", "B2")}, "input_size": {condition: {"chars_mean": round(mean(record[condition]["input_chars"] for record in records), 3), "estimated_tokens_mean": round(mean(record[condition]["estimated_input_tokens"] for record in records), 3)} for condition in ("B0", "B2", "B3")}}


def render_report(summary: dict[str, Any]) -> str:
    lines = ["# B3: Raw narrative + GLiNER2 events", "", "| Condition | n | ROUGE-L | SBERT | Mean chars |", "|---|---:|---:|---:|---:|"]
    for condition in ("B0", "B2", "B3"):
        metric, size = summary["overall"][condition], summary["input_size"][condition]
        lines.append(f"| {condition} | {metric['count']} | {metric['rouge_l_mean']:.6f} | {metric['sbert_mean']:.6f} | {size['chars_mean']:.1f} |")
    lines.extend(["", "| Comparison | Metric | Mean delta | Median delta | Better | Worse | Same |", "|---|---|---:|---:|---:|---:|---:|"])
    for pair, metrics in summary["pairwise"].items():
        for metric, value in metrics.items():
            lines.append(f"| {pair} | {metric} | {value['mean_delta']:.6f} | {value['median_delta']:.6f} | {value['improved']} | {value['degraded']} | {value['unchanged']} |")
    return "\n".join(lines) + "\n"


def run(args: Any) -> None:
    rows, manifest = load_reused_subset(args.benchmark, args.selection)
    b0, b2 = validate_sources(rows, args.source_dir)
    set_deterministic_seed(args.seed); args.output_dir.mkdir(parents=True, exist_ok=True)
    config = {"experiment_version": "representation_analysis_b3_v1", "condition": "raw_plus_source_grounded_gliner2_events", "source_dir": str(args.source_dir), "source_hashes": {name: sha256_file(args.source_dir / name) for name in ("b0_analysis.jsonl", "b2_extractions.jsonl")}, "downstream": {"provider": "openrouter", "model": DOWNSTREAM_MODEL, "generation_config": DOWNSTREAM_GENERATION_CONFIG}, "context_template": "Raw narrative:\\n{raw}\\n\\nSource-grounded atomic events:\\n{events_or_empty_marker}", "seed": args.seed, "runtime": runtime_device_report(), "dataset": manifest}
    write_or_validate_json(args.output_dir / "run_config.json", config); write_or_validate_json(args.output_dir / "dataset_manifest.json", manifest)
    contexts = {sample_id: build_augmented_context(str(row["input"]), b2[sample_id]["serialized_context"]) for row in rows for sample_id in [str(row["id"])]}
    b3 = ensure_analysis(rows, "B3", contexts, args.output_dir / "b3_analysis.jsonl", args)
    model = load_sbert_model(args.sbert_model, args.sbert_device)
    records = build_results(rows, b0, b2, b3, args.source_dir, model)
    write_jsonl(args.output_dir / "detailed_results.jsonl", records)
    summary = build_summary(records, config); write_json(args.output_dir / "evaluation_summary.json", summary)
    (args.output_dir / "report.md").write_text(render_report(summary), encoding="utf-8")
    print(json.dumps({"output_dir": str(args.output_dir), "sample_count": len(rows), "report": str(args.output_dir / "report.md")}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run B3 raw narrative plus frozen GLiNER2 event scaffolding")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK); parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR); parser.add_argument("--output-dir", type=Path, default=DEFAULT_B3_OUTPUT_DIR)
    parser.add_argument("--sbert-model", default=DEFAULT_SBERT_MODEL); parser.add_argument("--sbert-device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY"); parser.add_argument("--base-url", default=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--timeout", type=float, default=120.0); parser.add_argument("--max-attempts", type=int, default=5); parser.add_argument("--backoff-base", type=float, default=1.0); parser.add_argument("--seed", type=int, default=SEED)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
