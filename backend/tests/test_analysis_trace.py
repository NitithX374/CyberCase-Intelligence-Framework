import pytest

from app.services.case_analysis.contracts import ProviderCaseAnalysis
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    validate_analysis_trace,
)


def analysis(source_ids: list[str], technique_id: str = "T1190") -> ProviderCaseAnalysis:
    return ProviderCaseAnalysis.model_validate(
        {
            "version": "analysis_trace_v2",
            "answer": "Grounded answer",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The user reported exploitation.",
                    "epistemic_status": "reported",
                    "source_message_ids": source_ids,
                }
            ],
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
        }
    )


def test_trace_binds_reported_claims_to_messages_and_mitre_to_retrieval() -> None:
    trace = validate_analysis_trace(
        analysis(["message-1"]),
        source_message_ids={"message-1"},
        mitre_table=[{"technique_id": "T1190"}],
        analysis_mode="case_overview",
    )
    assert trace.version == "analysis_trace_v2"
    assert trace.claims[0].source_message_ids == ["message-1"]


def test_reported_claim_cannot_cite_a_non_evidence_message() -> None:
    with pytest.raises(AnalysisTraceProvenanceError):
        validate_analysis_trace(
            analysis(["analyst-question"]),
            source_message_ids={"message-1"},
            mitre_table=[{"technique_id": "T1190"}],
            analysis_mode="case_overview",
        )


def test_mitre_association_cannot_escape_bound_context() -> None:
    with pytest.raises(AnalysisTraceProvenanceError):
        validate_analysis_trace(
            analysis(["message-1"], technique_id="T1059"),
            source_message_ids={"message-1"},
            mitre_table=[{"technique_id": "T1190"}],
            analysis_mode="case_overview",
        )
