from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.analysis import CaseAnalysisResultRead
from app.schemas.chat import CaseChatRead, CaseChatResponse, ChatMessageCreate, ChatMessageRead
from app.services.auth.dependencies import get_current_user
from app.services.chat.case_chat import get_case_chat as get_case_chat_service
from app.services.chat.case_chat import post_case_message

router = APIRouter(prefix="/cases/{case_id}/chat", tags=["case-chat"])


@router.get("", response_model=CaseChatRead, status_code=status.HTTP_200_OK)
async def get_case_chat(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_case_chat_service(db, case_id=case_id, user_id=user.id)


@router.post(
    "/messages",
    response_model=CaseChatResponse,
    status_code=status.HTTP_200_OK,
)
async def create_case_chat_message(
    case_id: UUID,
    request: ChatMessageCreate,
    user: User = Depends(get_current_user),
):
    messages, step = await post_case_message(case_id=case_id, user_id=user.id, request=request)
    finished = step.result if step is not None and not step.needs_followup else None
    return CaseChatResponse(
        messages=[ChatMessageRead.model_validate(message) for message in messages],
        analysis=(
            CaseAnalysisResultRead.model_validate(finished).model_copy(
                update={"freshness": "current"}
            )
            if finished is not None
            else None
        ),
    )


__all__ = ["router"]
