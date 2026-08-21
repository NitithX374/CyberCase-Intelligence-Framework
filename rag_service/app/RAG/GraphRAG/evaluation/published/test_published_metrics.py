"""Unit tests for the TechniqueRAG-compatible metrics.

The equivalence with upstream `evaluate.py` was checked separately against a
reference copy of its functions (see NOTICE.md). These tests pin the protocol
quirks that make that equivalence hold, so a future refactor cannot quietly
drift away from the published protocol.

Run:
    cd rag_service/app
    python -m pytest RAG/GraphRAG/evaluation/published/test_published_metrics.py -q
"""

from __future__ import annotations

import pytest

from .metrics import extract_attack_ids, score_at_k, score_corpus, score_sample


class TestExtraction:
    def test_extracts_in_first_mention_order(self):
        text = "First T1059.001, then T1055, then T1059.001 again, then T1027."
        assert extract_attack_ids(text) == ["T1059.001", "T1055", "T1027"]

    def test_extracts_from_thai_prose(self):
        text = "ผู้โจมตีใช้ T1566.001 เพื่อส่งอีเมลหลอกลวง แล้วจึงรันคำสั่งผ่าน T1059"
        assert extract_attack_ids(text) == ["T1566.001", "T1059"]

    def test_ignores_non_technique_ids(self):
        # Tactic (TA), Group (G) and Software (S) IDs are out of scope here.
        assert extract_attack_ids("TA0001 G0016 S0154 T1105") == ["T1105"]

    def test_empty_input(self):
        assert extract_attack_ids("") == []
        assert extract_attack_ids(None) == []


class TestModes:
    def test_technique_mode_rolls_subtechniques_up(self):
        s = score_sample(["T1059.003"], ["T1059.001"], mode="technique")
        assert s.precision == 1.0 and s.recall == 1.0

    def test_subtechnique_mode_does_not(self):
        s = score_sample(["T1059.003"], ["T1059.001"], mode="subtechnique")
        assert s.precision == 0.0 and s.recall == 0.0

    def test_technique_mode_dedups_after_projection(self):
        # T1059.001 and T1059.003 collapse to one prediction, so precision is
        # 1.0 rather than 0.5 - this is upstream behaviour and it matters.
        s = score_sample(["T1059.001", "T1059.003"], ["T1059"], mode="technique")
        assert s.n_pred == 1
        assert s.precision == 1.0

    def test_rejects_unknown_mode(self):
        with pytest.raises(ValueError):
            score_sample(["T1059"], ["T1059"], mode="nonsense")


class TestSampleScoring:
    def test_partial_overlap(self):
        s = score_sample(["T1059", "T1055", "T9999"], ["T1059", "T1027"], mode="technique")
        assert s.n_hit == 1
        assert s.precision == pytest.approx(1 / 3)
        assert s.recall == pytest.approx(1 / 2)

    def test_empty_prediction_scores_zero_not_error(self):
        s = score_sample([], ["T1059"], mode="technique")
        assert s.precision == 0.0 and s.recall == 0.0 and s.reciprocal_rank == 0.0

    def test_validity_filter_drops_unknown_ids_before_scoring(self):
        valid = {"T1059"}
        s = score_sample(["T9999", "T1059"], ["T1059"], mode="technique", valid_ids=valid)
        assert s.n_pred == 1
        assert s.precision == 1.0

    def test_reciprocal_rank_uses_true_ranking(self):
        s = score_sample(["T1055", "T1027", "T1059"], ["T1059"], mode="technique")
        assert s.reciprocal_rank == pytest.approx(1 / 3)


class TestCorpusAggregation:
    def test_f1_is_computed_from_the_means_not_mean_of_f1s(self):
        # Sample A: P=1.0 R=0.5   Sample B: P=0.0 R=0.0
        # mean-of-F1  = (0.6667 + 0) / 2 = 0.3333
        # F1-of-means = 2*0.5*0.25 / 0.75 = 0.3333... coincidence at these
        # values, so use a case where they differ.
        samples = [
            (["T1059", "T1055"], ["T1059"]),   # P=0.5 R=1.0  F1=0.6667
            (["T1027"], ["T1027", "T1105"]),   # P=1.0 R=0.5  F1=0.6667
            ([], ["T1105"]),                   # P=0   R=0    F1=0
        ]
        c = score_corpus(samples, mode="technique")
        assert c.precision == pytest.approx(0.5)
        assert c.recall == pytest.approx(0.5)
        assert c.f1 == pytest.approx(0.5)
        mean_of_f1 = (2 / 3 + 2 / 3 + 0) / 3
        assert c.f1 != pytest.approx(mean_of_f1)

    def test_micro_f1_pools_counts(self):
        samples = [
            (["T1059", "T1055"], ["T1059"]),
            (["T1027"], ["T1027", "T1105"]),
        ]
        c = score_corpus(samples, mode="technique")
        # pooled: hits 2, preds 3, golds 3 -> P=R=F1=2/3
        assert c.f1_micro == pytest.approx(2 / 3)

    def test_counts_empty_predictions(self):
        c = score_corpus([([], ["T1059"]), (["T1059"], ["T1059"])], mode="technique")
        assert c.n_empty_predictions == 1
        assert c.n_samples == 2

    def test_empty_corpus_is_all_zero(self):
        c = score_corpus([], mode="technique")
        assert c.n_samples == 0 and c.f1 == 0.0


class TestAtK:
    def test_truncates_to_k_before_scoring(self):
        samples = [(["T1055", "T1027", "T1059"], ["T1059"])]
        assert score_at_k(samples, 1, mode="technique").recall == 0.0
        assert score_at_k(samples, 3, mode="technique").recall == 1.0

    def test_precision_at_1_is_hit_rate_for_single_label(self):
        samples = [(["T1059"], ["T1059"]), (["T1055"], ["T1059"])]
        assert score_at_k(samples, 1, mode="technique").precision == pytest.approx(0.5)
