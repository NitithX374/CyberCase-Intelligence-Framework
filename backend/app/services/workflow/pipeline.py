"""Execution pipeline for background chat runs."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from copy import deepcopy
from dataclasses import replace
from typing import Any
from uuid import UUID, uuid4

from app.config import settings
from app.database import async_session
from app.schemas.rag import QueryResponse
from app.services.case_analysis import (
    CASE_ANALYSIS_PROMPT_VERSION,
    CaseAnalysisFailure,
    request_case_analysis,
)
from app.services.case_state.mutator import (
    MUTATION_METADATA_KEY,
    CaseStateDelta,
    CaseStateDeltaInput,
    CaseStateMutationFailure,
    apply_case_state_delta,
    run_case_state_delta_extraction,
)
from app.services.case_state.projector import (
    project_case_state_to_retrieval_query,
)
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
from app.services.workflow.worker import (
    RUN_LEASE_DURATION,
    ChatRunWorker,
    ClaimedChatRun,
)


logger = logging.getLogger("app.chat")


def _log_stage(stage_name: str, run_id: UUID | str, detail: str = "") -> None:
    sep = "=" * 70
    msg = f"\n{sep}\n[CHAT RUN {run_id}] ▶ STAGE: {stage_name}"
    if detail:
        msg += f" — {detail}"
    msg += f"\n{sep}"
    print(msg, flush=True)
    logger.info("Chat run %s entering stage: %s %s", run_id, stage_name, detail)


async def process_chat_run(
    run_id: UUID,
    *,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    rag_call: Callable[[str], Awaitable[QueryResponse]] | None = None,
    ask_call: Callable[..., Awaitable[str]] | None = None,
    extraction_adapter: ExtractionModelAdapter | None = None,
) -> None:
    """Process one run in-process; queued work is lost if this process exits."""

    worker_id = f"chat-run:{uuid4()}"
    async with async_session() as claim_db:
        claimed_run = await ChatRunWorker(claim_db).claim_run(run_id, worker_id)

    if claimed_run is None:
        return

    _log_stage(
        "STARTING RUN",
        run_id,
        f"action={claimed_run.post_answer_action or 'initial_query'}",
    )
    followup_metadata_json: dict[str, Any] | None = None
    try:
        if not isinstance(claimed_run.content, str):
            raise ValueError("Chat run request content is not a string")
        if not isinstance(claimed_run.rag_query, str):
            raise ValueError("Chat run RAG query is not a string")
        if not isinstance(claimed_run.original_user_content, str):
            raise ValueError("Chat follow-up root content is not a string")
        if claimed_run.operation != "query":
            raise ValueError("Chat run operation is invalid")

        if claimed_run.post_answer_action == "add_case_info":
            _log_stage("EXTRACTING CASE STATE DELTA", run_id)
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
            delta, mutation_metadata = await run_case_state_delta_extraction(
                delta_input,
                adapter=extraction_adapter,
            )
            followup_metadata_json = {MUTATION_METADATA_KEY: mutation_metadata}
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
                _log_stage("NO CHANGES DETECTED (Skipping RAG)", run_id)
                outcome = map_case_state_no_change_response(
                    mutation_metadata=mutation_metadata,
                )
            else:
                merged_case_state_json = apply_case_state_delta(
                    claimed_run.case_state_json,
                    delta,
                    source_message_id=claimed_run.request_message_id,
                )
                retrieval_query = project_case_state_to_retrieval_query(
                    merged_case_state_json,
                )
                _log_stage("RAG RETRIEVAL (Querying GraphRAG)", run_id)
                response = await (rag_call or request_rag)(retrieval_query)
                rag_context_payload = _validated_rag_context_payload(response)
                analysis_context = rag_context_payload.to_analysis_context()
                _log_stage("ANALYZING UPDATED CASE OVERVIEW", run_id)
                raw_narrative = (
                    claimed_run.raw_case_narrative
                    or (
                        str(claimed_run.original_user_content)
                        if isinstance(claimed_run.original_user_content, str)
                        and claimed_run.original_user_content.strip()
                        and claimed_run.post_answer_action != "add_case_info"
                        else None
                    )
                )
                if (
                    settings.analysis_input_mode == "raw_direct"
                    and (not isinstance(raw_narrative, str) or not raw_narrative.strip())
                ):
                    raise CaseAnalysisFailure(
                        "analysis_context_missing",
                        "The accumulated raw case evidence could not be loaded for mutation in RAW_DIRECT mode",
                    )
                answer = await (ask_call or request_case_analysis)(
                    mode="case_overview",
                    case_state_json=merged_case_state_json,
                    raw_case_narrative=raw_narrative,
                    analysis_context=analysis_context,
                    question=None,
                )
                if not isinstance(answer, str) or not answer.strip():
                    raise CaseAnalysisFailure(
                        "analysis_invalid_response",
                        "The mutation Main Case Analysis returned no answer",
                    )
                extraction_metadata = build_merged_extraction_metadata(
                    merged_case_state_json,
                    source_message_ids=_source_message_ids_for_run(claimed_run),
                    mutation_metadata=mutation_metadata,
                )
                _log_stage("EVALUATING CLARIFICATION & FOLLOWUP POLICY", run_id)
                followup_resolution = await evaluate_followup_outcome(
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
                action = (
                    "clarification_answer"
                    if claimed_run.clarification_answer
                    else "add_case_info"
                )
                if followup_resolution.outcome is not None:
                    outcome = _attach_post_analysis_followup_outcome(
                        followup_resolution.outcome,
                        rag_context_payload=rag_context_payload,
                        validated_case_state_json=merged_case_state_json,
                        extraction_metadata=extraction_metadata,
                        action=action,
                        delta_json=delta.model_dump(mode="json"),
                        expected_parent_case_state_version_id=(
                            claimed_run.case_state_version_id
                        ),
                        mutation_metadata=mutation_metadata,
                    )
                else:
                    followup_metadata_json = {
                        **_mark_followup_rag_invoked_metadata(
                            followup_resolution.metadata_json
                        ),
                        EXTRACTION_METADATA_KEY: extraction_metadata,
                    }
                    outcome = map_case_state_mutation_response(
                        answer.strip(),
                        rag_context_payload=rag_context_payload,
                        merged_case_state_json=merged_case_state_json,
                        delta_json=delta.model_dump(mode="json"),
                        expected_parent_case_state_version_id=(
                            claimed_run.case_state_version_id
                        ),
                        mutation_metadata=mutation_metadata,
                        extraction_metadata=extraction_metadata,
                        followup_metadata_json=followup_metadata_json,
                        action=action,
                    )
            _log_stage("PERSISTING OUTCOME & COMPLETING RUN", run_id)
            async with async_session() as finalize_db:
                await ChatRunWorker(finalize_db).complete_run(
                    run_id,
                    worker_id,
                    outcome,
                )
            print(f"\n[CHAT RUN {run_id}] ✔ RUN COMPLETED SUCCESSFULLY\n{'='*70}\n", flush=True)
            return

        if claimed_run.post_answer_action == "ask":
            _log_stage("ANSWERING QUESTION (ASK Mode)", run_id)
            if not isinstance(claimed_run.case_state_json, dict):
                raise CaseAnalysisFailure(
                    "analysis_context_missing",
                    "The current case state could not be loaded for ASK",
                )
            if not isinstance(claimed_run.analysis_context, dict):
                raise CaseAnalysisFailure(
                    "analysis_context_missing",
                    "The latest completed analysis could not be loaded for ASK",
                )
            raw_narrative = claimed_run.raw_case_narrative
            if (
                settings.analysis_input_mode == "raw_direct"
                and (not isinstance(raw_narrative, str) or not raw_narrative.strip())
            ):
                raise CaseAnalysisFailure(
                    "analysis_context_missing",
                    "The accumulated raw case evidence could not be loaded for ASK in RAW_DIRECT mode",
                )
            answer = await (ask_call or request_case_analysis)(
                mode="question_answer",
                case_state_json=claimed_run.case_state_json,
                raw_case_narrative=raw_narrative,
                analysis_context=claimed_run.analysis_context,
                question=claimed_run.content,
            )
            if not isinstance(answer, str) or not answer.strip():
                raise CaseAnalysisFailure(
                    "analysis_invalid_response",
                    "The post-answer analysis returned no answer",
                )
            outcome = map_case_analysis_response(
                answer.strip(),
                analysis_context=claimed_run.analysis_context,
            )
            _log_stage("PERSISTING ASK OUTCOME", run_id)
            async with async_session() as finalize_db:
                await ChatRunWorker(finalize_db).complete_run(
                    run_id,
                    worker_id,
                    outcome,
                )
            print(f"\n[CHAT RUN {run_id}] ✔ ASK COMPLETED SUCCESSFULLY\n{'='*70}\n", flush=True)
            return

        _log_stage("EXTRACTING BASELINE CASE STATE", run_id)
        validated_case_state_json, extraction_metadata = (
            await run_validated_case_state_extraction(
                claimed_run,
                adapter=extraction_adapter,
            )
        )
        followup_metadata_json = {
            **(followup_metadata_json or {}),
            EXTRACTION_METADATA_KEY: extraction_metadata,
        }
        if validated_case_state_json is None:
            failure_code = extraction_metadata.get(
                "failure_code",
                "extraction_failed",
            )
            failure_message = extraction_metadata.get(
                "failure_message",
                "The extraction did not produce a validated Case State",
            )
            raise ExtractionStageFailure(
                str(failure_code),
                str(failure_message),
                followup_metadata_json,
            )

        _log_stage("RAG RETRIEVAL (Querying GraphRAG)", run_id)
        retrieval_query = project_case_state_to_retrieval_query(
            validated_case_state_json,
        )
        response = await (rag_call or request_rag)(retrieval_query)
        rag_context_payload = _validated_rag_context_payload(response)
        analysis_context = rag_context_payload.to_analysis_context()
        _log_stage("ANALYZING INITIAL CASE OVERVIEW", run_id)
        raw_narrative = (
            claimed_run.raw_case_narrative
            or (str(claimed_run.original_user_content) if isinstance(claimed_run.original_user_content, str) and claimed_run.original_user_content.strip() else None)
            or (str(claimed_run.content) if isinstance(claimed_run.content, str) and claimed_run.content.strip() else None)
        )
        if (
            settings.analysis_input_mode == "raw_direct"
            and (not isinstance(raw_narrative, str) or not raw_narrative.strip())
        ):
            raise CaseAnalysisFailure(
                "analysis_context_missing",
                "The initial raw case narrative could not be loaded in RAW_DIRECT mode",
            )
        answer = await (ask_call or request_case_analysis)(
            mode="case_overview",
            case_state_json=validated_case_state_json,
            raw_case_narrative=raw_narrative,
            analysis_context=analysis_context,
            question=None,
        )
        if not isinstance(answer, str) or not answer.strip():
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The initial Main Case Analysis returned no answer",
            )
        _log_stage("EVALUATING CLARIFICATION & FOLLOWUP POLICY", run_id)
        followup_resolution = await evaluate_followup_outcome(
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
            outcome = _attach_post_analysis_followup_outcome(
                followup_resolution.outcome,
                rag_context_payload=rag_context_payload,
                validated_case_state_json=validated_case_state_json,
                extraction_metadata=extraction_metadata,
                action="initial_analysis",
            )
        else:
            followup_metadata_json = {
                **_mark_followup_rag_invoked_metadata(
                    followup_resolution.metadata_json
                ),
                EXTRACTION_METADATA_KEY: extraction_metadata,
            }
            outcome = map_initial_case_analysis_response(
                answer.strip(),
                rag_context_payload=rag_context_payload,
                validated_case_state_json=validated_case_state_json,
                extraction_metadata=extraction_metadata,
                followup_metadata_json=followup_metadata_json,
            )

        _log_stage("PERSISTING OUTCOME & COMPLETING RUN", run_id)
        async with async_session() as finalize_db:
            await ChatRunWorker(finalize_db).complete_run(
                run_id,
                worker_id,
                outcome,
            )
        print(f"\n[CHAT RUN {run_id}] ✔ INITIAL RUN COMPLETED SUCCESSFULLY\n{'='*70}\n", flush=True)
    except ExtractionStageFailure as exc:
        print(f"\n[CHAT RUN {run_id}] ✖ FAILED AT EXTRACTION STAGE: [{exc.code}] {exc.message}\n{'='*70}\n", flush=True)
        await _record_failure(
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=exc.metadata_json,
        )
    except RagCallFailure as exc:
        print(f"\n[CHAT RUN {run_id}] ✖ FAILED AT RAG RETRIEVAL STAGE: [{exc.code}] {exc.message}\n{'='*70}\n", flush=True)
        await _record_failure(
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=followup_metadata_json,
        )
    except CaseStateMutationFailure as exc:
        print(f"\n[CHAT RUN {run_id}] ✖ FAILED AT MUTATION STAGE: [{exc.code}] {exc.message}\n{'='*70}\n", flush=True)
        await _record_failure(
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=followup_metadata_json,
        )
    except CaseAnalysisFailure as exc:
        print(f"\n[CHAT RUN {run_id}] ✖ FAILED AT ANALYSIS STAGE: [{exc.code}] {exc.message}\n{'='*70}\n", flush=True)
        await _record_failure(
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=followup_metadata_json,
        )
    except Exception as exc:
        print(f"\n[CHAT RUN {run_id}] ✖ FAILED WITH UNEXPECTED ERROR: {exc}\n{'='*70}\n", flush=True)
        await _record_failure(
            run_id,
            worker_id,
            "rag_processing_error",
            "Failed to process chat message",
            followup_metadata_json=followup_metadata_json,
        )


async def _record_failure(
    run_id: UUID,
    worker_id: str,
    error_code: str,
    error_message: str,
    followup_metadata_json: dict[str, Any] | None = None,
) -> None:
    async with async_session() as failure_db:
        await ChatRunWorker(failure_db).fail_run(
            run_id,
            worker_id,
            error_code,
            error_message,
            followup_metadata_json=followup_metadata_json,
        )


def _source_message_ids_for_run(claimed_run: ClaimedChatRun) -> list[UUID]:
    if claimed_run.extraction_input is not None:
        return [
            message.message_id for message in claimed_run.extraction_input.messages
        ]
    if claimed_run.request_message_id is not None:
        return [claimed_run.request_message_id]
    return []


def _attach_post_analysis_followup_outcome(
    outcome: AssistantOutcome,
    *,
    rag_context_payload: RagContextPayload,
    validated_case_state_json: dict[str, object],
    extraction_metadata: dict[str, Any],
    action: str,
    delta_json: dict[str, object] | None = None,
    expected_parent_case_state_version_id: UUID | None = None,
    mutation_metadata: dict[str, Any] | None = None,
) -> AssistantOutcome:
    """Carry the latest analysis artifacts through the pending-follow-up turn."""

    marked = _mark_followup_rag_invoked(outcome, outcome.metadata_json)
    metadata = deepcopy(marked.metadata_json)
    metadata.update(
        {
            EXTRACTION_METADATA_KEY: deepcopy(extraction_metadata),
            "analysis_kind": "grounded_main_analysis",
            "analysis_input_mode": settings.analysis_input_mode,
            "retrieved_context": rag_context_payload.context,
            "mitre_table": deepcopy(list(rag_context_payload.mitre_table)),
            "chat_action": {
                "action": action,
                "route": "analysis",
                "grounded_main_analysis": True,
                "state_mutated": True,
                "case_state_version_created": True,
                "rag_invoked": True,
                "retrieval_context_reused": False,
                "analysis_mode": "case_overview",
                "analysis_input_mode": settings.analysis_input_mode,
                "prompt_version": CASE_ANALYSIS_PROMPT_VERSION,
            },
        }
    )
    if delta_json is not None:
        metadata["case_state_delta"] = deepcopy(delta_json)
    if mutation_metadata is not None:
        metadata["chat_mutation"] = deepcopy(mutation_metadata)
    return replace(
        marked,
        retrieval_context_id=rag_context_payload.retrieval_context_id,
        metadata_json=metadata,
        validated_case_state_json=deepcopy(validated_case_state_json),
        rag_context_payload=rag_context_payload,
        case_state_delta_json=(deepcopy(delta_json) if delta_json is not None else None),
        expected_parent_case_state_version_id=expected_parent_case_state_version_id,
    )


__all__ = [
    "AssistantOutcome",
    "CaseStateDelta",
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
    "RUN_LEASE_DURATION",
    "RagCallFailure",
    "RagContextPayload",
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
