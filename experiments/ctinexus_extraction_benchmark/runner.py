from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from .runtime import prepare_runtime

prepare_runtime()

from .cache import append_jsonl, cache_matches, load_jsonl_cache, write_json
from .constants import (
    DATASET_SPLIT,
    DEFAULT_DATASET_DIR,
    DEFAULT_OUTPUT_DIR,
    EXPERIMENT_VERSION,
    GLINER_MODEL,
    CTINEXUS_ENTITY_TYPES,
    GLINER_RELATION_SCHEMA,
    GLINER_SCHEMA_VERSION,
    GLINER_THRESHOLD,
    NORMALIZATION_VERSION,
    PRODUCTION_MODEL,
    PRODUCTION_PROMPT_VERSION,
    PRODUCTION_SCHEMA_VERSION,
)
from .dataset import CTINexusCase, dataset_manifest, load_ctinexus_cases
from .evaluation import combined_error_examples, evaluate_condition
from .gliner import CtinexusGlinerExtractor, resolve_device
from .production import extract_production
from .projection import gliner_prediction, production_prediction
from .report import write_report
from .schemas import ExtractorPrediction


def _contracts(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "E1": {
            "model": config["production"]["model"],
            "prompt_version": config["production"]["prompt_version"],
            "schema_version": config["production"]["schema_version"],
        },
        "E2": {
            "model": config["gliner"]["model"],
            "schema_version": config["gliner"]["schema_version"],
            "threshold": config["gliner"]["threshold"],
            "relation_label_mode": "source_span_free_text",
        },
    }


def _config(output_dir: Path, dataset_dir: Path, gliner_device: str) -> dict[str, Any]:
    return {
        "experiment_version": EXPERIMENT_VERSION,
        "dataset_split": DATASET_SPLIT,
        "dataset_dir": str(dataset_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "normalization_version": NORMALIZATION_VERSION,
        "downstream_analysis_called": False,
        "production": {
            "model": PRODUCTION_MODEL,
            "entrypoint": "backend.app.services.extraction.extraction_runner.run_baseline_extraction",
            "prompt_version": PRODUCTION_PROMPT_VERSION,
            "schema_version": PRODUCTION_SCHEMA_VERSION,
        },
        "gliner": {
            "model": GLINER_MODEL,
            "device": resolve_device(gliner_device),
            "threshold": GLINER_THRESHOLD,
            "schema_version": GLINER_SCHEMA_VERSION,
            "entity_types": list(CTINEXUS_ENTITY_TYPES),
            "relation_schema": GLINER_RELATION_SCHEMA,
        },
        "evaluation": {
            "entity": "existing CTINexus exact normalized entity metric",
            "endpoint_edge": "existing CTINexus exact directed endpoint metric",
            "triplet": "existing CTINexus exact normalized directed triplet metric",
        },
    }


def _verify_config(output_dir: Path, config: dict[str, Any]) -> None:
    path = output_dir / "run_config.json"
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing_core = {key: value for key, value in existing.items() if key != "cache"}
        legacy = json.loads(json.dumps(config))
        legacy["gliner"].pop("entity_types", None)
        legacy["gliner"].pop("relation_schema", None)
        if existing_core == legacy:
            write_json(path, config)
        elif existing_core != config:
            raise ValueError(f"Existing output directory has a different benchmark contract: {path}")
    else:
        write_json(path, config)


def _offline_e1(case: CTINexusCase, config: dict[str, Any]) -> ExtractorPrediction:
    return production_prediction(
        case,
        None,
        model=config["production"]["model"],
        status="failed",
        failure_code="offline_smoke_only",
        failure_message="Offline smoke mode does not call the production model.",
        latency_ms=0.0,
        input_tokens=None,
        output_tokens=None,
        diagnostics={"api_calls": 0, "validation_failure": False, "empty_output": True},
        contract=config["production"],
    )


def _offline_e2(case: CTINexusCase, config: dict[str, Any]) -> ExtractorPrediction:
    prediction = gliner_prediction(
        case,
        model=config["gliner"]["model"],
        entities=[],
        relations=[],
        latency_ms=0.0,
        diagnostics={"device": config["gliner"]["device"], "model_load_ms": 0.0, "rejected_values": [], "source_grounding_failure_count": 0, "empty_output": True, "confidence": {"count": 0}},
        contract={"model": config["gliner"]["model"], "schema_version": config["gliner"]["schema_version"], "threshold": config["gliner"]["threshold"], "relation_label_mode": "source_span_free_text"},
    )
    prediction.status = "failed"
    prediction.graph.status = "failed"
    prediction.graph.failure_code = "offline_smoke_only"
    prediction.graph.failure_message = "Offline smoke mode does not load GLiNER2."
    return prediction


async def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    dataset_dir = Path(args.dataset_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    cases = load_ctinexus_cases(dataset_dir)
    if not cases:
        raise ValueError("The CTINexus test split contains no usable documents")
    config = _config(output_dir, dataset_dir, args.gliner_device)
    _verify_config(output_dir, config)
    manifest = dataset_manifest(cases, dataset_dir)
    write_json(output_dir / "dataset_manifest.json", manifest)
    contracts = _contracts(config)

    e1_cache_path = output_dir / "E1_production_predictions.jsonl"
    e2_cache_path = output_dir / "E2_gliner2_predictions.jsonl"
    e1_cache = load_jsonl_cache(e1_cache_path)
    e2_cache = load_jsonl_cache(e2_cache_path)
    e1_predictions: dict[str, ExtractorPrediction] = {}
    e2_predictions: dict[str, ExtractorPrediction] = {}
    e1_reused = 0
    e2_reused = 0

    for index, case in enumerate(cases, 1):
        cached = e1_cache.get(case.document.doc_id)
        if cached and cache_matches(cached, condition="E1", doc_id=case.document.doc_id, narrative_sha256=case.narrative_sha256, contract=contracts["E1"]):
            prediction = cached
            e1_reused += 1
        else:
            prediction = _offline_e1(case, config) if args.dry_run else await extract_production(case, config["production"]["model"])
            append_jsonl(e1_cache_path, prediction)
        e1_predictions[case.document.doc_id] = prediction
        print(f"E1 [{index}/{len(cases)}] {case.document.doc_id}: {prediction.status} entities={len(prediction.graph.entities)} relations={len(prediction.graph.triplets)}")

    missing_e2 = [case for case in cases if not (e2_cache.get(case.document.doc_id) and cache_matches(e2_cache[case.document.doc_id], condition="E2", doc_id=case.document.doc_id, narrative_sha256=case.narrative_sha256, contract=contracts["E2"]))]
    extractor = None if args.dry_run or not missing_e2 else CtinexusGlinerExtractor(model_name=config["gliner"]["model"], device=config["gliner"]["device"], threshold=config["gliner"]["threshold"])
    for index, case in enumerate(cases, 1):
        cached = e2_cache.get(case.document.doc_id)
        if cached and cache_matches(cached, condition="E2", doc_id=case.document.doc_id, narrative_sha256=case.narrative_sha256, contract=contracts["E2"]):
            prediction = cached
            e2_reused += 1
        else:
            prediction = _offline_e2(case, config) if args.dry_run else extractor.extract(case)
            append_jsonl(e2_cache_path, prediction)
        e2_predictions[case.document.doc_id] = prediction
        print(f"E2 [{index}/{len(cases)}] {case.document.doc_id}: {prediction.status} entities={len(prediction.graph.entities)} relations={len(prediction.graph.triplets)}")

    e1_summary, e1_rows = evaluate_condition(cases, e1_predictions, "E1")
    e2_summary, e2_rows = evaluate_condition(cases, e2_predictions, "E2")
    errors = combined_error_examples(cases, e1_rows, e2_rows, e1_predictions, e2_predictions)
    config["cache"] = {"E1_reused": e1_reused, "E2_reused": e2_reused, "E1_path": str(e1_cache_path), "E2_path": str(e2_cache_path)}
    e2_summary["confidence"] = _confidence_summary(e2_predictions)
    payload = write_report(output_dir, manifest, config, e1_summary, e2_summary, e1_rows, e2_rows, errors)
    print(f"E1 cache reused: {e1_reused}/{len(cases)}")
    print(f"E2 cache reused: {e2_reused}/{len(cases)}")
    print(f"Report: {output_dir / 'report.md'}")
    return payload


def _confidence_summary(predictions: dict[str, ExtractorPrediction]) -> dict[str, object]:
    return {
        "per_case": {doc_id: prediction.diagnostics.get("confidence", {}) for doc_id, prediction in sorted(predictions.items())},
        "source_grounding_failures": sum(int(prediction.diagnostics.get("source_grounding_failure_count", 0)) for prediction in predictions.values()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the extraction-only E1 vs E2 CTINexus benchmark.")
    parser.add_argument("--dataset-dir", default=str(DEFAULT_DATASET_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--gliner-device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    prepare_runtime()
    asyncio.run(run_benchmark(parse_args()))
