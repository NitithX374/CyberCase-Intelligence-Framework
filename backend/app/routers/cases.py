"""Case aggregate HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate
from app.schemas.chat import (
    CaseChatMessageAccepted,
    ChatMessageCreate,
    ChatRunRead,
    ChatThreadDetail,
    ChatThreadRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.cases import CaseService
from app.services.chat import (
    CaseChatError,
    ChatMessageService,
    ChatService,
    createCaseChatMessageAndRun,
)
from app.services.workflow import process_case_run

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/{case_id}/chat", response_model=ChatThreadRead, status_code=status.HTTP_200_OK)
async def ensure_case_chat(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ChatService(db).ensure_thread_for_case(case_id, user_id=user.id)


@router.get("/{case_id}/chat", response_model=ChatThreadDetail, status_code=status.HTTP_200_OK)
async def get_case_chat(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    thread = await chat_service.ensure_thread_for_case(case_id, user_id=user.id)
    return await chat_service.get_thread(thread.id, user_id=user.id)


@router.post(
    "/{case_id}/chat/messages",
    response_model=CaseChatMessageAccepted,
    status_code=status.HTTP_202_ACCEPTED,
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
        async with db.begin():
            message, run = await createCaseChatMessageAndRun(
                db,
                case_id=case_id,
                user_id=user.id,
                request=request,
            )
    except CaseChatError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail={"code": error.code, "message": error.message},
        ) from error
    background_tasks.add_task(process_case_run, run.id)
    return CaseChatMessageAccepted(message=message, run=run)


@router.get(
    "/{case_id}/chat/runs/{run_id}",
    response_model=ChatRunRead,
    status_code=status.HTTP_200_OK,
)
async def get_case_chat_run(
    case_id: UUID,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    thread = await chat_service.ensure_thread_for_case(case_id, user_id=user.id)
    service = ChatMessageService(db)
    return await service.get_run(thread.id, run_id)


@router.get("", response_model=list[CaseRead], status_code=status.HTTP_200_OK)
async def list_cases(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).listCases(user_id=user.id)


@router.get("/{case_id}", response_model=CaseRead, status_code=status.HTTP_200_OK)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).getCase(case_id, user_id=user.id)


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    request: CaseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).createCase(request, user_id=user.id)


@router.patch("/{case_id}", response_model=CaseRead, status_code=status.HTTP_200_OK)
async def update_case(
    case_id: UUID,
    request: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseService(db).updateCase(case_id, request, user_id=user.id)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    await CaseService(db).deleteCase(case_id, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
