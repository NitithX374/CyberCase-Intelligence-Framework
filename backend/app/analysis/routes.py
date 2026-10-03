from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.latest import get_latest_case_analysis
from app.analysis.run import AnalysisStep, run_case_analysis
from app.analysis.schemas import AnalysisStepRead, CaseAnalysisResultRead
from app.analysis.stream import STREAMED_RESPONSE, progress_response, wants_progress
from app.auth.guard import get_current_user
from app.cases.running import sole_analysis
from app.cases.service import analysis_freshness
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/cases/{case_id}", tags=["case-analysis"])


def analysis_step_read(step: AnalysisStep) -> AnalysisStepRead:
    if step.needs_followup:
        return AnalysisStepRead(status="need_followup")
    return AnalysisStepRead(
        status="completed",
        result=CaseAnalysisResultRead.model_validate(step.result).model_copy(
            update={"freshness": "current"}
        ),
    )


@router.post("/analysis", response_model=AnalysisStepRead, responses=STREAMED_RESPONSE)
async def analyse_case(
    case_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
):
    async def analyse() -> AnalysisStepRead:
        with sole_analysis(case_id):
            return analysis_step_read(await run_case_analysis(case_id=case_id, user_id=user.id))

    if wants_progress(request):
        return progress_response(analyse)
    return await analyse()


@router.get("/analysis", response_model=CaseAnalysisResultRead | None)
async def get_latest_analysis(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case, result = await get_latest_case_analysis(db, case_id=case_id, user_id=user.id)
    if result is None:
        return None
    return CaseAnalysisResultRead.model_validate(result).model_copy(
        update={"freshness": analysis_freshness(case, result)}
    )


__all__ = ["analysis_step_read", "router"]
