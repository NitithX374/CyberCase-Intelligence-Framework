from __future__ import annotations

import json

import numpy as np
import pytest
from research.attribution_benchmark.bge_similarity_report import write_results
from research.attribution_benchmark.bge_similarity_runtime import cosine_pairs, pair_batches
from research.attribution_benchmark.bge_translation_similarity import read_scores
from research.attribution_benchmark.receipts import digest


def test_cosine_is_scale_invariant_and_keeps_pair_alignment():
    vectors = np.array([[2, 0], [5, 0], [0, 3], [0, -2], [1, 0], [0, 1]])
    np.testing.assert_allclose(cosine_pairs(vectors), [1, -1, 0])


@pytest.mark.parametrize(
    "vectors",
    [np.array([[0, 0], [1, 2]]), np.array([[1, float("nan")], [1, 2]]), np.array([[1, 2]])],
)
def test_invalid_vectors_fail_instead_of_emitting_similarity(vectors):
    with pytest.raises(ValueError):
        cosine_pairs(vectors)


def test_resume_rejects_changed_translation_unknown_and_duplicate_pairs(tmp_path):
    path = tmp_path / "scores.jsonl"
    pair = {"source": "John sent an email.", "translation": "จอห์นส่งอีเมล"}
    record = {"key": "k", "contract_sha256": "contract", "pair_sha256": digest(pair), "cosine": 0.8}
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    assert read_scores(path, {"k": pair}, "contract")["k"]["cosine"] == 0.8
    with pytest.raises(ValueError, match="identity"):
        read_scores(path, {"k": {**pair, "translation": "จอห์นไม่ได้ส่งอีเมล"}}, "contract")
    with pytest.raises(ValueError, match="Unknown"):
        read_scores(path, {}, "contract")
    path.write_text((json.dumps(record) + "\n") * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        read_scores(path, {"k": pair}, "contract")


def test_sorted_length_batches_preserve_every_pair_without_padding_overflow():
    lengths = {"long": (400, 432), "a": (20, 22), "b": (25, 30)}
    batches = list(pair_batches(lengths, lengths, 2, 900))
    assert {key for batch in batches for key in batch} == set(lengths)
    for batch in batches:
        assert len(batch) <= 2
        assert 2 * len(batch) * max(max(lengths[key]) for key in batch) <= 900


def test_report_keeps_repeated_units_and_empty_bundles_distinct(tmp_path):
    pairs = {
        key: {
            "key": key,
            "source": f"original {key}",
            "translation": f"translated {key}",
            "roles": ["claim" if key == "c" else "source_unit"],
        }
        for key in ("c", "u")
    }
    scores = {
        key: {
            "key": key,
            "cosine": cosine,
            "en_tokens": 3,
            "th_tokens": 4,
            "en_truncated": False,
            "th_truncated": False,
        }
        for key, cosine in (("c", 0.8), ("u", 0.6))
    }
    examples = [
        {
            "id": "one",
            "split": "test",
            "gold": "attributable",
            "claim_key": "c",
            "unit_keys": ["u", "u"],
        },
        {
            "id": "two",
            "split": "test_ood",
            "gold": "not attributable",
            "claim_key": "c",
            "unit_keys": ["u"],
        },
        {
            "id": "empty",
            "split": "test_ood",
            "gold": "not attributable",
            "claim_key": "c",
            "unit_keys": [],
        },
    ]
    (tmp_path / "scores.jsonl").write_text("", encoding="utf-8")
    summary = write_results(
        tmp_path, examples, pairs, scores, {"runtime": {"revision": "r"}, "input": {}}
    )
    assert summary["splits"]["test"]["source_unit_occurrences"]["n"] == 2
    assert summary["splits"]["test"]["unique_source_units"]["n"] == 1
    rows = [
        json.loads(line)
        for line in (tmp_path / "rows.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert rows[2]["source_unit_mean_cosine"] is None
    assert rows[2]["gold"] == "not attributable"
