"""The three kinds of reply the chat can give.

A question about the case is answered from claims or not at all. A question
that is not about the case gets a plain answer with nothing bound to it. The
three are kept apart because the reader cannot tell them apart otherwise: being
told the analysis lacks information is only useful when adding material fixes it.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseGeneratedUnit,
    CaseSourceCitation,
)
from app.services.chat.case_answer import (
    CaseAnswerResponse,
    build_answer_context,
    generate_case_answer,
)
from app.services.sources import CaseSourceBundle, CaseSourceItem

QUOTE = "The finance share was encrypted overnight."


def analysed_case() -> tuple[CaseSourceBundle, CaseAnalysisTrace]:
    source_id = str(uuid4())
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The finance share was encrypted.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=QUOTE)],
    )
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=QUOTE),),
    )
    trace = CaseAnalysisTrace(analysis_mode="case_overview", summary=claim.text, claims=[claim])
    return bundle, trace


def answer_output(outcome: str, language_prompt: str, general: str = ""):
    bundle, trace = analysed_case()
    context = {
        "analysis_result_id": str(uuid4()),
        "source_revision": bundle.revision,
        "pipeline_config": {},
        "analysis_summary": trace.summary,
        "trace": trace.model_dump(mode="json"),
        "question": "1+1",
        "history": [],
    }
    units = (
        [CaseGeneratedUnit(text="The finance share was encrypted.", claim_ids=["A-01"])]
        if outcome == "answered"
        else []
    )

    async def fake_stage(**_kwargs):
        return CaseAnswerResponse(outcome=outcome, units=units, general_answer=general)

    import app.services.chat.case_answer as module

    original = module.request_stage
    module.request_stage = fake_stage
    try:
        output = asyncio.run(
            generate_case_answer(
                context=context,
                source_bundle=bundle,
                user_message=language_prompt,
            )
        )
    finally:
        module.request_stage = original
    return output


def answer_for(outcome: str, language_prompt: str, general: str = "") -> str:
    return answer_output(outcome, language_prompt, general).answer


def test_the_model_is_shown_the_whole_analysis_not_only_its_claims():
    """Asked which techniques were mapped, the chat needs the associations."""

    bundle, trace = analysed_case()
    context = {
        "analysis_result_id": str(uuid4()),
        "source_revision": bundle.revision,
        "pipeline_config": {},
        "analysis_summary": trace.summary,
        "trace": trace.model_dump(mode="json"),
        "question": "Which techniques were mapped?",
        "history": [],
    }
    seen: dict[str, object] = {}

    async def fake_stage(**kwargs):
        seen.update(kwargs["content"])
        return CaseAnswerResponse(outcome="general", units=[], general_answer="None.")

    import app.services.chat.case_answer as module

    original = module.request_stage
    module.request_stage = fake_stage
    try:
        asyncio.run(
            generate_case_answer(
                context=context,
                source_bundle=bundle,
                user_message="Answer this question.",
            )
        )
    finally:
        module.request_stage = original

    for section in (
        "claims",
        "involved_parties",
        "timeline",
        "impacts",
        "mitre_associations",
        "gaps",
    ):
        assert section in seen, section


def test_a_question_the_case_does_not_cover_says_how_to_fix_it():
    answer = answer_for("not_in_analysis", "Answer this question.")
    assert "Sources page" in answer
    assert "analyse the case again" in answer


def test_a_question_that_is_not_about_the_case_is_answered_anyway():
    answer = answer_for("general", "Answer this question.", general="Two.")
    assert answer == "Two."
    assert "Sources" not in answer


def test_a_general_reply_is_bound_to_no_claims():
    output = answer_output("general", "Answer this question.", general="Two.")
    assert output.trace.claims == []
    assert output.execution_receipt["outcome"] == "general"


def test_an_answered_reply_must_cite_something():
    with pytest.raises(ValidationError):
        CaseAnswerResponse(outcome="answered", units=[])


def test_a_general_reply_must_not_cite_the_case():
    with pytest.raises(ValidationError):
        CaseAnswerResponse(
            outcome="general",
            units=[CaseGeneratedUnit(text="Two.", claim_ids=["A-01"])],
            general_answer="Two.",
        )


def test_a_general_reply_must_carry_its_text():
    with pytest.raises(ValidationError):
        CaseAnswerResponse(outcome="general", units=[])


def test_only_a_general_reply_carries_that_text():
    with pytest.raises(ValidationError):
        CaseAnswerResponse(outcome="not_in_analysis", units=[], general_answer="Two.")


def test_the_answer_context_carries_only_what_the_call_needs():
    bundle, trace = analysed_case()
    context = build_answer_context(
        result=type(
            "Result",
            (),
            {
                "id": uuid4(),
                "pipeline_config": {},
                "summary": trace.summary,
                "trace_json": trace.model_dump(mode="json"),
            },
        )(),
        question="What happened?",
        history=[],
        source_bundle=bundle,
    )
    assert context["question"] == "What happened?"
    assert context["source_revision"] == 1
    assert context["history"] == []
