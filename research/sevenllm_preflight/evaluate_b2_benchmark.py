from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.pop("SSLKEYLOGFILE", None)

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .b2_config import (
    B2_MAX_INPUT_TOKENS,
    B2_MAX_TARGET_TOKENS,
    B2_MODEL_NAME,
    B2_MODEL_REVISION,
    FIXED_BENCHMARK_IDS,
    SELECTED_CATEGORIES,
    default_fixed_selection_path,
)
from .b2_leakage import load_fixed_benchmark_ids
from .b2_metrics import score_rows
from .b2_records import benchmark_id_for, build_input_text, language_for, load_data_file, write_jsonl
from .protocol import format_for


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fixed_rows(benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]) -> list[dict[str, Any]]:
    benchmark_ids = [benchmark_id_for(row) for row in benchmark_rows]
    if len(benchmark_ids) != len(set(benchmark_ids)):
        raise ValueError("Benchmark IDs are not unique")
    rows_by_id = {benchmark_id_for(row): row for row in benchmark_rows}
    if set(fixed_ids) != set(FIXED_BENCHMARK_IDS):
        raise ValueError("Evaluation requires the existing fixed 50 benchmark IDs")
    missing = sorted(set(fixed_ids) - set(rows_by_id), key=int)
    if missing:
        raise ValueError(f"Fixed benchmark rows are missing: {missing}")
    rows = [rows_by_id[sample_id] for sample_id in sorted(fixed_ids, key=int)]
    invalid = [
        str(row["id"])
        for row in rows
        if row.get("category") not in SELECTED_CATEGORIES or language_for(row) != "en"
    ]
    if invalid:
        raise ValueError(f"Fixed benchmark selection contains non-English or unsupported rows: {invalid}")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a supplied B2 checkpoint on the fixed 50-case benchmark")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--fixed-selection", type=Path, default=default_fixed_selection_path())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser.parse_args()


def choose_device(value: str) -> torch.device:
    if value == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available")
    if value == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(value)


def predict(rows: list[dict[str, Any]], model: Any, tokenizer: Any, device: torch.device, batch_size: int) -> list[dict[str, Any]]:
    model.eval()
    predictions: list[dict[str, Any]] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        inputs = tokenizer(
            [build_input_text(row) for row in batch],
            padding=True,
            truncation=True,
            max_length=B2_MAX_INPUT_TOKENS,
            return_tensors="pt",
        ).to(device)
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                do_sample=False,
                num_beams=1,
                max_new_tokens=B2_MAX_TARGET_TOKENS,
            )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        for row, raw in zip(batch, decoded):
            predictions.append(
                {
                    "condition": "B2",
                    "sample_id": str(row["id"]),
                    "category": row["category"],
                    "language": "en",
                    "format": format_for(row),
                    "input_text": build_input_text(row),
                    "gold_output_text": json.dumps(row["output"], ensure_ascii=False, separators=(",", ":"))
                    if isinstance(row["output"], (dict, list))
                    else str(row["output"]),
                    "prediction_raw": raw,
                }
            )
    return predictions


def main() -> None:
    args = parse_args()
    if args.batch_size < 1:
        raise ValueError("batch size must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fixed_ids = load_fixed_benchmark_ids(args.fixed_selection)
    rows = fixed_rows(load_data_file(args.benchmark), fixed_ids)
    device = choose_device(args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_path, local_files_only=True).to(device)
    predictions = predict(rows, model, tokenizer, device, args.batch_size)
    prediction_path = args.output_dir / "b2_benchmark_predictions.jsonl"
    write_jsonl(prediction_path, predictions)
    prediction_by_id = {record["sample_id"]: record for record in predictions}
    metrics = score_rows(rows, prediction_by_id)
    metrics["checkpoint_selection"] = "not performed"
    metrics["benchmark_scores_used_for_selection"] = False
    metrics_path = args.output_dir / "b2_benchmark_metrics.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "experiment": "SEvenLLM B2 fixed benchmark evaluation",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": {
            "path": str(args.model_path.resolve()),
            "name": B2_MODEL_NAME,
            "revision": B2_MODEL_REVISION,
            "config_sha256": file_sha256(args.model_path / "config.json") if (args.model_path / "config.json").exists() else None,
        },
        "benchmark": {
            "path": str(args.benchmark.resolve()),
            "sha256": file_sha256(args.benchmark),
            "fixed_selection_path": str(args.fixed_selection.resolve()),
            "fixed_ids": fixed_ids,
            "count": len(rows),
            "language": "English only",
            "test_only": True,
        },
        "generation": {
            "max_input_tokens": B2_MAX_INPUT_TOKENS,
            "max_new_tokens": B2_MAX_TARGET_TOKENS,
            "do_sample": False,
            "num_beams": 1,
            "device": str(device),
        },
        "outputs": {
            "predictions": str(prediction_path.resolve()),
            "metrics": str(metrics_path.resolve()),
        },
        "checkpoint_selection": "not performed",
        "benchmark_scores_used_for_selection": False,
    }
    manifest_path = args.output_dir / "b2_benchmark_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "predictions": str(prediction_path.resolve()),
                "metrics": str(metrics_path.resolve()),
                "manifest": str(manifest_path.resolve()),
                "sample_count": len(rows),
                "checkpoint_selection": "not performed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
