from experiments.ladder_joint_detection.models import (
    ClassificationRecord,
    EntityRecord,
    EntityToken,
)
from experiments.ladder_joint_detection.normalization import normalize_text, normalize_with_mapping
from experiments.ladder_joint_detection.spans import SpanMappingError, derive_spans


def test_normalization_preserves_case_and_words() -> None:
    assert normalize_text("  PowerShell   ( command )  " ) == "PowerShell (command)"


def test_normalization_mapping_tracks_original_ranges() -> None:
    mapped = normalize_with_mapping("  A   B  ")
    assert mapped.text == "A B"
    assert mapped.source_ranges[0] == (2, 3)
    assert mapped.source_ranges[-1] == (6, 7)


def test_derive_spans_from_atk_token_runs() -> None:
    classification = ClassificationRecord(
        "test-cls-000001",
        "The malware used PowerShell.",
        normalize_text("The malware used PowerShell."),
        1,
        "test",
        2,
    )
    tokens = (
        EntityToken("The", "O", 1),
        EntityToken("malware", "O", 2),
        EntityToken("used", "ATK", 3),
        EntityToken("PowerShell", "ATK", 4),
        EntityToken(".", "ATK", 5),
    )
    entity = EntityRecord(
        "test-ent-000001",
        tokens,
        "The malware used PowerShell .",
        normalize_text("The malware used PowerShell ."),
        "test",
        1,
        1,
        5,
        True,
    )
    assert derive_spans(classification, entity)[0].text == "used PowerShell."


def test_span_mapping_fails_closed_on_text_mismatch() -> None:
    classification = ClassificationRecord("test-cls-000001", "PowerShell", "PowerShell", 1, "test", 2)
    entity = EntityRecord(
        "test-ent-000001",
        (EntityToken("cmd", "ATK", 1),),
        "cmd",
        "cmd",
        "test",
        1,
        1,
        1,
        True,
    )
    try:
        derive_spans(classification, entity)
    except SpanMappingError:
        pass
    else:
        raise AssertionError("Expected exact span mapping to fail")
