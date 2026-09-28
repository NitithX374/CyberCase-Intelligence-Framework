from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.stream import STREAMED_RESPONSE, progress_response, wants_progress
from app.auth.guard import get_current_user
from app.chat.reply import get_case_chat as get_case_chat_service
from app.chat.reply import send_case_message
from app.chat.schemas import CaseChatRead, CaseChatResponse, ChatMessageCreate
from app.database import get_db
from app.models.user import User

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
    responses=STREAMED_RESPONSE,
)
async def create_case_chat_message(
    case_id: UUID,
    request: ChatMessageCreate,
    http_request: Request,
    user: User = Depends(get_current_user),
):
    async def send() -> CaseChatResponse:
        return await send_case_message(case_id=case_id, user_id=user.id, request=request)

    if wants_progress(http_request):
        return progress_response(send)
    return await send()


__all__ = ["router"]
