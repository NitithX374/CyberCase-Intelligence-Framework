from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .protocol import SELECTED_CATEGORIES, language_for


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def parse_category_counts(values: list[str]) -> dict[str, int] | None:
    if not values:
        return None
    counts: dict[str, int] = {}
    for value in values:
        category, separator, count_text = value.partition("=")
        if not separator or category not in SELECTED_CATEGORIES:
            raise ValueError(f"Invalid --category-count: {value}")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise ValueError(f"Invalid category count: {value}") from exc
        if count < 1 or category in counts:
            raise ValueError(f"Invalid category count: {value}")
        counts[category] = count
    if set(counts) != set(SELECTED_CATEGORIES):
        raise ValueError("Provide one positive count for each selected category")
    return counts


def selected_english(rows: list[dict[str, Any]], limit: int | None = None, category_counts: dict[str, int] | None = None) -> list[dict[str, Any]]:
    selected = [row for row in rows if row.get("category") in SELECTED_CATEGORIES and language_for(row) == "en"]
    if len(selected) != 300:
        raise ValueError(f"Pilot-1 requires 300 English rows, found {len(selected)}")
    if limit is not None and category_counts is not None:
        raise ValueError("Use either --limit or --category-count, not both")
    ordered = sorted(selected, key=lambda row: int(row["id"]))
    if category_counts is None:
        if limit is None:
            return ordered
        if not 1 <= limit <= len(ordered):
            raise ValueError(f"--limit must be between 1 and {len(ordered)}")
        return ordered[:limit]
    sampled: list[dict[str, Any]] = []
    for category in SELECTED_CATEGORIES:
        category_rows = [row for row in ordered if row["category"] == category]
        count = category_counts[category]
        if count > len(category_rows):
            raise ValueError(f"Category {category} has only {len(category_rows)} English rows")
        sampled.extend(category_rows[:count])
    return sorted(sampled, key=lambda row: int(row["id"]))


def selection_manifest(rows: list[dict[str, Any]], category_counts: dict[str, int] | None) -> dict[str, Any]:
    counts = {category: sum(row["category"] == category for row in rows) for category in SELECTED_CATEGORIES}
    formats: dict[str, int] = {}
    for row in rows:
        output_format = str(row["task"]).split("-")[-1]
        formats[output_format] = formats.get(output_format, 0) + 1
    return {
        "language": "en",
        "sample_count": len(rows),
        "selection_strategy": "lowest English dataset IDs within each category" if category_counts else "lowest English dataset IDs overall",
        "category_targets": category_counts or counts,
        "category_counts": counts,
        "format_counts": dict(sorted(formats.items())),
        "sample_ids": [str(row["id"]) for row in rows],
    }
