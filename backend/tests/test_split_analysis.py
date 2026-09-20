"""The split arm: one call reads the case, a second one judges what was read.

The single call asks for seven structures at once, five of which cross-reference
claim ids it is inventing as it writes. These tests hold the seam in place: the
reading call never sees ATT&CK, the judgement call never sees a claim it did not
receive, and an arm that costs two calls does not come back looking like one.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisGap,
    CaseAnalysisOutput,
    CaseMitreAssociation,
    CaseProviderJudgement,
    CaseProviderReading,
    CaseSourceCitation,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    merged_receipt,
)
from app.services.analysis.steps.bind import resolve_case_trace
from app.services.sources import CaseSourceBundle, CaseSourceItem
from experiments import analysis_arms
from experiments.analysis_arms import judge_reading, split
from experiments.split_analysis import (
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


def split_stages(*, seen: list[dict], reading: CaseProviderReading, technical_context=None):
    """The two stages with their model calls replaced by recorders."""

    async def fake_reading(**kwargs):
        seen.append({"stage": "reading", **kwargs})
        return CaseReadingOutput(
            reading=reading,
            execution_receipt={"calls": [{"stage": "case_reading"}]},
        )

    async def fake_judgement(**kwargs):
        seen.append({"stage": "judgement", **kwargs})
        trace = split_trace(
            kwargs["reading"],
            judgement(),
            mode=kwargs["mode"],
            retrieval_context_id=kwargs["retrieval_context_id"] if technical_context else None,
        )
        return CaseAnalysisOutput(
            answer=trace.summary,
            trace=trace,
            execution_receipt={"calls": [{"stage": "case_judgement"}]},
        )

    return {"reading_request": fake_reading, "judgement_request": fake_judgement}


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

    # The split still binds its trace to the case, exactly as the shipped arm does.
    assert called == ["retrieve_technical_context", "read_sources", "judge_reading", "bind_to_case"]


def test_the_reading_call_is_never_shown_the_technical_context():
    """A claim that named a technique because retrieval mentioned it would be
    grounded in the retrieval rather than in the case."""

    bundle = case_with_one_narrative()
    seen: list[dict] = []
    context = {"context": "T1486 encrypts data.", "mitre_table": [{"technique_id": "T1486"}]}

    asyncio.run(
        split(
            AnalysisInput(sources=bundle),
            **split_stages(seen=seen, reading=reading_of(bundle), technical_context=context),
        )
    )

    reading_call = next(call for call in seen if call["stage"] == "reading")
    judgement_call = next(call for call in seen if call["stage"] == "judgement")

    assert "technical_context" not in reading_call
    assert "retrieval_context_id" not in reading_call
    assert "technical_context" in judgement_call


def test_the_judgement_call_receives_the_claims_the_reading_wrote():
    bundle = case_with_one_narrative()
    seen: list[dict] = []
    reading = reading_of(bundle)

    asyncio.run(split(AnalysisInput(sources=bundle), **split_stages(seen=seen, reading=reading)))

    judgement_call = next(call for call in seen if call["stage"] == "judgement")
    assert judgement_call["reading"] is reading
    assert [claim.claim_id for claim in judgement_call["reading"].claims] == ["A-01"]


def test_an_arm_that_costs_two_calls_does_not_come_back_looking_like_one():
    bundle = case_with_one_narrative()
    artifacts = asyncio.run(
        split(AnalysisInput(sources=bundle), **split_stages(seen=[], reading=reading_of(bundle)))
    )
    assert [call["stage"] for call in artifacts.receipt["calls"]] == [
        "case_reading",
        "case_judgement",
    ]


def test_merging_receipts_keeps_every_call_and_the_last_of_everything_else():
    merged = merged_receipt(
        {"calls": [{"stage": "case_reading"}], "source_reference_type": "case_source"},
        {"calls": [{"stage": "case_judgement"}], "failure_code": "none"},
    )
    assert [call["stage"] for call in merged["calls"]] == ["case_reading", "case_judgement"]
    assert merged["source_reference_type"] == "case_source"
    assert merged["failure_code"] == "none"


def test_judging_needs_something_to_judge():
    bundle = case_with_one_narrative()

    async def unreachable(**_kwargs):
        raise AssertionError("the judgement call must not run without a reading")

    with pytest.raises(CaseAnalysisFailure) as failure:
        asyncio.run(
            judge_reading(AnalysisInput(sources=bundle), AnalysisArtifacts(), request=unreachable)
        )
    assert failure.value.code == "analysis_reading_missing"


def test_the_trace_takes_its_claims_from_the_reading_and_its_summary_from_the_judgement():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    trace = split_trace(
        reading,
        judgement(summary="Overnight encryption of a file share."),
        mode="case_overview",
    )

    assert [claim.claim_id for claim in trace.claims] == ["A-01"]
    assert trace.summary == "Overnight encryption of a file share."
    assert trace.involved_parties == reading.involved_parties
    # Nothing is bound yet: that is still the verify stage's job.
    assert trace.grounding is None


def test_a_split_trace_is_bound_to_the_case_the_same_way_a_direct_one_is():
    """A claim id the judgement invented is trimmed, and the loss is counted."""

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
        mode="case_overview",
    )

    bound = resolve_case_trace(trace, bundle, mitre_table=[{"technique_id": "T1486"}])

    assert bound.gaps[0].affected_claim_ids == ["A-01"]
    # No retrieval bound to this trace, so the association is dropped and counted.
    assert bound.mitre_associations == []
    assert bound.grounding.associations_outside_context == 1
    assert bound.grounding.citations_verified == 1


def test_the_judgement_is_shown_which_sentence_carries_each_claim():
    bundle = case_with_one_narrative()
    payload = reading_payload(reading_of(bundle))

    assert set(payload) == {"claims", "involved_parties", "timeline", "impacts"}
    assert payload["claims"][0]["supporting_citations"][0]["exact_quote"] == SOURCE_TEXT
