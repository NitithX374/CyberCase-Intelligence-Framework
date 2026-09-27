from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from case_mitre_test_support import _fixtures, _gate, _response

from app.errors import CaseAnalysisFailure
from app.services.analysis.pipeline import AnalysisInput
from app.services.analysis.steps.technical_context import CaseMitreAugmentation
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseAnalysisGap, CaseSourceCitation
from app.trace.trace import CaseMitreAssociation
from experiments import analysis_arms
from experiments.analysis_arms import ArmArtifacts, judge_reading, split
from experiments.split_analysis import (
    CaseJudgementOutput,
    CaseProviderJudgement,
    CaseProviderReading,
    CaseReadingOutput,
    reading_payload,
    split_trace,
)

SOURCE_TEXT = "The finance share was encrypted overnight."


def case_with_one_narrative() -> CaseSourceBundle:
    return CaseSourceBundle(
        revision=3,
        sources=(
            CaseSourceItem(source_id=str(uuid4()), source_kind="narrative", text=SOURCE_TEXT),
        ),
    )


def reading_of(bundle: CaseSourceBundle) -> CaseProviderReading:
    source_id = bundle.sources[0].source_id
    return CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="The finance share was encrypted.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    CaseSourceCitation(source_id=source_id, exact_quote=SOURCE_TEXT)
                ],
            )
        ],
        involved_parties=[],
        timeline=[],
        impacts=[],
    )


def judgement(**overrides) -> CaseProviderJudgement:
    return CaseProviderJudgement(
        version="case_analysis_trace_v1",
        summary=overrides.pop("summary", "A file share was encrypted overnight."),
        gaps=overrides.pop("gaps", []),
        mitre_associations=overrides.pop("mitre_associations", []),
    )


def split_stages(*, seen: list[dict], reading: CaseProviderReading):
    async def fake_reading(**kwargs):
        seen.append({"stage": "reading", **kwargs})
        return CaseReadingOutput(reading=reading, calls=({"stage": "case_reading"},))

    async def fake_judgement(**kwargs):
        seen.append({"stage": "judgement", **kwargs})
        context = kwargs["technical_context"]
        trace = split_trace(
            kwargs["reading"],
            judgement(),
            retrieval_context_id=context.retrieval_context_id if context else None,
        )
        return CaseJudgementOutput(trace=trace, calls=({"stage": "case_judgement"},))

    return {"reading_request": fake_reading, "judgement_request": fake_judgement}


def skip_the_gate(monkeypatch):
    original = analysis_arms.retrieve_technical_context

    async def skipped(data, so_far):
        return await original(
            data,
            so_far,
            gate=_gate({"decision": "SKIP", "source_message_ids": [], "trigger_text": []}),
            rag=_response,
        )

    monkeypatch.setattr(analysis_arms, "retrieve_technical_context", skipped)


def test_the_split_arm_is_two_calls_where_the_direct_arm_is_one(monkeypatch):
    called: list[str] = []

    def record(name):
        async def step(data, so_far, **_kwargs):
            called.append(name)
            return so_far

        return step

    for name in ("retrieve_technical_context", "read_sources", "judge_reading", "bind_to_case"):
        monkeypatch.setattr(analysis_arms, name, record(name))
    asyncio.run(split(AnalysisInput(sources=case_with_one_narrative())))

    assert called == ["retrieve_technical_context", "read_sources", "judge_reading", "bind_to_case"]


def test_the_reading_call_is_never_shown_the_technical_context(monkeypatch):
    bundle = case_with_one_narrative()
    _, _, _, applicability, context = _fixtures()
    seen: list[dict] = []

    async def retrieved(data, so_far, **_kwargs):
        augmentation = CaseMitreAugmentation("retrieved_from_rag", applicability, context)
        return ArmArtifacts(augmentation=augmentation)

    monkeypatch.setattr(analysis_arms, "retrieve_technical_context", retrieved)
    artifacts = asyncio.run(
        split(
            AnalysisInput(sources=bundle),
            **split_stages(seen=seen, reading=reading_of(bundle)),
        )
    )

    reading_call = next(call for call in seen if call["stage"] == "reading")
    judgement_call = next(call for call in seen if call["stage"] == "judgement")

    assert "technical_context" not in reading_call
    assert judgement_call["technical_context"] == context
    assert artifacts.trace.retrieval_context_id == context.retrieval_context_id


def test_the_judgement_call_receives_the_claims_the_reading_wrote(monkeypatch):
    bundle = case_with_one_narrative()
    seen: list[dict] = []
    reading = reading_of(bundle)

    skip_the_gate(monkeypatch)
    asyncio.run(split(AnalysisInput(sources=bundle), **split_stages(seen=seen, reading=reading)))

    judgement_call = next(call for call in seen if call["stage"] == "judgement")
    assert judgement_call["reading"] is reading
    assert [claim.claim_id for claim in judgement_call["reading"].claims] == ["A-01"]


def test_an_arm_that_costs_two_calls_does_not_come_back_looking_like_one(monkeypatch):
    bundle = case_with_one_narrative()
    skip_the_gate(monkeypatch)
    artifacts = asyncio.run(
        split(AnalysisInput(sources=bundle), **split_stages(seen=[], reading=reading_of(bundle)))
    )
    assert [call["stage"] for call in artifacts.calls] == ["case_reading", "case_judgement"]
    assert artifacts.trace.grounding is not None, "the split trace is bound like a direct one"


def test_judging_needs_something_to_judge():
    bundle = case_with_one_narrative()

    async def unreachable(**_kwargs):
        raise AssertionError("the judgement call must not run without a reading")

    with pytest.raises(CaseAnalysisFailure) as failure:
        asyncio.run(
            judge_reading(AnalysisInput(sources=bundle), ArmArtifacts(), request=unreachable)
        )
    assert failure.value.code == "analysis_reading_missing"


def test_the_trace_takes_its_claims_from_the_reading_and_its_summary_from_the_judgement():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    trace = split_trace(reading, judgement(summary="Overnight encryption of a file share."))

    assert [claim.claim_id for claim in trace.claims] == ["A-01"]
    assert trace.summary == "Overnight encryption of a file share."
    assert trace.involved_parties == reading.involved_parties
    assert trace.grounding is None


def test_a_split_trace_is_bound_to_the_case_the_same_way_a_direct_one_is():
    bundle = case_with_one_narrative()
    trace = split_trace(
        reading_of(bundle),
        judgement(
            gaps=[
                CaseAnalysisGap(
                    gap_id="G-01",
                    gap_key="who_paid",
                    topic="Payment",
                    status="NOT_PROVIDED",
                    description="No payment record was supplied.",
                    affected_claim_ids=["A-01", "A-77"],
                    reason="The loss cannot be sized without it.",
                    priority="high",
                    askable=True,
                    clarification_question="Was any ransom paid?",
                )
            ],
            mitre_associations=[
                CaseMitreAssociation(
                    association_id="MA-01",
                    technique_id="T1486",
                    claim_ids=["A-01"],
                    reason="The share was encrypted.",
                    status="candidate_only",
                    support_role="external_technical_context",
                )
            ],
        ),
    )

    bound = resolve_case_trace(trace, bundle, mitre_table=[{"technique_id": "T1486"}])

    assert bound.gaps[0].affected_claim_ids == ["A-01"]
    assert bound.mitre_associations == []
    assert bound.grounding.associations_outside_context == 1
    assert bound.grounding.citations_verified == 1


def test_the_judgement_is_shown_which_sentence_carries_each_claim():
    bundle = case_with_one_narrative()
    payload = reading_payload(reading_of(bundle))

    assert set(payload) == {"claims", "involved_parties", "timeline", "impacts"}
    assert payload["claims"][0]["supporting_citations"][0]["exact_quote"] == SOURCE_TEXT
