from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


PATTERNS = {
    "ipv4": r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])",
    "url": r"https?://[^\s<>\]\[\"']+",
    "cve": r"\bCVE-\d{4}-\d{4,7}\b",
    "attack_id": r"\bT\d{4}(?:\.\d{3})?\b",
    "hash": r"\b(?:[A-Fa-f0-9]{32}|[A-Fa-f0-9]{40}|[A-Fa-f0-9]{64})\b",
    "domain": r"\b(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b",
    "timestamp": r"\b\d{4}-\d{2}-\d{2}(?:[T ][0-9:.+-]+Z?)?\b",
    "windows_path": r"\b[A-Za-z]:\\[^\r\n,;]+",
}


def detect_source_strings(text: str) -> dict[str, list[str]]:
    return {name: sorted(set(re.findall(pattern, text, flags=re.IGNORECASE))) for name, pattern in PATTERNS.items()}


def retention_diagnostics(source: str, representation: str) -> dict[str, Any]:
    detected = detect_source_strings(source)
    missing: defaultdict[str, list[str]] = defaultdict(list)
    for kind, values in detected.items():
        missing[kind].extend(value for value in values if value not in representation)
    total = sum(len(values) for values in detected.values())
    absent = sum(len(values) for values in missing.values())
    return {"total": total, "preserved": total - absent, "missing": absent, "by_type": detected, "missing_by_type": dict(missing)}


def case_state_surface_values(case_state: dict[str, Any]) -> list[str]:
    ignored = {"fact_id", "entity_id", "relationship_id", "evidence_id", "event_id", "impact_id", "missing_id", "predicate", "category", "status", "confidence", "source_type", "artifact_type", "impact_type", "importance"}
    values: list[str] = []
    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, child_key)
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif isinstance(value, str) and key not in ignored and len(value.strip()) >= 4:
            values.append(value.strip())
    visit(case_state)
    return sorted(set(values))


def possible_unsupported_surface_values(source: str, case_state: dict[str, Any]) -> list[str]:
    source_lower = source.lower()
    return [value for value in case_state_surface_values(case_state) if value.lower() not in source_lower]
