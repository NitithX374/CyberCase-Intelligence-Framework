from __future__ import annotations

import json

import pytest
from fake_nli import FakeNli

from app.analysis import write
from app.analysis.claim_gate import check_judgement_references
from app.analysis.views import DerivedCaseViews
from app.errors import CaseAnalysisFailure
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace import claim_validation
from app.trace.claims import CaseAnalysisClaim, CaseFollowupExchange
from app.trace.nli_model import Judgement, NliUnavailable
from app.trace.trace import (
    CaseProviderJudgement,
    CaseProviderReading,
    CaseProviderReadingReply,
    CaseViewExtraction,
)


def fixtures():
    bundle = CaseSourceBundle(
        revision=3,
        sources=(
            CaseSourceItem(
                "S1", "document", "John sent an email.", document_id="D1", filename="email.pdf"
            ),
            CaseSourceItem(
                "S2",
                "document",
                "Alice lost 25,000 baht.",
                document_id="D2",
                filename="transfer.pdf",
            ),
        ),
    )
    claims = [
        {
            "claim_id": claim_id,
            "claim_type": "reported",
            "text": text,
            "epistemic_status": "reported",
            "supporting_citations": [
                {
                    "source_id": source.source_id,
                    "evidence_unit_ids": [evidence_units(source)[0].unit_id],
                }
            ],
        }
        for claim_id, text, source in (
            ("A-01", "John sent an email.", bundle.sources[0]),
            ("A-02", "John is the attacker.", bundle.sources[0]),
            ("A-03", "Alice lost 25,000 baht.", bundle.sources[1]),
        )
    ]
    return bundle, claims


def scorer_for_claims():
    return FakeNli(
        judge=lambda premise, hypothesis: Judgement(
            "neutral" if "attacker" in hypothesis else "entailment",
            0.1 if "attacker" in hypothesis else 0.99,
        )
    )


async def run_pipeline(
    monkeypatch, *, scorer=None, claims=None, history=(), summary="John sent an email [A-01]."
):
    bundle, initial = fixtures()
    calls = []
    view_inputs = []
    if scorer is not None:
        monkeypatch.setattr(claim_validation, "load_scorer", lambda: scorer)

    async def request(**kwargs):
        calls.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return CaseProviderReadingReply.model_validate(
                {
                    "version": "case_analysis_trace_v1",
                    "claims": initial if claims is None else claims,
                }
            )
        assert kwargs["stage"] == "case_judgement"
        return CaseProviderJudgement(version="case_analysis_trace_v1", summary=summary)

    async def views(accepted, *, config):
        view_inputs.extend(accepted)
        return DerivedCaseViews(
            [],
            [],
            [],
            CaseViewExtraction(
                method="llm",
                model="test",
                duration_ms=0,
                input_claim_ids=[claim.claim_id for claim in accepted],
                excluded_claim_ids=[],
            ),
        )

    monkeypatch.setattr(write, "request_stage", request)
    monkeypatch.setattr(write, "derive_claim_views", views)
    trace = await write.write_trace(
        sources=bundle,
        language="english",
        followup_history=history,
        config=AnalysisPipelineConfig(),
    )
    return trace, calls, view_inputs


@pytest.mark.asyncio
async def test_semantically_unsupported_claim_is_preserved_for_review_but_never_sent_downstream(
    monkeypatch,
):
    scorer = scorer_for_claims()
    trace, calls, views = await run_pipeline(monkeypatch, scorer=scorer)

    assert [call["stage"] for call in calls] == ["case_reading", "case_judgement"]
    assert [claim["claim_id"] for claim in calls[1]["content"]["reading"]["claims"]] == [
        "A-01",
        "A-03",
    ]
    assert [claim.claim_id for claim in views] == ["A-01", "A-03"]
    assert [claim.claim_id for claim in trace.claims] == ["A-01", "A-02", "A-03"]
    assert trace.claims[1].supporting_citations[0].exact_quote == "John sent an email."
    assert trace.claims[1].semantic_grounding.verdict == "not_supported"
    assert "attacker" not in json.dumps(calls[1]["content"])
    assert "semantic_grounding" not in json.dumps(calls[1]["content"])
    assert trace.grounding.claims_admitted_to_judgement == 2
    assert trace.grounding.claims_withheld_from_judgement == 1
    assert trace.grounding.claim_verifier_calls == 3
    assert trace.grounding.evidence_ids_resolved == 3


@pytest.mark.asyncio
async def test_unresolved_id_is_withheld_even_if_another_claim_has_resolved_evidence(monkeypatch):
    _, claims = fixtures()
    claims[1]["supporting_citations"][0]["evidence_unit_ids"] = ["S1:U001-stale"]
    trace, calls, _ = await run_pipeline(monkeypatch, scorer=scorer_for_claims(), claims=claims)

    assert trace.claims[1].semantic_grounding.verdict == "unassessed"
    assert trace.claims[1].semantic_grounding.reason == "no_resolved_source"
    assert [claim["claim_id"] for claim in calls[-1]["content"]["reading"]["claims"]] == [
        "A-01",
        "A-03",
    ]


@pytest.mark.asyncio
async def test_rejected_fact_cannot_leak_through_raw_followup_answer_or_question(monkeypatch):
    history = (
        CaseFollowupExchange("QA-01", "who", "Is John the attacker?", "John is the attacker."),
    )
    _, calls, _ = await run_pipeline(monkeypatch, scorer=scorer_for_claims(), history=history)

    assert calls[0]["content"]["followup_history"][0]["answer"] == history[0].answer
    assert calls[1]["content"]["followup_history"] == [
        {"qa_id": "QA-01", "gap_key": "who", "answered": True}
    ]
    assert "attacker" not in json.dumps(calls[1]["content"])


@pytest.mark.asyncio
async def test_followup_answer_still_supports_a_claim_through_the_same_source_unit_gate(
    monkeypatch,
):
    history = (
        CaseFollowupExchange(
            "QA-03", "when", "When did it arrive?", "The email arrived on Monday."
        ),
    )
    qa = CaseSourceItem("QA-03", "followup_answer", history[0].answer)
    _, claims = fixtures()
    claims.append(
        {
            "claim_id": "A-04",
            "claim_type": "reported",
            "text": history[0].answer,
            "epistemic_status": "reported",
            "supporting_citations": [
                {"source_id": "QA-03", "evidence_unit_ids": [evidence_units(qa)[0].unit_id]}
            ],
        }
    )
    trace, calls, _ = await run_pipeline(
        monkeypatch, scorer=scorer_for_claims(), claims=claims, history=history
    )

    approved = calls[1]["content"]["reading"]["claims"]
    assert [claim["claim_id"] for claim in approved] == ["A-01", "A-03", "A-04"]
    assert approved[-1]["supporting_citations"] == [{"exact_quote": history[0].answer}]
    citation = trace.claims[-1].supporting_citations[0]
    assert citation.source_id == "QA-03"
    assert citation.evidence_unit_ids == [evidence_units(qa)[0].unit_id]
    assert trace.claims[-1].semantic_grounding.verdict == "supported"


@pytest.mark.asyncio
async def test_no_admitted_claims_abstains_without_calling_judgement_or_views(monkeypatch):
    trace, calls, views = await run_pipeline(monkeypatch, scorer=FakeNli())

    assert [call["stage"] for call in calls] == ["case_reading"]
    assert views == []
    assert "no case summary was generated" in trace.summary
    assert len(trace.claims) == 3
    assert trace.grounding.claims_admitted_to_judgement == 0
    assert trace.grounding.claims_withheld_from_judgement == 3
    assert (
        trace.involved_parties == trace.timeline == trace.impacts == trace.mitre_associations == []
    )


@pytest.mark.asyncio
async def test_model_unavailability_stops_analysis_instead_of_using_unchecked_claims(monkeypatch):
    def unavailable():
        raise NliUnavailable("weights_missing")

    monkeypatch.setattr(claim_validation, "load_scorer", unavailable)
    with pytest.raises(CaseAnalysisFailure) as raised:
        await run_pipeline(monkeypatch)
    assert raised.value.code == "case_claim_verifier_unavailable"
    assert raised.value.status_code == 503


@pytest.mark.asyncio
async def test_verifier_exception_stops_analysis_without_a_successful_fallback(monkeypatch):
    def fail(premise, hypothesis):
        raise RuntimeError("inference failed")

    with pytest.raises(RuntimeError, match="inference failed"):
        await run_pipeline(monkeypatch, scorer=FakeNli(judge=fail))


@pytest.mark.asyncio
async def test_judgement_cannot_reintroduce_a_withheld_claim_id_in_its_summary(monkeypatch):
    with pytest.raises(CaseAnalysisFailure) as raised:
        await run_pipeline(
            monkeypatch, scorer=scorer_for_claims(), summary="John is the attacker [A-02]."
        )
    assert raised.value.code == "case_judgement_invalid_claim"


@pytest.mark.asyncio
async def test_long_input_is_scored_with_research_truncation_and_negative_verdict_withheld(
    monkeypatch,
):
    scorer = FakeNli(fits=lambda premise, hypothesis: False)
    trace, calls, _ = await run_pipeline(monkeypatch, scorer=scorer)
    assert all(claim.semantic_grounding.reason == "lr_not_supported" for claim in trace.claims)
    assert all(claim.semantic_grounding.truncated for claim in trace.claims)
    assert [call["stage"] for call in calls] == ["case_reading"]


@pytest.mark.parametrize(
    "fields",
    [
        {
            "gaps": [
                {
                    "gap_id": "G-01",
                    "gap_key": "who",
                    "topic": "Actor identity",
                    "status": "AMBIGUOUS",
                    "description": "Review the actor role.",
                    "affected_claim_ids": ["A-02"],
                    "reason": "Role is unclear.",
                    "priority": "high",
                    "askable": False,
                }
            ]
        },
        {
            "mitre_associations": [
                {
                    "association_id": "MA-01",
                    "technique_id": "T1566",
                    "claim_ids": ["A-02"],
                    "reason": "An email was sent.",
                    "status": "candidate_only",
                    "support_role": "external_technical_context",
                }
            ]
        },
    ],
)
def test_withheld_claim_ids_cannot_return_through_gaps_or_technical_associations(fields):
    admitted = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="John sent an email.",
                epistemic_status="reported",
            )
        ],
    )
    judgement = CaseProviderJudgement(
        version="case_analysis_trace_v1", summary="John sent an email [A-01].", **fields
    )
    with pytest.raises(CaseAnalysisFailure) as raised:
        check_judgement_references(judgement, admitted)
    assert raised.value.code == "case_judgement_invalid_claim"
