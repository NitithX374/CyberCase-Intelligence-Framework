from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage


@dataclass(frozen=True)
class RawEvidenceSnapshot:
    text: str
    source_message_ids: tuple[UUID, ...]
    sha256: str


def build_raw_evidence_snapshot(messages: list[ChatMessage]) -> RawEvidenceSnapshot:
    user_messages = sorted(
        (message for message in messages if message.role == "user"),
        key=lambda message: message.ordinal,
    )
    sections: list[str] = []
    source_message_ids: list[UUID] = []
    clarification_number = 0
    added_information_number = 0
    for index, message in enumerate(user_messages):
        content = message.content.strip()
        if not content:
            continue
        evidence_kind = message.metadata_json.get("evidence_kind")
        if index == 0:
            label = "INITIAL CASE NARRATIVE"
        elif evidence_kind == "clarification_answer":
            clarification_number += 1
            label = f"CLARIFICATION ANSWER #{clarification_number}"
        elif evidence_kind == "added_case_information":
            added_information_number += 1
            label = f"ADDED CASE INFORMATION #{added_information_number}"
        else:
            continue
        sections.append(f"[{label}]\n{content}")
        source_message_ids.append(message.id)
    text = "\n\n".join(sections)
    return RawEvidenceSnapshot(
        text=text,
        source_message_ids=tuple(source_message_ids),
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


async def load_raw_evidence_snapshot(
    db: AsyncSession,
    *,
    thread_id: UUID,
    through_ordinal: int | None = None,
) -> RawEvidenceSnapshot:
    statement = select(ChatMessage).where(
        ChatMessage.thread_id == thread_id,
        ChatMessage.role == "user",
    )
    if through_ordinal is not None:
        statement = statement.where(ChatMessage.ordinal <= through_ordinal)
    result = await db.execute(statement.order_by(ChatMessage.ordinal))
    return build_raw_evidence_snapshot(list(result.scalars().all()))


__all__ = [
    "RawEvidenceSnapshot",
    "build_raw_evidence_snapshot",
    "load_raw_evidence_snapshot",
]
