from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.case_materials import assembleCaseEvidence
from app.services.chat.caseAnswer import ANSWER_VERSION
from app.services.workflow.caseRunCompletion import (
    CaseRunCompletionError,
    _owns_run,
    _validated_output,
)


async def completeCaseAsk(
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
        if not _owns_run(run, case.id, claimed_attempt):
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

        assembled = await assembleCaseEvidence(db, case_id=case.id, user_id=None)
        trace = _validated_output(output, assembled)
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
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
            .returning(CaseRun.id)
        )
        if completion.scalar_one_or_none() is None:
            return False
        analysis_freshness = (
            "current"
            if run.evidence_revision == case.evidence_revision
            else "stale"
        )
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
                    "analysis_kind": "question_answer",
                    "analysis_state_scope": "response_scoped",
                    "context_analysis_result_id": str(context_result.id),
                    "evidence_source_ids": _trace_source_ids(trace),
                    "analysis_trace": trace.model_dump(mode="json"),
                    "answer_receipt": output.execution_receipt,
                    "analysis_freshness": analysis_freshness,
                    "evidence_revision": run.evidence_revision,
                    "case_evidence_revision": case.evidence_revision,
                    "has_newer_evidence": bool(case.evidence_revision > run.evidence_revision),
                    "chat_action": {
                        "action": "ask",
                        "route": "case",
                        "rag_invoked": False,
                        "retrieval_context_reused": False,
                        "analysis_mode": "question_answer",
                        "prompt_version": ANSWER_VERSION,
                    },
                }
            ),
        )
        db.add(message)
        case.updated_at = now
        await db.flush()
    return True


def _trace_source_ids(trace: CaseAnalysisTrace) -> list[str]:
    ids: list[str] = []
    for claim in trace.claims:
        ids.extend(claim.supporting_source_ids)
        ids.extend(claim.contradicting_source_ids)
    return list(dict.fromkeys(ids))


__all__ = ["completeCaseAsk"]
