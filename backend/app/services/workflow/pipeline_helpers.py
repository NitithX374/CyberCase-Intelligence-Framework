from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import replace
from typing import Any
from uuid import UUID

from app.config import settings
from app.services.case_analysis import CASE_ANALYSIS_PROMPT_VERSION
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.case_analysis.service import CaseAnalysisFailure
from app.services.extraction import EXTRACTION_METADATA_KEY
from app.services.followup.gate import _mark_followup_rag_invoked
from app.services.workflow.outcome import AssistantOutcome, RagContextPayload
from app.services.workflow.worker import ClaimedChatRun


logger = logging.getLogger("app.chat")


def log_stage(stage_name: str, run_id: UUID | str, detail: str = "") -> None:
    separator = "=" * 70
    message = f"\n{separator}\n[CHAT RUN {run_id}] ▶ STAGE: {stage_name}"
    if detail:
        message += f" — {detail}"
    message += f"\n{separator}"
    print(message, flush=True)
    logger.info("Chat run %s entering stage: %s %s", run_id, stage_name, detail)


def source_message_ids_for_run(claimed_run: ClaimedChatRun) -> list[UUID]:
    if claimed_run.extraction_input is not None:
        return [message.message_id for message in claimed_run.extraction_input.messages]
    if claimed_run.request_message_id is not None:
        return [claimed_run.request_message_id]
    return []


def coerce_analysis_result(value: object) -> CaseAnalysisResult:
    if isinstance(value, CaseAnalysisResult):
        answer = value.answer.strip()
        if not answer:
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The Main Case Analysis returned no answer",
            )
        if answer == value.answer:
            return value
        return CaseAnalysisResult(
            answer=answer,
            trace=value.trace,
            trace_failure=value.trace_failure,
        )
    if isinstance(value, str) and value.strip():
        return CaseAnalysisResult(answer=value.strip(), trace=None)
    raise CaseAnalysisFailure(
        "analysis_invalid_response",
        "The Main Case Analysis returned no answer",
    )


def attach_post_analysis_followup_outcome(
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
