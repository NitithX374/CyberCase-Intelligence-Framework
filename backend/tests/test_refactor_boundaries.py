import pytest
from pydantic import ValidationError

from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.response_identifiers import (
    normalize_analysis_identifiers,
)
from app.services.reports.report_view_model_builder import build_report_view_model
from test_general_case_analysis import parse, provider_payload, reported_claim
from test_report_view_model_and_pdf import make_realistic_report_read


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


def test_identifier_formatting_preserves_identity_and_input():
    original = {
        "claims": [{"claim_id": "claim-12", "supporting_source_message_ids": ["1"]}]
    }
    normalized = normalize_analysis_identifiers(original)
    assert normalized["claims"][0]["claim_id"] == "A-12"
    assert normalized["claims"][0]["supporting_source_message_ids"] == ["1"]
    assert original["claims"][0]["claim_id"] == "claim-12"


@pytest.mark.parametrize("snapshot", [{}, {"source_messages": []}])
def test_malformed_report_snapshot_does_not_enter_legacy_reader(snapshot):
    report, _ = make_realistic_report_read()
    report.source_snapshot = snapshot
    with pytest.raises(ValidationError):
        build_report_view_model(report)


def test_snapshot_without_mitre_does_not_resurrect_section_mappings():
    report, _ = make_realistic_report_read()
    report.source_snapshot["mitre_rows"] = []
    model = build_report_view_model(report)
    assert not model.has_mitre_mappings
    report.source_snapshot = None
    assert build_report_view_model(report).has_mitre_mappings


def test_metadata_preserves_legacy_extensions_and_rejects_invalid_known_values():
    metadata = {
        "evidence_kind": "analyst_question",
        "historical_extension": {"value": 1},
    }
    assert serialize_message_metadata(metadata) == metadata
    with pytest.raises(ValidationError):
        serialize_message_metadata({"chat_action": {"action": "invented"}})
