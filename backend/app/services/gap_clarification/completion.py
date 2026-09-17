from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_run import CaseRun
from app.models.chat import ChatMessage
from app.schemas.case_runs import CaseAnalysisCreate
from app.services.gap_clarification.runtime import GapClarificationError


async def enqueue_completion_analysis(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    session_id: str,
    answer: ChatMessage,
    next_question: ChatMessage | None,
    request_key: str,
) -> CaseRun | None:
    if next_question is not None:
        return None
    metadata = answer.metadata_json if isinstance(answer.metadata_json, dict) else {}
    followup = metadata.get("chat_followup")
    answer_data = followup.get("answer") if isinstance(followup, dict) else None
    if not isinstance(answer_data, dict) or answer_data.get("response_type") != "case_fact":
        return None
    if not answer_data.get("normalized_fact"):
        return None
    case = await db.scalar(select(Case).where(Case.id == case_id).with_for_update())
    if case is None or case.user_id != user_id:
        raise GapClarificationError("case_not_found", "Case not found", 404)
    request = CaseAnalysisCreate(
        idempotency_key=f"clarification:{session_id}:revision:{case.evidence_revision}",
        response_language="thai" if any("\u0e00" <= char <= "\u0e7f" for char in answer.content) else "english",
        expected_evidence_revision=case.evidence_revision,
    )
    from app.services.workflow.case_run_service import enqueue_case_analysis

    try:
        return await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=user_id,
            request=request,
            request_payload_extra={
                "action": "adaptive_gap_clarification_complete",
                "clarification_session_id": session_id,
                "answer_message_id": str(answer.id),
                "source_analysis_id": followup.get("source_analysis_id") if isinstance(followup, dict) else None,
                "source_revision": followup.get("source_revision") if isinstance(followup, dict) else None,
                "request_key": request_key,
            },
        )
    except Exception as error:
        from app.services.workflow.case_run_service import CaseRunError

        if isinstance(error, CaseRunError):
            raise GapClarificationError(error.code, error.message, error.status_code) from error
        raise


__all__ = ["enqueue_completion_analysis"]
