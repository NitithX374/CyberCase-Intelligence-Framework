from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_materials import assemble_case_evidence
from app.services.workflow.caseRunCompletion import (
    CaseRunCompletionError,
    owns_run,
    validated_output,
)


async def complete_case_ask(
    db: AsyncSession,
    run_id: UUID,
    claimed_attempt: int,
    output,
) -> bool:
    now = datetime.now(timezone.utc)
    async with db.begin():
        case_id = await db.scalar(select(CaseRun.case_id).where(CaseRun.id == run_id))
        if case_id is None:
            return False
        case = await db.scalar(select(Case).where(Case.id == case_id).with_for_update())
        if case is None:
            return False
        run = await db.scalar(select(CaseRun).where(CaseRun.id == run_id).with_for_update())
        if not owns_run(run, case.id, claimed_attempt):
            return False
        if run.operation != "ask" or run.request_message_id is None:
            raise CaseRunCompletionError("case_ask_run_invalid", "Case ASK run is incomplete")
        request_message = await db.get(ChatMessage, run.request_message_id)
        if request_message is None or request_message.case_id != case.id or request_message.role != "user":
            raise CaseRunCompletionError("case_ask_request_missing", "Case ASK request message is missing")
        if request_message.analysis_result_id is None:
            raise CaseRunCompletionError("case_ask_context_invalid", "Case ASK context result is missing from request message")
        context_result = await db.get(CaseAnalysisResult, request_message.analysis_result_id)
        if (
            context_result is None
            or context_result.case_id != case.id
        ):
            raise CaseRunCompletionError("case_ask_context_invalid", "Case ASK context result is invalid")

        assembled = await assemble_case_evidence(db, case_id=case.id, user_id=None)
        trace = validated_output(output, assembled)
        if trace.analysis_mode != "question_answer":
            raise CaseRunCompletionError("case_ask_trace_invalid", "Case ASK output is not response-scoped")
        completion = await db.execute(
            update(CaseRun)
            .where(
                CaseRun.id == run_id,
                CaseRun.status == "running",
                CaseRun.attempt_count == claimed_attempt,
            )
            .values(
                status="completed",
                error_code=None,
                error_message=None,
                finished_at=now,
                updated_at=now,
            )
            .returning(CaseRun.id)
        )
        if completion.scalar_one_or_none() is None:
            return False
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
            role="assistant",
            content=output.answer.strip(),
            retrieval_context_id=trace.retrieval_context_id,
            message_kind="conversation",
            analysis_result_id=request_message.analysis_result_id,
            in_reply_to_message_id=request_message.id,
            metadata_json=serialize_message_metadata(
                {
                    "action": "conversation",
                    "analysis_trace": trace.model_dump(mode="json"),
                }
            ),
        )
        db.add(message)
        case.updated_at = now
        await db.flush()
    return True
__all__ = ["complete_case_ask"]
