from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
from isolated_database import isolated_database

from app.followup.conversation import (
    asked_gap_keys,
    asked_in_round,
    case_messages,
    followup_history_from,
    followup_qa_ids,
    rounds_asked,
)
from app.models.case import Case
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import followup_registry_items, resolve_case_trace
from app.trace.claims import CaseFollowupExchange, followup_payload
from app.trace.trace import CaseAnalysisTrace

ANSWER = "The incident happened at 23:30 on 12 May."

NARRATIVE = CaseSourceItem(
    source_id="s1",
    source_kind="narrative",
    text="Files on the shared drive were reported encrypted.",
)
BUNDLE = CaseSourceBundle(revision=1, sources=(NARRATIVE,))
[ANSWER_UNIT] = evidence_units(CaseSourceItem("QA-01", "followup_answer", ANSWER))


def trace_citing(source_id: str, unit_id: str) -> CaseAnalysisTrace:
    return CaseAnalysisTrace.model_validate(
        {
            "analysis_mode": "case_overview",
            "summary": "An incident was reported.",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The incident happened late in the evening.",
                    "epistemic_status": "reported",
                    "supporting_source_ids": [source_id],
                    "supporting_citations": [
                        {"source_id": source_id, "evidence_unit_ids": [unit_id]}
                    ],
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
    assert followup_payload(history) == [
        {"qa_id": "QA-01", "gap_key": "t", "question": "When?", "answer": ANSWER}
    ]
    assert [item.source_id for item in followup_registry_items(history)] == ["QA-01"]


def test_a_unit_of_an_answer_survives_validation():
    history = (CaseFollowupExchange(qa_id="QA-01", gap_key="t", question="When?", answer=ANSWER),)
    bound = resolve_case_trace(
        trace_citing("QA-01", ANSWER_UNIT.unit_id), BUNDLE, followup_history=history
    )

    [citation] = bound.claims[0].supporting_citations
    assert citation.source_id == "QA-01"
    assert citation.exact_quote == ANSWER
    assert bound.claims[0].supporting_source_ids == ["QA-01"]
    assert bound.claims[0].invalid_evidence == []


def test_a_unit_the_answer_does_not_have_is_still_dropped():
    history = (CaseFollowupExchange(qa_id="QA-01", gap_key="t", question="When?", answer=ANSWER),)
    missing = ANSWER_UNIT.unit_id.replace("U001", "U002")
    bound = resolve_case_trace(trace_citing("QA-01", missing), BUNDLE, followup_history=history)

    assert bound.claims[0].supporting_citations == []
    assert [entry.reason for entry in bound.claims[0].invalid_evidence] == ["unknown_unit"]


def test_an_answer_cannot_be_cited_when_it_was_not_given():
    bound = resolve_case_trace(trace_citing("QA-01", ANSWER_UNIT.unit_id), BUNDLE)

    assert bound.claims[0].supporting_citations == []
    assert [entry.reason for entry in bound.claims[0].invalid_evidence] == ["unknown_source"]


@pytest.mark.asyncio
async def test_history_is_read_from_the_conversation_in_order():
    async with isolated_database() as session_factory:
        async with session_factory() as db, db.begin():
            user = User(
                email="history@example.com",
                name="Analyst",
                password_hash="x",
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
            chat = await case_messages(db, case_id)
        history = followup_history_from(chat)

    assert [item.qa_id for item in history] == ["QA-01", "QA-02"]
    assert history[0].answer == ANSWER
    assert history[0].gap_key == "topic:time"
    assert history[1].answer is None, "the outstanding question has no reply yet"
    first, answer, second = chat
    assert followup_qa_ids(chat) == {first.id: "QA-01", answer.id: "QA-01", second.id: "QA-02"}


def test_the_round_state_is_read_from_the_questions_in_the_chat():
    round_one, round_two = uuid.uuid4(), uuid.uuid4()

    def said(ordinal, *, gap_key=None, asked_by=None):
        return SimpleNamespace(
            id=uuid.uuid4(),
            ordinal=ordinal,
            gap_key=gap_key,
            analysis_result_id=asked_by,
            in_reply_to_message_id=None,
        )

    chat = [
        said(1, gap_key="topic:time", asked_by=round_one),
        said(2, asked_by=round_one),
        said(3, gap_key="topic:owner", asked_by=round_one),
        said(4, gap_key="topic:host", asked_by=round_two),
        said(5, gap_key="topic:orphaned"),
    ]

    assert asked_gap_keys(chat) == {"topic:time", "topic:owner", "topic:host", "topic:orphaned"}
    assert rounds_asked(chat) == 2
    assert asked_in_round(chat, round_one) == 2
    assert asked_in_round(chat, round_two) == 1
