from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.case_state.mutator import (
    MUTATION_METADATA_KEY,
    CaseStateDeltaInput,
    CaseStateMutationFailure,
)
from app.services.case_state.projector import project_case_state_to_retrieval_query
from app.services.extraction import EXTRACTION_METADATA_KEY, ExtractionModelAdapter
from app.services.followup.gate import (
    _mark_followup_rag_invoked_metadata,
)
from app.services.followup.schemas import GapAnalyzer, FollowUpPolicy
from app.services.workflow.outcome import (
    AssistantOutcome,
    RagContextPayload,
    _validated_rag_context_payload,
    build_merged_extraction_metadata,
    map_case_state_mutation_response,
    map_case_state_no_change_response,
)
from app.services.workflow.pipeline_dependencies import PipelineDependencies
from app.services.workflow.pipeline_helpers import (
    attach_post_analysis_followup_outcome,
    coerce_analysis_result,
    log_stage,
    source_message_ids_for_run,
)
from app.services.workflow.worker import ClaimedChatRun


async def run_mutation_stage(
    claimed_run: ClaimedChatRun,
    *,
    policy: FollowUpPolicy | None,
    gap_analyzer: GapAnalyzer | None,
    rag_request: Callable[..., Any],
    analysis_request: Callable[..., Any],
    followup_evaluator: Callable[..., Any],
    extraction_adapter: ExtractionModelAdapter | None,
    dependencies: PipelineDependencies,
    capture_metadata: Callable[[dict[str, Any]], None],
) -> tuple[AssistantOutcome, dict[str, Any]]:
    run_id = claimed_run.id
    log_stage("EXTRACTING CASE STATE DELTA", run_id)
    if not isinstance(claimed_run.case_state_json, dict):
        raise CaseStateMutationFailure(
            "case_state_parent_missing",
            "The current Case State could not be loaded for mutation",
        )
    if claimed_run.case_state_version_id is None:
        raise CaseStateMutationFailure(
            "case_state_parent_missing",
            "The current Case State version could not be loaded for mutation",
        )
    if claimed_run.request_message_id is None:
        raise CaseStateMutationFailure(
            "case_state_mutation_input_missing",
            "The mutation source message could not be identified",
        )

    try:
        delta_input = CaseStateDeltaInput(
            current_case_state=deepcopy(claimed_run.case_state_json),
            new_user_message=claimed_run.content,
            source_message_id=claimed_run.request_message_id,
            mutation_intent="add_case_info",
            pending_question=(
                claimed_run.pending_question
                if claimed_run.clarification_answer
                else None
            ),
        )
    except (TypeError, ValueError) as exc:
        raise CaseStateMutationFailure(
            "case_state_mutation_input_invalid",
            "The explicit mutation message could not be prepared",
        ) from exc

    delta, mutation_metadata = await dependencies.delta_extractor(
        delta_input,
        adapter=extraction_adapter,
    )
    capture_metadata(mutation_metadata)
    followup_metadata_json: dict[str, Any] = {
        MUTATION_METADATA_KEY: mutation_metadata,
    }
    if delta is None:
        raise CaseStateMutationFailure(
            str(mutation_metadata.get("failure_code", "case_state_delta_failed")),
            str(
                mutation_metadata.get(
                    "failure_message",
                    "The Case State delta failed validation",
                )
            ),
        )

    if not delta.changes and not claimed_run.clarification_answer:
        log_stage("NO CHANGES DETECTED (Skipping RAG)", run_id)
        return (
            map_case_state_no_change_response(mutation_metadata=mutation_metadata),
            followup_metadata_json,
        )

    merged_case_state_json = dependencies.apply_delta(
        claimed_run.case_state_json,
        delta,
        source_message_id=claimed_run.request_message_id,
    )
    retrieval_query = project_case_state_to_retrieval_query(merged_case_state_json)
    log_stage("RAG RETRIEVAL (Querying GraphRAG)", run_id)
    response = await rag_request(retrieval_query)
    rag_context_payload = _validated_rag_context_payload(response)
    analysis_context = rag_context_payload.to_analysis_context()
    log_stage("ANALYZING UPDATED CASE OVERVIEW", run_id)
    raw_narrative = claimed_run.raw_case_narrative or (
        str(claimed_run.original_user_content)
        if isinstance(claimed_run.original_user_content, str)
        and claimed_run.original_user_content.strip()
        and claimed_run.post_answer_action != "add_case_info"
        else None
    )
    if (
        settings.analysis_input_mode == "raw_direct"
        and (not isinstance(raw_narrative, str) or not raw_narrative.strip())
    ):
        raise CaseAnalysisFailure(
            "analysis_context_missing",
            "The accumulated raw case evidence could not be loaded for mutation in RAW_DIRECT mode",
        )
    analysis_result = coerce_analysis_result(
        await analysis_request(
            mode="case_overview",
            case_state_json=merged_case_state_json,
            raw_case_narrative=raw_narrative,
            analysis_context=analysis_context,
            question=None,
            user_message=claimed_run.content,
        )
    )
    answer = analysis_result.answer
    extraction_metadata = build_merged_extraction_metadata(
        merged_case_state_json,
        source_message_ids=source_message_ids_for_run(claimed_run),
        mutation_metadata=mutation_metadata,
    )
    log_stage("EVALUATING CLARIFICATION & FOLLOWUP POLICY", run_id)
    followup_resolution = await followup_evaluator(
        original_user_content=claimed_run.original_user_content,
        clarification_exchanges=claimed_run.clarification_exchanges,
        followup_root_ordinal=claimed_run.followup_root_ordinal,
        source_run_id=claimed_run.id,
        policy=policy,
        gap_analyzer=gap_analyzer,
        case_state=merged_case_state_json,
        analysis_answer=answer.strip(),
        analysis_context=analysis_context,
    )
    action = "clarification_answer" if claimed_run.clarification_answer else "add_case_info"
    if followup_resolution.outcome is not None:
        return (
            attach_post_analysis_followup_outcome(
                followup_resolution.outcome,
                rag_context_payload=rag_context_payload,
                validated_case_state_json=merged_case_state_json,
                extraction_metadata=extraction_metadata,
                action=action,
                delta_json=delta.model_dump(mode="json"),
                expected_parent_case_state_version_id=claimed_run.case_state_version_id,
                mutation_metadata=mutation_metadata,
            ),
            followup_metadata_json,
        )

    followup_metadata_json = {
        **_mark_followup_rag_invoked_metadata(followup_resolution.metadata_json),
        EXTRACTION_METADATA_KEY: extraction_metadata,
    }
    return (
        map_case_state_mutation_response(
            answer.strip(),
            rag_context_payload=rag_context_payload,
            merged_case_state_json=merged_case_state_json,
            delta_json=delta.model_dump(mode="json"),
            expected_parent_case_state_version_id=claimed_run.case_state_version_id,
            mutation_metadata=mutation_metadata,
            extraction_metadata=extraction_metadata,
            followup_metadata_json=followup_metadata_json,
            action=action,
            analysis_trace_draft=analysis_result.trace,
            analysis_trace_failure=analysis_result.trace_failure,
        ),
        followup_metadata_json,
    )
