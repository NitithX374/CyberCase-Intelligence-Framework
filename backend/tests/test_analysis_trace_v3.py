import pytest
from pydantic import ValidationError

from app.services.case_analysis.compatibility import read_analysis_trace
from app.services.case_analysis.contracts import AnalysisTrace, AnalysisTraceV3
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
    validate_analysis_trace_v3,
)


def build_trace(
    *,
    claims: list[dict[str, object]] | None = None,
    gaps: list[dict[str, object]] | None = None,
    retrieval_context_id: str | None = None,
) -> AnalysisTraceV3:
    return AnalysisTraceV3.model_validate(
        {
            "version": "analysis_trace_v3",
            "validation_status": "validated",
            "analysis_mode": "case_overview",
            "summary": "Evidence-bound case overview.",
            "claims": claims
            if claims is not None
            else [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The complainant reported a loss.",
                    "epistemic_status": "reported",
                    "supporting_source_message_ids": ["message-1"],
                    "contradicting_source_message_ids": [],
                    "reasoning_summary": None,
                }
            ],
            "gaps": gaps or [],
            "mitre_associations": [],
            "evidence_sha256": "a" * 64,
            "retrieval_context_id": retrieval_context_id,
        }
    )


def reported_claim(
    *,
    claim_id: str = "A-01",
    supporting: list[str] | None = None,
    contradicting: list[str] | None = None,
) -> dict[str, object]:
    return {
        "claim_id": claim_id,
        "claim_type": "reported",
        "text": "The complainant reported a loss.",
        "epistemic_status": "reported",
        "supporting_source_message_ids": supporting or [],
        "contradicting_source_message_ids": contradicting or [],
        "reasoning_summary": None,
    }


def analysis_gap(
    *,
    gap_id: str = "G-01",
    status: str = "NOT_PROVIDED",
    affected_claim_ids: list[str] | None = None,
    askable: bool = True,
) -> dict[str, object]:
    return {
        "gap_id": gap_id,
        "topic": "Missing case information",
        "status": status,
        "description": "The information is unavailable in the current evidence.",
        "affected_claim_ids": affected_claim_ids or [],
        "reason": "The authoritative sources do not establish it.",
        "priority": "medium",
        "askable": askable,
    }


def test_valid_reported_claim() -> None:
    trace = build_trace(claims=[reported_claim(supporting=["message-1"])])
    validated = validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert validated.claims[0].claim_type == "reported"


def test_reported_claim_without_support_is_rejected() -> None:
    trace = build_trace(claims=[reported_claim()])
    with pytest.raises(AnalysisTraceProvenanceError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids=set())
    assert raised.value.code == "analysis_trace_v3_reported_claim_unbound"


def test_valid_analytical_inference() -> None:
    trace = build_trace(
        claims=[
            {
                "claim_id": "A-01",
                "claim_type": "analytical_inference",
                "text": "The loss likely occurred before the inventory count.",
                "epistemic_status": "suspected",
                "supporting_source_message_ids": ["message-1"],
                "contradicting_source_message_ids": [],
                "reasoning_summary": "The item was absent at the first documented count.",
            }
        ]
    )
    validated = validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert validated.claims[0].reasoning_summary is not None


def test_valid_unknown_not_established_claim() -> None:
    trace = build_trace(
        claims=[
            {
                "claim_id": "A-01",
                "claim_type": "unknown",
                "text": "The time of the loss is not established.",
                "epistemic_status": "not_established",
                "supporting_source_message_ids": [],
                "contradicting_source_message_ids": [],
                "reasoning_summary": None,
            }
        ]
    )
    validated = validate_analysis_trace_v3(trace, source_message_ids=set())
    assert validated.claims[0].epistemic_status == "not_established"


@pytest.mark.parametrize(
    ("field_name", "expected_code"),
    [
        ("supporting_source_message_ids", "analysis_trace_v3_support_outside_evidence"),
        ("contradicting_source_message_ids", "analysis_trace_v3_contradiction_outside_evidence"),
    ],
)
def test_claim_source_outside_evidence_snapshot_is_rejected(
    field_name: str,
    expected_code: str,
) -> None:
    claim = reported_claim(supporting=["message-1"])
    claim[field_name] = ["outside-message"]
    trace = build_trace(claims=[claim])
    with pytest.raises(AnalysisTraceProvenanceError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert raised.value.code == expected_code


def test_same_source_cannot_support_and_contradict_claim() -> None:
    trace = build_trace(
        claims=[
            reported_claim(
                supporting=["message-1"],
                contradicting=["message-1"],
            )
        ]
    )
    with pytest.raises(AnalysisTraceProvenanceError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert raised.value.code == "analysis_trace_v3_conflicting_source_role"


def test_inference_without_reasoning_summary_is_rejected() -> None:
    trace = build_trace(
        claims=[
            {
                "claim_id": "A-01",
                "claim_type": "analytical_inference",
                "text": "The event likely occurred overnight.",
                "epistemic_status": "suspected",
                "supporting_source_message_ids": ["message-1"],
                "contradicting_source_message_ids": [],
                "reasoning_summary": None,
            }
        ]
    )
    with pytest.raises(AnalysisTraceStructureError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert raised.value.code == "analysis_trace_v3_inference_without_reasoning"


def test_duplicate_claim_id_is_rejected() -> None:
    trace = build_trace(
        claims=[
            reported_claim(supporting=["message-1"]),
            reported_claim(supporting=["message-2"]),
        ]
    )
    with pytest.raises(AnalysisTraceStructureError) as raised:
        validate_analysis_trace_v3(
            trace,
            source_message_ids={"message-1", "message-2"},
        )
    assert raised.value.code == "analysis_trace_v3_duplicate_claim_id"


def test_duplicate_gap_id_is_rejected() -> None:
    gap = analysis_gap()
    trace = build_trace(gaps=[gap, gap])
    with pytest.raises(AnalysisTraceStructureError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert raised.value.code == "analysis_trace_v3_duplicate_gap_id"


def test_gap_referencing_nonexistent_claim_is_rejected() -> None:
    trace = build_trace(gaps=[analysis_gap(status="AMBIGUOUS", affected_claim_ids=["A-99"])])
    with pytest.raises(AnalysisTraceStructureError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert raised.value.code == "analysis_trace_v3_gap_unknown_claim"


def test_explicitly_unknown_case_level_gap_parses_correctly() -> None:
    trace = build_trace(gaps=[analysis_gap(status="EXPLICITLY_UNKNOWN", askable=False)])
    validated = validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert validated.gaps[0].status == "EXPLICITLY_UNKNOWN"
    assert validated.gaps[0].askable is False


def test_explicitly_unknown_gap_cannot_be_askable() -> None:
    trace = build_trace(gaps=[analysis_gap(status="EXPLICITLY_UNKNOWN")])
    with pytest.raises(AnalysisTraceStructureError) as raised:
        validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert raised.value.code == "analysis_trace_v3_explicit_unknown_askable"


def test_reported_claim_can_preserve_conflicting_evidence() -> None:
    claim = reported_claim(
        supporting=["message-1"],
        contradicting=["message-2"],
    )
    claim["epistemic_status"] = "contradicted"
    trace = build_trace(claims=[claim])
    validated = validate_analysis_trace_v3(
        trace,
        source_message_ids={"message-1", "message-2"},
    )
    assert validated.claims[0].claim_type == "reported"
    assert validated.claims[0].epistemic_status == "contradicted"
    assert validated.claims[0].contradicting_source_message_ids == ["message-2"]


def test_v2_trace_remains_readable_without_v3_reinterpretation() -> None:
    trace = read_analysis_trace(
        {
            "version": "analysis_trace_v2",
            "validation_status": "validated",
            "analysis_mode": "case_overview",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "A source reported a loss.",
                    "epistemic_status": "reported",
                    "source_message_ids": ["message-1"],
                }
            ],
            "mitre_associations": [],
            "retrieval_context_id": "context-1",
            "evidence_sha256": "b" * 64,
        }
    )
    assert isinstance(trace, AnalysisTrace)
    assert trace.version == "analysis_trace_v2"
    assert trace.claims[0].source_message_ids == ["message-1"]
    assert not hasattr(trace, "gaps")


def test_v3_trace_with_null_retrieval_context_is_valid() -> None:
    trace = build_trace(retrieval_context_id=None)
    validated = validate_analysis_trace_v3(trace, source_message_ids={"message-1"})
    assert validated.retrieval_context_id is None


def test_v3_case_overview_requires_evidence_hash() -> None:
    payload = build_trace().model_dump()
    payload.pop("evidence_sha256")
    with pytest.raises(ValidationError):
        AnalysisTraceV3.model_validate(payload)
