from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.latest import get_latest_case_analysis
from app.analysis.run import AnalysisStep, run_case_analysis
from app.analysis.schemas import AnalysisStepRead, CaseAnalysisResultRead
from app.auth.guard import get_current_user
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


@router.post("/analysis", response_model=AnalysisStepRead)
async def analyse_case(
    case_id: UUID,
    user: User = Depends(get_current_user),
):
    step = await run_case_analysis(case_id=case_id, user_id=user.id)
    return analysis_step_read(step)


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
