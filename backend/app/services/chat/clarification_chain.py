from dataclasses import dataclass
from typing import Sequence

from app.models.chat import ChatMessage
from app.services.followup import ClarificationExchange


@dataclass(frozen=True)
class ClarificationChain:
    root_ordinal: int
    original_user_content: str
    exchanges: tuple[ClarificationExchange, ...]
    pending_question: str | None = None


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
    pending_question: str | None = None
    latest_answer: str | None = None
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
            if pending_question is not None and latest_answer is not None:
                exchanges.append(
                    ClarificationExchange(
                        question=pending_question,
                        answer=latest_answer,
                    )
                )
            pending_question = message.content
            latest_answer = None
        elif message.role == "user" and pending_question is not None:
            latest_answer = message.content

    if pending_answer is not None:
        latest_answer = pending_answer
    if pending_question is not None and latest_answer is not None:
        exchanges.append(
            ClarificationExchange(
                question=pending_question,
                answer=latest_answer,
            )
        )

    return ClarificationChain(
        root_ordinal=root.ordinal,
        original_user_content=root.content,
        exchanges=tuple(exchanges),
        pending_question=pending_question,
    )


__all__ = ["ClarificationChain", "reconstruct_clarification_chain"]
