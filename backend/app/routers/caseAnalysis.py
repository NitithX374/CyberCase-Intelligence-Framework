from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.caseRuns import (
    CaseAnalysisAccepted,
    CaseAnalysisCreate,
    CaseAnalysisResultRead,
    CaseRunRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.case_materials import CaseMaterialsError
from app.services.workflow.caseRunService import (
    CaseRunError,
    analysis_freshness,
    enqueue_case_analysis,
    get_case_analysis_result,
    get_latest_case_analysis,
    get_owned_case_run,
    list_case_analysis_results,
)
from app.services.workflow import process_case_run

router = APIRouter(prefix="/cases/{case_id}", tags=["case-analysis"])


def _case_run_http_error(error: CaseRunError | CaseMaterialsError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.post("/analysis", response_model=CaseAnalysisAccepted, status_code=status.HTTP_202_ACCEPTED)
async def start_case_analysis(
    case_id: UUID,
    request: CaseAnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await commit_dependency_transaction(db)
        async with db.begin():
            run = await enqueue_case_analysis(
                db,
                case_id=case_id,
                user_id=user.id,
                request=request,
            )
            await db.flush()
            await db.refresh(run)
    except (CaseRunError, CaseMaterialsError) as error:
        raise _case_run_http_error(error) from error
    background_tasks.add_task(process_case_run, run.id)
    return CaseAnalysisAccepted(run=run)


@router.get("/analysis", response_model=CaseAnalysisResultRead | None)
async def get_latest_analysis(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        case, result = await get_latest_case_analysis(
            db,
            case_id=case_id,
            user_id=user.id,
        )
    except CaseRunError as error:
        raise _case_run_http_error(error) from error
    if result is None:
        return None
    payload = CaseAnalysisResultRead.model_validate(result)
    return payload.model_copy(update={"freshness": analysis_freshness(case, result)})


@router.get("/analysis/results", response_model=list[CaseAnalysisResultRead])
async def list_analysis_results(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        case, results = await list_case_analysis_results(
            db,
            case_id=case_id,
            user_id=user.id,
        )
    except CaseRunError as error:
        raise _case_run_http_error(error) from error
    return [
        CaseAnalysisResultRead.model_validate(result).model_copy(
            update={"freshness": analysis_freshness(case, result)}
        )
        for result in results
    ]


@router.get("/analysis/results/{result_id}", response_model=CaseAnalysisResultRead)
async def get_analysis_result(
    case_id: UUID,
    result_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        case, result = await get_case_analysis_result(
            db,
            case_id=case_id,
            result_id=result_id,
            user_id=user.id,
        )
    except CaseRunError as error:
        raise _case_run_http_error(error) from error
    payload = CaseAnalysisResultRead.model_validate(result)
    return payload.model_copy(update={"freshness": analysis_freshness(case, result)})


@router.get("/runs/{run_id}", response_model=CaseRunRead)
async def get_case_run(
    case_id: UUID,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        run = await get_owned_case_run(
            db,
            case_id=case_id,
            run_id=run_id,
            user_id=user.id,
        )
    except CaseRunError as error:
        raise _case_run_http_error(error) from error
    return run


__all__ = ["router"]
