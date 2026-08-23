from __future__ import annotations

from typing import Any


def load_sbert_model(model_name: str, device: str) -> Any:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("sentence-transformers is required for SBERT evaluation") from exc
    return SentenceTransformer(model_name, device=device)


def score_condition(
    rows: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    condition: str,
    sbert_model: Any,
) -> dict[str, dict[str, float]]:
    from research.sevenllm_preflight.score_pilot import score_model

    prediction_records = {
        sample_id: {
            "sample_id": sample_id,
            "condition": condition,
            "provider": "openrouter" if condition == "B0" else None,
            "prediction_raw": record["prediction_raw"],
            "raw_prediction": record["prediction_raw"],
        }
        for sample_id, record in predictions.items()
    }
    report = score_model(rows, prediction_records, sbert_model)
    rouge = {
        str(record["id"]): float(record["rouge_l"])
        for record in report["generation"]["records"]
    }
    semantic = {
        str(record["id"]): float(record["sbert"])
        for record in report["generation"].get("sbert_records", [])
    }
    expected = {str(row["id"]) for row in rows}
    if set(rouge) != expected or set(semantic) != expected:
        raise ValueError(f"Incomplete evaluation records for {condition}")
    return {
        sample_id: {"rouge_l": rouge[sample_id], "sbert": semantic[sample_id]}
        for sample_id in sorted(expected, key=int)
    }

