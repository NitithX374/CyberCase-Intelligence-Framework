import pytest
from app.services.case_analysis.stateSelector import (
    select_latest_canonical_case_overview,
)
from test_canonical_analysis_state import message, trace_payload


@pytest.mark.parametrize("trace", [
    {"version": "analysis_trace_v2"},
    {"version": "analysis_trace_v9", "analysis_mode": "case_overview"},
    {"version": "analysis_trace_v3", "analysis_mode": "case_overview"},
    {},
])
def test_newer_retired_or_invalid_overview_blocks_older_valid_record(trace):
    old = message(2, trace_payload("case_overview", summary="Old", gaps=[]))
    latest = message(4, trace)
    latest.metadata_json["analysis_kind"] = "grounded_main_analysis"
    assert select_latest_canonical_case_overview(
        [latest, old], evidence_sha256="a" * 64,
        source_message_ids={"message-1"},
    ) is None


@pytest.mark.parametrize("scope", [
    {"analysis_state_scope": "response_scoped"},
    {"canonical_case_state": False},
    {"chat_action": {"action": "ask"}},
])
def test_response_scope_wins_over_legacy_marker(scope):
    old = message(2, trace_payload("case_overview", summary="Old", gaps=[]))
    latest = message(4, {"version": "analysis_trace_v2"})
    latest.metadata_json.update({"analysis_kind": "grounded_main_analysis", **scope})
    selected = select_latest_canonical_case_overview(
        [old, latest], evidence_sha256="a" * 64,
        source_message_ids={"message-1"},
    )
    assert selected.message.id == old.id
