from collections import Counter

from experiments.ladder_joint_detection.constants import SPLITS
from experiments.ladder_joint_detection.matching import build_audit_bundle
from experiments.ladder_joint_detection.parsing import load_sources
from experiments.ladder_joint_detection.validation import validate_audit_bundle


def test_real_ladder_sources_preserve_expected_contract() -> None:
    source = load_sources()
    assert not source.malformed
    assert set(source.classifications) == set(SPLITS)
    assert set(source.entities) == set(SPLITS)
    assert Counter(record.sentence_label for record in source.classifications["test"]) == Counter({0: 331, 1: 331})
    assert {token.label for record in source.entities["test"] for token in record.tokens} <= {"ATK", "O"}


def test_real_ladder_audit_is_partial_and_conflict_free() -> None:
    source = load_sources()
    bundle = build_audit_bundle(source)
    repeated = build_audit_bundle(source)
    validate_audit_bundle(bundle)
    assert bundle.rows == repeated.rows
    assert bundle.decision == "PARTIALLY_SAFE"
    assert bundle.classification_label_conflict_keys == ()
    assert bundle.negative_conflict_keys == ()
    assert bundle.negative_span_supervision_safe is True
