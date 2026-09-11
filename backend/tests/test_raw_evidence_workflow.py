from uuid import uuid4

from app.models.chat import ChatMessage
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
