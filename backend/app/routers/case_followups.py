from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.case_followups import (
    CaseFollowUpRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.followup.case_followup import (
    CaseFollowUpError,
    get_case_followups,
)

router = APIRouter(prefix="/cases/{case_id}/followups", tags=["case-followups"])


def followup_http_error(error: CaseFollowUpError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.get("", response_model=list[CaseFollowUpRead])
async def list_case_followups(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await get_case_followups(db, case_id=case_id, user_id=user.id)
    except CaseFollowUpError as error:
        raise followup_http_error(error) from error


__all__ = ["router"]
