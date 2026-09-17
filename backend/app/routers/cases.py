"""Case aggregate HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.case_runs import CaseRunRead
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate
from app.schemas.chat import (
    CaseChatMessageResult,
    CaseChatRead,
    ChatMessageCreate,
    ChatMessageRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.cases import CaseService
from app.services.case_analysis.contracts import CaseAnalysisFailure
from app.services.chat.case_chat import (
    CaseChatError,
    ask_case,
    get_case_chat as get_case_chat_service,
    submit_case_followup_answer,
)
from app.services.workflow import process_case_run

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/{case_id}/chat", response_model=CaseChatRead, status_code=status.HTTP_200_OK)
async def get_case_chat(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await get_case_chat_service(db, case_id=case_id, user_id=user.id)
    except CaseChatError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail={"code": error.code, "message": error.message},
        ) from error


@router.post(
    "/{case_id}/chat/messages",
    response_model=CaseChatMessageResult,
    status_code=status.HTTP_200_OK,
)
async def create_case_chat_message(
    case_id: UUID,
    request: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await commit_dependency_transaction(db)
    try:
        if request.intent == "followup_answer":
            async with db.begin():
                message, assistant_message, reply_message, run = await submit_case_followup_answer(
                    db,
                    case_id=case_id,
                    user_id=user.id,
                    request=request,
                )
                result = CaseChatMessageResult(
                    message=ChatMessageRead.model_validate(message),
                    assistant_message=(
                        ChatMessageRead.model_validate(assistant_message)
                        if assistant_message is not None
                        else None
                    ),
                    reply_message=(
                        ChatMessageRead.model_validate(reply_message)
                        if reply_message is not None
                        else None
                    ),
                    run=CaseRunRead.model_validate(run) if run is not None else None,
                )
            if result.run is not None:
                background_tasks.add_task(process_case_run, result.run.id)
            return result
        else:
            user_read, assistant_read = await ask_case(
                db,
                case_id=case_id,
                user_id=user.id,
                request=request,
            )
            return CaseChatMessageResult(
                message=user_read,
                assistant_message=assistant_read,
                run=None,
            )
    except CaseChatError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail={"code": error.code, "message": error.message},
        ) from error
    except CaseAnalysisFailure as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": error.code, "message": error.message},
        ) from error
    except TimeoutError as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "chat_answer_timeout", "message": "Chat answer generation timed out"},
        ) from error


@router.get("", response_model=list[CaseRead], status_code=status.HTTP_200_OK)
async def list_cases(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).list_cases(user_id=user.id)


@router.get("/{case_id}", response_model=CaseRead, status_code=status.HTTP_200_OK)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).get_case(case_id, user_id=user.id)


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    request: CaseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).create_case(request, user_id=user.id)


@router.patch("/{case_id}", response_model=CaseRead, status_code=status.HTTP_200_OK)
async def update_case(
    case_id: UUID,
    request: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).update_case(case_id, request, user_id=user.id)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    await CaseService(db).delete_case(case_id, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
