from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

import app.services.chat.case_answer as module
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseGeneratedUnit,
    CaseSourceCitation,
)
from app.services.chat.case_answer import (
    CaseAnswerResponse,
    GeneralCaseAnswerResponse,
    generate_case_answer,
)
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem

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


def stored_analysis(trace: CaseAnalysisTrace):
    return SimpleNamespace(
        id=uuid4(),
        summary=trace.summary,
        trace_json=trace.model_dump(mode="json"),
    )


def message(role: str, content: str):
    return SimpleNamespace(id=uuid4(), role=role, content=content)


def answered_with(monkeypatch, response, *, analysed: bool = True, **overrides):
    bundle, trace = analysed_case()
    seen: dict[str, object] = {}

    async def fake_stage(**kwargs):
        seen.update(kwargs)
        return response

    monkeypatch.setattr(module, "request_stage", fake_stage)
    arguments = {
        "result": stored_analysis(trace) if analysed else None,
        "question": "1+1",
        "history": [],
        "sources": bundle,
        "language": "english",
        **overrides,
    }
    return asyncio.run(generate_case_answer(**arguments)), seen


def answer_output(monkeypatch, outcome: str, general: str = "", language: str = "english"):
    units = (
        [CaseGeneratedUnit(text="The finance share was encrypted.", claim_ids=["A-01"])]
        if outcome == "answered"
        else []
    )
    output, _ = answered_with(
        monkeypatch,
        CaseAnswerResponse(outcome=outcome, units=units, general_answer=general),
        language=language,
    )
    return output


def test_the_model_is_shown_the_whole_analysis_not_only_its_claims(monkeypatch):
    _, seen = answered_with(
        monkeypatch,
        CaseAnswerResponse(outcome="general", units=[], general_answer="None."),
        question="Which techniques were mapped?",
    )

    assert seen["stage"] == "chat_answer"
    for section in (
        "claims",
        "involved_parties",
        "timeline",
        "impacts",
        "mitre_associations",
        "gaps",
    ):
        assert section in seen["content"], section


def test_chat_uses_the_configured_model_for_a_stored_analysis(monkeypatch):
    _, seen = answered_with(
        monkeypatch,
        CaseAnswerResponse(outcome="general", units=[], general_answer="CyberCase"),
        question="Who are you?",
    )

    assert seen["config"].model == "deepseek/deepseek-v4.1-flash"


def test_the_answer_is_written_in_the_language_it_is_given(monkeypatch):
    _, seen = answered_with(
        monkeypatch,
        CaseAnswerResponse(outcome="general", units=[], general_answer="สอง"),
        language="thai",
    )
    assert seen["content"]["response_language"] == "thai"

    answer = answer_output(monkeypatch, "not_in_analysis", language="thai")
    assert answer.answer == module.NOT_IN_ANALYSIS["thai"]


def test_a_question_the_case_does_not_cover_says_how_to_fix_it(monkeypatch):
    answer = answer_output(monkeypatch, "not_in_analysis").answer
    assert "Sources page" in answer
    assert "analyse the case again" in answer


def test_a_question_that_is_not_about_the_case_is_answered_anyway(monkeypatch):
    answer = answer_output(monkeypatch, "general", general="Two.").answer
    assert answer == "Two."
    assert "Sources" not in answer


def test_a_general_reply_is_bound_to_no_claims(monkeypatch):
    output = answer_output(monkeypatch, "general", general="Two.")
    assert output.trace.claims == []
    assert output.trace.analysis_mode == "question_answer"


def test_an_answered_reply_carries_the_claims_it_cites(monkeypatch):
    output = answer_output(monkeypatch, "answered")
    assert output.answer == "The finance share was encrypted."
    assert [claim.claim_id for claim in output.trace.claims] == ["A-01"]


def test_an_empty_message_in_the_history_is_left_out(monkeypatch):
    earlier = [message("user", "What happened?"), message("assistant", "  "), message("user", "?")]
    _, seen = answered_with(
        monkeypatch,
        CaseAnswerResponse(outcome="general", units=[], general_answer="Two."),
        history=earlier,
    )

    assert [item["content"] for item in seen["content"]["conversation_history"]] == [
        "What happened?",
        "?",
    ]


def test_before_an_analysis_the_question_is_answered_from_the_sources(monkeypatch):
    output, seen = answered_with(
        monkeypatch,
        GeneralCaseAnswerResponse(answer=" The share was encrypted. "),
        analysed=False,
        history=[message("assistant", "")],
    )

    assert seen["stage"] == "chat_general_answer"
    assert seen["content"]["case_sources"][0]["text"] == QUOTE
    assert seen["content"]["conversation_history"] == []
    assert output.answer == "The share was encrypted."
    assert output.trace is None


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
