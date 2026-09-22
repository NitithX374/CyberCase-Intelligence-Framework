import json

from experiments.annoctr_external_validation.conversion import (
    convert_annotations,
    reconstruct_sentence,
)


def test_reconstruct_sentence_uses_context_fields_only() -> None:
    row = {
        "mention": "DNS over HTTPS",
        "_context_left": "The actor used ",
        "_context_right": " for command traffic.",
        "sentence_left": "ignored neighboring sentence",
        "sentence_right": "ignored next sentence",
    }
    assert reconstruct_sentence(row) == "The actor used DNS over HTTPS for command traffic."


def test_aggregate_technique_and_explicit_negative_rows(tmp_path) -> None:
    source = tmp_path / "rows.jsonl"
    rows = [
        {
            "mention": "ReconHellcat",
            "_context_left": "",
            "_context_right": " used the service.",
            "entity_type": "GROUP",
            "label_link": "http://example.test/group",
            "label_title": "ReconHellcat",
            "document": "doc-a",
        },
        {
            "mention": "DNS over HTTPS",
            "_context_left": "ReconHellcat used ",
            "_context_right": " for command traffic.",
            "entity_type": "TECHNIQUE",
            "label_link": "https://attack.mitre.org/techniques/T1071/004",
            "label_title": "DNS over HTTPS",
            "document": "doc-a",
        },
        {
            "mention": "The report was signed.",
            "_context_left": "",
            "_context_right": "",
            "entity_type": "TECHNIQUE",
            "label_link": "No Annotation",
            "label_title": "No Annotation",
            "document": "doc-a",
        },
    ]
    source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    result = convert_annotations(source)
    labels = {(sample.text, sample.gold_label) for sample in result.samples}
    assert ("ReconHellcat used DNS over HTTPS for command traffic.", 1) in labels
    assert ("The report was signed.", 0) in labels
    assert result.statistics["explicit_negative_rows"] == 1
