import asyncio
from uuid import uuid4

from app.models.chat import ChatMessage, ChatThread
from app.services.chat.chat_run_creation import _followup_position
from app.services.chat.clarification_chain import reconstruct_clarification_chain
from app.services.chat.raw_evidence import build_raw_evidence_snapshot
from app.services.followup.context import build_bounded_context
from app.services.followup.schemas import ClarificationExchange


def test_raw_evidence_hash_ignores_workflow_context_and_assistant_question() -> None:
    thread_id = uuid4()
    initial_id = uuid4()
    answer_id = uuid4()
    base = [
        ChatMessage(
            id=initial_id,
            thread_id=thread_id,
            ordinal=1,
            role="user",
            content="A bicycle was reported missing.",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=2,
            role="assistant",
            content="What time did it happen?",
            metadata_json={"chat_followup": {"kind": "clarification"}},
        ),
        ChatMessage(
            id=answer_id,
            thread_id=thread_id,
            ordinal=3,
            role="user",
            content="ไม่ทราบ",
            metadata_json={"evidence_kind": "clarification_answer"},
        ),
    ]
    enriched = list(base)
    enriched[2] = ChatMessage(
        id=answer_id,
        thread_id=thread_id,
        ordinal=3,
        role="user",
        content="ไม่ทราบ",
        metadata_json={
            "evidence_kind": "clarification_answer",
            "clarification_context": {"answered_gap_key": "topic:incident-time"},
        },
    )

    plain = build_raw_evidence_snapshot(base)
    contextual = build_raw_evidence_snapshot(enriched)

    assert plain.sha256 == contextual.sha256
    assert contextual.source_message_ids == (initial_id, answer_id)
    assert contextual.sources[1].content == "ไม่ทราบ"
    assert "What time did it happen?" not in contextual.text


def test_followup_position_copies_question_context_to_answer_metadata() -> None:
    thread_id = uuid4()
    question_id = uuid4()
    messages = [
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=1,
            role="user",
            content="case",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=question_id,
            thread_id=thread_id,
            ordinal=2,
            role="assistant",
            content="ทราบเวลาที่เกิดเหตุหรือไม่?",
            metadata_json={
                "chat_followup": {
                    "kind": "clarification",
                    "root_ordinal": 1,
                    "followup_context": {
                        "gap_id": "G-01",
                        "gap_topic": "เวลาที่เกิดเหตุ",
                        "gap_key": "topic:incident-time",
                        "evidence_sha256": "a" * 64,
                    },
                }
            },
        ),
    ]

    class Scalars:
        def all(self):
            return messages

    class Result:
        def scalars(self):
            return Scalars()

    class Database:
        async def execute(self, statement):
            return Result()

    thread = ChatThread(
        id=thread_id,
        status="awaiting_followup",
        next_message_ordinal=3,
    )
    root, round_number, context = asyncio.run(
        _followup_position(Database(), thread, "ไม่ทราบ", 3)
    )

    assert root == 1
    assert round_number == 1
    assert context == {
        "question_message_id": str(question_id),
        "answered_gap_id": "G-01",
        "answered_gap_topic": "เวลาที่เกิดเหตุ",
        "answered_gap_key": "topic:incident-time",
        "question_evidence_sha256": "a" * 64,
    }


def test_short_answer_context_is_structural_and_does_not_rewrite_user_content() -> None:
    payload = build_bounded_context(
        original_user_content="case",
        clarification_exchanges=(
            ClarificationExchange(
                question="ทราบเวลาที่เกิดเหตุหรือไม่?",
                answer="ไม่ทราบ",
                gap_id="G-02",
                gap_topic="เวลาที่เกิดเหตุ",
                gap_key="topic:incident-time",
                evidence_sha256="a" * 64,
                question_message_id=str(uuid4()),
            ),
        ),
        raw_evidence="[CLARIFICATION ANSWER #1]\nไม่ทราบ",
    )

    clarification = payload["clarification_exchanges"][0]
    assert clarification["user_answer"] == "ไม่ทราบ"
    assert clarification["assistant_question"] == "ทราบเวลาที่เกิดเหตุหรือไม่?"
    assert clarification["workflow_context"]["requested_gap_topic"] == ("เวลาที่เกิดเหตุ")
    assert "incident time is unknown" not in str(payload)


def test_mismatched_answer_context_cannot_override_asked_gap_topic() -> None:
    thread_id = uuid4()
    question_id = uuid4()
    messages = [
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=1,
            role="user",
            content="case",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=question_id,
            thread_id=thread_id,
            ordinal=2,
            role="assistant",
            content="What time did it happen?",
            metadata_json={
                "chat_followup": {
                    "kind": "clarification",
                    "root_ordinal": 1,
                    "followup_context": {
                        "gap_topic": "incident time",
                        "gap_key": "topic:incident-time",
                    },
                }
            },
        ),
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=3,
            role="user",
            content="unknown",
            metadata_json={
                "evidence_kind": "clarification_answer",
                "clarification_context": {
                    "question_message_id": str(uuid4()),
                    "answered_gap_topic": "CCTV subject identity",
                    "answered_gap_key": "topic:cctv-subject-identity",
                },
            },
        ),
    ]

    chain = reconstruct_clarification_chain(messages, root_ordinal=1)

    assert chain is not None
    assert chain.exchanges[0].gap_topic == "incident time"
    assert chain.exchanges[0].gap_key == "topic:incident-time"
