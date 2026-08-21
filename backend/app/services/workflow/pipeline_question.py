from __future__ import annotations

from typing import Any, Callable

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure
from app.services.workflow.outcome import AssistantOutcome, map_case_analysis_response
from app.services.workflow.pipeline_helpers import coerce_analysis_result, log_stage
from app.services.workflow.worker import ClaimedChatRun


async def run_question_stage(
    claimed_run: ClaimedChatRun,
    *,
    analysis_request: Callable[..., Any],
) -> AssistantOutcome:
    run_id = claimed_run.id
    log_stage("ANSWERING QUESTION (ASK Mode)", run_id)
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
    analysis_result = coerce_analysis_result(
        await analysis_request(
            mode="question_answer",
            case_state_json=claimed_run.case_state_json,
            raw_case_narrative=raw_narrative,
            analysis_context=claimed_run.analysis_context,
            question=claimed_run.content,
            user_message=claimed_run.content,
        )
    )
    return map_case_analysis_response(
        analysis_result.answer,
        analysis_context=claimed_run.analysis_context,
        analysis_trace_draft=analysis_result.trace,
        analysis_trace_failure=analysis_result.trace_failure,
        expected_case_state_version_id=claimed_run.case_state_version_id,
    )
