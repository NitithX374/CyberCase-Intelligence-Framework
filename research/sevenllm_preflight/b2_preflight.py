from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sentencepiece as spm
import transformers
from transformers import AutoTokenizer

from .b2_config import (
    B2_BENCHMARK_COMMIT,
    B2_DATASET_FILE,
    B2_DATASET_REPOSITORY,
    B2_MAX_INPUT_TOKENS,
    B2_MAX_TARGET_TOKENS,
    B2_MODEL_NAME,
    B2_MODEL_REVISION,
    B2_SEED,
    B2_VALIDATION_RATIO,
    B2_EXCLUDED_FIELDS,
    SELECTED_CATEGORIES,
    default_fixed_selection_path,
    training_defaults,
)
from .b2_leakage import check_leakage, load_fixed_benchmark_ids
from .b2_records import load_data_file, filter_english_training_rows, write_jsonl
from .b2_split import category_counts, split_examples
from .statistics import percentile


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tokenize_lengths(tokenizer: Any, input_text: str, target_text: str) -> tuple[int, int]:
    input_tokens = tokenizer(input_text, add_special_tokens=True, truncation=False)["input_ids"]
    target_tokens = tokenizer(text_target=target_text, add_special_tokens=True, truncation=False)["input_ids"]
    return len(input_tokens), len(target_tokens)


def measure_examples(examples: list[dict[str, Any]], tokenizer: Any) -> list[dict[str, Any]]:
    measured: list[dict[str, Any]] = []
    for example in examples:
        input_tokens, target_tokens = tokenize_lengths(tokenizer, example["input_text"], example["target_text"])
        measured.append({**example, "input_tokens": input_tokens, "target_tokens": target_tokens})
    return measured


def length_summary(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]:
    values = [int(row[field]) for row in rows]
    exceeding = [row["example_id"] for row in rows if int(row[field]) > threshold]
    if not values:
        return {
            "count": 0,
            "p50": None,
            "p95": None,
            "maximum": None,
            "threshold": threshold,
            "exceeding_count": 0,
            "exceeding_example_ids": [],
        }
    return {
        "count": len(values),
        "p50": round(percentile(values, 0.50), 3),
        "p95": round(percentile(values, 0.95), 3),
        "maximum": max(values),
        "threshold": threshold,
        "exceeding_count": len(exceeding),
        "exceeding_example_ids": exceeding,
    }


def category_length_summary(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]:
    return {
        category: length_summary([row for row in rows if row["category"] == category], field, threshold)
        for category in SELECTED_CATEGORIES
    }


def tokenizer_metadata(tokenizer: Any, tokenizer_source: str) -> dict[str, Any]:
    return {
        "source": tokenizer_source,
        "name_or_path": tokenizer.name_or_path,
        "class": f"{tokenizer.__class__.__module__}.{tokenizer.__class__.__name__}",
        "is_fast": tokenizer.is_fast,
        "model_max_length": tokenizer.model_max_length,
        "vocab_size": tokenizer.vocab_size,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "sentencepiece_version": spm.__version__,
        "transformers_version": transformers.__version__,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the leakage-safe SEvenLLM B2 local preflight")
    parser.add_argument("--instruct-dataset", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--fixed-selection", type=Path, default=default_fixed_selection_path())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--tokenizer-path", type=Path)
    parser.add_argument("--model-revision", default=B2_MODEL_REVISION)
    parser.add_argument("--dataset-revision", default="main")
    parser.add_argument("--validation-ratio", type=float, default=B2_VALIDATION_RATIO)
    parser.add_argument("--seed", type=int, default=B2_SEED)
    return parser.parse_args()


def build_manifest(
    args: argparse.Namespace,
    filtered: list[dict[str, Any]],
    train: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    invalid: list[dict[str, Any]],
    leakage: dict[str, Any],
    tokenizer: dict[str, Any],
    hard_blockers: list[str],
    train_path: Path,
    validation_path: Path,
) -> dict[str, Any]:
    return {
        "experiment": "SEvenLLM B2 training",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "preflight": {
            "status": "PASS" if not hard_blockers else "FAIL",
            "passed": not hard_blockers,
            "hard_blockers": hard_blockers,
            "length_overflow_is_reported": True,
            "length_overflow_policy": "fixed-length right truncation during training; no rows are silently dropped",
        },
        "fixed_decisions": {
            "base_model": B2_MODEL_NAME,
            "model_revision": args.model_revision,
            "language": "English only",
            "training_source": f"{B2_DATASET_REPOSITORY}/{B2_DATASET_FILE}",
            "selected_categories": list(SELECTED_CATEGORIES),
            "input_template": "task: <category>\\ninstruction: <instruction>\\ncontext: <input>",
            "target_field": "output",
            "excluded_fields": list(B2_EXCLUDED_FIELDS),
            "benchmark_policy": "SEvenLLM-Bench is test-only",
            "first_run_epochs": training_defaults()["num_train_epochs"],
            "learning_rate": training_defaults()["learning_rate"],
            "optimizer": training_defaults()["optim"],
            "warmup_ratio": training_defaults()["warmup_ratio"],
            "gradient_checkpointing": True,
            "mixed_precision": "auto when supported",
            "seed": args.seed,
        },
        "source": {
            "instruct_dataset_path": str(args.instruct_dataset.resolve()),
            "instruct_dataset_sha256": file_sha256(args.instruct_dataset),
            "instruct_dataset_repository": B2_DATASET_REPOSITORY,
            "instruct_dataset_file": B2_DATASET_FILE,
            "instruct_dataset_revision": args.dataset_revision,
            "source_row_count": args.source_row_count,
            "benchmark_path": str(args.benchmark.resolve()),
            "benchmark_sha256": file_sha256(args.benchmark),
            "benchmark_commit": B2_BENCHMARK_COMMIT,
            "fixed_selection_path": str(args.fixed_selection.resolve()),
            "fixed_selection_sha256": file_sha256(args.fixed_selection),
        },
        "filter": {
            "filtered_training_examples": len(filtered),
            "category_counts": category_counts(filtered),
            "invalid_selected_records": invalid,
            "language": "en",
            "language_detection": "metadata or task token when present; otherwise exclude CJK characters from category, instruction, input, and output",
            "categories_are_exact": True,
        },
        "split": {
            "strategy": "deterministic category-stratified split",
            "validation_ratio": args.validation_ratio,
            "seed": args.seed,
            "train_count": len(train),
            "validation_count": len(validation),
            "train_category_counts": category_counts(train),
            "validation_category_counts": category_counts(validation),
            "train_example_ids": [row["example_id"] for row in train],
            "validation_example_ids": [row["example_id"] for row in validation],
        },
        "tokenizer": tokenizer,
        "tokenization": {
            "all": {
                "input": length_summary(filtered, "input_tokens", B2_MAX_INPUT_TOKENS),
                "target": length_summary(filtered, "target_tokens", B2_MAX_TARGET_TOKENS),
            },
            "train": {
                "input": length_summary(train, "input_tokens", B2_MAX_INPUT_TOKENS),
                "target": length_summary(train, "target_tokens", B2_MAX_TARGET_TOKENS),
            },
            "validation": {
                "input": length_summary(validation, "input_tokens", B2_MAX_INPUT_TOKENS),
                "target": length_summary(validation, "target_tokens", B2_MAX_TARGET_TOKENS),
            },
            "max_input_tokens": B2_MAX_INPUT_TOKENS,
            "max_target_tokens": B2_MAX_TARGET_TOKENS,
        },
        "leakage_check": leakage,
        "artifacts": {
            "train_jsonl": str(train_path.resolve()),
            "validation_jsonl": str(validation_path.resolve()),
            "train_jsonl_sha256": file_sha256(train_path),
            "validation_jsonl_sha256": file_sha256(validation_path),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "transformers": transformers.__version__,
            "sentencepiece": spm.__version__,
            "weights_loaded": False,
            "benchmark_scores_used": False,
        },
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.fixed_selection = args.fixed_selection.resolve()
    fixed_ids = load_fixed_benchmark_ids(args.fixed_selection)
    source_rows = load_data_file(args.instruct_dataset)
    benchmark_rows = load_data_file(args.benchmark)
    args.source_row_count = len(source_rows)
    filtered, invalid = filter_english_training_rows(source_rows)
    tokenizer_source = str(args.tokenizer_path.resolve()) if args.tokenizer_path else B2_MODEL_NAME
    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer_path if args.tokenizer_path else B2_MODEL_NAME,
        revision=None if args.tokenizer_path else args.model_revision,
        local_files_only=bool(args.tokenizer_path),
    )
    measured = measure_examples(filtered, tokenizer)
    train, validation = split_examples(measured, args.validation_ratio, args.seed)
    leakage = check_leakage({"train": train, "validation": validation}, benchmark_rows, fixed_ids)
    hard_blockers: list[str] = []
    if not measured:
        hard_blockers.append("no English examples remain after the exact category filter")
    if invalid:
        hard_blockers.append(f"{len(invalid)} selected English records failed schema validation")
    missing_categories = [category for category, count in category_counts(measured).items() if count == 0]
    if missing_categories:
        hard_blockers.append(f"selected categories have no English examples: {missing_categories}")
    if not leakage["passed"]:
        hard_blockers.append("training or validation overlaps SEvenLLM-Bench or the fixed 50 benchmark set")
    train_path = args.output_dir / "b2_train.jsonl"
    validation_path = args.output_dir / "b2_validation.jsonl"
    write_jsonl(train_path, train)
    write_jsonl(validation_path, validation)
    manifest = build_manifest(
        args,
        measured,
        train,
        validation,
        invalid,
        leakage,
        tokenizer_metadata(tokenizer, tokenizer_source),
        hard_blockers,
        train_path,
        validation_path,
    )
    manifest_path = args.output_dir / "b2_dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "manifest": str(manifest_path.resolve()),
                "status": manifest["preflight"]["status"],
                "filtered_training_examples": len(measured),
                "category_counts": manifest["filter"]["category_counts"],
                "train_count": len(train),
                "validation_count": len(validation),
                "input_tokens": manifest["tokenization"]["all"]["input"],
                "target_tokens": manifest["tokenization"]["all"]["target"],
                "leakage_passed": leakage["passed"],
                "hard_blockers": hard_blockers,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if hard_blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
