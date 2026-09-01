from dataclasses import dataclass
from typing import Mapping, Sequence

from app.models.chat import ChatMessage
from app.services.followup import ClarificationExchange


@dataclass(frozen=True)
class ClarificationChain:
    root_ordinal: int
    original_user_content: str
    exchanges: tuple[ClarificationExchange, ...]
    pending_question: str | None = None
    pending_context: dict[str, str] | None = None


def _followup_root_ordinal(message: ChatMessage) -> int | None:
    metadata = message.metadata_json
    if not isinstance(metadata, dict):
        return None
    followup = metadata.get("chat_followup")
    if not isinstance(followup, dict):
        return None
    root_ordinal = followup.get("root_ordinal")
    if (
        not isinstance(root_ordinal, int)
        or isinstance(root_ordinal, bool)
        or root_ordinal < 1
    ):
        return None
    return root_ordinal


def _is_clarification_message(message: ChatMessage) -> bool:
    metadata = message.metadata_json
    if not isinstance(metadata, dict):
        return False
    followup = metadata.get("chat_followup")
    return isinstance(followup, dict) and followup.get("kind") == "clarification"


def _is_terminal_assistant_message(message: ChatMessage) -> bool:
    if message.role != "assistant":
        return False
    if _is_clarification_message(message):
        return False
    if message.retrieval_context_id is not None:
        return True
    metadata = message.metadata_json
    return isinstance(metadata, dict) and "mitre_table" in metadata


def _followup_context(message: ChatMessage) -> dict[str, str]:
    metadata = message.metadata_json
    followup = metadata.get("chat_followup") if isinstance(metadata, dict) else None
    context = followup.get("followup_context") if isinstance(followup, dict) else None
    if not isinstance(context, Mapping):
        return {}
    return {
        key: value
        for key in ("gap_id", "gap_topic", "gap_key", "evidence_sha256")
        if isinstance((value := context.get(key)), str) and value
    }


def _answer_context(message: ChatMessage | None) -> dict[str, str]:
    if message is None or not isinstance(message.metadata_json, dict):
        return {}
    context = message.metadata_json.get("clarification_context")
    if not isinstance(context, Mapping):
        return {}
    mapping = {
        "answered_gap_id": "gap_id",
        "answered_gap_topic": "gap_topic",
        "answered_gap_key": "gap_key",
        "question_evidence_sha256": "evidence_sha256",
        "question_message_id": "question_message_id",
    }
    return {
        target: value
        for source, target in mapping.items()
        if isinstance((value := context.get(source)), str) and value
    }


def _exchange(
    question: ChatMessage,
    answer: str,
    answer_message: ChatMessage | None,
) -> ClarificationExchange:
    answer_context = _answer_context(answer_message)
    if answer_context.get("question_message_id") != str(question.id):
        answer_context = {}
    context = {**_followup_context(question), **answer_context}
    return ClarificationExchange(
        question=question.content,
        answer=answer,
        gap_id=context.get("gap_id"),
        gap_topic=context.get("gap_topic"),
        gap_key=context.get("gap_key"),
        evidence_sha256=context.get("evidence_sha256"),
        question_message_id=context.get("question_message_id", str(question.id)),
        answer_message_id=(
            str(answer_message.id) if answer_message is not None else None
        ),
    )


def reconstruct_clarification_chain(
    messages: Sequence[ChatMessage],
    *,
    root_ordinal: int | None = None,
    pending_answer: str | None = None,
) -> ClarificationChain | None:
    ordered = sorted(messages, key=lambda message: message.ordinal)
    if not ordered:
        return None

    latest_assistant_index = next(
        (
            index
            for index in range(len(ordered) - 1, -1, -1)
            if ordered[index].role == "assistant"
        ),
        None,
    )
    if root_ordinal is None and latest_assistant_index is not None:
        root_ordinal = _followup_root_ordinal(ordered[latest_assistant_index])

    root_index = next(
        (
            index
            for index, message in enumerate(ordered)
            if message.role == "user" and message.ordinal == root_ordinal
        ),
        None,
    )
    if root_index is None and latest_assistant_index is not None:
        root_index = next(
            (
                index
                for index in range(latest_assistant_index - 1, -1, -1)
                if ordered[index].role == "user"
            ),
            None,
        )
    if root_index is None:
        root_index = next(
            (
                index
                for index in range(len(ordered) - 1, -1, -1)
                if ordered[index].role == "user"
            ),
            None,
        )
    if root_index is None:
        return None

    root = ordered[root_index]
    exchanges: list[ClarificationExchange] = []
    pending_question_message: ChatMessage | None = None
    latest_answer_message: ChatMessage | None = None
    active_messages = ordered[root_index + 1 :]
    marked_indices = [
        index
        for index, message in enumerate(active_messages)
        if _is_clarification_message(message)
    ]
    first_marked_index = marked_indices[0] if marked_indices else None
    for index, message in enumerate(active_messages):
        if message.role == "assistant":
            if _is_terminal_assistant_message(message):
                continue
            if (
                first_marked_index is not None
                and index > first_marked_index
                and not _is_clarification_message(message)
            ):
                continue
            if (
                pending_question_message is not None
                and latest_answer_message is not None
            ):
                exchanges.append(
                    _exchange(
                        pending_question_message,
                        latest_answer_message.content,
                        latest_answer_message,
                    )
                )
            pending_question_message = message
            latest_answer_message = None
        elif message.role == "user" and pending_question_message is not None:
            latest_answer_message = message

    if pending_answer is not None:
        latest_answer = pending_answer
    else:
        latest_answer = (
            latest_answer_message.content if latest_answer_message is not None else None
        )
    if pending_question_message is not None and latest_answer is not None:
        exchanges.append(
            _exchange(
                pending_question_message,
                latest_answer,
                latest_answer_message,
            )
        )

    pending_context = None
    if pending_question_message is not None:
        pending_context = {
            **_followup_context(pending_question_message),
            "question_message_id": str(pending_question_message.id),
        }

    return ClarificationChain(
        root_ordinal=root.ordinal,
        original_user_content=root.content,
        exchanges=tuple(exchanges),
        pending_question=(
            pending_question_message.content
            if pending_question_message is not None
            else None
        ),
        pending_context=pending_context,
    )


__all__ = ["ClarificationChain", "reconstruct_clarification_chain"]
