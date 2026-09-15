from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.schemas.case_clarifications import (
    CaseClarificationAnswer,
    CaseClarificationRead,
)
from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_materials import CaseMaterialsError, CaseMaterialsService
from app.services.followup.case_clarification_history import (
    get_owned_clarifications,
    load_case_clarification_exchanges,
)
from app.services.followup.case_clarification_support import (
    CaseClarificationError,
    CaseClarificationHistoryError,
    answer_fingerprint,
    owned_case,
)
from app.services.workflow.case_run_service import CaseRunError


async def submit_clarification_answer(
    db: AsyncSession,
    *,
    case_id: UUID,
    clarification_id: UUID,
    user_id: UUID | None,
    request: CaseClarificationAnswer,
) -> tuple[CaseClarificationRead, CaseRun]:
    case = await owned_case(db, case_id, user_id, lock=True)

    q_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case.id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
        .order_by(ChatMessage.ordinal.desc())
    )
    questions = list(q_result.scalars().all())
    question = None
    for q in questions:
        if q.id == clarification_id:
            question = q
            break

    if question is None:
        raise CaseClarificationError("clarification_not_found", "Clarification not found", status.HTTP_404_NOT_FOUND)

    existing_answer = await db.scalar(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case.id,
            ChatMessage.role == "user",
            ChatMessage.message_kind == "followup_answer",
            ChatMessage.in_reply_to_message_id == question.id,
        )
    )
    fingerprint = answer_fingerprint(request)
    if existing_answer is not None:
        existing_fp = answer_fingerprint(CaseClarificationAnswer(answer=existing_answer.content, idempotency_key="check"))
        if existing_fp != fingerprint:
            raise CaseClarificationError("clarification_answer_conflict", "Clarification already has another answer")
        run = await db.scalar(
            select(CaseRun)
            .where(CaseRun.case_id == case.id, CaseRun.request_message_id == existing_answer.id)
            .order_by(CaseRun.created_at.desc())
            .with_for_update()
        )
        if run is None:
            run = await db.scalar(
                select(CaseRun)
                .where(CaseRun.case_id == case.id)
                .order_by(CaseRun.created_at.desc())
                .with_for_update()
            )
        if run is None:
            raise CaseClarificationError("clarification_run_missing", "Clarification answer run is missing")
        if run.status == "failed":
            from app.services.workflow.case_run_service import requeue_failed_case_run

            try:
                await requeue_failed_case_run(db, case, run)
            except CaseRunError as error:
                raise CaseClarificationError(error.code, error.message, error.status_code) from error

        read_items = await get_owned_clarifications(db, case_id=case.id, user_id=user_id)
        clarification_read = next((item for item in read_items if item.id == clarification_id or item.question_message_id == question.id), None)
        if clarification_read is None:
            raise CaseClarificationError("clarification_not_found", "Clarification not found", status.HTTP_404_NOT_FOUND)
        return clarification_read, run

    if case.latest_analysis_result_id and question.analysis_result_id and case.latest_analysis_result_id != question.analysis_result_id:
        raise CaseClarificationError("clarification_superseded", "This clarification belongs to an older analysis")
    if question.analysis_result_id is None:
        raise CaseClarificationError("clarification_context_invalid", "This clarification has no pinned analysis result")
    question_result = await db.get(CaseAnalysisResult, question.analysis_result_id)
    if question_result is None or question_result.case_id != case.id:
        raise CaseClarificationError("clarification_context_invalid", "This clarification has an invalid analysis result")

    active = await db.scalar(
        select(CaseRun.id).where(CaseRun.case_id == case.id, CaseRun.status.in_(("queued", "running")))
    )
    if active is not None:
        raise CaseClarificationError("case_run_active", "Case already has an active analysis run")

    next_ordinal = (
        await db.scalar(
            select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                ChatMessage.case_id == case.id
            )
        )
        + 1
    )
    message = ChatMessage(
        case_id=case.id,
        ordinal=next_ordinal,
        role="user",
        content=request.answer.strip(),
        message_kind="followup_answer",
        analysis_result_id=question.analysis_result_id,
        in_reply_to_message_id=question.id,
        metadata_json=serialize_message_metadata(
            {
                "action": "follow_up",
            }
        ),
    )
    db.add(message)
    await db.flush()

    try:
        from app.services.workflow.case_run_service import enqueue_case_analysis
        from app.schemas.case_runs import CaseAnalysisCreate

        await CaseMaterialsService(db).add_text_source(
            case_id=case.id,
            user_id=user_id,
            source_kind="followup_answer",
            text=request.answer,
            provenance_json={
                "origin": "case_clarification",
                "clarification_id": str(clarification_id),
                "origin_message_id": str(message.id),
            },
            origin_message_id=message.id,
        )
        run = await enqueue_case_analysis(
            db,
            case_id=case.id,
            user_id=user_id,
            request=CaseAnalysisCreate(
                idempotency_key=request.idempotency_key,
                response_language=request.response_language,
                expected_evidence_revision=case.evidence_revision,
            ),
            request_message_id=message.id,
            request_payload_extra={
                "content": request.answer.strip(),
                "action": "follow_up",
            },
        )
    except (CaseMaterialsError, CaseRunError) as error:
        raise CaseClarificationError(error.code, error.message, getattr(error, "status_code", 409)) from error

    case.updated_at = datetime.now(timezone.utc)
    await db.flush()

    read_items = await get_owned_clarifications(db, case_id=case.id, user_id=user_id)
    clarification_read = next((item for item in read_items if item.id == clarification_id or item.question_message_id == question.id), None)
    if clarification_read is None:
        raise CaseClarificationError("clarification_not_found", "Clarification read serialization failed")
    return clarification_read, run


__all__ = [
    "CaseClarificationError",
    "CaseClarificationHistoryError",
    "answer_fingerprint",
    "get_owned_clarifications",
    "load_case_clarification_exchanges",
    "submit_clarification_answer",
]
