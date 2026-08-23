from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

from app.schemas.rag import QueryResponse
from app.services.case_analysis import CaseAnalysisFailure
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.clients.rag_client import RagCallFailure
from app.services.followup.schemas import FollowUpPolicy, GapAnalyzer
from app.services.workflow.outcome import (
    AssistantOutcome,
    bind_followup_question,
    fresh_analysis_outcome,
    question_outcome,
    validated_rag_context_payload,
)
from app.services.workflow.pipeline_dependencies import PipelineDependencies
from app.services.workflow.pipeline_failure import record_failure


async def process_chat_run(
    run_id: UUID,
    *,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    rag_call: Callable[[str], Awaitable[QueryResponse]] | None = None,
    ask_call: Callable[..., Awaitable[object]] | None = None,
    dependencies: PipelineDependencies,
) -> None:
    worker_id = f"chat-run:{uuid4()}"
    async with dependencies.session_factory() as claim_db:
        claimed = await dependencies.worker_type(claim_db).claim_run(run_id, worker_id)
    if claimed is None:
        return
    try:
        analysis_request = ask_call or dependencies.analysis_request
        if claimed.action == "ask":
            outcome = await _run_question(claimed, analysis_request)
        else:
            outcome = await _run_fresh_analysis(
                claimed,
                rag_request=rag_call or dependencies.rag_request,
                analysis_request=analysis_request,
                followup_evaluator=dependencies.followup_evaluator,
                policy=policy,
                gap_analyzer=gap_analyzer,
            )
        async with dependencies.session_factory() as completion_db:
            await dependencies.worker_type(completion_db).complete_run(
                run_id, worker_id, outcome
            )
    except RagCallFailure as error:
        await record_failure(dependencies, run_id, worker_id, error.code, error.message)
    except CaseAnalysisFailure as error:
        await record_failure(dependencies, run_id, worker_id, error.code, error.message)
    except Exception:
        await record_failure(
            dependencies,
            run_id,
            worker_id,
            "chat_processing_error",
            "Failed to process chat message",
        )


async def _run_fresh_analysis(
    claimed,
    *,
    rag_request,
    analysis_request,
    followup_evaluator,
    policy,
    gap_analyzer,
) -> AssistantOutcome:
    response = await rag_request(claimed.raw_evidence)
    rag_context = validated_rag_context_payload(response)
    analysis_context = rag_context.to_analysis_context()
    analysis_context["source_message_ids"] = [
        str(value) for value in claimed.source_message_ids
    ]
    result = _coerce_analysis_result(
        await analysis_request(
            mode="case_overview",
            raw_evidence=claimed.raw_evidence,
            analysis_context=analysis_context,
            question=None,
            user_message=claimed.content,
        )
    )
    followup = await followup_evaluator(
        original_user_content=claimed.original_user_content,
        clarification_exchanges=claimed.clarification_exchanges,
        followup_root_ordinal=claimed.followup_root_ordinal,
        source_run_id=claimed.id,
        policy=policy,
        gap_analyzer=gap_analyzer,
        raw_evidence=claimed.raw_evidence,
        analysis_answer=result.answer,
        analysis_context=analysis_context,
    )
    if followup.outcome is not None:
        return bind_followup_question(
            followup.outcome,
            rag_context=rag_context,
            evidence_sha256=claimed.evidence_sha256,
            source_message_ids=claimed.source_message_ids,
        )
    return fresh_analysis_outcome(
        result.answer,
        action=claimed.action,
        rag_context=rag_context,
        evidence_sha256=claimed.evidence_sha256,
        source_message_ids=claimed.source_message_ids,
        followup_metadata=followup.metadata_json,
        trace=result.trace,
        trace_failure=result.trace_failure,
    )


async def _run_question(claimed, analysis_request) -> AssistantOutcome:
    if claimed.analysis_context is None:
        raise CaseAnalysisFailure(
            "analysis_context_missing",
            "No completed analytical context is available for ASK",
        )
    context = dict(claimed.analysis_context)
    context["source_message_ids"] = [str(value) for value in claimed.source_message_ids]
    result = _coerce_analysis_result(
        await analysis_request(
            mode="question_answer",
            raw_evidence=claimed.raw_evidence,
            analysis_context=context,
            question=claimed.content,
            user_message=claimed.content,
        )
    )
    return question_outcome(
        result.answer,
        analysis_context=context,
        evidence_sha256=claimed.evidence_sha256,
        source_message_ids=claimed.source_message_ids,
        trace=result.trace,
        trace_failure=result.trace_failure,
    )


def _coerce_analysis_result(value: object) -> CaseAnalysisResult:
    if isinstance(value, CaseAnalysisResult) and value.answer.strip():
        return value
    if isinstance(value, str) and value.strip():
        return CaseAnalysisResult(answer=value.strip(), trace=None)
    raise CaseAnalysisFailure(
        "analysis_invalid_response",
        "The Main Case Analysis returned no answer",
    )


__all__ = ["process_chat_run"]
