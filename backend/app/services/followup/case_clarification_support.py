from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.schemas.case_clarifications import CaseClarificationAnswer


class CaseClarificationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class CaseClarificationHistoryError(CaseClarificationError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message)


def answer_fingerprint(request: CaseClarificationAnswer) -> str:
    return f"{request.answer.strip()}:{request.response_language}"


async def owned_case(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
    *,
    lock: bool = False,
) -> Case:
    statement = select(Case).where(Case.id == case_id)
    if lock:
        statement = statement.with_for_update()
    case = await db.scalar(statement)
    if case is None or case.user_id != user_id:
        raise CaseClarificationError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


__all__ = [
    "CaseClarificationError",
    "CaseClarificationHistoryError",
    "answer_fingerprint",
    "owned_case",
]
