"""Chat thread, message, and report HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageAccepted,
    ChatMessageCreate,
    ChatRunRead,
    ChatThreadCreate,
    ChatThreadDetail,
    ChatThreadRead,
    ChatThreadUpdate,
)
from app.schemas.reports import (
    ChatReportCreate,
    ChatReportRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.chat import (
    ChatMessageService,
    ChatService,
)
from app.services.reports import (
    ReportGenerationError,
    ReportService,
)
from app.services.workflow import process_chat_run

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get(
    "",
    response_model=list[ChatThreadRead],
    status_code=status.HTTP_200_OK,
)
async def list_chat_threads(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.list_threads(user_id=user.id)


@router.get(
    "/{thread_id}",
    response_model=ChatThreadDetail,
    status_code=status.HTTP_200_OK,
)
async def get_chat_thread(
    thread_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.get_thread(thread_id, user_id=user.id)


@router.post(
    "",
    response_model=ChatThreadRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_thread(
    request: ChatThreadCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.create_thread(request, user_id=user.id)


@router.patch(
    "/{thread_id}",
    response_model=ChatThreadRead,
    status_code=status.HTTP_200_OK,
)
async def update_chat_thread(
    thread_id: UUID,
    request: ChatThreadUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.update_thread(
        thread_id, request, user_id=user.id
    )


@router.delete(
    "/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat_thread(
    thread_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    service = ChatService(db)
    await service.delete_thread(thread_id, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{thread_id}/messages",
    response_model=ChatMessageAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_chat_message(
    thread_id: UUID,
    request: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    await chat_service.get_thread(thread_id, user_id=user.id)
    service = ChatMessageService(db)
    await db.commit()
    message, run = await service.create_message_and_run(thread_id, request)
    background_tasks.add_task(process_chat_run, run.id)
    return ChatMessageAccepted(
        message=message,
        run=run,
    )


@router.get(
    "/{thread_id}/runs/{run_id}",
    response_model=ChatRunRead,
    status_code=status.HTTP_200_OK,
)
async def get_chat_run(
    thread_id: UUID,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    await chat_service.get_thread(thread_id, user_id=user.id)
    service = ChatMessageService(db)
    return await service.get_run(thread_id, run_id)


def _report_http_exception(error: ReportGenerationError) -> HTTPException:
    status_code = (
        status.HTTP_404_NOT_FOUND
        if "not found" in error.message.lower()
        else status.HTTP_409_CONFLICT
    )
    return HTTPException(
        status_code=status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.post(
    "/{thread_id}/reports",
    response_model=ChatReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate_chat_report(
    thread_id: UUID,
    request: ChatReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    await chat_service.get_thread(thread_id, user_id=user.id)
    service = ReportService(db)
    try:
        await db.commit()
        return await service.generate_report(thread_id, request)
    except ReportGenerationError as error:
        raise _report_http_exception(error) from error


@router.get(
    "/{thread_id}/reports",
    response_model=list[ChatReportRead],
    status_code=status.HTTP_200_OK,
)
async def list_chat_reports(
    thread_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    await chat_service.get_thread(thread_id, user_id=user.id)
    service = ReportService(db)
    try:
        return await service.list_reports(thread_id)
    except ReportGenerationError as error:
        raise _report_http_exception(error) from error


@router.get(
    "/{thread_id}/reports/{report_id}",
    response_model=ChatReportRead,
    status_code=status.HTTP_200_OK,
)
async def get_chat_report(
    thread_id: UUID,
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    await chat_service.get_thread(thread_id, user_id=user.id)
    service = ReportService(db)
    try:
        return await service.get_report(thread_id, report_id)
    except ReportGenerationError as error:
        raise _report_http_exception(error) from error


@router.get(
    "/{thread_id}/reports/{report_id}/pdf",
    response_class=Response,
    status_code=status.HTTP_200_OK,
)
async def download_chat_report_pdf(
    thread_id: UUID,
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat_service = ChatService(db)
    await chat_service.get_thread(thread_id, user_id=user.id)
    service = ReportService(db)
    try:
        content, filename = await service.get_report_pdf(thread_id, report_id)
    except ReportGenerationError as error:
        raise _report_http_exception(error) from error
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
