from app.trace.trace import CaseInvolvedParty, CaseTimelineItem, CaseViewExtraction


def test_saved_extraction_metadata_reads_without_the_retired_extractor_fields():
    saved = CaseViewExtraction.model_validate(
        {
            "method": "retired-local-extractor",
            "model": "historical/model",
            "revision": "c" * 40,
            "library_version": "historical-version",
            "device": "cpu",
            "threshold": 0.5,
            "quantization": "int8",
            "runtime_revision": "d" * 40,
            "field_resolution_issues": [],
            "input_claim_ids": ["A-01"],
            "excluded_claim_ids": [],
            "duration_ms": 120,
        }
    )
    assert saved.method == "retired-local-extractor"
    assert saved.status == "completed"
    assert saved.warning is None
    assert "library_version" not in saved.model_dump()
    assert CaseViewExtraction.model_validate_json(saved.model_dump_json()) == saved


def test_saved_view_rows_read_without_claim_spans_or_projection_verdicts():
    party = CaseInvolvedParty.model_validate(
        {
            "name": "John",
            "role": "Victim",
            "claim_ids": ["A-01"],
            "field_spans": {"name": {"claim_id": "A-01", "start": 0, "end": 4}},
            "projection_grounding": {"verdict": "supported", "reason": "entailed"},
        }
    )
    assert party.name == "John"
    assert "field_spans" not in party.model_dump()
    assert "projection_grounding" not in party.model_dump()
    event = CaseTimelineItem(time="12 May 2026", event="A transfer occurred.", claim_ids=["A-01"])
    assert event.time == "12 May 2026"
