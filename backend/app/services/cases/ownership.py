from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import LoaderOption

from app.errors import AppError
from app.models.case import Case


async def owned_case(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
    *,
    lock: bool = False,
    options: Sequence[LoaderOption] = (),
) -> Case:
    statement = select(Case).options(*options).where(Case.id == case_id)
    if lock:
        statement = statement.with_for_update()
    case = await db.scalar(statement)
    if case is None or case.user_id != user_id:
        raise AppError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


__all__ = ["owned_case"]
