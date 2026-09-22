from experiments.ladder_joint_detection.matching import build_audit_bundle
from experiments.ladder_joint_detection.models import (
    ClassificationRecord,
    EntityRecord,
    EntityToken,
    SourceData,
)
from experiments.ladder_joint_detection.normalization import normalize_text
from experiments.ladder_joint_detection.validation import validate_audit_bundle


def _classification(text: str, label: int, row: int) -> ClassificationRecord:
    return ClassificationRecord(f"train-cls-{row:06d}", text, normalize_text(text), label, "train", row + 1)


def _entity(text: str, labels: tuple[str, ...], block: int) -> EntityRecord:
    tokens = tuple(EntityToken(token, label, block + index) for index, (token, label) in enumerate(zip(text.split(), labels, strict=True)))
    return EntityRecord(
        f"train-ent-{block:06d}",
        tokens,
        text,
        normalize_text(text),
        "train",
        block,
        block,
        block + len(tokens) - 1,
        "ATK" in labels,
    )


def test_partial_supervision_preserves_unmatched_positive() -> None:
    source = SourceData(
        {"train": (_classification("used PowerShell", 1, 1), _classification("ordinary", 1, 2), _classification("quiet", 0, 3)), "dev": (), "test": ()},
        {"train": (_entity("used PowerShell", ("ATK", "ATK"), 1),), "dev": (), "test": ()},
        (),
    )
    bundle = build_audit_bundle(source)
    validate_audit_bundle(bundle)
    rows = {row.classification.original_text: row for row in bundle.rows}
    assert bundle.decision == "PARTIALLY_SAFE"
    assert rows["used PowerShell"].span_loss_mask is True
    assert rows["ordinary"].span_loss_mask is False
    assert rows["quiet"].span_loss_mask is True


def test_negative_conflict_masks_negative_span_supervision() -> None:
    source = SourceData(
        {"train": (_classification("conflict", 0, 1),), "dev": (), "test": ()},
        {"train": (_entity("conflict", ("ATK",), 1),), "dev": (), "test": ()},
        (),
    )
    bundle = build_audit_bundle(source)
    row = bundle.rows[0]
    assert bundle.negative_span_supervision_safe is False
    assert row.has_span_annotation is False
    assert row.span_loss_mask is False
