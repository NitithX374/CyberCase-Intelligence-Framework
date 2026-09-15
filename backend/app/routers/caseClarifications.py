from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.caseClarifications import (
    CaseClarificationRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.followup.caseClarification import (
    CaseClarificationError,
    get_owned_clarifications,
)

router = APIRouter(prefix="/cases/{case_id}/clarifications", tags=["case-clarifications"])


def clarification_http_error(error: CaseClarificationError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.get("", response_model=list[CaseClarificationRead])
async def list_case_clarifications(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await get_owned_clarifications(db, case_id=case_id, user_id=user.id)
    except CaseClarificationError as error:
        raise clarification_http_error(error) from error


__all__ = ["router"]
