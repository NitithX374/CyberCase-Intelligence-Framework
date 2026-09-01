import pytest

from app.services.case_analysis.contracts import AnalysisTraceV3, CaseAnalysisResult
from app.services.case_analysis.gap_assembly import (
    assemble_claim_linked_gaps,
    enrich_case_analysis_result,
)
from app.services.case_analysis.validation import AnalysisTraceStructureError
from app.services.followup.schemas import GapAnalysis, GapItem


def claim(claim_id: str, text: str) -> dict[str, object]:
    return {
        "claim_id": claim_id,
        "claim_type": "reported",
        "text": text,
        "epistemic_status": "reported",
        "supporting_source_message_ids": ["message-1"],
        "contradicting_source_message_ids": [],
        "reasoning_summary": None,
    }


def trace(
    *,
    claims: list[dict[str, object]] | None = None,
    with_mitre: bool = False,
) -> AnalysisTraceV3:
    return AnalysisTraceV3.model_validate(
        {
            "analysis_mode": "case_overview",
            "summary": "Evidence-bound case overview.",
            "claims": claims
            or [claim("A-01", "The suspect may possess the missing property.")],
            "gaps": [],
            "mitre_associations": (
                [
                    {
                        "association_id": "MA-01",
                        "technique_id": "T1190",
                        "claim_ids": ["A-01"],
                        "reason": "External context may explain the observed activity.",
                        "status": "candidate_only",
                        "support_role": "external_technical_context",
                    }
                ]
                if with_mitre
                else []
            ),
            "evidence_sha256": "a" * 64,
            "retrieval_context_id": "ctx-1" if with_mitre else None,
        }
    )


def gap(
    *,
    topic: str = "Property identity",
    status: str = "NOT_PROVIDED",
    affects: str = "A-01 — suspect possession of the missing property",
    priority: str = "medium",
    askable: bool = True,
) -> GapItem:
    return GapItem.model_validate(
        {
            "topic": topic,
            "status": status,
            "description": "The supplied evidence does not establish this information.",
            "affects": affects,
            "reason": "Resolving it materially constrains the current analysis.",
            "priority": priority,
            "askable": askable,
        }
    )


def assemble(value: AnalysisTraceV3, gaps: list[GapItem]) -> AnalysisTraceV3:
    return assemble_claim_linked_gaps(
        value,
        GapAnalysis(gaps=gaps),
        source_message_ids={"message-1"},
        mitre_table=[{"technique_id": "T1190"}],
    )


def test_gap_links_to_one_claim_by_stable_id() -> None:
    result = assemble(trace(), [gap()])
    assert result.gaps[0].gap_id == "G-01"
    assert result.gaps[0].affected_claim_ids == ["A-01"]


def test_one_gap_can_affect_multiple_claims() -> None:
    value = trace(
        claims=[
            claim("A-01", "The suspect may possess the missing property."),
            claim("A-02", "The object in the footage may be the missing property."),
        ]
    )
    result = assemble(value, [gap(affects="A-01, A-02 — property association")])
    assert result.gaps[0].affected_claim_ids == ["A-01", "A-02"]


def test_free_text_affects_is_linked_conservatively() -> None:
    value = trace(
        claims=[
            claim("A-01", "The suspect may possess the missing property."),
            claim("A-02", "The witness reported seeing a blue vehicle."),
        ]
    )
    result = assemble(
        value,
        [gap(affects="whether the suspect possessed the missing property")],
    )
    assert result.gaps[0].affected_claim_ids == ["A-01"]


def test_case_level_gap_may_have_no_claim_link() -> None:
    result = assemble(trace(), [gap(affects="overall administrative completeness")])
    assert result.gaps[0].affected_claim_ids == []


@pytest.mark.parametrize(
    ("status", "askable"),
    [
        ("NOT_PROVIDED", True),
        ("EXPLICITLY_UNKNOWN", False),
        ("AMBIGUOUS", True),
        ("CONFLICTING", True),
    ],
)
def test_gap_status_is_preserved(status: str, askable: bool) -> None:
    result = assemble(trace(), [gap(status=status, askable=askable)])
    assert result.gaps[0].status == status
    assert result.gaps[0].askable is askable


def test_priority_order_controls_stable_gap_ids() -> None:
    result = assemble(
        trace(),
        [
            gap(topic="Low", priority="low"),
            gap(topic="High first", priority="high"),
            gap(topic="High second", priority="high"),
        ],
    )
    assert [(item.gap_id, item.topic) for item in result.gaps] == [
        ("G-01", "High first"),
        ("G-02", "High second"),
        ("G-03", "Low"),
    ]


def test_gap_assembly_preserves_analysis_and_provenance_bindings() -> None:
    original = trace(with_mitre=True)
    result = assemble(original, [gap()])
    assert result.claims == original.claims
    assert result.mitre_associations == original.mitre_associations
    assert result.evidence_sha256 == original.evidence_sha256
    assert result.retrieval_context_id == original.retrieval_context_id


def test_unknown_direct_claim_reference_fails_without_persisting_empty_gaps() -> None:
    original = trace()
    with pytest.raises(AnalysisTraceStructureError) as raised:
        assemble(original, [gap(affects="A-99")])
    assert raised.value.code == "analysis_trace_v3_gap_unknown_claim"

    result = enrich_case_analysis_result(
        CaseAnalysisResult(answer="analysis", trace=original),
        GapAnalysis(gaps=[gap(affects="A-99")]),
        source_message_ids={"message-1"},
    )
    assert result.trace is None
    assert result.trace_failure is not None
    assert result.trace_failure.failure_code == "analysis_trace_v3_gap_unknown_claim"


def test_missing_gap_analysis_marks_v3_trace_unavailable() -> None:
    result = enrich_case_analysis_result(
        CaseAnalysisResult(answer="analysis", trace=trace()),
        None,
        source_message_ids={"message-1"},
    )
    assert result.trace is None
    assert result.trace_failure is not None
    assert (
        result.trace_failure.failure_code
        == "analysis_trace_v3_gap_analysis_unavailable"
    )


@pytest.mark.parametrize(
    "case_claim",
    [
        "The stolen bicycle was last seen outside the shop.",
        "The payment was sent to the reported merchant account.",
        "The complainant reported being struck during the dispute.",
        "Both parties claim an interest in the same property.",
    ],
)
def test_general_case_without_rag_or_mitre_validates(case_claim: str) -> None:
    value = trace(claims=[claim("A-01", case_claim)])
    result = assemble(value, [gap(affects="case-level unresolved context")])
    assert result.retrieval_context_id is None
    assert result.mitre_associations == []


def test_cyber_case_with_mitre_still_validates() -> None:
    result = assemble(trace(with_mitre=True), [gap()])
    assert result.mitre_associations[0].technique_id == "T1190"
