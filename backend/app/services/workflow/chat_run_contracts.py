from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.followup.schemas import ClarificationExchange


RUN_LEASE_DURATION = timedelta(minutes=6)


@dataclass(frozen=True)
class ClaimedChatRun:
    id: UUID
    thread_id: UUID
    request_message_id: UUID
    content: str
    action: str
    raw_evidence: str
    evidence_sha256: str
    source_message_ids: tuple[UUID, ...]
    evidence_sources: tuple[RawEvidenceSource, ...]
    document_source_context: tuple[dict[str, object], ...]
    original_user_content: str
    clarification_exchanges: tuple[ClarificationExchange, ...]
    followup_root_ordinal: int
    analysis_context: dict[str, object] | None = None


__all__ = ["ClaimedChatRun", "RUN_LEASE_DURATION"]
