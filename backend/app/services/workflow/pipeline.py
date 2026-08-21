from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from app.config import settings
from app.database import async_session
from app.schemas.rag import QueryResponse
from app.services.case_analysis import (
    CASE_ANALYSIS_PROMPT_VERSION,
    CaseAnalysisFailure,
    request_case_analysis,
)
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.case_state.mutator import (
    MUTATION_METADATA_KEY,
    CaseStateDelta,
    CaseStateDeltaInput,
    CaseStateMutationFailure,
    apply_case_state_delta,
    run_case_state_delta_extraction,
)
from app.services.case_state.projector import project_case_state_to_retrieval_query
from app.services.case_state.raw_evidence import (
    extract_raw_case_evidence_segments,
    format_raw_case_evidence_segments,
    resolve_raw_case_evidence_history,
)
from app.services.chat.chat_message import (
    ClarificationChain,
    reconstruct_clarification_chain,
)
from app.services.clients.rag_client import RagCallFailure, request_rag
from app.services.extraction import (
    EXTRACTION_METADATA_KEY,
    ExtractionModelAdapter,
    ExtractionStageFailure,
    attach_llm_extraction,
    build_extraction_input,
    normalize_case_state,
    run_baseline_extraction,
    run_validated_case_state_extraction,
    validate_baseline_extraction,
)
from app.services.followup.gate import (
    FollowUpResolution,
    _answer_indicates_unavailable,
    _coerce_gap_analysis_result,
    _coerce_policy_result,
    _empty_gap_analysis_trace,
    _followup_failure_code,
    _followup_metadata,
    _gap_analysis_trace,
    _gap_reason_code,
    _invoke_policy_method,
    _mark_followup_rag_invoked,
    _mark_followup_rag_invoked_metadata,
    _normalized_question,
    _safe_token_count,
    _selected_askable_gap,
    evaluate_followup_outcome,
    resolve_followup_outcome,
)
from app.services.followup.schemas import (
    ClarificationExchange,
    FollowUpDecision,
    FollowUpPolicy,
    FollowUpPolicyResult,
    FollowUpReasonCode,
    GapAnalysis,
    GapAnalysisResult,
    GapAnalyzer,
    GapItem,
    GapPriority,
    GapStatus,
)
from app.services.workflow.outcome import (
    AssistantOutcome,
    RagContextPayload,
    _validated_rag_context_payload,
    build_merged_extraction_metadata,
    map_case_analysis_response,
    map_case_state_mutation_response,
    map_case_state_no_change_response,
    map_initial_case_analysis_response,
    map_rag_response,
)
from app.services.workflow.pipeline_dependencies import PipelineDependencies
from app.services.workflow.pipeline_execution import (
    process_chat_run as execute_chat_run,
)
from app.services.workflow.pipeline_failure import record_failure
from app.services.workflow.pipeline_helpers import (
    attach_post_analysis_followup_outcome,
    coerce_analysis_result,
    log_stage,
    source_message_ids_for_run,
)
from app.services.workflow.worker import RUN_LEASE_DURATION, ChatRunWorker, ClaimedChatRun


def _build_dependencies() -> PipelineDependencies:
    return PipelineDependencies(
        session_factory=async_session,
        worker_type=ChatRunWorker,
        delta_extractor=run_case_state_delta_extraction,
        baseline_extractor=run_validated_case_state_extraction,
        apply_delta=apply_case_state_delta,
        rag_request=request_rag,
        analysis_request=request_case_analysis,
        followup_evaluator=evaluate_followup_outcome,
    )


async def process_chat_run(
    run_id: UUID,
    *,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    rag_call: Callable[[str], Awaitable[QueryResponse]] | None = None,
    ask_call: Callable[..., Awaitable[object]] | None = None,
    extraction_adapter: ExtractionModelAdapter | None = None,
) -> None:
    return await execute_chat_run(
        run_id,
        policy=policy,
        gap_analyzer=gap_analyzer,
        rag_call=rag_call,
        ask_call=ask_call,
        extraction_adapter=extraction_adapter,
        dependencies=_build_dependencies(),
    )


async def _record_failure(
    run_id: UUID,
    worker_id: str,
    error_code: str,
    error_message: str,
    followup_metadata_json: dict[str, Any] | None = None,
) -> None:
    await record_failure(
        _build_dependencies(),
        run_id,
        worker_id,
        error_code,
        error_message,
        followup_metadata_json=followup_metadata_json,
    )


__all__ = [
    "AssistantOutcome",
    "CaseAnalysisResult",
    "CaseStateDelta",
    "CaseStateDeltaInput",
    "CaseStateMutationFailure",
    "ChatRunWorker",
    "ClaimedChatRun",
    "ClarificationChain",
    "ClarificationExchange",
    "EXTRACTION_METADATA_KEY",
    "ExtractionModelAdapter",
    "ExtractionStageFailure",
    "FollowUpDecision",
    "FollowUpPolicy",
    "FollowUpPolicyResult",
    "FollowUpReasonCode",
    "FollowUpResolution",
    "GapAnalysis",
    "GapAnalysisResult",
    "GapAnalyzer",
    "GapItem",
    "GapPriority",
    "GapStatus",
    "MUTATION_METADATA_KEY",
    "RagCallFailure",
    "RagContextPayload",
    "RUN_LEASE_DURATION",
    "_answer_indicates_unavailable",
    "_coerce_gap_analysis_result",
    "_coerce_policy_result",
    "_empty_gap_analysis_trace",
    "_followup_failure_code",
    "_followup_metadata",
    "_gap_analysis_trace",
    "_gap_reason_code",
    "_invoke_policy_method",
    "_mark_followup_rag_invoked",
    "_mark_followup_rag_invoked_metadata",
    "_normalized_question",
    "_safe_token_count",
    "_selected_askable_gap",
    "_validated_rag_context_payload",
    "apply_case_state_delta",
    "async_session",
    "attach_llm_extraction",
    "build_extraction_input",
    "build_merged_extraction_metadata",
    "evaluate_followup_outcome",
    "extract_raw_case_evidence_segments",
    "format_raw_case_evidence_segments",
    "map_case_analysis_response",
    "map_case_state_mutation_response",
    "map_case_state_no_change_response",
    "map_initial_case_analysis_response",
    "map_rag_response",
    "normalize_case_state",
    "process_chat_run",
    "project_case_state_to_retrieval_query",
    "reconstruct_clarification_chain",
    "request_rag",
    "resolve_followup_outcome",
    "resolve_raw_case_evidence_history",
    "run_baseline_extraction",
    "run_case_state_delta_extraction",
    "run_validated_case_state_extraction",
    "validate_baseline_extraction",
]
