import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from app.services.case_analysis.case_analysis_executor import MainCaseAnalysisService
from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.case_analysis_response_parser import (
    parse_case_analysis_response,
)
from app.services.case_analysis.contracts import AnalysisTraceV3


DOMAIN_CLAIMS = [
    ("theft", "The owner reported that a bicycle was missing."),
    ("fraud", "The customer reported transferring money after a representation."),
    ("assault", "A witness reported an injury after a physical confrontation."),
    ("property", "One party reported possessing the disputed property."),
    ("cybercrime", "The administrator reported a PowerShell network connection."),
]


def reported_claim(
    text: str,
    *,
    supporting: list[str] | None = None,
    contradicting: list[str] | None = None,
    status: str = "reported",
) -> dict[str, object]:
    return {
        "claim_id": "A-01",
        "claim_type": "reported",
        "text": text,
        "epistemic_status": status,
        "supporting_source_message_ids": supporting or ["S1"],
        "contradicting_source_message_ids": contradicting or [],
        "reasoning_summary": None,
    }


def provider_payload(
    claims: list[dict[str, object]],
    *,
    answer: str = "Grounded case answer.",
    associations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "version": "analysis_trace_v3",
        "answer": answer,
        "summary": "Grounded case summary with current uncertainty preserved.",
        "claims": claims,
        "mitre_associations": associations or [],
    }


def response_for(payload: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={"content": [{"type": "text", "text": json.dumps(payload)}]},
    )


def parse(
    payload: dict[str, object],
    *,
    sources: set[str] | None = None,
    context: dict[str, object] | None = None,
    mode: str = "case_overview",
):
    return parse_case_analysis_response(
        response_for(payload),
        source_message_ids=sources or {"S1"},
        analysis_context=context or {},
        analysis_mode=mode,
        evidence_sha256="a" * 64,
    )


@pytest.mark.parametrize(("domain", "claim_text"), DOMAIN_CLAIMS)
def test_same_runtime_contract_handles_five_case_domains_without_required_mitre(
    domain: str,
    claim_text: str,
) -> None:
    result = parse(provider_payload([reported_claim(claim_text)]))
    assert isinstance(result.trace, AnalysisTraceV3)
    assert result.trace.retrieval_context_id is None
    assert result.trace.mitre_associations == []
    assert result.trace.claims[0].supporting_source_message_ids == ["S1"]
    if domain == "assault":
        assert "attack" not in result.answer.lower()
        assert "cyber" not in result.answer.lower()


def test_property_case_preserves_conflicting_reported_sources() -> None:
    claim = reported_claim(
        "The parties reported conflicting accounts of possession.",
        supporting=["S1"],
        contradicting=["S2"],
        status="contradicted",
    )
    result = parse(provider_payload([claim]), sources={"S1", "S2"})
    assert result.trace is not None
    assert result.trace.claims[0].claim_type == "reported"
    assert result.trace.claims[0].epistemic_status == "contradicted"
    assert result.trace.claims[0].contradicting_source_message_ids == ["S2"]


def test_analytical_inference_retains_sources_and_visible_reasoning() -> None:
    inference = {
        "claim_id": "A-01",
        "claim_type": "analytical_inference",
        "text": "The available evidence suggests the transfer followed the representation.",
        "epistemic_status": "suspected",
        "supporting_source_message_ids": ["S1", "S2"],
        "contradicting_source_message_ids": [],
        "reasoning_summary": "The messages precede the documented transfer.",
    }
    result = parse(provider_payload([inference]), sources={"S1", "S2"})
    assert result.trace is not None
    assert result.trace.claims[0].reasoning_summary == (
        "The messages precede the documented transfer."
    )


def test_analytical_inference_without_authoritative_support_is_rejected() -> None:
    inference = {
        "claim_id": "A-01",
        "claim_type": "analytical_inference",
        "text": "The available evidence suggests a connection.",
        "epistemic_status": "suspected",
        "supporting_source_message_ids": [],
        "contradicting_source_message_ids": [],
        "reasoning_summary": "The inference relies on an unsupported premise.",
    }
    with pytest.raises(CaseAnalysisFailure) as raised:
        parse(provider_payload([inference]))
    assert raised.value.code == "analysis_trace_v3_inference_unbound"


def test_missing_information_remains_not_established() -> None:
    unknown = {
        "claim_id": "A-01",
        "claim_type": "unknown",
        "text": "The identity of the person shown in the footage is not established.",
        "epistemic_status": "not_established",
        "supporting_source_message_ids": [],
        "contradicting_source_message_ids": [],
        "reasoning_summary": None,
    }
    result = parse(provider_payload([unknown]), sources=set())
    assert result.trace is not None
    assert result.trace.claims[0].epistemic_status == "not_established"
    assert "suspect appears" not in result.trace.claims[0].text.lower()


@pytest.mark.parametrize("invalid_source", ["assistant-message", "retrieval-context-1"])
def test_non_authoritative_sources_are_rejected(invalid_source: str) -> None:
    payload = provider_payload(
        [reported_claim("A generated source asserted an event.", supporting=[invalid_source])]
    )
    with pytest.raises(CaseAnalysisFailure) as raised:
        parse(
            payload,
            sources={"S1"},
            context={"retrieval_context_id": "retrieval-context-1"},
        )
    assert raised.value.code == "analysis_trace_v3_support_outside_evidence"


def test_cyber_case_accepts_bound_optional_mitre_context() -> None:
    association = {
        "association_id": "MA-01",
        "technique_id": "T1059.001",
        "claim_ids": ["A-01"],
        "reason": "PowerShell is relevant external technical context.",
        "status": "candidate_only",
        "support_role": "external_technical_context",
    }
    result = parse(
        provider_payload(
            [reported_claim("The administrator reported PowerShell activity.")],
            associations=[association],
        ),
        context={
            "retrieval_context_id": "ctx-cyber",
            "mitre_table": [{"technique_id": "T1059.001"}],
        },
    )
    assert result.trace is not None
    assert result.trace.retrieval_context_id == "ctx-cyber"
    assert result.trace.mitre_associations[0].status == "candidate_only"


@pytest.mark.parametrize(
    ("context", "expected_code"),
    [
        (
            {"mitre_table": [{"technique_id": "T1059.001"}]},
            "analysis_trace_v3_mitre_without_retrieval",
        ),
        (
            {
                "retrieval_context_id": "ctx-cyber",
                "mitre_table": [{"technique_id": "T1190"}],
            },
            "analysis_trace_v3_mitre_outside_context",
        ),
    ],
)
def test_mitre_association_requires_bound_admitted_context(
    context: dict[str, object],
    expected_code: str,
) -> None:
    association = {
        "association_id": "MA-01",
        "technique_id": "T1059.001",
        "claim_ids": ["A-01"],
        "reason": "Optional technical context.",
        "status": "candidate_only",
        "support_role": "external_technical_context",
    }
    payload = provider_payload(
        [reported_claim("The administrator reported PowerShell activity.")],
        associations=[association],
    )
    with pytest.raises(CaseAnalysisFailure) as raised:
        parse(payload, context=context)
    assert raised.value.code == expected_code


def test_question_answer_mode_returns_direct_answer_with_v3_trace() -> None:
    result = parse(
        provider_payload(
            [reported_claim("The complainant reported a missing bicycle.")],
            answer="The reported missing property was a bicycle.",
        ),
        mode="question_answer",
    )
    assert result.answer == "The reported missing property was a bicycle."
    assert result.trace is not None
    assert result.trace.analysis_mode == "question_answer"


def test_invalid_provider_structure_uses_safe_trace_failure() -> None:
    payload = provider_payload([reported_claim("A source reported a loss.")])
    payload.pop("summary")
    result = parse(payload)
    assert result.answer == "Grounded case answer."
    assert result.trace is None
    assert result.trace_failure is not None
    assert result.trace_failure.version == "analysis_trace_v3"
    assert result.trace_failure.failure_code == "analysis_trace_structure_invalid"


def test_service_requests_v3_schema_with_optional_external_context(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class Client:
        async def post(self, url, *, headers, json):
            captured.update(json)
            return response_for(
                provider_payload([reported_claim("The owner reported a missing bicycle.")])
            )

    monkeypatch.setattr(
        "app.services.case_analysis.case_analysis_executor.resolve_core_llm_target",
        lambda model: SimpleNamespace(
            model=model,
            provider="anthropic",
            messages_url="https://example.test/messages",
            headers={},
        ),
    )
    result = asyncio.run(
        MainCaseAnalysisService(client=Client()).analyze(
            mode="case_overview",
            raw_evidence="[INITIAL CASE NARRATIVE]\nA bicycle was reported missing.",
            analysis_context={"source_message_ids": ["S1"]},
            question=None,
            user_message="Please analyze this case.",
        )
    )
    schema = captured["output_config"]["format"]["schema"]
    assert schema["properties"]["version"]["const"] == "analysis_trace_v3"
    assert result.trace is not None
    assert result.trace.retrieval_context_id is None
