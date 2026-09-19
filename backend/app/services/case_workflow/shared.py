"""What both halves of the workflow hold in common.

The error they raise, the snapshot an analysis is taken from, and the two small
queries that every write needs: whose case this is, and where the next message
goes in the order.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.chat import ChatMessage
from app.services.sources import CaseSourceBundle


class CaseWorkflowError(Exception):
    def __init__(
        self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class CaseUnderAnalysis:
    """What one analysis reads, captured before the connection is released."""

    case_id: UUID
    source_bundle: CaseSourceBundle

    @property
    def source_revision(self) -> int:
        """The revision the bundle was read at, which the store must still find."""

        return self.source_bundle.revision


async def owned_case(db: AsyncSession, case_id: UUID, user_id: UUID | None) -> Case:
    case = await db.scalar(select(Case).where(Case.id == case_id).with_for_update())
    if case is None or case.user_id != user_id:
        raise CaseWorkflowError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


async def next_ordinal(db: AsyncSession, case_id: UUID) -> int:
    highest = await db.scalar(
        select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
            ChatMessage.case_id == case_id
        )
    )
    return int(highest) + 1


__all__ = [
    "CaseUnderAnalysis",
    "CaseWorkflowError",
    "next_ordinal",
    "owned_case",
]
