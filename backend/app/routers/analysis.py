from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.analysis import (
    AnalysisStepRead,
    CaseAnalysisCreate,
    CaseAnalysisResultRead,
    FollowupQuestionRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.workflow.run_analysis import (
    AnalysisStep,
    analysis_freshness,
    get_latest_case_analysis,
    run_case_analysis,
)

router = APIRouter(prefix="/cases/{case_id}", tags=["case-analysis"])


def analysis_step_read(step: AnalysisStep) -> AnalysisStepRead:
    if step.question is not None and step.gap is not None:
        return AnalysisStepRead(
            status="need_followup",
            round=step.rounds_spent,
            max_rounds=settings.chat_followup_max_rounds,
            question=FollowupQuestionRead(
                message_id=step.question.id,
                gap_id=step.gap.gap_id,
                gap_key=step.gap.gap_key,
                question=step.question.content,
            ),
        )
    return AnalysisStepRead(
        status="completed",
        round=step.rounds_spent,
        max_rounds=settings.chat_followup_max_rounds,
        stop_reason=step.stop_reason,
        result=CaseAnalysisResultRead.model_validate(step.result).model_copy(
            update={"freshness": "current"}
        ),
    )


@router.post("/analysis", response_model=AnalysisStepRead)
async def analyse_case(
    case_id: UUID,
    request: CaseAnalysisCreate,
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
