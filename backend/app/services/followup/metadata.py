from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID

from app.config import settings
from app.services.followup.prompts import (
    FOLLOWUP_POLICY_VERSION,
    FOLLOWUP_PROMPT_VERSION,
    GAP_ANALYSIS_PROMPT_VERSION,
    GAP_ANALYSIS_VERSION,
)
from app.services.followup.schemas import GapAnalysisResult
from app.services.llm.core_llm import resolve_core_llm_target


def empty_gap_analysis_trace(
    *,
    status: str = "not_run",
    latency_ms: float | None = None,
    failure_code: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "version": GAP_ANALYSIS_VERSION,
        "prompt_version": GAP_ANALYSIS_PROMPT_VERSION,
        "gaps": [],
        "latency_ms": latency_ms,
        "input_tokens": None,
        "output_tokens": None,
        "provider": None,
        "model": None,
        "failure_code": failure_code,
    }


def gap_analysis_trace(result: GapAnalysisResult) -> dict[str, Any]:
    return {
        "status": "completed",
        "version": GAP_ANALYSIS_VERSION,
        "prompt_version": GAP_ANALYSIS_PROMPT_VERSION,
        "gaps": [gap.model_dump(mode="json") for gap in result.analysis.gaps],
        "latency_ms": result.latency_ms,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "provider": result.provider,
        "model": result.model,
        "failure_code": None,
    }


def followup_metadata(
    *,
    source_run_id: UUID,
    followup_root_ordinal: int,
    round_number: int,
    prior_exchange_count: int,
    action: str,
    question: str,
    reason_code: str,
    stop_reason: str,
    latency_ms: float | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    provider: str | None = None,
    model: str | None = None,
    failure_code: str | None = None,
    decision: str | None = None,
    decision_source: str | None = None,
    policy_decision: str | None = None,
    selected_gap: str | None = None,
    selected_gap_detail: dict[str, Any] | None = None,
    requested_selected_gap: str | None = None,
    followup_context: dict[str, str] | None = None,
    gap_analysis: dict[str, Any] | None = None,
    rag_skipped: bool = True,
    rag_invoked: bool = False,
) -> dict[str, Any]:
    target = resolve_core_llm_target(
        settings.chat_followup_policy_model, require_key=False
    )
    return {
        "chat_followup": {
            "kind": "clarification" if action == "ask_followup" else "decision",
            "policy_version": FOLLOWUP_POLICY_VERSION,
            "prompt_version": FOLLOWUP_PROMPT_VERSION,
            "provider": provider or target.provider,
            "model": model or target.model,
            "action": action,
            "decision": decision or action,
            "decision_source": decision_source,
            "policy_decision": policy_decision,
            "question": question,
            "selected_gap": selected_gap,
            "selected_gap_detail": deepcopy(selected_gap_detail),
            "requested_selected_gap": requested_selected_gap,
            "followup_context": deepcopy(followup_context),
            "reason_code": reason_code,
            "source_run_id": str(source_run_id),
            "root_ordinal": followup_root_ordinal,
            "round": round_number,
            "prior_exchange_count": prior_exchange_count,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "failure_code": failure_code,
            "stop_reason": stop_reason,
            "gap_analysis": deepcopy(gap_analysis or empty_gap_analysis_trace()),
            "rag_skipped": rag_skipped,
            "rag_invoked": rag_invoked,
        }
    }
