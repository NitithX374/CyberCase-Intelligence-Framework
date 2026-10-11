from __future__ import annotations

import asyncio
import json
import threading

import pytest
from fake_nli import FakeNli

from app.analysis import write
from app.analysis.claim_gate import check_judgement_references, checked_claim_support
from app.analysis.views import DerivedCaseViews
from app.errors import CaseAnalysisFailure
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace import claim_validation
from app.trace.claims import CaseAnalysisClaim, CaseFollowupExchange, CaseSourceCitation
from app.trace.nli_model import Judgement, NliUnavailable
from app.trace.trace import (
    CaseGroundingReport,
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


def with_stale_unit(claims, index):
    claims[index]["supporting_citations"][0]["evidence_unit_ids"] = ["S1:U001-stale"]
    return claims


async def run_pipeline(
    monkeypatch,
    *,
    scorer=None,
    claims=None,
    history=(),
    summary="John sent an email [A-01].",
    on_judgement=None,
    language="english",
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
        if on_judgement is not None:
            await on_judgement()
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
        language=language,
        followup_history=history,
        config=AnalysisPipelineConfig(),
    )
    return trace, calls, view_inputs


@pytest.mark.asyncio
async def test_a_claim_the_check_does_not_support_still_reaches_judgement_and_views_unlabelled(
    monkeypatch,
):
    scorer = scorer_for_claims()
    trace, calls, views = await run_pipeline(monkeypatch, scorer=scorer)

    assert [call["stage"] for call in calls] == ["case_reading", "case_judgement"]
    assert [claim["claim_id"] for claim in calls[1]["content"]["reading"]["claims"]] == [
        "A-01",
        "A-02",
        "A-03",
    ]
    assert [claim.claim_id for claim in views] == ["A-01", "A-02", "A-03"]
    assert all(claim.semantic_grounding is None for claim in views)
    sent = json.dumps(calls[1]["content"])
    for label in ("semantic_grounding", "not_supported", "lr_not_supported", "verdict"):
        assert label not in sent
    assert "attacker" in sent
    assert "not_supported" not in calls[1]["system"]
    assert [claim.claim_id for claim in trace.claims] == ["A-01", "A-02", "A-03"]
    assert trace.claims[1].supporting_citations[0].exact_quote == "John sent an email."
    assert trace.claims[1].semantic_grounding.verdict == "not_supported"
    assert trace.claims[0].semantic_grounding.verdict == "supported"
    assert trace.grounding.claims_admitted_to_judgement == 3
    assert trace.grounding.claims_withheld_from_judgement == 0
    assert trace.grounding.claims_semantically_not_supported == 1
    assert trace.grounding.claim_verifier_calls == 3
    assert trace.grounding.evidence_ids_resolved == 3
    assert trace.view_extraction.excluded_claim_ids == []


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
    assert trace.grounding.claims_withheld_from_judgement == 1
    assert trace.view_extraction.excluded_claim_ids == ["A-02"]


@pytest.mark.asyncio
async def test_raw_followup_answer_and_question_never_reach_the_judgement(monkeypatch):
    history = (
        CaseFollowupExchange("QA-01", "when", "When did it arrive?", "It arrived on Monday."),
    )
    _, calls, _ = await run_pipeline(monkeypatch, scorer=scorer_for_claims(), history=history)

    assert calls[0]["content"]["followup_history"][0]["answer"] == history[0].answer
    assert calls[1]["content"]["followup_history"] == [
        {"qa_id": "QA-01", "gap_key": "when", "answered": True}
    ]
    assert history[0].answer not in json.dumps(calls[1]["content"])
    assert history[0].question not in json.dumps(calls[1]["content"])


@pytest.mark.asyncio
async def test_followup_answer_still_supports_a_claim_through_the_same_source_unit_check(
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

    sent = calls[1]["content"]["reading"]["claims"]
    assert [claim["claim_id"] for claim in sent] == ["A-01", "A-02", "A-03", "A-04"]
    assert sent[-1]["supporting_citations"] == [{"exact_quote": history[0].answer}]
    citation = trace.claims[-1].supporting_citations[0]
    assert citation.source_id == "QA-03"
    assert citation.evidence_unit_ids == [evidence_units(qa)[0].unit_id]
    assert trace.claims[-1].semantic_grounding.verdict == "supported"


@pytest.mark.asyncio
async def test_no_claim_with_resolved_support_abstains_without_calling_judgement_or_views(
    monkeypatch,
):
    _, claims = fixtures()
    for claim in claims:
        claim["supporting_citations"][0]["evidence_unit_ids"] = ["S1:U001-stale"]
    trace, calls, views = await run_pipeline(monkeypatch, scorer=FakeNli(), claims=claims)

    assert [call["stage"] for call in calls] == ["case_reading"]
    assert views == []
    assert "no case summary was generated" in trace.summary
    assert len(trace.claims) == 3
    assert all(claim.semantic_grounding.verdict == "unassessed" for claim in trace.claims)
    assert trace.grounding.claims_admitted_to_judgement == 0
    assert trace.grounding.claims_withheld_from_judgement == 3
    assert trace.grounding.claim_verifier_calls == 0
    assert (
        trace.involved_parties == trace.timeline == trace.impacts == trace.mitre_associations == []
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("language", "words"), [("english", "no case summary"), ("thai", "บทสรุปคดี")]
)
async def test_claims_withheld_by_the_citation_checks_abstain_in_the_readers_language(
    monkeypatch, language, words
):
    _, claims = fixtures()
    for claim in claims:
        claim["epistemic_status"] = "suspected"
    trace, calls, _ = await run_pipeline(
        monkeypatch, scorer=FakeNli(), claims=claims, language=language
    )

    assert [call["stage"] for call in calls] == ["case_reading"]
    assert words in trace.summary
    assert "Source passage" not in trace.summary
    assert all(claim.semantic_grounding.reason == "claim_uncertain" for claim in trace.claims)


@pytest.mark.asyncio
async def test_claims_the_check_does_not_support_are_labels_not_an_abstention(monkeypatch):
    trace, calls, views = await run_pipeline(monkeypatch, scorer=FakeNli())

    assert [call["stage"] for call in calls] == ["case_reading", "case_judgement"]
    assert [claim.claim_id for claim in views] == ["A-01", "A-02", "A-03"]
    assert trace.summary == "John sent an email [A-01]."
    assert all(claim.semantic_grounding.verdict == "not_supported" for claim in trace.claims)
    assert trace.grounding.claims_admitted_to_judgement == 3
    assert trace.grounding.claims_withheld_from_judgement == 0


@pytest.mark.asyncio
async def test_an_unavailable_verifier_leaves_claims_unassessed_and_the_analysis_completes(
    monkeypatch, caplog
):
    def unavailable():
        raise NliUnavailable("weights_missing")

    monkeypatch.setattr(claim_validation, "load_scorer", unavailable)
    _, claims = fixtures()
    with_stale_unit(claims, 1)
    with caplog.at_level("ERROR", logger="app.case_analysis"):
        trace, calls, views = await run_pipeline(monkeypatch, claims=claims)

    assert [call["stage"] for call in calls] == ["case_reading", "case_judgement"]
    assert [claim.claim_id for claim in views] == ["A-01", "A-03"]
    assert [claim.semantic_grounding.verdict for claim in trace.claims] == [
        "unassessed",
        "unassessed",
        "unassessed",
    ]
    assert [claim.semantic_grounding.reason for claim in trace.claims] == [
        "verifier_unavailable",
        "no_resolved_source",
        "verifier_unavailable",
    ]
    assert trace.grounding.claims_admitted_to_judgement == 2
    assert trace.grounding.claims_withheld_from_judgement == 1
    assert trace.grounding.claim_verifier_calls == 0
    assert trace.summary == "John sent an email [A-01]."
    assert "weights_missing" in caplog.text


@pytest.mark.asyncio
async def test_verifier_exception_stops_analysis_without_a_successful_fallback(monkeypatch):
    def fail(premise, hypothesis):
        raise RuntimeError("inference failed")

    with pytest.raises(RuntimeError, match="inference failed"):
        await run_pipeline(monkeypatch, scorer=FakeNli(judge=fail))


@pytest.mark.asyncio
async def test_the_checks_and_the_judgement_wait_for_each_other_so_they_run_together(
    monkeypatch,
):
    requested = threading.Event()
    started = threading.Event()

    def judge(premise, hypothesis):
        started.set()
        assert requested.wait(5), "the checks finished before the judgement was requested"
        return Judgement("entailment", 0.99)

    async def on_judgement():
        requested.set()
        assert await asyncio.to_thread(started.wait, 5), "the judgement ran before the checks"

    trace, calls, _ = await run_pipeline(
        monkeypatch, scorer=FakeNli(judge=judge), on_judgement=on_judgement
    )

    assert [call["stage"] for call in calls] == ["case_reading", "case_judgement"]
    assert all(claim.semantic_grounding.verdict == "supported" for claim in trace.claims)


@pytest.mark.asyncio
async def test_cancelling_the_checks_stops_the_scoring_of_the_remaining_claims(monkeypatch):
    first = threading.Event()
    release = threading.Event()

    def judge(premise, hypothesis):
        first.set()
        release.wait(5)
        return Judgement("entailment", 0.99)

    scorer = FakeNli(judge=judge)
    monkeypatch.setattr(claim_validation, "load_scorer", lambda: scorer)
    claims = [
        CaseAnalysisClaim(
            claim_id=f"A-0{number}",
            claim_type="reported",
            text="John sent an email.",
            epistemic_status="reported",
            supporting_citations=[
                CaseSourceCitation(
                    source_id="S1",
                    exact_quote="John sent an email.",
                    pointer_state="direct",
                    start=0,
                    end=19,
                    evidence_unit_ids=["S1:U001-fixture"],
                )
            ],
        )
        for number in (1, 2, 3)
    ]
    reading = CaseProviderReading(version="case_analysis_trace_v1", claims=claims)
    task = asyncio.create_task(checked_claim_support(reading, CaseGroundingReport()))

    try:
        assert await asyncio.to_thread(first.wait, 5)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    finally:
        release.set()
    await asyncio.sleep(0.3)

    assert task.cancelled()
    assert len(scorer.judged) == 1


@pytest.mark.asyncio
async def test_a_failed_judgement_cancels_the_checks_running_beside_it(monkeypatch):
    release = threading.Event()

    def judge(premise, hypothesis):
        release.wait(5)
        return Judgement("entailment", 0.99)

    async def on_judgement():
        raise CaseAnalysisFailure("case_judgement_failed", "The judgement failed", 502)

    try:
        with pytest.raises(CaseAnalysisFailure) as raised:
            await run_pipeline(monkeypatch, scorer=FakeNli(judge=judge), on_judgement=on_judgement)
        assert raised.value.code == "case_judgement_failed"
        pending = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        assert pending == []
    finally:
        release.set()


@pytest.mark.asyncio
async def test_judgement_cannot_cite_a_claim_that_was_withheld_before_it(monkeypatch):
    _, claims = fixtures()
    with_stale_unit(claims, 1)
    with pytest.raises(CaseAnalysisFailure) as raised:
        await run_pipeline(
            monkeypatch,
            scorer=scorer_for_claims(),
            claims=claims,
            summary="John is the attacker [A-02].",
        )
    assert raised.value.code == "case_judgement_invalid_claim"


@pytest.mark.asyncio
async def test_long_input_is_scored_with_research_truncation_and_a_negative_verdict_is_a_label(
    monkeypatch,
):
    scorer = FakeNli(fits=lambda premise, hypothesis: False)
    trace, calls, _ = await run_pipeline(monkeypatch, scorer=scorer)
    assert all(claim.semantic_grounding.reason == "lr_not_supported" for claim in trace.claims)
    assert all(claim.semantic_grounding.truncated for claim in trace.claims)
    assert [call["stage"] for call in calls] == ["case_reading", "case_judgement"]


def test_withheld_claim_ids_cannot_return_through_gaps():
    fields = {
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
    }
    given = CaseProviderReading(
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
        check_judgement_references(judgement, given)
    assert raised.value.code == "case_judgement_invalid_claim"
