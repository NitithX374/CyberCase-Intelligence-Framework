from __future__ import annotations

from statistics import mean, quantiles
from typing import Iterable

from .dataset import CTINexusCase
from .schemas import ExtractorPrediction
from .typed_metrics import entity_type_metrics, relation_type_metrics
from .type_mapping import map_production_entity_type

from backend.experiments.ctinexus.metrics import calculate_micro_metrics, evaluate_document
from backend.experiments.ctinexus.normalize import normalize_entity_name
from backend.experiments.ctinexus.schemas import DocumentEvaluation


def _stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "p50": None, "p95": None, "min": None, "max": None}
    ordered = sorted(values)
    percentiles = quantiles(ordered, n=100, method="inclusive") if len(ordered) > 1 else [ordered[0]] * 99
    return {
        "count": len(values),
        "mean": round(mean(values), 3),
        "p50": round(percentiles[49], 3),
        "p95": round(percentiles[94], 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
    }


def _coverage(predictions: Iterable[ExtractorPrediction]) -> dict[str, object]:
    records = list(predictions)
    count = len(records)
    successful = [record for record in records if record.status == "success"]
    empty = [record for record in successful if record.graph.entities == [] and record.graph.triplets == []]
    validation_failures = [record for record in records if record.diagnostics.get("validation_failure")]
    return {
        "cases": count,
        "successful_extractions": len(successful),
        "extraction_failures": count - len(successful),
        "validation_failures": len(validation_failures),
        "empty_output_cases": len(empty),
        "mean_predicted_entities_per_case": round(sum(len(record.graph.entities) for record in records) / count, 3) if count else 0.0,
        "mean_predicted_relations_per_case": round(sum(len(record.graph.triplets) for record in records) / count, 3) if count else 0.0,
    }


def _latency(predictions: Iterable[ExtractorPrediction], condition: str) -> dict[str, object]:
    records = list(predictions)
    values = [float(record.graph.latency_ms) for record in records]
    result: dict[str, object] = {"inference_latency_ms": _stats(values)}
    if condition == "E1":
        input_tokens = [record.graph.input_tokens for record in records if record.graph.input_tokens is not None]
        output_tokens = [record.graph.output_tokens for record in records if record.graph.output_tokens is not None]
        result.update(
            {
                "api_calls": sum(int(record.diagnostics.get("api_calls", 0)) for record in records),
                "input_tokens": {"total": sum(input_tokens), "mean": round(mean(input_tokens), 3) if input_tokens else None},
                "output_tokens": {"total": sum(output_tokens), "mean": round(mean(output_tokens), 3) if output_tokens else None},
                "approximate_cost": None,
            }
        )
    else:
        load_times = [float(record.diagnostics["model_load_ms"]) for record in records if record.diagnostics.get("model_load_ms") is not None]
        memory = [float(record.diagnostics["peak_memory_mb"]) for record in records if record.diagnostics.get("peak_memory_mb") is not None]
        devices = sorted({record.diagnostics.get("device") for record in records if record.diagnostics.get("device")})
        result.update({"model_load_ms": max(load_times, default=None), "device": devices, "peak_memory_mb": max(memory, default=None)})
    return result


def _example(doc_id: str, category: str, values: object) -> dict[str, object]:
    return {"doc_id": doc_id, "category": category, "values": values}


def _error_examples(
    cases: list[CTINexusCase],
    evaluations: dict[str, DocumentEvaluation],
    predictions: dict[str, ExtractorPrediction],
) -> dict[str, list[dict[str, object]]]:
    examples: dict[str, list[dict[str, object]]] = {
        "production_correct_gliner_misses": [],
        "gliner_correct_production_misses": [],
        "both_miss": [],
        "entity_correct_name_wrong_type": [],
        "correct_endpoint_wrong_or_missing_relation": [],
        "production_hallucinated_or_unsupported": [],
        "gliner_span_grounding_failure": [],
    }
    for case in cases:
        doc_id = case.document.doc_id
        evaluation = evaluations[doc_id]
        other = evaluations.get(doc_id + "::E2")
        if other is None:
            continue
        e1_only = sorted(set(evaluation.entity_tp) - set(other.entity_tp))
        e2_only = sorted(set(other.entity_tp) - set(evaluation.entity_tp))
        both_miss = sorted(set(evaluation.entity_fn) & set(other.entity_fn))
        if e1_only and len(examples["production_correct_gliner_misses"]) < 3:
            examples["production_correct_gliner_misses"].append(_example(doc_id, "entity", e1_only))
        if e2_only and len(examples["gliner_correct_production_misses"]) < 3:
            examples["gliner_correct_production_misses"].append(_example(doc_id, "entity", e2_only))
        if both_miss and len(examples["both_miss"]) < 3:
            examples["both_miss"].append(_example(doc_id, "entity", both_miss))
        gold_types_by_name: dict[str, set[str]] = {}
        for item in case.gold_entities:
            gold_types_by_name.setdefault(normalize_entity_name(item.text), set()).add(item.entity_type)
        for condition, prediction in (("E1", predictions[doc_id]), ("E2", predictions[doc_id + "::E2"])):
            for item in prediction.typed_entities:
                name = normalize_entity_name(item.text)
                mapped_type = map_production_entity_type(item.entity_type) if condition == "E1" else item.entity_type
                if name in gold_types_by_name and mapped_type not in gold_types_by_name[name] and len(examples["entity_correct_name_wrong_type"]) < 3:
                    examples["entity_correct_name_wrong_type"].append(_example(doc_id, condition, {"text": item.text, "predicted_type": item.entity_type, "gold_types": sorted(gold_types_by_name[name])}))
        for endpoint in sorted(set(evaluation.endpoint_tp) | set(other.endpoint_tp)):
            e1_rel = [item for item in evaluation.triplet_tp if (item[0], item[2]) == endpoint]
            e2_rel = [item for item in other.triplet_tp if (item[0], item[2]) == endpoint]
            if (e1_rel or e2_rel) and not (e1_rel and e2_rel) and len(examples["correct_endpoint_wrong_or_missing_relation"]) < 3:
                examples["correct_endpoint_wrong_or_missing_relation"].append(_example(doc_id, "endpoint", {"edge": endpoint, "e1": e1_rel, "e2": e2_rel}))
                break
        if evaluation.entity_fp or evaluation.triplet_fp:
            if len(examples["production_hallucinated_or_unsupported"]) < 3:
                examples["production_hallucinated_or_unsupported"].append(_example(doc_id, "production_fp", {"entities": evaluation.entity_fp, "triplets": evaluation.triplet_fp}))
        rejected = predictions[doc_id + "::E2"].diagnostics.get("rejected_values", [])
        if rejected and len(examples["gliner_span_grounding_failure"]) < 3:
            examples["gliner_span_grounding_failure"].append(_example(doc_id, "gliner_rejected", rejected[:5]))
    return examples


def evaluate_condition(cases: list[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    evaluations: list[DocumentEvaluation] = []
    for case in cases:
        evaluations.append(evaluate_document(case.document, predictions[case.document.doc_id].graph))
    aggregate = calculate_micro_metrics(evaluations)
    typed_entities, type_diagnostics = entity_type_metrics(cases, predictions, condition)
    typed_relations = relation_type_metrics(cases, predictions)
    evaluation_rows = [item.model_dump(mode="json") for item in evaluations]
    summary = {
        "condition": condition,
        "overall": aggregate.model_dump(mode="json"),
        "coverage": _coverage(predictions.values()),
        "latency_and_cost": _latency(predictions.values(), condition),
        "entity_type_metrics": typed_entities,
        "entity_type_diagnostics": type_diagnostics,
        "relation_type_metrics": typed_relations,
    }
    return summary, evaluation_rows


def combined_error_examples(
    cases: list[CTINexusCase],
    e1_rows: list[dict[str, object]],
    e2_rows: list[dict[str, object]],
    e1_predictions: dict[str, ExtractorPrediction],
    e2_predictions: dict[str, ExtractorPrediction],
) -> dict[str, list[dict[str, object]]]:
    evaluations: dict[str, DocumentEvaluation] = {}
    for row in e1_rows:
        evaluations[row["doc_id"]] = DocumentEvaluation.model_validate(row)
    for row in e2_rows:
        evaluations[f"{row['doc_id']}::E2"] = DocumentEvaluation.model_validate(row)
    predictions = {**e1_predictions, **{f"{key}::E2": value for key, value in e2_predictions.items()}}
    e1_by_doc = {key: value for key, value in evaluations.items() if not key.endswith("::E2")}
    remapped = {}
    for doc_id, evaluation in e1_by_doc.items():
        remapped[doc_id] = evaluation
        remapped[f"{doc_id}::E2"] = evaluations[f"{doc_id}::E2"]
    return _error_examples(cases, remapped, predictions)
