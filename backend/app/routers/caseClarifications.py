from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.caseClarifications import (
    CaseClarificationAccepted,
    CaseClarificationAnswer,
    CaseClarificationRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.followup.caseClarification import (
    CaseClarificationError,
    get_owned_clarifications,
    submit_clarification_answer,
)
from app.services.workflow import process_case_run

router = APIRouter(prefix="/cases/{case_id}/clarifications", tags=["case-clarifications"])


def _clarification_http_error(error: CaseClarificationError) -> HTTPException:
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
        raise _clarification_http_error(error) from error


@router.post(
    "/{clarification_id}/answers",
    response_model=CaseClarificationAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def answer_case_clarification(
    case_id: UUID,
    clarification_id: UUID,
    request: CaseClarificationAnswer,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            clarification, run = await submit_clarification_answer(
                db,
                case_id=case_id,
                clarification_id=clarification_id,
                user_id=user.id,
                request=request,
            )
    except CaseClarificationError as error:
        raise _clarification_http_error(error) from error
    background_tasks.add_task(process_case_run, run.id)
    return CaseClarificationAccepted(clarification=clarification, run=run)


__all__ = ["router"]
