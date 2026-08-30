from __future__ import annotations

import time
from statistics import mean
from typing import Any

from .constants import EVENT_FIELDS, EVENT_SCHEMA


class GlinerEventExtractor:
    def __init__(self, model_name: str, device: str, threshold: float = 0.5, model: Any = None) -> None:
        self.model_name = model_name
        self.device = device
        self.threshold = threshold
        if model is None:
            from gliner2 import GLiNER2
            model = GLiNER2.from_pretrained(model_name, map_location=device)
        self.model = model

    def extract(self, source: str) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            result = self.model.extract_json(source, EVENT_SCHEMA, threshold=self.threshold, include_confidence=True, include_spans=True)
            events, rejected = self._ground_events(source, result.get("cyber_event", []))
            confidences = [float(value["confidence"]) for event in events for value in event.values() if value.get("confidence") is not None]
            return {
                "status": "complete", "extraction_success": True, "events": events,
                "rejected_values": rejected, "event_count": len(events),
                "confidence": {"count": len(confidences), "mean": round(mean(confidences), 6) if confidences else None, "min": min(confidences, default=None)},
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "model": self.model_name, "device": self.device, "threshold": self.threshold,
            }
        except Exception as exc:
            return {"status": "failed", "extraction_success": False, "events": [], "rejected_values": [], "failure_reason": f"{type(exc).__name__}: {exc}", "latency_ms": round((time.perf_counter() - started) * 1000, 3), "model": self.model_name, "device": self.device, "threshold": self.threshold}

    def _ground_events(self, source: str, raw_events: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        candidates = raw_events if isinstance(raw_events, list) else [raw_events]
        events: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        for event_index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                rejected.append({"event_index": event_index, "reason": "event_not_object"})
                continue
            grounded: dict[str, Any] = {}
            for field in EVENT_FIELDS:
                values = candidate.get(field, [])
                values = values if isinstance(values, list) else [values]
                for value in values:
                    accepted = self._ground_value(source, value)
                    if accepted is not None:
                        grounded[field] = accepted
                        break
                    rejected.append({"event_index": event_index, "field": field, "value": value, "reason": "not_exactly_source_grounded"})
            if grounded:
                events.append(grounded)
        return events, rejected

    @staticmethod
    def _ground_value(source: str, value: Any) -> dict[str, Any] | None:
        if isinstance(value, str):
            text, confidence, start, end = value, None, None, None
        elif isinstance(value, dict):
            text, confidence = str(value.get("text", "")), value.get("confidence")
            start, end = value.get("start"), value.get("end")
        else:
            return None
        if not text:
            return None
        if isinstance(start, int) and isinstance(end, int):
            if source[start:end] != text:
                return None
        else:
            start = source.find(text)
            if start < 0:
                return None
            end = start + len(text)
        return {"text": text, "start": start, "end": end, "confidence": confidence}
