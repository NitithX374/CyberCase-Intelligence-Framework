from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.services.chat.case_answer as module
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.chat.case_answer import NOT_IN_ANALYSIS, generate_case_answer
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
    return bundle, CaseAnalysisTrace(
        analysis_mode="case_overview", summary=claim.text, claims=[claim]
    )


def answered(monkeypatch, raw: dict):
    bundle, trace = analysed_case()
    seen: dict[str, object] = {}

    async def parsed_like_the_provider(**kwargs):
        seen.update(kwargs)
        return kwargs["schema"].model_validate(raw)

    monkeypatch.setattr(module, "request_stage", parsed_like_the_provider)
    result = SimpleNamespace(
        id=uuid4(),
        summary=trace.summary,
        trace_json=trace.model_dump(mode="json"),
        external_context_json={},
    )
    output = asyncio.run(
        generate_case_answer(
            result=result,
            question="What happened?",
            history=[],
            sources=bundle,
            language="english",
        )
    )
    return output, seen


def cited(output) -> list[str]:
    return [claim.claim_id for claim in output.trace.claims]


def test_the_model_is_asked_for_the_shape_it_can_follow(monkeypatch):
    _, seen = answered(monkeypatch, {"outcome": "general", "units": [], "general_answer": "Hi."})

    assert seen["schema"].__name__ == "CaseProviderAnswer"


def test_a_unit_that_cites_no_claim_is_dropped_and_the_rest_is_answered(monkeypatch):
    output, _ = answered(
        monkeypatch,
        {
            "outcome": "answered",
            "units": [
                {"text": "The share was encrypted.", "claim_ids": ["A-01"]},
                {"text": "The attacker was a former employee.", "claim_ids": []},
            ],
            "general_answer": "",
        },
    )

    assert output.answer == "The share was encrypted."
    assert cited(output) == ["A-01"]


def test_an_answer_whose_units_cite_nothing_says_the_analysis_does_not_cover_it(monkeypatch):
    output, _ = answered(
        monkeypatch,
        {
            "outcome": "answered",
            "units": [{"text": "The attacker was a former employee.", "claim_ids": []}],
            "general_answer": "",
        },
    )

    assert output.answer == NOT_IN_ANALYSIS["english"]
    assert cited(output) == []


def test_an_answered_reply_that_only_has_general_text_is_given_as_general(monkeypatch):
    output, _ = answered(
        monkeypatch, {"outcome": "answered", "units": [], "general_answer": "Two."}
    )

    assert output.answer == "Two."
    assert cited(output) == []


def test_a_general_reply_without_text_is_answered_from_the_claims_it_cites(monkeypatch):
    output, _ = answered(
        monkeypatch,
        {
            "outcome": "general",
            "units": [{"text": "The share was encrypted.", "claim_ids": ["A-01"]}],
            "general_answer": "",
        },
    )

    assert output.answer == "The share was encrypted."
    assert cited(output) == ["A-01"]


def test_a_general_reply_without_text_or_claims_says_the_analysis_does_not_cover_it(
    monkeypatch,
):
    output, _ = answered(monkeypatch, {"outcome": "general", "units": [], "general_answer": " "})

    assert output.answer == NOT_IN_ANALYSIS["english"]


def test_a_general_reply_carries_no_claims_even_if_the_model_added_some(monkeypatch):
    output, _ = answered(
        monkeypatch,
        {
            "outcome": "general",
            "units": [{"text": "The share was encrypted.", "claim_ids": ["A-01"]}],
            "general_answer": "ATT&CK is a catalogue of attacker behaviour.",
        },
    )

    assert output.answer == "ATT&CK is a catalogue of attacker behaviour."
    assert cited(output) == []


def test_a_claim_outside_the_analysis_is_dropped_instead_of_failing_the_answer(monkeypatch):
    output, _ = answered(
        monkeypatch,
        {
            "outcome": "answered",
            "units": [
                {"text": "The share was encrypted.", "claim_ids": ["A-01", "A-09"]},
                {"text": "A ransom note was left.", "claim_ids": ["A-09"]},
            ],
            "general_answer": "",
        },
    )

    assert output.answer == "The share was encrypted."
    assert cited(output) == ["A-01"]


def test_an_answer_too_long_for_one_summary_is_still_refused_with_its_code(monkeypatch):
    unit = {"text": "x" * 3_900, "claim_ids": ["A-01"]}

    with pytest.raises(CaseAnalysisFailure) as refused:
        answered(monkeypatch, {"outcome": "answered", "units": [unit] * 7, "general_answer": ""})

    assert refused.value.code == "chat_answer_invalid"
    assert refused.value.status_code == 502
