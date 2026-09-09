import pytest
from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    AnalysisTrace,
    AnalysisTraceV3,
    read_analysis_trace,
)
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    validate_analysis_trace_v3,
)


def analysis_v3(
    source_ids: list[str], technique_id: str = "T1190"
) -> AnalysisTraceV3:
    return AnalysisTraceV3.model_validate(
        {
            "version": "analysis_trace_v3",
            "validation_status": "validated",
            "analysis_mode": "case_overview",
            "summary": "Grounded case overview",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The user reported exploitation.",
                    "epistemic_status": "reported",
                    "supporting_source_message_ids": source_ids,
                    "contradicting_source_message_ids": [],
                    "reasoning_summary": None,
                }
            ],
            "gaps": [],
            "mitre_associations": [
                {
                    "association_id": "MA-01",
                    "technique_id": technique_id,
                    "claim_ids": ["A-01"],
                    "reason": "The reported behavior is consistent with exploitation.",
                    "status": "candidate_only",
                    "support_role": "external_technical_context",
                }
            ],
            "evidence_sha256": "a" * 64,
            "retrieval_context_id": "retrieval-context-1",
        }
    )


def test_trace_binds_reported_claims_to_messages_and_mitre_to_retrieval() -> None:
    trace = validate_analysis_trace_v3(
        analysis_v3(["message-1"]),
        source_message_ids={"message-1"},
        mitre_table=[{"technique_id": "T1190"}],
    )
    assert trace.version == "analysis_trace_v3"
    assert trace.claims[0].supporting_source_message_ids == ["message-1"]


def test_reported_claim_cannot_cite_a_non_evidence_message() -> None:
    with pytest.raises(AnalysisTraceProvenanceError):
        validate_analysis_trace_v3(
            analysis_v3(["analyst-question"]),
            source_message_ids={"message-1"},
            mitre_table=[{"technique_id": "T1190"}],
        )


def test_mitre_association_cannot_escape_bound_context() -> None:
    with pytest.raises(AnalysisTraceProvenanceError):
        validate_analysis_trace_v3(
            analysis_v3(["message-1"], technique_id="T1059"),
            source_message_ids={"message-1"},
            mitre_table=[{"technique_id": "T1190"}],
        )


def test_v3_validation_rejects_legacy_v2_shape() -> None:
    legacy_payload = {
        "version": "analysis_trace_v2",
        "claims": [{"claim_id": "A-01", "source_message_ids": ["msg-1"]}],
        "mitre_associations": [],
    }
    with pytest.raises(ValidationError):
        AnalysisTraceV3.model_validate(legacy_payload)


def test_legacy_v2_trace_read_only_deserialization() -> None:
    legacy_record = {
        "version": "analysis_trace_v2",
        "validation_status": "validated",
        "analysis_mode": "case_overview",
        "claims": [
            {
                "claim_id": "A-01",
                "claim_type": "reported",
                "text": "The user reported an incident.",
                "epistemic_status": "reported",
                "source_message_ids": ["message-1"],
            }
        ],
        "mitre_associations": [],
        "retrieval_context_id": "ctx-1",
        "evidence_sha256": "f" * 64,
    }
    parsed = read_analysis_trace(legacy_record)
    assert isinstance(parsed, AnalysisTrace)
    assert parsed.version == "analysis_trace_v2"
    assert parsed.claims[0].source_message_ids == ["message-1"]
    assert not hasattr(parsed, "gaps")
