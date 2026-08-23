from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.sevenllm_preflight.protocol import format_for, gold_output_text, language_for
from research.sevenllm_preflight.selection import load_jsonl


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUESTED_CATEGORIES = (
    "Threat Analysis",
    "Summary Generation",
    "Impact Scope",
)
DEFAULT_BENCHMARK = PROJECT_ROOT / "tmp" / "sevenllm_b2_test_all.jsonl"
DEFAULT_SELECTION = PROJECT_ROOT / "research" / "sevenllm_preflight" / "results" / "pilot_1_en" / "pilot_1_en_50_selection.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _selection_ids(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ids = [str(value) for value in payload.get("sample_ids", [])]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError(f"Expected exactly 50 unique IDs in frozen selection: {path}")
    return ids


def _row_language(row: dict[str, Any]) -> str:
    return language_for(row).lower()


def load_reused_subset(benchmark_path: Path, selection_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected_ids = _selection_ids(selection_path)
    by_id = {str(row["id"]): row for row in load_jsonl(benchmark_path)}
    missing = [sample_id for sample_id in selected_ids if sample_id not in by_id]
    if missing:
        raise ValueError(f"Frozen selection IDs missing from benchmark: {missing}")
    fixed_rows = [by_id[sample_id] for sample_id in selected_ids]
    rows = [
        row
        for row in fixed_rows
        if row.get("category") in REQUESTED_CATEGORIES
        and _row_language(row) == "en"
        and format_for(row) == "generation"
    ]
    if not rows:
        raise ValueError("Frozen selection produced no requested English generation rows")
    if len({str(row["id"]) for row in rows}) != len(rows):
        raise ValueError("Duplicate sample ID in reused experiment subset")
    counts = Counter(str(row["category"]) for row in rows)
    if set(counts) != set(REQUESTED_CATEGORIES):
        raise ValueError(f"Requested categories are incomplete: {dict(counts)}")
    manifest = {
        "source": "SEvenLLM-Bench fixed Pilot-1 selection",
        "selection_path": str(selection_path),
        "selection_sha256": sha256_file(selection_path),
        "benchmark_path": str(benchmark_path),
        "benchmark_sha256": sha256_file(benchmark_path),
        "fixed_pilot50_ids": selected_ids,
        "experiment_sample_ids": [str(row["id"]) for row in rows],
        "experiment_sample_count": len(rows),
        "language": "en",
        "categories": list(REQUESTED_CATEGORIES),
        "category_counts": {category: counts[category] for category in REQUESTED_CATEGORIES},
        "format": "generation",
        "split_policy": "reuse the existing 50-case selection, then filter to the three requested categories",
        "gold_field": "output",
        "excluded_fields": ["thought"],
        "benchmark_role": "test-only evaluation source",
    }
    return sorted(rows, key=lambda row: int(row["id"])), manifest


def gold_text(row: dict[str, Any]) -> str:
    return gold_output_text(row)

