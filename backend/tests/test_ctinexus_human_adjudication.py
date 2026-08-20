"""Tests for CTINexus blind human-validation sampling, blinding, and scoring."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest

from experiments.ctinexus.prepare_human_adjudication import (
    CSV_OUTPUT_PATH,
    HUMAN_ADJUDICATION_SEED,
    KEY_OUTPUT_PATH,
    METADATA_OUTPUT_PATH,
    generate_human_adjudication_files,
    sample_human_validation_pairs,
)
from experiments.ctinexus.score_human_adjudication import (
    calculate_cohens_kappa,
    score_human_validation,
)


class HumanAdjudicationSamplingAndBlindingTests(unittest.TestCase):
    def test_1_human_csv_contains_no_llm_judgment_information(self) -> None:
        self.assertTrue(CSV_OUTPUT_PATH.exists(), f"CSV output file missing: {CSV_OUTPUT_PATH}")

        forbidden_headers = [
            "llm_label",
            "llm_reason",
            "judge_model",
            "prompt_version",
            "match_type",
            "semantic_result",
            "strict_result",
        ]

        with open(CSV_OUTPUT_PATH, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            for h in header:
                self.assertNotIn(h.lower(), forbidden_headers)

            for row_idx, row in enumerate(reader, 1):
                # human_label (col 9) and human_note (col 10) must initially be blank
                self.assertEqual(row[9], "", f"human_label must be blank at row {row_idx}")
                self.assertEqual(row[10], "", f"human_note must be blank at row {row_idx}")

    def test_2_row_id_values_are_unique_and_sequential(self) -> None:
        with open(CSV_OUTPUT_PATH, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            row_ids = [int(r["row_id"]) for r in reader]

        self.assertEqual(len(row_ids), len(set(row_ids)), "row_id values must be strictly unique")
        self.assertEqual(row_ids, list(range(1, len(row_ids) + 1)), "row_ids must be sequential starting from 1")

    def test_3_key_json_and_csv_have_identical_row_ids(self) -> None:
        with open(CSV_OUTPUT_PATH, "r", encoding="utf-8", newline="") as f:
            csv_ids = {int(r["row_id"]) for r in csv.DictReader(f)}

        with open(KEY_OUTPUT_PATH, "r", encoding="utf-8") as f:
            key_records = json.load(f)
            key_ids = {int(r["row_id"]) for r in key_records}

        self.assertEqual(csv_ids, key_ids, "CSV and Key JSON must have identical row_id sets")
        self.assertGreaterEqual(len(csv_ids), 60, "Must contain at least 60 sampled pairs")
        self.assertLessEqual(len(csv_ids), 100, "Must contain at most 100 sampled pairs")

    def test_4_sampling_is_deterministic_with_seed_42(self) -> None:
        with open(METADATA_OUTPUT_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.assertEqual(meta["sampling_seed"], HUMAN_ADJUDICATION_SEED)
        self.assertEqual(meta["sampling_seed"], 42)

        # Re-generating with seed 42 produces exact same rows
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_csv = Path(tmp_dir) / "test.csv"
            tmp_key = Path(tmp_dir) / "test_key.json"
            tmp_meta = Path(tmp_dir) / "test_meta.json"

            generate_human_adjudication_files(
                csv_out=tmp_csv,
                key_out=tmp_key,
                metadata_out=tmp_meta,
                seed=42,
            )

            with open(KEY_OUTPUT_PATH, "r", encoding="utf-8") as f1, open(tmp_key, "r", encoding="utf-8") as f2:
                self.assertEqual(json.load(f1), json.load(f2), "Sampling must be 100% reproducible with seed 42")

    def test_5_no_duplicate_triplet_pair_exists(self) -> None:
        with open(KEY_OUTPUT_PATH, "r", encoding="utf-8") as f:
            records = json.load(f)

        seen = set()
        for r in records:
            key = (r["doc_id"], tuple(r["predicted_triplet"]), tuple(r["gold_triplet"]))
            self.assertNotIn(key, seen, f"Duplicate triplet pair detected: {key}")
            seen.add(key)


class HumanAdjudicationScoringMetricsTests(unittest.TestCase):
    def test_6_cohens_kappa_calculation_correctness(self) -> None:
        # Perfect agreement: kappa = 1.0
        self.assertEqual(calculate_cohens_kappa(a=50, b=0, c=0, d=50), 1.0)

        # Pure chance agreement: kappa ~ 0.0
        # If both guess 50% randomly on equal distribution
        self.assertAlmostEqual(calculate_cohens_kappa(a=25, b=25, c=25, d=25), 0.0, places=4)

        # Known standard case:
        # a=20, b=5, c=10, d=15 (Total=50)
        # Po = (20+15)/50 = 0.70
        # Pe = (25/50 * 30/50) + (25/50 * 20/50) = 0.30 + 0.20 = 0.50
        # Kappa = (0.70 - 0.50) / (1 - 0.50) = 0.20 / 0.50 = 0.40
        self.assertAlmostEqual(calculate_cohens_kappa(a=20, b=5, c=10, d=15), 0.40, places=4)

    def test_7_scoring_with_simulated_human_labels(self) -> None:
        key_data = [
            {"row_id": 1, "doc_id": "d1", "gold_triplet": ["a", "r", "b"], "predicted_triplet": ["a", "r", "b"], "llm_label": "EQUIVALENT", "llm_reason": "Exact", "judge_model": "4o-mini", "prompt_version": "v1"},
            {"row_id": 2, "doc_id": "d1", "gold_triplet": ["a", "r", "b"], "predicted_triplet": ["a", "r", "c"], "llm_label": "NOT_EQUIVALENT", "llm_reason": "Diff obj", "judge_model": "4o-mini", "prompt_version": "v1"},
            {"row_id": 3, "doc_id": "d1", "gold_triplet": ["x", "r", "y"], "predicted_triplet": ["x", "r", "z"], "llm_label": "NOT_EQUIVALENT", "llm_reason": "Diff obj", "judge_model": "4o-mini", "prompt_version": "v1"},
            {"row_id": 4, "doc_id": "d1", "gold_triplet": ["p", "r", "q"], "predicted_triplet": ["p", "r", "q"], "llm_label": "EQUIVALENT", "llm_reason": "Exact", "judge_model": "4o-mini", "prompt_version": "v1"},
        ]

        # Human agrees on 1 & 2, disagrees on 3 (Human calls it EQUIVALENT), leaves 4 blank
        csv_rows = [
            {"row_id": "1", "human_label": "EQUIVALENT", "human_note": "Agree"},
            {"row_id": "2", "human_label": "NOT_EQUIVALENT", "human_note": "Agree"},
            {"row_id": "3", "human_label": "equivalent", "human_note": "Disagreement"},  # lowercase should be handled
            {"row_id": "4", "human_label": "", "human_note": ""},  # blank
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_key = Path(tmp_dir) / "key.json"
            tmp_csv = Path(tmp_dir) / "human.csv"

            with open(tmp_key, "w", encoding="utf-8") as f:
                json.dump(key_data, f)

            with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["row_id", "human_label", "human_note"])
                writer.writeheader()
                writer.writerows(csv_rows)

            report = score_human_validation(csv_path=tmp_csv, key_path=tmp_key)

            self.assertEqual(report.total_rows, 4)
            self.assertEqual(report.labeled_rows, 3)
            self.assertEqual(report.unlabeled_rows, 1)
            self.assertEqual(report.agreement_count, 2)
            self.assertAlmostEqual(report.percent_agreement, 66.67, places=2)
            self.assertEqual(len(report.disagreements), 1)
            self.assertEqual(report.disagreements[0].row_id, 3)
            self.assertEqual(report.disagreements[0].llm_label, "NOT_EQUIVALENT")
            self.assertEqual(report.disagreements[0].human_label, "EQUIVALENT")

    def test_8_blank_labels_are_safely_counted_without_error(self) -> None:
        # When all rows are blank initially
        report = score_human_validation(csv_path=CSV_OUTPUT_PATH, key_path=KEY_OUTPUT_PATH)
        self.assertEqual(report.labeled_rows, 0)
        self.assertEqual(report.unlabeled_rows, report.total_rows)
        self.assertEqual(report.agreement_count, 0)
        self.assertEqual(report.percent_agreement, 0.0)
        self.assertEqual(report.cohens_kappa, 0.0)

    def test_9_invalid_human_label_raises_value_error(self) -> None:
        key_data = [
            {"row_id": 1, "doc_id": "d1", "gold_triplet": ["a", "r", "b"], "predicted_triplet": ["a", "r", "b"], "llm_label": "EQUIVALENT", "llm_reason": "Exact", "judge_model": "4o-mini", "prompt_version": "v1"},
        ]
        csv_rows = [
            {"row_id": "1", "human_label": "MAYBE_EQUIVALENT", "human_note": ""},
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_key = Path(tmp_dir) / "key.json"
            tmp_csv = Path(tmp_dir) / "human.csv"

            with open(tmp_key, "w", encoding="utf-8") as f:
                json.dump(key_data, f)

            with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["row_id", "human_label", "human_note"])
                writer.writeheader()
                writer.writerows(csv_rows)

            with self.assertRaises(ValueError) as ctx:
                score_human_validation(csv_path=tmp_csv, key_path=tmp_key)

            self.assertIn("Invalid human_label 'MAYBE_EQUIVALENT'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
