from __future__ import annotations

import uuid

import pytest
from isolated_database import isolated_database

from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.user import User
from app.services.analysis.contracts import (
    CaseAnalysisTrace,
    CaseFollowupExchange,
    followup_payload,
)
from app.services.analysis.steps.bind import followup_registry_items, resolve_case_trace
from app.services.chat.followup import load_followup_history
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem

ANSWER = "The incident happened at 23:30 on 12 May."

NARRATIVE = CaseSourceItem(
    source_id="s1",
    source_kind="narrative",
    text="Files on the shared drive were reported encrypted.",
)
BUNDLE = CaseSourceBundle(revision=1, sources=(NARRATIVE,))


def trace_citing(source_id: str, quote: str) -> CaseAnalysisTrace:
    return CaseAnalysisTrace.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "analysis_mode": "case_overview",
            "validation_status": "validated",
            "summary": "An incident was reported.",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The incident happened late in the evening.",
                    "epistemic_status": "reported",
                    "supporting_source_ids": [source_id],
                    "supporting_citations": [{"source_id": source_id, "exact_quote": quote}],
                }
            ],
            "gaps": [],
            "mitre_associations": [],
        }
    )


def test_an_unanswered_question_is_withheld_from_the_model():
    history = (
        CaseFollowupExchange(qa_id="QA-01", gap_key="t", question="When?", answer=ANSWER),
        CaseFollowupExchange(qa_id="QA-02", gap_key="u", question="Who?"),
    )
    assert followup_payload(history) == [{"qa_id": "QA-01", "question": "When?", "answer": ANSWER}]
    assert [item.source_id for item in followup_registry_items(history)] == ["QA-01"]


def test_a_quote_from_an_answer_survives_validation():
    history = (CaseFollowupExchange(qa_id="QA-01", gap_key="t", question="When?", answer=ANSWER),)
    bound = resolve_case_trace(
        trace_citing("QA-01", "23:30 on 12 May"), BUNDLE, followup_history=history
    )

    citation = bound.claims[0].supporting_citations[0]
    assert citation.source_id == "QA-01"
    assert citation.exact_quote == "23:30 on 12 May"
    assert bound.grounding.citations_verified == 1
    assert bound.grounding.citations_unfound == 0
    assert bound.grounding.sources_total == 2


def test_a_quote_the_answer_does_not_contain_is_still_dropped():
    history = (CaseFollowupExchange(qa_id="QA-01", gap_key="t", question="When?", answer=ANSWER),)
    bound = resolve_case_trace(
        trace_citing("QA-01", "03:00 on 1 January"), BUNDLE, followup_history=history
    )

    assert bound.claims[0].supporting_citations == []
    assert bound.grounding.citations_unfound == 1


def test_an_answer_cannot_be_cited_when_it_was_not_given():
    bound = resolve_case_trace(trace_citing("QA-01", "23:30 on 12 May"), BUNDLE)

    assert bound.claims[0].supporting_citations == []
    assert bound.grounding.citations_unfound == 1


@pytest.mark.asyncio
async def test_history_is_read_from_the_conversation_in_order():
    async with isolated_database() as session_factory:
        async with session_factory() as db, db.begin():
            user = User(
                email="history@example.com",
                name="Analyst",
                password_hash="x",
                oauth_provider="password",
                oauth_subject_id="history@example.com",
            )
            db.add(user)
            await db.flush()
            case = Case(user_id=user.id, title="History case", source_revision=1)
            db.add(case)
            await db.flush()
            first = ChatMessage(
                case_id=case.id,
                ordinal=1,
                role="assistant",
                content="When did the incident happen?",
                message_kind="followup_question",
                gap_key="topic:time",
            )
            db.add(first)
            await db.flush()
            db.add(
                ChatMessage(
                    case_id=case.id,
                    ordinal=2,
                    role="user",
                    content=ANSWER,
                    message_kind="followup_answer",
                    in_reply_to_message_id=first.id,
                )
            )
            db.add(
                ChatMessage(
                    case_id=case.id,
                    ordinal=3,
                    role="assistant",
                    content="Who owns the workstation?",
                    message_kind="followup_question",
                    gap_key="topic:owner",
                )
            )
            case_id: uuid.UUID = case.id

        async with session_factory() as db:
            history = await load_followup_history(db, case_id)

    assert [item.qa_id for item in history] == ["QA-01", "QA-02"]
    assert history[0].answer == ANSWER
    assert history[0].gap_key == "topic:time"
    assert history[1].answer is None, "the outstanding question has no reply yet"
