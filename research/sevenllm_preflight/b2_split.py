from __future__ import annotations

import random
from collections import Counter
from typing import Any

from .b2_config import SELECTED_CATEGORIES


def split_examples(
    examples: list[dict[str, Any]],
    validation_ratio: float,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio must be between zero and one")
    randomizer = random.Random(seed)
    train: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    for category in SELECTED_CATEGORIES:
        category_rows = [row for row in examples if row["category"] == category]
        randomizer.shuffle(category_rows)
        validation_count = max(1, int(len(category_rows) * validation_ratio + 0.5))
        validation_count = min(validation_count, len(category_rows) - 1)
        validation.extend(category_rows[:validation_count])
        train.extend(category_rows[validation_count:])
    return sorted(train, key=lambda row: row["source_line"]), sorted(validation, key=lambda row: row["source_line"])


def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(row["category"] for row in rows)
    return {category: counts.get(category, 0) for category in SELECTED_CATEGORIES}
