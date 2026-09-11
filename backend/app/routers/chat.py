"""Chat thread, message, and report HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import commit_dependency_transaction, get_db
from app.models.user import User
from app.schemas.chat import (
    CaseChatMessageAccepted,
    ChatCaseLinkRead,
    ChatMessageAccepted,
    ChatMessageCreate,
    ChatRunRead,
    ChatThreadCreate,
    ChatThreadDetail,
    ChatThreadRead,
    ChatThreadUpdate,
)
from app.schemas.reports import (
    CaseReportCreate,
    ChatReportCreate,
    ChatReportRead,
)
from app.services.auth.dependencies import get_current_user
from app.services.chat import (
    CaseChatError,
    ChatMessageService,
    ChatService,
    createCaseChatMessageAndRun,
)
from app.services.reports import (
    CaseReportService,
    ReportGenerationConflict,
    ReportGenerationError,
    ReportNotFound,
    ReportService,
    ReportServiceError,
)
from app.services.workflow import process_case_run

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
    "/{thread_id}/case-link",
    response_model=ChatCaseLinkRead,
    status_code=status.HTTP_200_OK,
)
async def get_chat_case_link(
    thread_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ChatService(db).get_case_link(thread_id, user_id=user.id)


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
    response_model=CaseChatMessageAccepted | ChatMessageAccepted,
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
    thread = await chat_service.get_thread(thread_id, user_id=user.id)
    if thread.case is not None:
        await commit_dependency_transaction(db)
        try:
            async with db.begin():
                message, run = await createCaseChatMessageAndRun(
                    db,
                    case_id=thread.case.id,
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
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail={
            "code": "legacy_chat_execution_retired",
            "message": (
                "This historical Chat thread is read-only. "
                "Create or open a Case to start new analysis."
            ),
        },
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
    thread = await chat_service.get_thread(thread_id, user_id=user.id)
    if thread.case_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat thread is not linked to a case. Reports require a case.",
        )
    service = CaseReportService(db)
    try:
        await db.commit()
        return await service.generate_report(
            thread.case_id,
            CaseReportCreate(idempotency_key=request.idempotency_key),
        )
    except ReportServiceError as error:
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
    thread = await chat_service.get_thread(thread_id, user_id=user.id)
    if thread.case_id is None:
        return []
    service = CaseReportService(db)
    try:
        return await service.list_reports(thread.case_id)
    except ReportServiceError as error:
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
    thread = await chat_service.get_thread(thread_id, user_id=user.id)
    if thread.case_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    service = CaseReportService(db)
    try:
        return await service.get_report(thread.case_id, report_id)
    except ReportServiceError as error:
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
    thread = await chat_service.get_thread(thread_id, user_id=user.id)
    if thread.case_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    service = CaseReportService(db)
    try:
        content, filename = await service.get_report_pdf(thread.case_id, report_id)
    except ReportServiceError as error:
        raise _report_http_exception(error) from error
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
