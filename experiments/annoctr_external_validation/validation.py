from __future__ import annotations

from collections import Counter
from typing import Any

from .conversion import ConversionResult
from .source import DatasetSources


class ValidationError(ValueError):
    pass


def validate_dataset(result: ConversionResult, sources: DatasetSources) -> dict[str, Any]:
    samples = result.samples
    if not samples:
        raise ValidationError("The binary AnnoCTR dataset is empty")
    labels = {sample.gold_label for sample in samples}
    if labels != {0, 1}:
        raise ValidationError(f"Expected both binary labels, got {sorted(labels)}")
    keys = [(sample.document, sample.text) for sample in samples]
    duplicate_keys = [key for key, count in Counter(keys).items() if count > 1]
    if duplicate_keys:
        raise ValidationError(f"Duplicate sentence rows remain: {duplicate_keys[:3]}")
    empty_text = [sample.document for sample in samples if not sample.text.strip()]
    if empty_text:
        raise ValidationError(f"Empty text remains for documents: {empty_text[:3]}")
    split_by_document = {
        document: split
        for split, documents in sources.split_documents.items()
        for document in documents
    }
    unknown_documents = sorted(
        {sample.document for sample in samples if sample.document not in split_by_document}
    )
    if unknown_documents:
        raise ValidationError(f"Samples reference unknown documents: {unknown_documents[:3]}")
    mixed_split_documents = sorted(
        {
            sample.document
            for sample in samples
            if split_by_document[sample.document] != "test"
        }
    )
    if mixed_split_documents:
        raise ValidationError(
            f"Non-test documents entered the external dataset: {mixed_split_documents[:3]}"
        )
    conflicting_groups = [
        group.sample.document
        for group in result.groups
        if group.sample.gold_label == 0 and group.technique_rows > 0
    ]
    if conflicting_groups:
        raise ValidationError(
            f"Negative sentence has a technique annotation: {conflicting_groups[:3]}"
        )
    document_counts = Counter(sample.document for sample in samples)
    test_documents = set(sources.split_documents["test"])
    return {
        "official_split_document_count": len(test_documents),
        "dataset_document_count": len(document_counts),
        "documents_without_linking_rows": sorted(test_documents - set(document_counts)),
        "document_counts": dict(sorted(document_counts.items())),
        "duplicate_output_rows": 0,
        "empty_text_rows": 0,
        "mixed_split_rows": 0,
        "negative_technique_conflicts": 0,
        "native_sentence_candidates": [str(path) for path in sources.native_candidates],
    }
