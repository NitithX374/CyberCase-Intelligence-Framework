from __future__ import annotations

from typing import Any, Callable

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure
from app.services.extraction import (
    EXTRACTION_METADATA_KEY,
    ExtractionModelAdapter,
    ExtractionStageFailure,
)
from app.services.followup.gate import _mark_followup_rag_invoked_metadata
from app.services.followup.schemas import GapAnalyzer, FollowUpPolicy
from app.services.workflow.outcome import (
    AssistantOutcome,
    _validated_rag_context_payload,
    map_initial_case_analysis_response,
)
from app.services.workflow.pipeline_dependencies import PipelineDependencies
from app.services.workflow.pipeline_helpers import (
    attach_post_analysis_followup_outcome,
    coerce_analysis_result,
    log_stage,
)
from app.services.workflow.worker import ClaimedChatRun


async def run_initial_stage(
    claimed_run: ClaimedChatRun,
    *,
    policy: FollowUpPolicy | None,
    gap_analyzer: GapAnalyzer | None,
    rag_request: Callable[..., Any],
    analysis_request: Callable[..., Any],
    followup_evaluator: Callable[..., Any],
    extraction_adapter: ExtractionModelAdapter | None,
    dependencies: PipelineDependencies,
) -> tuple[AssistantOutcome, dict[str, Any]]:
    run_id = claimed_run.id
    log_stage("EXTRACTING BASELINE CASE STATE", run_id)
    validated_case_state_json, extraction_metadata = (
        await dependencies.baseline_extractor(
            claimed_run,
            adapter=extraction_adapter,
        )
    )
    followup_metadata_json = {EXTRACTION_METADATA_KEY: extraction_metadata}
    if validated_case_state_json is None:
        failure_code = extraction_metadata.get("failure_code", "extraction_failed")
        failure_message = extraction_metadata.get(
            "failure_message",
            "The extraction did not produce a validated Case State",
        )
        raise ExtractionStageFailure(
            str(failure_code),
            str(failure_message),
            followup_metadata_json,
        )

    log_stage("RAG RETRIEVAL (Querying GraphRAG)", run_id)
    from app.services.case_state.projector import project_case_state_to_retrieval_query

    retrieval_query = project_case_state_to_retrieval_query(validated_case_state_json)
    response = await rag_request(retrieval_query)
    rag_context_payload = _validated_rag_context_payload(response)
    analysis_context = rag_context_payload.to_analysis_context()
    log_stage("ANALYZING INITIAL CASE OVERVIEW", run_id)
    raw_narrative = (
        claimed_run.raw_case_narrative
        or (
            str(claimed_run.original_user_content)
            if isinstance(claimed_run.original_user_content, str)
            and claimed_run.original_user_content.strip()
            else None
        )
        or (
            str(claimed_run.content)
            if isinstance(claimed_run.content, str) and claimed_run.content.strip()
            else None
        )
    )
    if (
        settings.analysis_input_mode == "raw_direct"
        and (not isinstance(raw_narrative, str) or not raw_narrative.strip())
    ):
        raise CaseAnalysisFailure(
            "analysis_context_missing",
            "The initial raw case narrative could not be loaded in RAW_DIRECT mode",
        )
    analysis_result = coerce_analysis_result(
        await analysis_request(
            mode="case_overview",
            case_state_json=validated_case_state_json,
            raw_case_narrative=raw_narrative,
            analysis_context=analysis_context,
            question=None,
            user_message=claimed_run.content,
        )
    )
    answer = analysis_result.answer
    log_stage("EVALUATING CLARIFICATION & FOLLOWUP POLICY", run_id)
    followup_resolution = await followup_evaluator(
        original_user_content=claimed_run.original_user_content,
        clarification_exchanges=claimed_run.clarification_exchanges,
        followup_root_ordinal=claimed_run.followup_root_ordinal,
        source_run_id=claimed_run.id,
        policy=policy,
        gap_analyzer=gap_analyzer,
        case_state=validated_case_state_json,
        analysis_answer=answer.strip(),
        analysis_context=analysis_context,
    )
    if followup_resolution.outcome is not None:
        outcome = attach_post_analysis_followup_outcome(
            followup_resolution.outcome,
            rag_context_payload=rag_context_payload,
            validated_case_state_json=validated_case_state_json,
            extraction_metadata=extraction_metadata,
            action="initial_analysis",
        )
    else:
        followup_metadata_json = {
            **_mark_followup_rag_invoked_metadata(followup_resolution.metadata_json),
            EXTRACTION_METADATA_KEY: extraction_metadata,
        }
        outcome = map_initial_case_analysis_response(
            answer.strip(),
            rag_context_payload=rag_context_payload,
            validated_case_state_json=validated_case_state_json,
            extraction_metadata=extraction_metadata,
            followup_metadata_json=followup_metadata_json,
            analysis_trace_draft=analysis_result.trace,
            analysis_trace_failure=analysis_result.trace_failure,
        )
    return outcome, followup_metadata_json
