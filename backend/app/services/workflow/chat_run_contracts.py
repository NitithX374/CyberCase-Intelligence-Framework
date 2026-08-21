from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import UUID

from app.services.extraction.llm_extraction import ExtractionInput
from app.services.followup.schemas import ClarificationExchange

RUN_LEASE_DURATION = timedelta(minutes=6)

def is_no_change_case_update(metadata: dict[str, Any]) -> bool:
    action = metadata.get("chat_action")
    return (
        isinstance(action, dict)
        and action.get("action") == "add_case_info"
        and action.get("status") == "no_change"
        and action.get("state_mutated") is False
    )

@dataclass(frozen=True)
class ClaimedChatRun:
    """Detached input needed after the claim transaction has closed."""

    id: UUID
    operation: str
    input_rag_session_id: str | None
    content: object
    rag_query: object
    original_user_content: object
    clarification_exchanges: tuple[ClarificationExchange, ...]
    followup_root_ordinal: int
    pending_question: str | None = None
    extraction_input: ExtractionInput | None = None
    post_answer_action: str | None = None
    clarification_answer: bool = False
    request_message_id: UUID | None = None
    case_state_version_id: UUID | None = None
    case_state_json: dict[str, object] | None = None
    analysis_context: dict[str, object] | None = None
    raw_case_narrative: str | None = None
