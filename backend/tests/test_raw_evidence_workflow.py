from uuid import uuid4

import pytest

from app.models.chat import ChatMessage, ChatThread
from app.services.chat.chat_run_creation import _resolve_action
from app.services.chat.raw_evidence import build_raw_evidence_snapshot


def message(ordinal: int, content: str, evidence_kind: str) -> ChatMessage:
    return ChatMessage(
        id=uuid4(),
        thread_id=uuid4(),
        ordinal=ordinal,
        role="user",
        content=content,
        metadata_json={"evidence_kind": evidence_kind},
    )


def test_raw_evidence_is_chronological_and_excludes_questions() -> None:
    initial = message(1, "Initial narrative", "initial_case_narrative")
    question = message(3, "What does this mean?", "analyst_question")
    clarification = message(5, "The IP was 192.0.2.4", "clarification_answer")
    added = message(7, "A new log was found", "added_case_information")
    snapshot = build_raw_evidence_snapshot([added, question, initial, clarification])
    assert snapshot.source_message_ids == (initial.id, clarification.id, added.id)
    assert [(source.message_id, source.content) for source in snapshot.sources] == [
        (initial.id, "Initial narrative"),
        (clarification.id, "The IP was 192.0.2.4"),
        (added.id, "A new log was found"),
    ]
    assert "[INITIAL CASE NARRATIVE]\nInitial narrative" in snapshot.text
    assert "[CLARIFICATION ANSWER #1]" in snapshot.text
    assert "[ADDED CASE INFORMATION #1]" in snapshot.text
    assert "What does this mean?" not in snapshot.text
    assert len(snapshot.sha256) == 64


def test_first_message_and_post_answer_actions_have_explicit_evidence_kinds() -> None:
    thread = ChatThread(status="idle", next_message_ordinal=1)
    assert _resolve_action(thread, None) == (
        "initial_analysis",
        "initial_case_narrative",
    )
    thread.status = "answered"
    thread.next_message_ordinal = 3
    assert _resolve_action(thread, "ask") == ("ask", "analyst_question")
    assert _resolve_action(thread, "add_case_info") == (
        "add_case_info",
        "added_case_information",
    )


def test_answered_thread_requires_an_explicit_action() -> None:
    thread = ChatThread(status="answered", next_message_ordinal=3)
    with pytest.raises(Exception) as error:
        _resolve_action(thread, None)
    assert getattr(error.value, "status_code", None) == 422


def test_clarification_answer_is_evidence() -> None:
    thread = ChatThread(status="awaiting_followup", next_message_ordinal=3)
    assert _resolve_action(thread, None) == (
        "add_case_info",
        "clarification_answer",
    )
