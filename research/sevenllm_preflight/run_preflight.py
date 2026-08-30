from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import sentencepiece as spm
import transformers
from transformers import AutoTokenizer

from .protocol import (
    SELECTED_CATEGORIES,
    build_b0_prompt,
    build_mt5_input,
    format_for,
    gold_output_text,
    instruction_text,
    language_for,
    metadata_for,
    FORMAT_COMPATIBILITY,
    PROMPT_PROTOCOL,
)
from .evaluation import SCORING_PROTOCOL
from .models import B0_CANDIDATES, B0_RECOMMENDATION
from .statistics import distribution, grouped_distributions, grouped_output_distributions


THRESHOLDS = (512, 768, 1024)


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def token_count(tokenizer: Any, text: str, add_eos: bool = True) -> int:
    return len(tokenizer(text, add_special_tokens=add_eos)["input_ids"])


def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row.get("category") in SELECTED_CATEGORIES]
    ids = [int(row["id"]) for row in selected]
    format_counts: dict[str, int] = {}
    invalid: list[dict[str, Any]] = []
    for row in selected:
        output_format = format_for(row)
        format_counts[output_format] = format_counts.get(output_format, 0) + 1
        if output_format == "choice":
            instruction = row["instruction"]
            valid_choices = isinstance(instruction, dict) and set(instruction.get("choice", {})) == {"A", "B", "C", "D"}
            valid_output = isinstance(row["output"], str) and row["output"] in {"A", "B", "C", "D"}
            if not valid_choices or not valid_output:
                invalid.append({"id": row["id"], "reason": "invalid choice structure"})
        elif output_format == "generation":
            if not isinstance(row["instruction"], str) or not isinstance(row["output"], str) or not row["output"].strip():
                invalid.append({"id": row["id"], "reason": "invalid generation structure"})
        elif not isinstance(row["instruction"], str) or not isinstance(row["output"], dict):
            invalid.append({"id": row["id"], "reason": "invalid extraction structure"})
    return {
        "dataset_row_count": len(rows),
        "selected_row_count": len(selected),
        "selected_ids_unique": len(ids) == len(set(ids)),
        "selected_id_minimum": min(ids),
        "selected_id_maximum": max(ids),
        "format_counts": dict(sorted(format_counts.items())),
        "invalid_records": invalid,
    }


def build_records(rows: list[dict[str, Any]], tokenizer: Any) -> list[dict[str, Any]]:
    records = []
    for row in rows:
        if row.get("category") not in SELECTED_CATEGORIES:
            continue
        input_text = build_mt5_input(row)
        output_text = gold_output_text(row)
        prefix_text = input_text.split("context:", 1)[0] + "context:"
        record = {
            **metadata_for(row),
            "input_tokens": token_count(tokenizer, input_text),
            "output_tokens": token_count(tokenizer, output_text),
            "prefix_tokens_without_eos": token_count(tokenizer, prefix_text, add_eos=False),
            "context_tokens_without_eos": token_count(tokenizer, str(row["input"]), add_eos=False),
            "input_text": input_text,
            "b0_prompt": build_b0_prompt(row),
            "gold_output_text": output_text,
            "instruction_text": instruction_text(row),
        }
        records.append(record)
    return sorted(records, key=lambda record: int(record["sample_id"]))


def truncation_analysis(records: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    affected = [record for record in records if int(record["input_tokens"]) > limit]
    right_context_loss = sum(max(0, int(record["input_tokens"]) - limit) for record in affected)
    left_prefix_loss = sum(min(int(record["prefix_tokens_without_eos"]), max(0, int(record["input_tokens"]) - limit)) for record in affected)
    return {
        "limit": limit,
        "affected_count": len(affected),
        "affected_percentage": round(100 * len(affected) / len(records), 3),
        "right_truncation": {
            "preserves_prefix": True,
            "loses_context_suffix": len(affected) > 0,
            "total_tokens_lost": right_context_loss,
        },
        "left_truncation": {
            "preserves_prefix": False,
            "loses_context_prefix": len(affected) > 0,
            "prefix_tokens_lost": left_prefix_loss,
        },
        "recommendation": "Do not truncate in this preflight; choose a pilot policy only after hardware smoke validation.",
    }


def longest_records(records: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    fields = ("sample_id", "category", "language", "format", "task", "input_tokens", "output_tokens")
    ordered = sorted(records, key=lambda record: int(record["input_tokens"]), reverse=True)[:limit]
    return [{field: record[field] for field in fields} for record in ordered]


def build_manifest(args: argparse.Namespace, tokenizer: dict[str, Any], config: dict[str, Any], validation: dict[str, Any], records: list[dict[str, Any]], input_stats: dict[str, Any], output_stats: dict[str, Any], truncation: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataset": {
            "source": "https://github.com/CSJianYang/SEevenLLM",
            "benchmark_file": "code/score/f1_rougel/test_all.jsonl",
            "commit": args.dataset_commit,
            "selected_categories": list(SELECTED_CATEGORIES),
            "sample_ids": [record["sample_id"] for record in records],
            "selected_count": len(records),
            "excluded_samples": [],
        },
        "models": {
            "B0": {
                "status": "selected from preflight comparison; weights not loaded",
                "recommendation": B0_RECOMMENDATION,
                "candidates": B0_CANDIDATES,
            },
            "B1": {
                "name": "google/mt5-base",
                "revision": args.model_revision,
                "status": "preflight only; no weights loaded",
                "tokenizer": tokenizer,
                "config": config,
            },
        },
        "prompt_protocol": {
            "mT5": "task: <category>\\ninstruction: <instruction or question/options>\\ncontext: <input>; choice rows append answer:",
            "B0": "same task, instruction, and context with only a minimal response-format instruction",
            "excluded_fields": ["thought", "gold output", "filename", "hidden metadata"],
        },
        "generation_parameters": {
            "B0": {"do_sample": False, "num_beams": 1, "max_new_tokens": 512, "temperature": None, "top_p": None},
            "B1": {"do_sample": False, "num_beams": 1, "max_new_tokens": 512},
        },
        "tokenization_statistics": {
            "input": input_stats,
            "output": output_stats,
            "truncation": truncation,
        },
        "format_compatibility": {
            "dataset_validation": validation,
            "templates": PROMPT_PROTOCOL,
            "formats": FORMAT_COMPATIBILITY,
        },
        "evaluation": SCORING_PROTOCOL,
        "runtime": {
            "python": sys.version.split()[0],
            "transformers": transformers.__version__,
            "sentencepiece": spm.__version__,
            "weights_loaded": False,
            "full_inference_run": False,
        },
        "verdict": {
            "status": "READY FOR PILOT",
            "input_policy": "no truncation; all 593 measured inputs are retained",
            "output_policy": "max_new_tokens=512 for both models",
            "operational_prerequisite": "pin transformers==5.8.0 and sentencepiece==0.2.2, or pin an equivalently verified pair before execution",
            "hard_blockers": [],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-commit", default="a84b86aabf2b5be35a2cbbac546511883cc5ff85")
    parser.add_argument("--model-revision", default="2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f")
    parser.add_argument("--conservative-limit", type=int, default=512)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_config = load_json(args.model_dir / "config.json")
    tokenizer_config = load_json(args.model_dir / "tokenizer_config.json")
    tokenizer_instance = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True)
    rows = load_rows(args.dataset)
    selected_rows = [row for row in rows if row.get("category") in SELECTED_CATEGORIES]
    validation = validate_rows(rows)
    records = build_records(selected_rows, tokenizer_instance)
    input_stats = {
        "all": distribution([int(record["input_tokens"]) for record in records], THRESHOLDS),
        "category": grouped_distributions(records, "category", THRESHOLDS),
        "language": grouped_distributions(records, "language", THRESHOLDS),
        "format": grouped_distributions(records, "format", THRESHOLDS),
    }
    input_stats["confirmed_practical_limit"] = None
    input_stats["confirmed_practical_limit_status"] = "UNCONFIRMED; mT5 config exposes relative attention rather than an absolute position limit"
    input_stats["exceeding_confirmed_practical_limit"] = None
    output_stats = {
        "all": distribution([int(record["output_tokens"]) for record in records], ()),
        "category": grouped_output_distributions(records, "category"),
        "language": grouped_output_distributions(records, "language"),
        "format": grouped_output_distributions(records, "format"),
    }
    tokenizer = {
        "name": "google/mt5-base",
        "revision": args.model_revision,
        "sentencepiece_version": spm.__version__,
        "transformers_version": transformers.__version__,
        "measurement_class": f"{tokenizer_instance.__class__.__module__}.{tokenizer_instance.__class__.__name__}",
        "is_fast": tokenizer_instance.is_fast,
        "config_tokenizer_class": model_config.get("tokenizer_class"),
        "tokenizer_config_model_max_length": tokenizer_config.get("model_max_length"),
        "reported_model_max_length": tokenizer_instance.model_max_length,
        "reported_model_max_length_source": "loaded tokenizer model_max_length; tokenizer_config omits model_max_length",
        "tokenizer_config_name_or_path": tokenizer_config.get("name_or_path"),
        "vocabulary_size": tokenizer_instance.vocab_size,
        "special_tokens": {
            "pad": tokenizer_instance.pad_token_id,
            "eos": tokenizer_instance.eos_token_id,
            "unk": tokenizer_instance.unk_token_id,
        },
        "eos_added_to_lengths": True,
    }
    config = {
        key: model_config.get(key)
        for key in (
            "model_type", "architectures", "vocab_size", "d_model", "d_ff", "d_kv", "num_layers",
            "num_decoder_layers", "num_heads", "relative_attention_num_buckets",
            "max_position_embeddings", "n_positions", "max_length", "is_encoder_decoder", "pad_token_id",
            "eos_token_id", "decoder_start_token_id", "transformers_version",
        )
    }
    config["relative_attention_max_distance"] = model_config.get("relative_attention_max_distance", 128)
    config["relative_attention_max_distance_serialized"] = model_config.get("relative_attention_max_distance")
    config["relative_attention_max_distance_source"] = "MT5Config default when absent from serialized config"
    truncation = truncation_analysis(records, args.conservative_limit)
    manifest = build_manifest(args, tokenizer, config, validation, records, input_stats, output_stats, truncation)
    manifest["longest_examples"] = longest_records(records)
    (args.output_dir / "preflight_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "preflight_records.jsonl").write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
