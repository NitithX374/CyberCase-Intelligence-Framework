from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage
from app.services.analysis.technical_context_contracts import CaseRagContextPayload
from app.services.sources.case_source_bundle import CaseSourceBundle
from app.trace.claims import CaseFollowupExchange


@dataclass(frozen=True)
class CaseUnderAnalysis:
    case_id: UUID
    source_bundle: CaseSourceBundle
    followup_history: tuple[CaseFollowupExchange, ...] = ()
    reused_context: CaseRagContextPayload | None = None
    asked_gap_keys: frozenset[str] = frozenset()
    rounds_spent: int = 1

    @property
    def source_revision(self) -> int:
        return self.source_bundle.revision


async def next_ordinal(db: AsyncSession, case_id: UUID) -> int:
    highest = await db.scalar(
        select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
            ChatMessage.case_id == case_id
        )
    )
    return int(highest) + 1


__all__ = [
    "CaseUnderAnalysis",
    "next_ordinal",
]
