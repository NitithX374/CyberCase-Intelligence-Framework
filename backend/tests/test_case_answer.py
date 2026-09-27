from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.chat.compose as module
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.chat.answer import answer_metadata
from app.chat.compose import CHAT_OUTPUT_TOKENS, UNANSWERED, generate_case_answer
from app.config import settings
from app.errors import CaseAnalysisFailure
from app.llm.settings import configured_pipeline
from app.schemas.rag import LegalReferenceResult
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseFollowupExchange,
    CaseSourceCitation,
)
from app.trace.trace import CaseAnalysisTrace

NARRATIVE_ID = "narrative-1"
DOCUMENT_ID = "statement-1"
NARRATIVE = "On 3 March the victim received a call from someone claiming to be a police officer."
FILLER = "Routine account activity was recorded without incident on this page. " * 110
ACCOUNT_LINE = "The victim transferred money to account 123-4-56789 twice."
REPLY = "It started at around two in the morning."


def case_sources() -> CaseSourceBundle:
    text = f"{FILLER}\n{ACCOUNT_LINE}"
    statement = CaseSourceItem(
        source_id=DOCUMENT_ID,
        source_kind="document",
        text=text,
        document_id="document-uuid",
        filename="statement.pdf",
        provenance={
            "extraction_method": "native_pdf",
            "pages": [
                {"page_number": 1, "start_offset": 0, "end_offset": len(FILLER)},
                {"page_number": 20, "start_offset": len(FILLER) + 1, "end_offset": len(text)},
            ],
        },
    )
    narrative = CaseSourceItem(source_id=NARRATIVE_ID, source_kind="narrative", text=NARRATIVE)
    return CaseSourceBundle(revision=1, sources=(narrative, statement))


def stored_analysis():
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The victim was called by someone posing as police.",
        epistemic_status="reported",
        supporting_source_ids=[NARRATIVE_ID],
        supporting_citations=[
            CaseSourceCitation(
                source_id=NARRATIVE_ID, exact_quote="someone claiming to be a police officer"
            )
        ],
    )
    gap = CaseAnalysisGap(
        gap_id="G-01",
        gap_key="topic:suspect-identity",
        topic="Identity of the caller",
        status="NOT_PROVIDED",
        description="Nothing names the caller.",
        reason="No source identifies the caller.",
        priority="high",
        askable=True,
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview", summary=claim.text, claims=[claim], gaps=[gap]
    )
    return SimpleNamespace(
        id=uuid4(),
        summary=trace.summary,
        trace_json=trace.model_dump(mode="json"),
        external_context_json={},
    )


def technical_context() -> CaseRagContextPayload:
    return CaseRagContextPayload(
        retrieval_context_id="context-1",
        context="T1566 Phishing: adversaries send messages to gain access.",
        mitre_table=({"technique_id": "T1566", "name": "Phishing"},),
        legal_relevance=LegalReferenceResult(),
    )


def message(role: str, content: str):
    return SimpleNamespace(id=uuid4(), role=role, content=content)


def unit(text: str, basis: str = "case_fact", claim_ids=(), quotes=()) -> dict:
    return {
        "text": text,
        "basis": basis,
        "claim_ids": list(claim_ids),
        "quotes": [{"source_id": source_id, "exact_quote": quote} for source_id, quote in quotes],
    }


def reply(*units: dict, suggestion: str = "none") -> dict:
    return {"units": list(units), "suggestion": suggestion}


def ask(monkeypatch, raw: dict, *, analysed: bool = False, **overrides):
    seen: dict[str, object] = {}

    async def parsed_like_the_provider(**kwargs):
        seen.update(kwargs)
        return kwargs["schema"].model_validate(raw)

    monkeypatch.setattr(module, "request_stage", parsed_like_the_provider)
    arguments = {
        "result": stored_analysis() if analysed else None,
        "question": "Where did the money go?",
        "history": [],
        "sources": case_sources(),
        "language": "english",
        **overrides,
    }
    return asyncio.run(generate_case_answer(**arguments)), seen


def test_before_an_analysis_the_model_reads_every_source_in_full(monkeypatch):
    _, seen = ask(monkeypatch, reply(unit("Two sources.", "general")))

    content = seen["content"]
    assert content["analysis"] is None
    assert content["analysis_status"] == "none"
    statement = next(s for s in content["case_sources"] if s["source_id"] == DOCUMENT_ID)
    assert ACCOUNT_LINE in statement["text"] and len(statement["text"]) > 6_000
    assert statement["document"]["filename"] == "statement.pdf"


def test_a_fact_quoted_from_deep_in_a_document_is_cited_with_its_page(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(
            unit(
                "The money went to account 123-4-56789.",
                quotes=[(DOCUMENT_ID, "transferred money to account 123-4-56789")],
            )
        ),
    )

    [answered] = output.units
    [citation] = answered.supporting_citations
    assert (citation.source_id, citation.filename, citation.page_numbers) == (
        DOCUMENT_ID,
        "statement.pdf",
        [20],
    )
    assert answered.supporting_source_ids == [DOCUMENT_ID]


def test_a_quote_that_is_not_in_the_source_loses_its_citation_but_not_its_text(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(
            unit(
                "The victim transferred money three times.",
                quotes=[(DOCUMENT_ID, "transferred money three times")],
            )
        ),
    )

    [answered] = output.units
    assert answered.text == "The victim transferred money three times."
    assert answered.basis == "case_fact"
    assert answered.supporting_citations == []


def test_a_summary_cites_each_source_it_draws_on(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(
            unit("A caller posed as police.", quotes=[(NARRATIVE_ID, "claiming to be a police")]),
            unit("Money went to 123-4-56789.", quotes=[(DOCUMENT_ID, "account 123-4-56789")]),
        ),
    )

    assert [u.supporting_source_ids for u in output.units] == [[NARRATIVE_ID], [DOCUMENT_ID]]
    assert output.answer == "A caller posed as police.\n\nMoney went to 123-4-56789."


def test_an_interpretation_stays_marked_as_one(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(unit("This looks like a call-centre impersonation scam.", "interpretation")),
    )

    assert [u.basis for u in output.units] == ["interpretation"]


def test_a_technique_is_explained_only_from_the_retrieved_context(monkeypatch):
    _, with_context = ask(
        monkeypatch,
        reply(unit("T1566 is phishing.", "technical")),
        analysed=True,
        technical_context=technical_context(),
    )
    _, without_context = ask(monkeypatch, reply(unit("I do not know.", "general")))

    assert with_context["content"]["technical_context"]["mitre_table"] == [
        {"technique_id": "T1566", "name": "Phishing"}
    ]
    assert without_context["content"]["technical_context"] is None


def test_after_an_analysis_a_claim_is_cited_with_the_sources_behind_it(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(unit("A caller posed as police.", claim_ids=["A-1"])),
        analysed=True,
        analysis_status="current",
    )

    [answered] = output.units
    assert answered.claim_ids == ["A-01"]
    assert [c.source_id for c in answered.supporting_citations] == [NARRATIVE_ID]
    assert [claim.claim_id for claim in output.trace.claims] == ["A-01"]


def test_after_an_analysis_the_model_still_reads_the_sources_and_the_gaps(monkeypatch):
    _, seen = ask(monkeypatch, reply(unit("See the sources.", "general")), analysed=True)

    content = seen["content"]
    assert {s["source_id"] for s in content["case_sources"]} == {NARRATIVE_ID, DOCUMENT_ID}
    assert [c["claim_id"] for c in content["analysis"]["claims"]] == ["A-01"]
    assert [g["topic"] for g in content["analysis"]["gaps"]] == ["Identity of the caller"]


def test_a_claim_outside_the_analysis_is_dropped_instead_of_failing(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(unit("A ransom note was left.", claim_ids=["A-09"])),
        analysed=True,
    )

    [answered] = output.units
    assert answered.claim_ids == []
    assert answered.supporting_citations == []
    assert output.trace is None


def test_a_stale_analysis_is_reported_to_the_model(monkeypatch):
    _, seen = ask(
        monkeypatch, reply(unit("Noted.", "general")), analysed=True, analysis_status="stale"
    )

    assert seen["content"]["analysis_status"] == "stale"


@pytest.mark.parametrize(
    ("offered", "kept"),
    [("add_source", "add_source"), ("run_analysis", "run_analysis"), ("reboot", "none")],
)
def test_the_suggestion_to_add_a_source_or_analyse_again_is_kept(monkeypatch, offered, kept):
    output, _ = ask(
        monkeypatch, reply(unit("Add it as a source first.", "general"), suggestion=offered)
    )

    assert output.suggestion == kept


def test_a_follow_up_answer_is_visible_and_can_be_quoted(monkeypatch):
    followups = (
        CaseFollowupExchange(
            qa_id="QA-01", gap_key="topic:start", question="When did it start?", answer=REPLY
        ),
    )
    output, seen = ask(
        monkeypatch,
        reply(unit("It began around two.", quotes=[("QA-01", "around two in the morning")])),
        followups=followups,
    )

    assert [item["qa_id"] for item in seen["content"]["followup_history"]] == ["QA-01"]
    [answered] = output.units
    assert [c.source_id for c in answered.supporting_citations] == ["QA-01"]


def test_an_unknown_basis_is_checked_like_a_case_fact(monkeypatch):
    output, _ = ask(monkeypatch, reply(unit("The caller was a man.", "opinion")))

    assert [u.basis for u in output.units] == ["case_fact"]


def test_malformed_units_do_not_cost_the_answer(monkeypatch):
    output, _ = ask(
        monkeypatch,
        {
            "units": [
                "not a unit",
                {"text": "A caller posed as police.", "claim_ids": "A-01", "quotes": "none"},
                {"text": "   "},
            ]
        },
        analysed=True,
    )

    [answered] = output.units
    assert answered.claim_ids == ["A-01"]
    assert output.suggestion == "none"


def test_an_empty_reply_says_the_question_could_not_be_answered(monkeypatch):
    output, _ = ask(monkeypatch, reply(), language="thai")

    assert output.answer == UNANSWERED["thai"]
    assert output.units == ()


def test_an_answer_too_long_for_one_message_is_refused_with_its_code(monkeypatch):
    long_unit = unit("x" * 3_900, "general")

    with pytest.raises(CaseAnalysisFailure) as refused:
        ask(monkeypatch, reply(*[long_unit] * 7))

    assert refused.value.code == "chat_answer_invalid"
    assert refused.value.status_code == 502


def test_chat_uses_the_configured_model(monkeypatch):
    monkeypatch.setattr(settings, "case_analysis_model", "example/configured-model")
    _, seen = ask(monkeypatch, reply(unit("Hello.", "general")))

    assert seen["config"].model == "example/configured-model"
    assert seen["schema"].__name__ == "ChatReply"


def test_a_chat_answer_has_an_output_budget_far_below_the_analysis(monkeypatch):
    _, seen = ask(monkeypatch, reply(unit("Hello.", "general")))

    assert seen["config"].output_tokens == CHAT_OUTPUT_TOKENS
    assert seen["config"].output_tokens < configured_pipeline().output_tokens


def test_the_answer_is_written_in_the_language_it_is_given(monkeypatch):
    _, seen = ask(monkeypatch, reply(unit("สอง", "general")), language="thai")

    assert seen["content"]["response_language"] == "thai"


def test_an_empty_message_in_the_history_is_left_out(monkeypatch):
    history = [message("user", "What happened?"), message("assistant", "   ")]
    _, seen = ask(monkeypatch, reply(unit("Two.", "general")), history=history)

    assert [turn["content"] for turn in seen["content"]["conversation_history"]] == [
        "What happened?"
    ]


def test_the_stored_message_keeps_the_units_and_the_suggestion(monkeypatch):
    output, _ = ask(
        monkeypatch,
        reply(
            unit("A caller posed as police.", claim_ids=["A-01"]),
            unit("It may be a scam.", "interpretation"),
            suggestion="run_analysis",
        ),
        analysed=True,
    )

    metadata = answer_metadata(output)

    assert [u.basis for u in metadata["answer_units"]] == ["case_fact", "interpretation"]
    assert metadata["suggestion"] == "run_analysis"
    assert [c.claim_id for c in metadata["analysis_trace"].claims] == ["A-01"]


def test_a_plain_answer_stores_no_suggestion():
    output = module.CaseAnalysisOutput(answer="Hello.", trace=None)

    assert answer_metadata(output) == {}
