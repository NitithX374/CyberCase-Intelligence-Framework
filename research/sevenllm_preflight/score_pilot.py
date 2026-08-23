from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from rouge import Rouge
from sentence_transformers import SentenceTransformer, util

from .protocol import format_for, language_for, normalize_choice_output
from .selection import load_jsonl, parse_category_counts, selected_english


def predictions_by_id(path: Path, expected_ids: set[str], limit: int | None = None, restrict_to_ids: bool = False) -> dict[str, dict[str, Any]]:
    predictions = load_jsonl(path)
    if limit is not None:
        if len(predictions) < limit:
            raise ValueError(f"Prediction file has fewer than {limit} records: {path}")
        predictions = predictions[:limit]
    elif restrict_to_ids:
        predictions = [record for record in predictions if str(record.get("sample_id")) in expected_ids]
    actual_ids = {str(record["sample_id"]) for record in predictions}
    if actual_ids != expected_ids or len(predictions) != len(expected_ids):
        raise ValueError(f"Prediction IDs do not exactly match Pilot-1: {path}")
    if any(record.get("language") not in {"en", "EN"} for record in predictions):
        raise ValueError(f"Non-English prediction found: {path}")
    if any(record.get("error") for record in predictions):
        raise ValueError(f"Failed prediction found: {path}")
    return {str(record["sample_id"]): record for record in predictions}


def prediction_text(record: dict[str, Any]) -> str:
    if record.get("condition") == "B0" and record.get("provider") == "openrouter":
        value = record.get("prediction_raw")
    else:
        value = record.get("raw_prediction")
    if not isinstance(value, str):
        raise ValueError(f"Prediction text is missing for sample {record.get('sample_id')}")
    return value


def flatten_values(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        for child in value.values():
            values.extend(flatten_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(flatten_values(child))
    else:
        values.append(str(value))
    return values


def extraction_f1(gold: Any, prediction: Any) -> tuple[float, float, float]:
    gold_values = flatten_values(gold)
    prediction_values = flatten_values(prediction)
    overlap = sum(min(gold_values.count(value), prediction_values.count(value)) for value in set(gold_values) & set(prediction_values))
    precision = overlap / len(prediction_values) if prediction_values else 0.0
    recall = overlap / len(gold_values) if gold_values else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def parse_json_prediction(raw: str) -> Any | None:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def rouge_l(gold: str, prediction: str) -> float:
    if not gold or not prediction:
        return 0.0
    return float(Rouge().get_scores(gold, prediction)[0]["rouge-l"]["f"])


def english_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s", text) if sentence.strip()]


def sbert_records(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], model: SentenceTransformer) -> list[dict[str, Any]]:
    groups: list[tuple[dict[str, Any], list[str], list[str]]] = []
    texts: list[str] = []
    for row in rows:
        if format_for(row) != "generation":
            continue
        gold = english_sentences(str(row["output"]))
        prediction = english_sentences(prediction_text(predictions[str(row["id"])]))
        groups.append((row, gold, prediction))
        texts.extend(gold)
        texts.extend(prediction)
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    cursor = 0
    records: list[dict[str, Any]] = []
    for row, gold, prediction in groups:
        gold_embeddings = embeddings[cursor : cursor + len(gold)]
        cursor += len(gold)
        prediction_embeddings = embeddings[cursor : cursor + len(prediction)]
        cursor += len(prediction)
        score = 0.0 if not prediction else float(util.cos_sim(gold_embeddings, prediction_embeddings).max(dim=1).values.mean().item())
        records.append({"id": str(row["id"]), "category": row["category"], "language": "en", "format": "generation", "sbert": score})
    return records


def group_mean(records: list[dict[str, Any]], key: str, metric: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for record in records:
        grouped[str(record[key])].append(float(record[metric]))
    return {name: round(sum(values) / len(values), 6) for name, values in sorted(grouped.items())}


def metric_mean(records: list[dict[str, Any]], metric: str) -> float:
    return round(sum(float(record[metric]) for record in records) / len(records), 6) if records else 0.0


def model_identity(predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    record = next(iter(predictions.values()))
    if record.get("condition") == "B0":
        return {
            "condition": "B0",
            "provider": record.get("provider"),
            "requested_model": record.get("requested_model"),
            "returned_models": sorted({str(item.get("returned_model", "")) for item in predictions.values()}),
            "generation_config": record.get("generation_config"),
        }
    return {
        "condition": "B1",
        "model": record.get("model"),
        "model_revision": record.get("model_revision"),
        "generation_config": record.get("generation"),
    }


def score_model(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], sbert_model: SentenceTransformer | None = None) -> dict[str, Any]:
    generation_records: list[dict[str, Any]] = []
    choice_records: list[dict[str, Any]] = []
    extraction_records: list[dict[str, Any]] = []
    for row in rows:
        record = predictions[str(row["id"])]
        output = prediction_text(record)
        item = {"category": row["category"], "language": "en", "format": format_for(row), "id": str(row["id"])}
        if format_for(row) == "generation":
            generation_records.append({**item, "rouge_l": rouge_l(str(row["output"]), output)})
        elif format_for(row) == "choice":
            normalized = normalize_choice_output(output)
            choice_records.append({**item, "correct": int(normalized == row["output"]), "normalized": normalized})
        else:
            parsed = parse_json_prediction(output)
            precision, recall, f1 = extraction_f1(row["output"], parsed) if parsed is not None else (0.0, 0.0, 0.0)
            extraction_records.append({**item, "json_parse_success": parsed is not None, "precision": precision, "recall": recall, "f1": f1})
    report = {
        "generation": {
            "count": len(generation_records),
            "rouge_l_mean": metric_mean(generation_records, "rouge_l"),
            "by_category": group_mean(generation_records, "category", "rouge_l"),
            "records": generation_records,
        },
        "choice": {
            "count": len(choice_records),
            "correct": sum(record["correct"] for record in choice_records),
            "accuracy": metric_mean(choice_records, "correct"),
            "by_category": group_mean(choice_records, "category", "correct"),
            "records": choice_records,
        },
        "extraction": {
            "count": len(extraction_records),
            "precision": metric_mean(extraction_records, "precision"),
            "recall": metric_mean(extraction_records, "recall"),
            "f1": metric_mean(extraction_records, "f1"),
            "records": extraction_records,
        },
    }
    if sbert_model is not None:
        secondary = sbert_records(rows, predictions, sbert_model)
        report["generation"]["sbert_mean"] = metric_mean(secondary, "sbert")
        report["generation"]["sbert_by_category"] = group_mean(secondary, "category", "sbert")
        report["generation"]["sbert_records"] = secondary
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--b0", type=Path, required=True)
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--category-count", action="append", default=[])
    parser.add_argument("--sbert-dir", type=Path)
    parser.add_argument("--sbert-device", choices=("cpu", "cuda"), default="cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    category_counts = parse_category_counts(args.category_count)
    rows = selected_english(load_jsonl(args.dataset), args.limit, category_counts)
    ids = {str(row["id"]) for row in rows}
    restrict_to_ids = category_counts is not None
    b0 = predictions_by_id(args.b0, ids, args.limit, restrict_to_ids)
    b1 = predictions_by_id(args.b1, ids, args.limit, restrict_to_ids)
    sbert_model = SentenceTransformer(str(args.sbert_dir), device=args.sbert_device) if args.sbert_dir else None
    report = {
        "pilot": "Pilot-1",
        "language": "en",
        "sample_count": len(rows),
        "chinese_inference": False,
        "selection": {
            "strategy": "lowest English dataset IDs within each category" if category_counts else "lowest English dataset IDs overall",
            "category_targets": category_counts,
            "sample_ids": [str(row["id"]) for row in rows],
        },
        "models": {
            "B0": {"identity": model_identity(b0), **score_model(rows, b0, sbert_model)},
            "B1": {"identity": model_identity(b1), **score_model(rows, b1, sbert_model)},
        },
        "official_primary_metrics": {"generation": "ROUGE-L", "choice": "exact match after A-D normalization", "extraction": "flattened-leaf precision/recall/F1"},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sample_count": len(rows), "models": list(report["models"])}, indent=2))


if __name__ == "__main__":
    main()
