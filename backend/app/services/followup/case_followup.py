"""Case follow-up persistence, history loading, and answer workflow service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_materials import CaseSource
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.schemas.case_followups import (
    CaseFollowUpAnswer,
    CaseFollowUpRead,
    FollowUpState,
)
from app.schemas.message_metadata import serialize_message_metadata
from app.services.followup.contracts import FollowUpExchange


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


async def load_followup_exchanges(
    db: AsyncSession,
    case_id: UUID,
) -> tuple[FollowUpExchange, ...]:
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case_id,
            ChatMessage.role == "user",
            ChatMessage.message_kind == "followup_answer",
        )
        .order_by(ChatMessage.ordinal)
    )
    answer_messages = list(result.scalars().all())
    exchanges: list[FollowUpExchange] = []
    for answer_message in answer_messages:
        question_message = await question_for_answer(db, case_id, answer_message)
        if question_message is None:
            continue
        gap = followup_gap(question_message.metadata_json)
        answer = followup_answer(answer_message.metadata_json)
        if gap is None or answer is None:
            continue
        round_number = followup_round(question_message.metadata_json)
        disposition = answer.get("disposition")
        if disposition not in {"answered", "unavailable", "skipped"}:
            continue
        exchanges.append(
            FollowUpExchange(
                question=str(gap.get("clarification_question") or question_message.content),
                answer=str(answer.get("answer") or ""),
                disposition=disposition,
                gap_id=str(gap.get("gap_id")),
                gap_topic=str(gap.get("topic") or ""),
                gap_key=str(gap.get("gap_key") or ""),
                question_message_id=str(question_message.id),
                answer_message_id=str(answer_message.id),
                round_number=round_number,
            )
        )
    return tuple(exchanges)




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




async def submit_followup_answer(
    db: AsyncSession,
    *,
    case_id: UUID,
    followup_id: UUID,
    user_id: UUID | None,
    answer: CaseFollowUpAnswer,
    idempotency_key: str,
    response_language: str,
) -> tuple[ChatMessage, CaseRun]:
    case = await owned_case(db, case_id, user_id, lock=True)
    question = await db.scalar(
        select(ChatMessage).where(
            ChatMessage.id == followup_id,
            ChatMessage.case_id == case.id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
    )
    if question is None:
        raise CaseFollowUpError(
            "followup_not_found",
            "Follow-up not found",
            status.HTTP_404_NOT_FOUND,
        )

    metadata = (
        question.metadata_json if isinstance(question.metadata_json, dict) else {}
    )
    followup = metadata.get("chat_followup")
    gap = followup_gap(metadata)
    source_revision = (
        followup.get("source_revision") if isinstance(followup, dict) else None
    )
    source_analysis_id = (
        followup.get("source_analysis_id") if isinstance(followup, dict) else None
    )
    if (
        gap is None
        or not isinstance(source_revision, int)
        or isinstance(source_revision, bool)
        or not isinstance(source_analysis_id, str)
        or question.analysis_result_id is None
        or source_analysis_id != str(question.analysis_result_id)
    ):
        raise CaseFollowUpError(
            "clarification_context_invalid",
            "Clarification provenance is invalid",
        )

    answer_payload = answer.model_dump(mode="json")
    answer_content = format_followup_answer(answer)
    expected_payload = {
        "operation": "analysis",
        "response_language": response_language,
        "expected_evidence_revision": source_revision + 1,
        "content": answer_content,
        "action": "follow_up",
        "answer": answer_payload,
        "source_analysis_id": source_analysis_id,
        "source_revision": source_revision,
    }
    existing_run = await db.scalar(
        select(CaseRun)
        .where(
            CaseRun.case_id == case.id,
            CaseRun.idempotency_key == idempotency_key,
        )
        .with_for_update()
    )
    if existing_run is not None:
        if existing_run.request_payload != expected_payload:
            raise CaseFollowUpError(
                "idempotency_conflict",
                "Idempotency key was already used with different clarification answer",
            )
        answer_message = await answer_message_for_run(db, existing_run)
        if answer_message is None:
            raise CaseFollowUpError(
                "clarification_answer_missing",
                "Clarification answer message is missing",
            )
        await requeue_existing_run(db, case, existing_run)
        return answer_message, existing_run

    if case.evidence_revision != source_revision:
        raise CaseFollowUpError(
            "clarification_stale",
            "Case evidence changed while this clarification was open. Reload the Case.",
        )
    if case.latest_analysis_result_id != question.analysis_result_id:
        raise CaseFollowUpError(
            "clarification_superseded",
            "This clarification belongs to an older analysis",
        )
    if str(gap.get("gap_id")) != answer.gap_id:
        raise CaseFollowUpError(
            "clarification_gap_mismatch",
            "This answer does not belong to the selected clarification gap",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    active_run = await db.scalar(
        select(CaseRun.id).where(
            CaseRun.case_id == case.id,
            CaseRun.status.in_(("queued", "running")),
        )
    )
    if active_run is not None:
        raise CaseFollowUpError(
            "case_run_active", "Case already has an active analysis run"
        )

    next_ordinal = (
        await db.scalar(
            select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                ChatMessage.case_id == case.id
            )
        )
        + 1
    )
    round_number = followup.get("round", 1) if isinstance(followup, dict) else 1
    answer_metadata = {
        "action": "follow_up",
        "chat_followup": {
            "source_analysis_id": source_analysis_id,
            "source_revision": source_revision,
            "round": round_number,
            "answer": answer_payload,
        },
    }
    answer_message = ChatMessage(
        case_id=case.id,
        ordinal=next_ordinal,
        role="user",
        content=answer_content,
        message_kind="followup_answer",
        analysis_result_id=question.analysis_result_id,
        in_reply_to_message_id=question.id,
        metadata_json=serialize_message_metadata(answer_metadata),
    )
    db.add(answer_message)
    await db.flush()

    if answer.disposition == "answered":
        db.add(
            CaseSource(
                case_id=case.id,
                source_kind="followup_answer",
                origin_message_id=answer_message.id,
                exact_text=answer.answer,
                provenance_json={
                    "origin": "case_followup",
                    "question_message_id": str(question.id),
                    "source_analysis_id": source_analysis_id,
                    "source_revision": source_revision,
                    "gap_id": answer.gap_id,
                    "gap_key": gap.get("gap_key"),
                    "topic": gap.get("topic"),
                    "clarification_question": gap.get("clarification_question"),
                },
                source_metadata_json={"disposition": answer.disposition},
            )
        )
    case.evidence_revision += 1
    await db.flush()

    try:
        from app.schemas.case_runs import CaseAnalysisCreate
        from app.services.workflow.case_run_service import (
            CaseRunError,
            enqueue_case_analysis,
        )

        run = await enqueue_case_analysis(
            db,
            case_id=case.id,
            user_id=user_id,
            request=CaseAnalysisCreate(
                idempotency_key=idempotency_key,
                response_language=response_language,
                expected_evidence_revision=case.evidence_revision,
            ),
            request_message_id=answer_message.id,
            request_payload_extra={
                "content": answer_content,
                "action": "follow_up",
                "answer": answer_payload,
                "source_analysis_id": source_analysis_id,
                "source_revision": source_revision,
            },
        )
    except CaseRunError as error:
        raise CaseFollowUpError(
            error.code, error.message, error.status_code
        ) from error

    case.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return answer_message, run




async def question_for_answer(
    db: AsyncSession,
    case_id: UUID,
    answer_message: ChatMessage,
) -> ChatMessage | None:
    if answer_message.in_reply_to_message_id:
        question = await db.get(ChatMessage, answer_message.in_reply_to_message_id)
        if question is not None:
            return question
    return await db.scalar(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case_id,
            ChatMessage.ordinal < answer_message.ordinal,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
        .order_by(ChatMessage.ordinal.desc())
    )


def followup_gap(metadata: dict[str, object]) -> dict[str, object] | None:
    followup = metadata.get("chat_followup")
    gap = followup.get("gap") if isinstance(followup, dict) else None
    return dict(gap) if isinstance(gap, dict) else None


def followup_answer(metadata: dict[str, object]) -> dict[str, object] | None:
    followup = metadata.get("chat_followup")
    answer = followup.get("answer") if isinstance(followup, dict) else None
    return dict(answer) if isinstance(answer, dict) else None


def followup_round(metadata: dict[str, object]) -> int:
    followup = metadata.get("chat_followup")
    value = followup.get("round") if isinstance(followup, dict) else None
    return value if isinstance(value, int) and value > 0 else 1


def answered_gap_id(message: ChatMessage) -> str | None:
    answer = followup_answer(message.metadata_json)
    if not answer or answer.get("disposition") not in {"answered", "unavailable", "skipped"}:
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


async def answer_message_for_run(
    db: AsyncSession,
    run: CaseRun,
) -> ChatMessage | None:
    if run.request_message_id is None:
        return None
    return await db.get(ChatMessage, run.request_message_id)


async def requeue_existing_run(
    db: AsyncSession,
    case: Case,
    run: CaseRun,
) -> None:
    if run.status != "failed":
        return
    from app.services.workflow.case_run_service import (
        CaseRunError,
        requeue_failed_case_run,
    )

    try:
        await requeue_failed_case_run(db, case, run)
    except CaseRunError as error:
        raise CaseFollowUpError(
            error.code, error.message, error.status_code
        ) from error


def format_followup_answer(answer: CaseFollowUpAnswer) -> str:
    return answer.answer if answer.disposition == "answered" else answer.disposition


__all__ = [
    "CaseFollowUpError",
    "CaseFollowUpHistoryError",
    "format_followup_answer",
    "get_case_followups",
    "load_followup_exchanges",
    "owned_case",
    "submit_followup_answer",
]
