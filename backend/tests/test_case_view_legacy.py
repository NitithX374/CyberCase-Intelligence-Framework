import pytest
from pydantic import ValidationError

from app.trace.trace import CaseInvolvedParty, CaseTimelineItem, CaseViewExtraction


def test_saved_extraction_metadata_does_not_require_an_installed_extractor():
    saved = CaseViewExtraction.model_validate(
        {
            "method": "retired-local-extractor",
            "model": "historical/model",
            "revision": "c" * 40,
            "library_version": "historical-version",
            "device": "cpu",
            "threshold": 0.5,
            "input_claim_ids": ["A-01"],
            "excluded_claim_ids": [],
            "duration_ms": 120,
        }
    )
    assert saved.method == "retired-local-extractor"
    assert saved.status == "completed"
    assert saved.warning is None
    assert CaseViewExtraction.model_validate_json(saved.model_dump_json()) == saved
    party = CaseInvolvedParty.model_validate(
        {
            "name": "John",
            "role": "Victim",
            "claim_ids": ["A-01"],
            "field_spans": {"name": {"claim_id": "A-01", "start": 0, "end": 4}},
        }
    )
    assert party.field_spans["name"].end == 4
    event = CaseTimelineItem(time="12 May 2026", event="A transfer occurred.", claim_ids=["A-01"])
    assert event.time == "12 May 2026"


def test_legacy_revision_hash_validation_is_preserved():
    with pytest.raises(ValidationError):
        CaseViewExtraction(
            method="retired-local-extractor",
            model="historical/model",
            revision="not-a-sha",
            input_claim_ids=[],
            excluded_claim_ids=[],
            duration_ms=0,
        )
