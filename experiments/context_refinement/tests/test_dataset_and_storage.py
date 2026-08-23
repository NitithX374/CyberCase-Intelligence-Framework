from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.context_refinement.dataset import REQUESTED_CATEGORIES, load_reused_subset
from experiments.context_refinement.storage import index_records


class DatasetAndStorageTests(unittest.TestCase):
    def test_existing_selection_is_reused_then_filtered(self) -> None:
        ids = [str(value) for value in range(1, 51)]
        categories = [
            *(["Threat Analysis"] * 15),
            *(["Summary Generation"] * 7),
            *(["Impact Scope"] * 6),
            *(["Risk Assessment"] * 22),
        ]
        rows = [
            {
                "id": int(sample_id),
                "category": category,
                "task": "test-en-gen",
                "instruction": "Do the task.",
                "input": f"context {sample_id}",
                "output": f"gold {sample_id}",
            }
            for sample_id, category in zip(ids, categories)
        ]
        with patch("experiments.context_refinement.dataset._selection_ids", return_value=ids):
            with patch("experiments.context_refinement.dataset.load_jsonl", return_value=rows):
                with patch("experiments.context_refinement.dataset.sha256_file", return_value="test-sha256"):
                    selected, manifest = load_reused_subset(Path("benchmark.jsonl"), Path("selection.json"))
        self.assertEqual(len(selected), 28)
        self.assertEqual(manifest["experiment_sample_count"], 28)
        self.assertEqual(set(manifest["categories"]), set(REQUESTED_CATEGORIES))
        self.assertEqual(manifest["category_counts"], {"Threat Analysis": 15, "Summary Generation": 7, "Impact Scope": 6})
        self.assertTrue(all("thought" not in row for row in selected))

    def test_jsonl_index_rejects_duplicate_keys(self) -> None:
        path = Path("records.jsonl")
        with patch(
            "experiments.context_refinement.storage.read_jsonl",
            return_value=[
                {"sample_id": "1", "condition": "B0"},
                {"sample_id": "1", "condition": "B0"},
            ],
        ):
            with self.assertRaises(ValueError):
                index_records(path, ("sample_id", "condition"))


if __name__ == "__main__":
    unittest.main()
