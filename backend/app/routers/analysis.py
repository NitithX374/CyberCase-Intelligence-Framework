"""Analysis endpoints. The analysis runs inside the request that asks for it."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.analysis import CaseAnalysisCreate, CaseAnalysisResultRead
from app.services.auth.dependencies import get_current_user
from app.services.case_workflow import (
    CaseWorkflowError,
    analysis_freshness,
    get_latest_case_analysis,
    run_case_analysis,
)

router = APIRouter(prefix="/cases/{case_id}", tags=["case-analysis"])


def workflow_http_error(error: CaseWorkflowError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.post("/analysis", response_model=CaseAnalysisResultRead)
async def analyse_case(
    case_id: UUID,
    request: CaseAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Analyse the case and return the result. This call is slow by nature."""

    await commit_dependency_transaction(db)
    try:
        result = await run_case_analysis(
            case_id=case_id,
            user_id=user.id,
            response_language=request.response_language,
        )
    except CaseWorkflowError as error:
        raise workflow_http_error(error) from error
    return CaseAnalysisResultRead.model_validate(result).model_copy(update={"freshness": "current"})


@router.get("/analysis", response_model=CaseAnalysisResultRead | None)
async def get_latest_analysis(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        case, result = await get_latest_case_analysis(db, case_id=case_id, user_id=user.id)
    except CaseWorkflowError as error:
        raise workflow_http_error(error) from error
    if result is None:
        return None
    return CaseAnalysisResultRead.model_validate(result).model_copy(
        update={"freshness": analysis_freshness(case, result)}
    )


__all__ = ["router"]
