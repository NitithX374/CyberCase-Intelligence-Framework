import pytest
from pydantic import ValidationError

from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_analysis.contracts import CaseAnalysisFailure
from app.services.case_analysis.caseAnalysisResponseParser import (
    normalize_analysis_identifiers,
)
from test_general_case_analysis import parse, provider_payload, reported_claim


@pytest.mark.parametrize("source", ["1", "0", "S1", "source"])
def test_source_aliases_are_never_guessed(source):
    payload = provider_payload([reported_claim("Reported text", supporting=[source])])
    with pytest.raises(CaseAnalysisFailure):
        parse(
            payload,
            sources={"message-one", "message-two"},
            context={"source_message_ids": ["message-one", "message-two"]},
        )


def test_missing_source_is_not_filled_for_single_document():
    claim = reported_claim("Reported text")
    del claim["supporting_source_message_ids"]
    with pytest.raises(CaseAnalysisFailure) as error:
        parse(provider_payload([claim]), sources={"only-message"})
    assert error.value.code == "analysis_trace_v3_reported_claim_unbound"


def test_claim_identifiers_are_strictly_prefixed_and_leave_original_unchanged():
    original = {
        "claims": [
            {
                "claim_id": "claim-12",
                "supporting_source_message_ids": ["1"],
            }
        ]
    }
    normalized = normalize_analysis_identifiers(original)
    assert normalized["claims"][0]["claim_id"] == "A-12"
    assert normalized["claims"][0]["supporting_source_message_ids"] == ["1"]
    assert original["claims"][0]["claim_id"] == "claim-12"


def test_metadata_preserves_legacy_extensions_and_rejects_invalid_known_values():
    metadata = {
        "evidence_kind": "analyst_question",
        "historical_extension": {"value": 1},
    }
    assert serialize_message_metadata(metadata) == metadata
    with pytest.raises(ValidationError):
        serialize_message_metadata({"chat_action": {"action": "invented"}})
