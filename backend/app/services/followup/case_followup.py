"""Read-only Case follow-up history service."""

from __future__ import annotations

from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_materials import CaseSource
from app.models.case_run import CaseAnalysisResult
from app.models.chat import ChatMessage
from app.schemas.case_followups import (
    CaseFollowUpRead,
    FollowUpState,
)


class CaseFollowUpError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_409_CONFLICT,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class CaseFollowUpHistoryError(CaseFollowUpError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message)


async def owned_case(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
    *,
    lock: bool = False,
) -> Case:
    statement = select(Case).where(Case.id == case_id)
    if lock:
        statement = statement.with_for_update()
    case = await db.scalar(statement)
    if case is None or case.user_id != user_id:
        raise CaseFollowUpError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


async def get_case_followups(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None = None,
) -> list[CaseFollowUpRead]:
    case = await owned_case(db, case_id, user_id)
    question_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case.id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
        .order_by(ChatMessage.created_at, ChatMessage.ordinal)
    )
    question_messages = list(question_result.scalars().all())
    if not question_messages:
        return []

    answer_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case.id,
            ChatMessage.role == "user",
            ChatMessage.message_kind == "followup_answer",
        )
        .order_by(ChatMessage.ordinal)
    )
    answer_messages = list(answer_result.scalars().all())
    answer_source_by_message_id = await answer_sources_by_message_id(db, answer_messages)
    followups: list[CaseFollowUpRead] = []

    for question_message in question_messages:
        origin_result_id = question_message.analysis_result_id
        if origin_result_id is None:
            raise CaseFollowUpHistoryError(
                "followup_context_invalid",
                "Follow-up question has no pinned analysis result",
            )
        origin_result = await db.get(CaseAnalysisResult, origin_result_id)
        if origin_result is None or origin_result.case_id != case.id:
            raise CaseFollowUpHistoryError(
                "followup_context_invalid",
                "Follow-up question has an invalid analysis result",
            )

        metadata = (
            question_message.metadata_json
            if isinstance(question_message.metadata_json, dict)
            else {}
        )
        gap = followup_gap(metadata)
        if gap is None:
            raise CaseFollowUpHistoryError(
                "followup_context_invalid",
                "Follow-up question has no follow-up gap",
            )
        answer_message = next(
            (
                answer
                for answer in answer_messages
                if answer.in_reply_to_message_id == question_message.id
            ),
            None,
        )
        complete = (
            answer_message is not None
            and answered_gap_id(answer_message) == str(gap.get("gap_id"))
        )
        if complete:
            state: FollowUpState = "answered"
        else:
            state = (
                "superseded"
                if case.latest_analysis_result_id
                and case.latest_analysis_result_id != origin_result_id
                else "pending"
            )
        answered_at = (
            answer_message.created_at if complete and answer_message else None
        )
        followups.append(
            CaseFollowUpRead(
                id=question_message.id,
                case_id=case.id,
                origin_analysis_result_id=origin_result_id,
                gap_key=str(gap.get("gap_key") or ""),
                gap_id=str(gap.get("gap_id") or ""),
                topic=str(gap.get("topic") or ""),
                question=question_message.content,
                metadata_json=metadata,
                state=state,
                answer_evidence_source_id=(
                    answer_source_by_message_id.get(answer_message.id)
                    if complete and answer_message
                    else None
                ),
                question_message_id=question_message.id,
                answer_message_id=(
                    answer_message.id if complete and answer_message else None
                ),
                answer_fingerprint=None,
                answered_at=answered_at,
                created_at=question_message.created_at,
                updated_at=answered_at or question_message.created_at,
            )
        )
    return followups

def followup_gap(metadata: dict[str, object]) -> dict[str, object] | None:
    followup = metadata.get("chat_followup")
    gap = followup.get("gap") if isinstance(followup, dict) else None
    return dict(gap) if isinstance(gap, dict) else None


def answered_gap_id(message: ChatMessage) -> str | None:
    followup = message.metadata_json.get("chat_followup") if isinstance(message.metadata_json, dict) else None
    answer = followup.get("answer") if isinstance(followup, dict) else None
    if not isinstance(answer, dict) or answer.get("disposition") not in {"answered", "unavailable", "skipped"}:
        return None
    gap_id = answer.get("gap_id")
    return str(gap_id) if gap_id else None


async def answer_sources_by_message_id(
    db: AsyncSession,
    answer_messages: list[ChatMessage],
) -> dict[UUID, UUID]:
    message_ids = [message.id for message in answer_messages]
    if not message_ids:
        return {}
    result = await db.execute(
        select(CaseSource).where(CaseSource.origin_message_id.in_(message_ids))
    )
    sources: dict[UUID, UUID] = {}
    for source in result.scalars().all():
        if source.origin_message_id is not None:
            sources.setdefault(source.origin_message_id, source.id)
    return sources


__all__ = [
    "CaseFollowUpError",
    "CaseFollowUpHistoryError",
    "get_case_followups",
    "owned_case",
]
