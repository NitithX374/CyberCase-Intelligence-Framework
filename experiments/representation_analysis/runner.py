from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from experiments.context_refinement.llm_client import OpenRouterPilotClient
from experiments.context_refinement.metrics import load_sbert_model, score_condition
from experiments.context_refinement.reproducibility import runtime_device_report, set_deterministic_seed

from .analysis import analysis_record, validate_shared_prompt, validated_b0_cache
from .constants import CONDITIONS, DOWNSTREAM_GENERATION_CONFIG, DOWNSTREAM_MODEL, EVENT_SCHEMA, EXPERIMENT_VERSION, REPRESENTATION_TYPES
from .dataset import gold_text, load_reused_subset
from .diagnostics import possible_unsupported_surface_values, retention_diagnostics
from .gliner_adapter import GlinerEventExtractor
from .production_extraction import extract_case_state, production_extraction_contract
from .reporting import build_summary, render_markdown
from .serializers import estimate_tokens, serialize_case_state, serialize_events
from .storage import append_jsonl, index_records, write_json, write_jsonl, write_or_validate_json


STAGE_FILES = {"B0": "b0_analysis.jsonl", "B1x": "b1_extractions.jsonl", "B1": "b1_analysis.jsonl", "B2x": "b2_extractions.jsonl", "B2": "b2_analysis.jsonl"}


def run_config(args: Any, manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "experiment_version": EXPERIMENT_VERSION, "dataset": manifest, "seed": args.seed,
        "conditions": {"B0": "raw narrative", "B1": "production LLM CaseState", "B2": "GLiNER2 atomic events"},
        "downstream": {"provider": "openrouter", "model": DOWNSTREAM_MODEL, "generation_config": DOWNSTREAM_GENERATION_CONFIG, "prompt": "research.sevenllm_preflight.protocol.build_b0_prompt", "api_key_env": args.api_key_env, "base_url": args.base_url.rstrip("/")},
        "b1": production_extraction_contract(),
        "b2": {"model": args.gliner_model, "device": args.gliner_device, "threshold": args.gliner_threshold, "schema": EVENT_SCHEMA, "source_grounding_required": True, "fallback": None},
        "evaluation": {"rouge_l": "research.sevenllm_preflight.score_pilot.rouge_l", "sbert": args.sbert_model, "sbert_device": args.sbert_device},
        "protocol": {"language": "en", "thought_used": False, "context_only_difference": True, "benchmark_used_for_selection": False},
    }


async def ensure_b1(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]:
    indexed = index_records(path, ("sample_id",))
    for row in rows:
        sample_id, source = str(row["id"]), str(row["input"])
        if (sample_id,) not in indexed:
            result = await extract_case_state(sample_id, source)
            context = serialize_case_state(result["case_state"]) if result["extraction_success"] else None
            record = {"sample_id": sample_id, "category": row["category"], "source": source, "serialized_context": context, **result}
            if context is not None:
                record["diagnostics"] = retention_diagnostics(source, context)
                record["possible_unsupported_surface_values"] = possible_unsupported_surface_values(source, result["case_state"])
            append_jsonl(path, record)
            indexed[(sample_id,)] = record
    return {key[0]: value for key, value in indexed.items()}


def ensure_b2(rows: list[dict[str, Any]], path: Path, args: Any) -> dict[str, dict[str, Any]]:
    indexed = index_records(path, ("sample_id",))
    missing = [row for row in rows if (str(row["id"]),) not in indexed]
    extractor = GlinerEventExtractor(args.gliner_model, args.gliner_device, args.gliner_threshold) if missing else None
    for row in missing:
        sample_id, source = str(row["id"]), str(row["input"])
        result = extractor.extract(source)
        context = serialize_events(result["events"]) if result["extraction_success"] else None
        record = {"sample_id": sample_id, "category": row["category"], "source": source, "serialized_context": context, "diagnostics": retention_diagnostics(source, context or ""), **result}
        append_jsonl(path, record)
        indexed[(sample_id,)] = record
    return {key[0]: value for key, value in indexed.items()}


def ensure_analysis(rows: list[dict[str, Any]], condition: str, contexts: dict[str, str], path: Path, args: Any, cache: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    indexed = index_records(path, ("sample_id",))
    missing = [row for row in rows if (str(row["id"]),) not in indexed]
    if condition == "B0" and cache:
        for row in list(missing):
            sample_id = str(row["id"])
            if sample_id in cache:
                record = analysis_record(row, condition, contexts[sample_id], cache[sample_id], str(args.b0_cache))
                append_jsonl(path, record); indexed[(sample_id,)] = record; missing.remove(row)
    if missing:
        with OpenRouterPilotClient(args.api_key_env, args.base_url, args.timeout, args.max_attempts, args.backoff_base) as client:
            for row in missing:
                sample_id, context = str(row["id"]), contexts[str(row["id"])]
                if condition != "B0": validate_shared_prompt(row, context)
                prompt = __import__("experiments.representation_analysis.prompting", fromlist=["build_condition_prompt"]).build_condition_prompt(row, context)
                record = analysis_record(row, condition, context, client.predict(prompt, sample_id, condition))
                append_jsonl(path, record); indexed[(sample_id,)] = record
    return {key[0]: value for key, value in indexed.items()}


def assemble(rows: list[dict[str, Any]], analyses: dict[str, dict[str, dict[str, Any]]], extractions: dict[str, dict[str, dict[str, Any]]], model: Any) -> list[dict[str, Any]]:
    scored_rows = {condition: [row for row in rows if str(row["id"]) in analyses[condition]] for condition in CONDITIONS}
    scores = {condition: score_condition(scored_rows[condition], analyses[condition], condition, model) for condition in CONDITIONS}
    records: list[dict[str, Any]] = []
    for row in rows:
        sample_id, source = str(row["id"]), str(row["input"])
        record: dict[str, Any] = {"sample_id": sample_id, "category": row["category"], "task": row["task"], "instruction": row["instruction"], "language": "en", "gold_output": gold_text(row)}
        for condition in CONDITIONS:
            analysis = analyses[condition].get(sample_id)
            extraction = extractions.get(condition, {}).get(sample_id, {})
            if analysis is None:
                record[condition] = {"status": "extraction_failed", "representation_type": REPRESENTATION_TYPES[condition], "failure_code": extraction.get("failure_code"), "failure_reason": extraction.get("failure_reason"), "extraction_diagnostics": {"latency_ms": extraction.get("latency_ms"), "model": extraction.get("model")}, "rouge_l": None, "sbert": None}
                continue
            diagnostics = retention_diagnostics(source, analysis["input_context"])
            record[condition] = {"status": "complete", "representation_type": REPRESENTATION_TYPES[condition], "analysis_input": source if condition == "B0" else extraction.get("case_state", extraction.get("events")), "serialized_input": analysis["input_context"], "input_chars": len(analysis["input_context"]), "estimated_input_tokens": estimate_tokens(analysis["input_context"]), "diagnostics": diagnostics, "extraction_diagnostics": {"latency_ms": extraction.get("latency_ms"), "model": extraction.get("model"), "confidence": extraction.get("confidence"), "rejected_values": extraction.get("rejected_values"), "possible_unsupported_surface_values": extraction.get("possible_unsupported_surface_values")}, "downstream_output": analysis["prediction_raw"], "returned_model": analysis["returned_model"], **scores[condition][sample_id]}
        records.append(record)
    return records


def run_experiment(args: Any) -> None:
    rows, manifest = load_reused_subset(args.benchmark, args.selection)
    set_deterministic_seed(args.seed); output = args.output_dir; output.mkdir(parents=True, exist_ok=True)
    config = run_config(args, manifest); config["runtime"] = runtime_device_report()
    write_or_validate_json(output / "run_config.json", config); write_or_validate_json(output / "dataset_manifest.json", manifest)
    b1 = asyncio.run(ensure_b1(rows, output / STAGE_FILES["B1x"]))
    b2 = ensure_b2(rows, output / STAGE_FILES["B2x"], args)
    failures = [sample_id for sample_id, value in b2.items() if not value["extraction_success"]]
    if failures: raise RuntimeError(f"B2 extraction failed without fallback: {failures}")
    contexts = {"B0": {str(row["id"]): str(row["input"]) for row in rows}, "B1": {key: value["serialized_context"] for key, value in b1.items() if value["extraction_success"]}, "B2": {key: value["serialized_context"] for key, value in b2.items()}}
    cache = validated_b0_cache(args.b0_cache, rows) if args.b0_cache.exists() else {}
    analyses = {condition: ensure_analysis([row for row in rows if str(row["id"]) in contexts[condition]], condition, contexts[condition], output / STAGE_FILES[condition], args, cache if condition == "B0" else None) for condition in CONDITIONS}
    model = load_sbert_model(args.sbert_model, args.sbert_device)
    records = assemble(rows, analyses, {"B1": b1, "B2": b2}, model)
    write_jsonl(output / "detailed_results.jsonl", records)
    summary = build_summary(records, config); write_json(output / "evaluation_summary.json", summary)
    (output / "report.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps({"output_dir": str(output), "sample_count": len(rows), "report": str(output / "report.md")}, indent=2))
