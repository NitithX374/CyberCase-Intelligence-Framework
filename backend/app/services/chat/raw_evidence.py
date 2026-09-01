from __future__ import annotations

import hashlib
from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage


@dataclass(frozen=True)
class RawEvidenceSource:
    message_id: UUID
    content: str
    document_sources: tuple[dict[str, object], ...] = ()


@dataclass(frozen=True)
class RawEvidenceSnapshot:
    text: str
    sources: tuple[RawEvidenceSource, ...]
    sha256: str

    @property
    def source_message_ids(self) -> tuple[UUID, ...]:
        return tuple(source.message_id for source in self.sources)

    @property
    def document_source_context(self) -> tuple[dict[str, object], ...]:
        return tuple(
            {
                "source_message_id": str(source.message_id),
                "documents": [deepcopy(value) for value in source.document_sources],
            }
            for source in self.sources
            if source.document_sources
        )


def build_raw_evidence_snapshot(messages: list[ChatMessage]) -> RawEvidenceSnapshot:
    user_messages = sorted(
        (message for message in messages if message.role == "user"),
        key=lambda message: message.ordinal,
    )
    sections: list[str] = []
    sources: list[RawEvidenceSource] = []
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
        raw_documents = message.metadata_json.get("document_sources", [])
        if not isinstance(raw_documents, list):
            raw_documents = []
        document_sources = tuple(
            deepcopy(value)
            for value in raw_documents
            if isinstance(value, dict)
        )
        sources.append(
            RawEvidenceSource(
                message_id=message.id,
                content=content,
                document_sources=document_sources,
            )
        )
    text = "\n\n".join(sections)
    return RawEvidenceSnapshot(
        text=text,
        sources=tuple(sources),
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
    "RawEvidenceSource",
    "build_raw_evidence_snapshot",
    "load_raw_evidence_snapshot",
]
