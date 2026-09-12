from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.caseRun import CaseRun
from app.models.chat import ChatMessage, ChatThread


THREAD_REFERENCE_CODE = "chat_thread_has_retained_runs"
THREAD_REFERENCE_MESSAGE = "Chat thread cannot be deleted while retained Case runs reference its messages"


async def delete_chat_thread(db: AsyncSession, thread: ChatThread) -> None:
    referenced_run_id = await db.scalar(
        select(CaseRun.id)
        .join(ChatMessage, CaseRun.request_message_id == ChatMessage.id)
        .where(ChatMessage.thread_id == thread.id)
        .limit(1)
    )
    if referenced_run_id is not None:
        await db.rollback()
        raise _thread_reference_error()

    try:
        await db.delete(thread)
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        if _is_thread_reference_violation(error):
            raise _thread_reference_error() from error
        raise


def _thread_reference_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": THREAD_REFERENCE_CODE, "message": THREAD_REFERENCE_MESSAGE},
    )


def _is_thread_reference_violation(error: IntegrityError) -> bool:
    candidates = (error, error.orig, getattr(error.orig, "__cause__", None))
    return any(
        getattr(candidate, "constraint_name", None) == "fk_case_runs_request_message_id"
        or getattr(getattr(candidate, "diag", None), "constraint_name", None)
        == "fk_case_runs_request_message_id"
        for candidate in candidates
    )


__all__ = ["THREAD_REFERENCE_CODE", "THREAD_REFERENCE_MESSAGE", "delete_chat_thread"]
