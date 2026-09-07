from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

from app.schemas.rag import QueryResponse
from app.services.case_analysis import (
    CaseAnalysisFailure,
    enrich_case_analysis_result,
    validate_canonical_case_overview_trace,
)
from app.services.case_analysis.contracts import (
    AnalysisTraceV3,
    CaseAnalysisResult,
)
from app.services.case_analysis.mitre_applicability_contracts import (
    MITRE_APPLICABILITY_GATE_VERSION,
    MitreApplicabilityRecord,
)
from app.services.case_analysis.mitre_applicability_gate import (
    evaluate_mitre_applicability,
)
from app.services.clients.rag_client import RagCallFailure
from app.services.followup.schemas import FollowUpPolicy, GapAnalyzer
from app.services.followup.contracts import FollowUpResolution
from app.services.followup.gap_stage import run_gap_analysis_stage
from app.services.workflow.outcome import (
    AssistantOutcome,
    bind_followup_question,
    fresh_analysis_outcome,
    question_outcome,
)
from dataclasses import dataclass
from typing import Any

from app.services.workflow.run_heartbeat import maintain_run_lease
from app.services.workflow.rag_routing import (
    RagAttempt,
    attempt_mitre_applicability,
    attempt_optional_rag,
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


@dataclass(frozen=True)
class PipelineDependencies:
    session_factory: Callable[..., Any]
    worker_type: type[Any]
    rag_request: Callable[..., Any]
    analysis_request: Callable[..., Any]
    followup_evaluator: Callable[..., Awaitable[FollowUpResolution]]


async def record_failure(
    dependencies: PipelineDependencies,
    run_id: UUID,
    worker_id: str,
    error_code: str,
    error_message: str,
    followup_metadata_json: dict[str, Any] | None = None,
) -> None:
    async with dependencies.session_factory() as failure_db:
        await dependencies.worker_type(failure_db).fail_run(
            run_id,
            worker_id,
            error_code,
            error_message,
            followup_metadata_json=followup_metadata_json,
        )


logger = logging.getLogger("app.chat")


async def process_chat_run(
    run_id: UUID,
    *,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    rag_call: Callable[[str], Awaitable[QueryResponse]] | None = None,
    ask_call: Callable[..., Awaitable[object]] | None = None,
    applicability_call: Callable[..., Awaitable[MitreApplicabilityRecord]]
    | None = None,
    dependencies: PipelineDependencies,
) -> None:
    worker_id = f"chat-run:{uuid4()}"
    async with dependencies.session_factory() as claim_db:
        claimed = await dependencies.worker_type(claim_db).claim_run(run_id, worker_id)
    if claimed is None:
        return
    try:
        async with maintain_run_lease(dependencies.session_factory, run_id, worker_id):
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
                    applicability_gate=applicability_call
                    or evaluate_mitre_applicability,
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
        logger.exception("Chat processing failed run_id=%s", run_id)
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
    applicability_gate,
) -> AssistantOutcome:
    applicability = await attempt_mitre_applicability(
        claimed,
        applicability_gate,
    )
    rag_invoked = applicability.decision == "RETRIEVE"
    rag_attempt = (
        await attempt_optional_rag(claimed, rag_request)
        if rag_invoked
        else RagAttempt(status="no_applicable_context", context=None)
    )
    logger.info(
        "MITRE applicability routed gate_version=%s source_run_id=%s "
        "decision=%s cited_source_count=%s trigger_count=%s rag_invoked=%s",
        MITRE_APPLICABILITY_GATE_VERSION,
        claimed.id,
        applicability.decision,
        len(applicability.source_message_ids),
        len(applicability.trigger_text),
        rag_invoked,
    )
    rag_context = rag_attempt.context
    analysis_context = (
        rag_context.to_analysis_context() if rag_context is not None else {}
    )
    analysis_context["source_message_ids"] = [
        str(value) for value in claimed.source_message_ids
    ]
    analysis_context["_source_text_by_message_id"] = {
        str(source.message_id): source.content for source in claimed.evidence_sources
    }
    if claimed.document_source_context:
        analysis_context["document_source_context"] = list(
            claimed.document_source_context
        )
    result = _coerce_analysis_result(
        await analysis_request(
            mode="case_overview",
            raw_evidence=claimed.raw_evidence,
            analysis_context=analysis_context,
            question=None,
            user_message=claimed.content,
        )
    )
    analysis_claims = None
    if isinstance(result.trace, AnalysisTraceV3):
        analysis_claims = [
            {
                "claim_id": claim.claim_id,
                "text": claim.text,
                "claim_type": claim.claim_type,
                "epistemic_status": claim.epistemic_status,
            }
            for claim in result.trace.claims
        ]
    gap_stage = None
    if isinstance(result.trace, AnalysisTraceV3):
        gap_stage = await run_gap_analysis_stage(
            original_user_content=claimed.original_user_content,
            clarification_exchanges=claimed.clarification_exchanges,
            policy=policy,
            gap_analyzer=gap_analyzer,
            raw_evidence=claimed.raw_evidence,
            analysis_answer=result.answer,
            analysis_context=analysis_context,
            analysis_claims=analysis_claims,
            source_run_id=claimed.id,
        )
        result = enrich_case_analysis_result(
            result,
            gap_stage.canonical_analysis,
            source_message_ids={str(value) for value in claimed.source_message_ids},
            mitre_table=analysis_context.get("mitre_table", []),
        )
    canonical_trace = None
    if isinstance(result.trace, AnalysisTraceV3):
        canonical_trace = validate_canonical_case_overview_trace(
            result.trace,
            evidence_sha256=claimed.evidence_sha256,
            source_message_ids={str(value) for value in claimed.source_message_ids},
            mitre_table=analysis_context.get("mitre_table", []),
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
        analysis_claims=analysis_claims,
        canonical_trace=canonical_trace,
        precomputed_gap_stage=gap_stage,
        evidence_sha256=claimed.evidence_sha256,
        canonical_state_required=True,
    )
    if followup.question is not None:
        return bind_followup_question(
            AssistantOutcome(
                content=followup.question,
                retrieval_context_id=None,
                metadata_json=followup.metadata_json,
                thread_status="awaiting_followup",
            ),
            rag_context=rag_context,
            rag_status=rag_attempt.status,
            rag_failure_code=rag_attempt.failure_code,
            rag_invoked=rag_invoked,
            mitre_applicability=applicability.model_dump(mode="json"),
            evidence_sha256=claimed.evidence_sha256,
            source_message_ids=claimed.source_message_ids,
            trace=result.trace,
            trace_failure=result.trace_failure,
        )
    return fresh_analysis_outcome(
        result.answer,
        action=claimed.action,
        rag_context=rag_context,
        rag_status=rag_attempt.status,
        rag_failure_code=rag_attempt.failure_code,
        rag_invoked=rag_invoked,
        mitre_applicability=applicability.model_dump(mode="json"),
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
    context["_source_text_by_message_id"] = {
        str(source.message_id): source.content for source in claimed.evidence_sources
    }
    if claimed.document_source_context:
        context["document_source_context"] = list(claimed.document_source_context)
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


__all__ = ["PipelineDependencies", "process_chat_run", "record_failure"]
