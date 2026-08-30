from __future__ import annotations

import time
from statistics import mean, quantiles
from typing import Any

from .constants import (
    CTINEXUS_ENTITY_TYPES,
    GLINER_MODEL,
    GLINER_RELATION_SCHEMA,
    GLINER_SCHEMA_VERSION,
    GLINER_THRESHOLD,
)
from .dataset import CTINexusCase
from .projection import gliner_prediction
from .schemas import TypedEntityPrediction, TypedRelationPrediction


def resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def _confidence_values(items: list[TypedEntityPrediction], relations: list[TypedRelationPrediction]) -> list[float]:
    values = [item.confidence for item in items if item.confidence is not None]
    values.extend(item.confidence for item in relations if item.confidence is not None)
    return [float(value) for value in values]


def _distribution(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "p50": None, "p95": None, "min": None, "max": None}
    ordered = sorted(values)
    percentiles = quantiles(ordered, n=100, method="inclusive") if len(ordered) > 1 else [ordered[0]] * 99
    return {
        "count": len(values),
        "mean": round(mean(values), 6),
        "p50": round(percentiles[49], 6),
        "p95": round(percentiles[94], 6),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }


def _field_value(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    return value


class CtinexusGlinerExtractor:
    def __init__(
        self,
        *,
        model_name: str = GLINER_MODEL,
        device: str = "auto",
        threshold: float = GLINER_THRESHOLD,
    ) -> None:
        from experiments.representation_analysis.gliner_adapter import GlinerEventExtractor

        self.model_name = model_name
        self.device = resolve_device(device)
        self.threshold = threshold
        started = time.perf_counter()
        self._base_adapter = GlinerEventExtractor(model_name, self.device, threshold)
        self.model = self._base_adapter.model
        self.model_load_ms = round((time.perf_counter() - started) * 1000, 3)

    def _ground(self, source: str, value: Any) -> dict[str, Any] | None:
        return self._base_adapter._ground_value(source, value)

    def _extract_entities(self, source: str) -> tuple[list[TypedEntityPrediction], list[dict[str, Any]]]:
        raw = self.model.extract_entities(
            source,
            list(CTINEXUS_ENTITY_TYPES),
            threshold=self.threshold,
            include_confidence=True,
            include_spans=True,
        )
        payload = raw.get("entities", raw) if isinstance(raw, dict) else raw
        values: list[tuple[str, Any]] = []
        if isinstance(payload, dict):
            for entity_type, candidates in payload.items():
                candidate_values = candidates if isinstance(candidates, list) else [candidates]
                values.extend((str(entity_type), value) for value in candidate_values)
        elif isinstance(payload, list):
            for value in payload:
                if isinstance(value, dict):
                    entity_type = value.get("type") or value.get("label") or value.get("entity_type")
                    if entity_type:
                        values.append((str(entity_type), value))
        accepted: list[TypedEntityPrediction] = []
        rejected: list[dict[str, Any]] = []
        for entity_type, candidate in values:
            grounded = self._ground(source, candidate)
            if grounded is None:
                rejected.append({"kind": "entity", "type": entity_type, "value": candidate, "reason": "not_exactly_source_grounded"})
                continue
            accepted.append(
                TypedEntityPrediction(
                    text=grounded["text"],
                    entity_type=entity_type,
                    start=grounded["start"],
                    end=grounded["end"],
                    confidence=grounded.get("confidence"),
                )
            )
        return accepted, rejected

    def _extract_relations(self, source: str) -> tuple[list[TypedRelationPrediction], list[dict[str, Any]]]:
        raw = self.model.extract_json(
            source,
            GLINER_RELATION_SCHEMA,
            threshold=self.threshold,
            include_confidence=True,
            include_spans=True,
        )
        candidates = raw.get("ctinexus_relation", []) if isinstance(raw, dict) else []
        candidates = candidates if isinstance(candidates, list) else [candidates]
        accepted: list[TypedRelationPrediction] = []
        rejected: list[dict[str, Any]] = []
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                rejected.append({"kind": "relation", "index": index, "reason": "relation_not_object", "value": candidate})
                continue
            fields = {name: self._ground(source, _field_value(candidate.get(name))) for name in ("subject", "relation", "object")}
            missing = [name for name, value in fields.items() if value is None]
            if missing:
                rejected.append({"kind": "relation", "index": index, "reason": "relation_field_not_exactly_source_grounded", "missing": missing, "value": candidate})
                continue
            subject, relation, target = fields["subject"], fields["relation"], fields["object"]
            confidence_values = [item.get("confidence") for item in (subject, relation, target) if item.get("confidence") is not None]
            accepted.append(
                TypedRelationPrediction(
                    subject=subject["text"],
                    relation=relation["text"],
                    object=target["text"],
                    subject_start=subject["start"],
                    subject_end=subject["end"],
                    relation_start=relation["start"],
                    relation_end=relation["end"],
                    object_start=target["start"],
                    object_end=target["end"],
                    confidence=mean(float(value) for value in confidence_values) if confidence_values else None,
                )
            )
        return accepted, rejected

    def extract(self, case: CTINexusCase):
        import torch

        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        try:
            entities, entity_rejections = self._extract_entities(case.document.text)
            relations, relation_rejections = self._extract_relations(case.document.text)
            inference_ms = round((time.perf_counter() - started) * 1000, 3)
            memory_mb = None
            if self.device == "cuda":
                memory_mb = round(torch.cuda.max_memory_allocated() / (1024 * 1024), 3)
            confidences = _confidence_values(entities, relations)
            diagnostics = {
                "inference_latency_ms": inference_ms,
                "model_load_ms": self.model_load_ms,
                "device": self.device,
                "threshold": self.threshold,
                "peak_memory_mb": memory_mb,
                "confidence": _distribution(confidences),
                "source_grounding_failure_count": len(entity_rejections) + len(relation_rejections),
                "rejected_values": entity_rejections + relation_rejections,
                "empty_output": not entities and not relations,
            }
            contract = {
                "model": self.model_name,
                "schema_version": GLINER_SCHEMA_VERSION,
                "threshold": self.threshold,
                "entity_types": list(CTINEXUS_ENTITY_TYPES),
                "relation_schema": GLINER_RELATION_SCHEMA,
                "relation_label_mode": "source_span_free_text",
            }
            return gliner_prediction(
                case,
                model=self.model_name,
                entities=entities,
                relations=relations,
                latency_ms=inference_ms,
                diagnostics=diagnostics,
                contract=contract,
            )
        except Exception as exc:
            inference_ms = round((time.perf_counter() - started) * 1000, 3)
            diagnostics = {
                "inference_latency_ms": inference_ms,
                "model_load_ms": self.model_load_ms,
                "device": self.device,
                "threshold": self.threshold,
                "source_grounding_failure_count": 0,
                "rejected_values": [],
                "failure_reason": f"{type(exc).__name__}: {exc}",
                "empty_output": True,
            }
            prediction = gliner_prediction(
                case,
                model=self.model_name,
                entities=[],
                relations=[],
                latency_ms=inference_ms,
                diagnostics=diagnostics,
                contract={"model": self.model_name, "schema_version": GLINER_SCHEMA_VERSION},
            )
            prediction.graph.status = "failed"
            prediction.graph.failure_code = "gliner_extraction_failed"
            prediction.graph.failure_message = diagnostics["failure_reason"]
            prediction.status = "failed"
            return prediction
