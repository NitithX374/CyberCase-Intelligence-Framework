from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.sevenllm_preflight.protocol import format_for, language_for

from .compressor import LLMLingua2Refiner
from .dataset import load_reused_subset
from .evaluation import evaluate_pairs
from .llm_client import GENERATION_CONFIG, MODEL, OpenRouterPilotClient
from .metrics import load_sbert_model
from .prompting import build_condition_prompt, validate_context_only_prompt_change
from .protected_spans import compare_protected_spans
from .reproducibility import runtime_device_report, set_deterministic_seed
from .reporting import build_summary, render_markdown
from .storage import append_jsonl, index_records, write_json, write_jsonl, write_or_validate_json


RAW_CONTEXT_FILE = "raw_contexts.jsonl"
REFINED_CONTEXT_FILE = "refined_contexts.jsonl"
PREDICTION_FILE = "predictions.jsonl"
PAIRED_FILE = "paired_results.jsonl"
CONFIG_FILE = "run_config.json"
DATASET_MANIFEST_FILE = "dataset_manifest.json"


def _raw_context_record(row: dict[str, Any]) -> dict[str, Any]:
    context = str(row["input"])
    return {
        "sample_id": str(row["id"]),
        "category": row["category"],
        "task": row["task"],
        "language": language_for(row),
        "format": format_for(row),
        "raw_context": context,
        "raw_context_chars": len(context),
    }


def _refined_context_record(row: dict[str, Any], result: Any, refiner_config: dict[str, Any]) -> dict[str, Any]:
    raw_context = result.raw_context
    refined_context = result.refined_context
    return {
        "sample_id": str(row["id"]),
        "category": row["category"],
        "task": row["task"],
        "language": language_for(row),
        "format": format_for(row),
        "raw_context": raw_context,
        "refined_context": refined_context,
        "raw_context_chars": len(raw_context),
        "refined_context_chars": len(refined_context),
        "origin_tokens": result.origin_tokens,
        "refined_tokens": result.refined_tokens,
        "protected_span_diagnostics": compare_protected_spans(raw_context, refined_context),
        "refiner_config": refiner_config,
    }


def _ensure_raw_contexts(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]:
    indexed = index_records(path, ("sample_id",))
    for row in rows:
        sample_id = str(row["id"])
        expected = _raw_context_record(row)
        existing = indexed.get((sample_id,))
        if existing is None:
            append_jsonl(path, expected)
            indexed[(sample_id,)] = expected
        elif existing != expected:
            raise ValueError(f"Raw context artifact differs for sample {sample_id}")
    return {key[0]: value for key, value in indexed.items()}


def _ensure_refined_contexts(
    rows: list[dict[str, Any]],
    path: Path,
    refiner: LLMLingua2Refiner,
) -> dict[str, dict[str, Any]]:
    indexed = index_records(path, ("sample_id",))
    for row in rows:
        sample_id = str(row["id"])
        existing = indexed.get((sample_id,))
        if existing is None:
            result = refiner.refine(str(row["input"]))
            record = _refined_context_record(row, result, refiner.config)
            append_jsonl(path, record)
            indexed[(sample_id,)] = record
        else:
            if existing.get("refiner_config") != refiner.config:
                raise ValueError(f"Refiner configuration differs for sample {sample_id}")
            if existing.get("raw_context") != str(row["input"]):
                raise ValueError(f"Refiner raw context differs for sample {sample_id}")
    return {key[0]: value for key, value in indexed.items()}


def _prediction_record(
    row: dict[str, Any],
    condition: str,
    context: str,
    prompt: str,
    response: dict[str, Any],
) -> dict[str, Any]:
    return {
        **response,
        "sample_id": str(row["id"]),
        "category": row["category"],
        "task": row["task"],
        "language": language_for(row),
        "format": format_for(row),
        "condition": condition,
        "context_variant": "raw" if condition == "B0" else "refined",
        "input_context": context,
        "prompt": prompt,
    }


def _ensure_predictions(
    rows: list[dict[str, Any]],
    condition: str,
    contexts: dict[str, dict[str, Any]],
    prediction_path: Path,
    client: OpenRouterPilotClient,
    existing: dict[tuple[str, str], dict[str, Any]],
) -> None:
    for row in rows:
        sample_id = str(row["id"])
        key = (sample_id, condition)
        if key in existing:
            record = existing[key]
            if record.get("error") or record.get("requested_model") != MODEL or record.get("generation_config") != GENERATION_CONFIG:
                raise ValueError(f"Existing prediction contract is invalid for {key}")
            continue
        context = contexts[sample_id]["raw_context"] if condition == "B0" else contexts[sample_id]["refined_context"]
        prompt = build_condition_prompt(row, context)
        if condition == "B1":
            validate_context_only_prompt_change(row, contexts[sample_id]["raw_context"], context)
        response = client.predict(prompt, sample_id, condition)
        record = _prediction_record(row, condition, context, prompt, response)
        append_jsonl(prediction_path, record)
        existing[key] = record


def _run_config(args: Any, dataset_manifest: dict[str, Any], runtime: dict[str, Any], seed_report: dict[str, Any]) -> dict[str, Any]:
    compressor = None
    if args.condition in {"refined", "both"}:
        compressor = {
            "name": "llmlingua2",
            "model_name": args.compressor_model,
            "compression_rate": args.compression_rate,
            "device_map": args.compressor_device or runtime["device"],
            "force_tokens": [],
            "force_reserve_digit": False,
            "task_aware": False,
        }
    return {
        "experiment_version": "context_refinement_v1",
        "dataset": dataset_manifest,
        "categories": list(dataset_manifest["categories"]),
        "language": "en",
        "conditions": args.condition,
        "seed": args.seed,
        "seed_report": seed_report,
        "runtime": runtime,
        "llm": {
            "provider": "openrouter",
            "model": MODEL,
            "base_url": args.base_url.rstrip("/"),
            "generation_config": GENERATION_CONFIG,
            "api_key_env": args.api_key_env,
        },
        "compressor": compressor,
        "evaluation": {
            "rouge_l": "research.sevenllm_preflight.score_pilot.rouge_l",
            "sbert": args.sbert_model,
            "sbert_device": args.sbert_device,
            "llm_judge": None,
        },
        "protocol": {
            "prompt_source": "research.sevenllm_preflight.protocol.build_b0_prompt",
            "context_only_difference": True,
            "thought_used": False,
        },
    }


def _write_report(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], sbert_model_name: str, sbert_device: str) -> None:
    raw_contexts = {key[0]: value for key, value in index_records(output_dir / RAW_CONTEXT_FILE, ("sample_id",)).items()}
    refined_contexts = {key[0]: value for key, value in index_records(output_dir / REFINED_CONTEXT_FILE, ("sample_id",)).items()}
    prediction_records = index_records(output_dir / PREDICTION_FILE, ("sample_id", "condition"))
    expected_keys = {(str(row["id"]), condition) for row in rows for condition in ("B0", "B1")}
    if set(prediction_records) != expected_keys:
        raise ValueError("Cannot report until every paired B0/B1 prediction is present")
    model = load_sbert_model(sbert_model_name, sbert_device)
    paired = evaluate_pairs(rows, raw_contexts, refined_contexts, prediction_records, model)
    write_jsonl(output_dir / PAIRED_FILE, paired)
    summary = build_summary(paired, config)
    write_json(output_dir / "evaluation_summary.json", summary)
    (output_dir / "report.md").write_text(render_markdown(summary), encoding="utf-8")


def run_experiment(args: Any) -> None:
    if args.condition == "both" and not args.sbert_model:
        raise ValueError("--sbert-model is required for a paired run")
    rows, dataset_manifest = load_reused_subset(args.benchmark, args.selection)
    runtime = runtime_device_report()
    seed_report = set_deterministic_seed(args.seed)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    config = _run_config(args, dataset_manifest, runtime, seed_report)
    write_or_validate_json(output_dir / CONFIG_FILE, config)
    write_or_validate_json(output_dir / DATASET_MANIFEST_FILE, dataset_manifest)
    raw_contexts = _ensure_raw_contexts(rows, output_dir / RAW_CONTEXT_FILE)
    refined_contexts: dict[str, dict[str, Any]] = {}
    if args.condition in {"refined", "both"}:
        refiner = LLMLingua2Refiner(
            model_name=args.compressor_model,
            compression_rate=args.compression_rate,
            device_map=args.compressor_device or runtime["device"],
        )
        refined_contexts = _ensure_refined_contexts(rows, output_dir / REFINED_CONTEXT_FILE, refiner)
    prediction_path = output_dir / PREDICTION_FILE
    predictions = index_records(prediction_path, ("sample_id", "condition"))
    needed_conditions = ["B0"] if args.condition == "raw" else ["B1"] if args.condition == "refined" else ["B0", "B1"]
    missing = [condition for condition in needed_conditions if any((str(row["id"]), condition) not in predictions for row in rows)]
    if missing:
        with OpenRouterPilotClient(
            api_key_env=args.api_key_env,
            base_url=args.base_url,
            timeout=args.timeout,
            max_attempts=args.max_attempts,
            backoff_base=args.backoff_base,
        ) as client:
            for condition in needed_conditions:
                contexts = raw_contexts if condition == "B0" else refined_contexts
                _ensure_predictions(rows, condition, contexts, prediction_path, client, predictions)
    if args.condition == "both":
        _write_report(output_dir, rows, config, args.sbert_model, args.sbert_device)
    print(json.dumps({"output_dir": str(output_dir), "sample_count": len(rows), "condition": args.condition}, indent=2))


def report_existing(args: Any) -> None:
    rows, _ = load_reused_subset(args.benchmark, args.selection)
    output_dir = args.output_dir
    config = json.loads((output_dir / CONFIG_FILE).read_text(encoding="utf-8"))
    stored_sbert = config.get("evaluation", {}).get("sbert")
    if stored_sbert not in {None, args.sbert_model}:
        raise ValueError("Report SBERT model differs from the stored run configuration")
    config["evaluation"] = {
        **config.get("evaluation", {}),
        "sbert": args.sbert_model,
        "sbert_device": args.sbert_device,
    }
    _write_report(output_dir, rows, config, args.sbert_model, args.sbert_device)
    print(json.dumps({"output_dir": str(output_dir), "sample_count": len(rows), "report": str(output_dir / "report.md")}, indent=2))
