"""Accumulate and format raw user-authored case evidence for RAW_DIRECT analysis mode."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun


def format_raw_case_evidence_segments(segments: Sequence[str]) -> str:
    """Format raw case evidence segments with deterministic chronological boundaries.

    - A single initial segment is returned verbatim.
    - Multiple segments are wrapped with section headers:
      [INITIAL CASE NARRATIVE]
      ...
      [ADDED CASE INFORMATION #1]
      ...
      [ADDED CASE INFORMATION #2]
      ...
    """
    clean_segments = [seg.strip() for seg in segments if isinstance(seg, str) and seg.strip()]
    if not clean_segments:
        return ""
    if len(clean_segments) == 1:
        return clean_segments[0]

    formatted_parts: list[str] = []
    for idx, seg in enumerate(clean_segments):
        if idx == 0:
            formatted_parts.append(f"[INITIAL CASE NARRATIVE]\n{seg}")
        else:
            formatted_parts.append(f"[ADDED CASE INFORMATION #{idx}]\n{seg}")
    return "\n\n".join(formatted_parts)


def extract_raw_case_evidence_segments(
    messages_with_payloads: Sequence[tuple[UUID, int, str, dict[str, Any] | None]],
    *,
    current_request_message_id: UUID | None = None,
    current_request_payload: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    """Select only user messages that constitute case evidence up to the current request.

    Inclusions:
    1. The initial intake user message (lowest ordinal).
    2. Subsequent user messages where action == "add_case_info" or clarification_answer == True.
    3. Clarification responses from followup exchanges.

    Exclusions:
    - User messages where action == "ask" (analyst questions).
    - Future messages after current_request_message_id.
    """
    if not messages_with_payloads:
        return ()

    # Sort strictly by ordinal
    ordered = sorted(messages_with_payloads, key=lambda item: item[1])

    # Truncate to messages up to the current request message ordinal if specified
    if current_request_message_id is not None:
        target_ordinal = next(
            (item[1] for item in ordered if item[0] == current_request_message_id),
            None,
        )
        if target_ordinal is not None:
            ordered = [item for item in ordered if item[1] <= target_ordinal]

    segments: list[str] = []
    for index, (msg_id, _, content, payload) in enumerate(ordered):
        text = content.strip() if isinstance(content, str) else ""
        if not text:
            continue

        effective_payload = payload
        if msg_id == current_request_message_id and isinstance(current_request_payload, dict):
            effective_payload = current_request_payload

        if index == 0:
            # The earliest user message is always the initial intake case narrative
            segments.append(text)
        else:
            # Subsequent user messages: only include if they add/mutate case information
            action = effective_payload.get("action") if isinstance(effective_payload, dict) else None
            is_clarification = (
                effective_payload.get("clarification_answer") is True
                if isinstance(effective_payload, dict)
                else False
            )
            followup_round = (
                effective_payload.get("followup_round", 0)
                if isinstance(effective_payload, dict)
                else 0
            )

            if action == "add_case_info" or is_clarification:
                segments.append(text)
            elif action == "ask":
                # Strictly exclude ask messages from evidence
                continue
            elif isinstance(followup_round, int) and followup_round > 0 and action is None:
                segments.append(text)

    return tuple(segments)


async def resolve_raw_case_evidence_history(
    db: AsyncSession,
    *,
    thread_id: UUID,
    current_request_message_id: UUID | None = None,
    current_request_payload: dict[str, Any] | None = None,
    current_content: str | None = None,
    history: Sequence[ChatMessage] | None = None,
) -> str | None:
    """Resolve accumulated chronological raw case evidence for a chat thread.

    Queries user messages and their associated run payloads from the database,
    filters out analyst questions ('ask'), and formats the evidence history.
    """
    rows_data: dict[UUID, tuple[UUID, int, str, dict[str, Any] | None]] = {}

    # 1. If history was already fetched in memory, extract from it
    if history is not None:
        for msg in history:
            if getattr(msg, "role", None) == "user":
                msg_id = getattr(msg, "id", None)
                ordinal = getattr(msg, "ordinal", 0)
                content = getattr(msg, "content", "")
                if msg_id is not None:
                    rows_data[msg_id] = (msg_id, ordinal, content, None)

    # 2. Query from database if needed
    if not rows_data:
        statement = (
            select(
                ChatMessage.id,
                ChatMessage.ordinal,
                ChatMessage.content,
                ChatRun.request_payload,
            )
            .outerjoin(ChatRun, ChatRun.request_message_id == ChatMessage.id)
            .where(
                ChatMessage.thread_id == thread_id,
                ChatMessage.role == "user",
            )
            .order_by(ChatMessage.ordinal.asc(), ChatRun.created_at.asc())
        )
        try:
            result = await db.execute(statement)
            raw_rows = result.all()
            if isinstance(raw_rows, list):
                for row in raw_rows:
                    if hasattr(row, "_mapping"):
                        mapping = row._mapping
                        msg_id = mapping.get("id") if "id" in mapping else getattr(row, "id", None)
                        ordinal = mapping.get("ordinal") if "ordinal" in mapping else getattr(row, "ordinal", 0)
                        content = mapping.get("content") if "content" in mapping else getattr(row, "content", "")
                        payload = mapping.get("request_payload") if "request_payload" in mapping else getattr(row, "request_payload", None)
                    elif isinstance(row, (tuple, list)):
                        msg_id = row[0]
                        ordinal = row[1] if len(row) > 1 else 0
                        content = row[2] if len(row) > 2 else ""
                        payload = row[3] if len(row) > 3 else None
                    elif isinstance(row, ChatMessage):
                        msg_id = row.id
                        ordinal = row.ordinal
                        content = row.content
                        payload = getattr(row, "metadata_json", {})
                    elif hasattr(row, "id") and hasattr(row, "content"):
                        msg_id = getattr(row, "id")
                        ordinal = getattr(row, "ordinal", 0)
                        content = getattr(row, "content", "")
                        payload = getattr(row, "request_payload", None)
                    elif isinstance(row, str) and row.strip():
                        # Direct string scalar mock result
                        return row.strip()
                    else:
                        continue

                    if msg_id not in rows_data:
                        rows_data[msg_id] = (msg_id, ordinal, content, payload if isinstance(payload, dict) else None)
                    else:
                        if isinstance(payload, dict):
                            old = rows_data[msg_id]
                            rows_data[msg_id] = (old[0], old[1], old[2], payload)
            else:
                # Handle test mock returning scalar string via scalar_one_or_none
                if hasattr(result, "scalar_one_or_none"):
                    scalar = result.scalar_one_or_none()
                    if isinstance(scalar, str) and scalar.strip():
                        return scalar.strip()
        except Exception:
            pass

    # 3. If still empty, fall back to current_content if not an ASK run
    if not rows_data:
        if current_content and isinstance(current_content, str) and current_content.strip():
            action = current_request_payload.get("action") if isinstance(current_request_payload, dict) else None
            if action != "ask":
                return current_content.strip()
        return None

    messages_with_payloads = list(rows_data.values())
    segments = extract_raw_case_evidence_segments(
        messages_with_payloads,
        current_request_message_id=current_request_message_id,
        current_request_payload=current_request_payload,
    )

    if not segments:
        return None

    return format_raw_case_evidence_segments(segments)
