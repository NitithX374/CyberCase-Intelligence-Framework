from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from app.services.extraction.extraction_contracts import ExtractionInput, ExtractionSourceMessage
from app.services.extraction.extraction_utils import (
    is_terminal_assistant_message, message_content, message_id, message_ordinal, message_role,
)

def build_extraction_input(
    *,
    thread_id: UUID,
    messages: Sequence[object],
    root_ordinal: int,
) -> ExtractionInput:
    """Select only the case statement and user answers from persisted history.

    Assistant messages are used only as structural markers. Their content is
    never copied into the returned packet.
    """

    ordered = sorted(
        (message for message in messages if message_ordinal(message) is not None),
        key=lambda message: message_ordinal(message) or 0,
    )
    root = next(
        (
            message
            for message in ordered
            if message_ordinal(message) == root_ordinal
            and message_role(message) == "user"
        ),
        None,
    )
    if root is None:
        raise ValueError("the extraction root user message was not found")

    selected: list[ExtractionSourceMessage] = [
        ExtractionSourceMessage(
            message_id=message_id(root),
            ordinal=root_ordinal,
            source_type="user_case_statement",
            content=message_content(root),
        )
    ]
    clarification_seen = False
    for message in ordered:
        ordinal = message_ordinal(message)
        if ordinal is None or ordinal <= root_ordinal:
            continue
        role = message_role(message)
        if role == "assistant":
            clarification_seen = not is_terminal_assistant_message(message)
            continue
        if role == "user" and clarification_seen:
            selected.append(
                ExtractionSourceMessage(
                    message_id=message_id(message),
                    ordinal=ordinal,
                    source_type="clarification_answer",
                    content=message_content(message),
                )
            )

    return ExtractionInput(thread_id=thread_id, messages=selected)
