from experiments.annoctr_external_validation.conversion import (
    BinarySample,
    ConversionResult,
    SentenceGroup,
)
from experiments.annoctr_external_validation.source import DatasetSources
from experiments.annoctr_external_validation.validation import validate_dataset


def _sources() -> DatasetSources:
    return DatasetSources(
        root=__import__("pathlib").Path("."),
        corpus_root=__import__("pathlib").Path("."),
        linking_path=__import__("pathlib").Path("rows.jsonl"),
        text_root=__import__("pathlib").Path("."),
        split_documents={"train": ("train-doc",), "dev": ("dev-doc",), "test": ("test-doc",)},
        native_candidates=(),
    )


def _result(samples: tuple[BinarySample, ...]) -> ConversionResult:
    groups = tuple(
        SentenceGroup(
            sample=sample,
            row_count=1,
            technique_rows=int(sample.has_attack_technique),
            explicit_negative_rows=int(not sample.has_attack_technique),
            entity_types=("TECHNIQUE",),
            source_lines=(1,),
        )
        for sample in samples
    )
    return ConversionResult(samples=samples, groups=groups, statistics={})


def test_validation_rejects_non_test_documents() -> None:
    samples = (
        BinarySample("attack", 1, "train-doc", True, "test"),
        BinarySample("ordinary", 0, "test-doc", False, "test"),
    )
    try:
        validate_dataset(_result(samples), _sources())
    except ValueError as error:
        assert "Non-test documents" in str(error)
    else:
        raise AssertionError("Expected non-test document validation failure")
