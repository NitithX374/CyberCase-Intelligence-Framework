from __future__ import annotations

import asyncio
import inspect
import json
import re
import time
import unicodedata
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import replace
from typing import TYPE_CHECKING, Any
from uuid import UUID

import httpx

from app.config import settings
from app.services.followup.prompts import FOLLOWUP_POLICY_VERSION, FOLLOWUP_PROMPT_VERSION, GAP_ANALYSIS_PROMPT_VERSION, GAP_ANALYSIS_VERSION
from app.services.followup.schemas import GapAnalysis, GapAnalysisResult, GapItem, FollowUpDecision, FollowUpPolicyResult
from app.services.llm.core_llm import resolve_core_llm_target

if TYPE_CHECKING:
    from app.services.workflow.outcome import AssistantOutcome

async def _invoke_policy_method(
    method: Any,
    kwargs: dict[str, object],
) -> object:
    """Call old test/custom policies without dropping new completeness context."""

    try:
        parameters = inspect.signature(method).parameters
    except (TypeError, ValueError):
        parameters = {}
    accepts_kwargs = any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    if not accepts_kwargs and parameters:
        kwargs = {key: value for key, value in kwargs.items() if key in parameters}
    return await method(**kwargs)


def _coerce_gap_analysis_result(
    raw_result: object,
    *,
    elapsed_ms: float,
) -> GapAnalysisResult:
    if isinstance(raw_result, GapAnalysisResult):
        return GapAnalysisResult(
            analysis=_normalize_gap_analysis_semantics(
                GapAnalysis.model_validate(raw_result.analysis)
            ),
            latency_ms=(
                raw_result.latency_ms
                if raw_result.latency_ms is not None
                else elapsed_ms
            ),
            input_tokens=_safe_token_count(raw_result.input_tokens),
            output_tokens=_safe_token_count(raw_result.output_tokens),
            provider=raw_result.provider,
            model=raw_result.model,
        )
    return GapAnalysisResult(
        analysis=_normalize_gap_analysis_semantics(
            GapAnalysis.model_validate(raw_result)
        ),
        latency_ms=elapsed_ms,
    )


def _normalize_gap_analysis_semantics(analysis: GapAnalysis) -> GapAnalysis:
    return GapAnalysis(
        gaps=[
            GapItem.model_validate(
                {
                    **gap.model_dump(mode="json"),
                    "status": "NOT_PROVIDED",
                }
            )
            if gap.status == "EXPLICITLY_UNKNOWN" and gap.askable
            else gap
            for gap in analysis.gaps
        ]
    )


def _empty_gap_analysis_trace(
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


def _gap_analysis_trace(result: GapAnalysisResult) -> dict[str, Any]:
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


def _required_material_gap(analysis: GapAnalysis) -> GapItem | None:
    return next(
        (
            gap
            for gap in analysis.gaps
            if gap.priority == "high"
            and gap.askable
            and gap.status in ("NOT_PROVIDED", "AMBIGUOUS", "CONFLICTING")
        ),
        None,
    )


def _required_gap_question(original_user_content: str, gap: GapItem) -> str:
    topic = gap.topic.strip().rstrip(" ?？")[:180].rstrip()
    if re.search(r"[\u0E00-\u0E7F]", original_user_content):
        return f"กรุณาให้ข้อมูลเพิ่มเติมเกี่ยวกับ {topic} ได้หรือไม่?"
    return f"Could you provide the missing case information about {topic}?"


def _selected_askable_gap(
    analysis: GapAnalysis,
    selected_gap: str | None,
    *,
    compatibility: bool,
) -> GapItem | None:
    if not isinstance(selected_gap, str) or not selected_gap.strip():
        return None
    if compatibility:
        return GapItem(
            topic=selected_gap,
            status="NOT_PROVIDED",
            description="Legacy policy supplied a selected follow-up topic.",
            affects="The legacy follow-up policy contract.",
            reason="Retained only for compatibility with injected policies.",
            priority="high",
            askable=True,
        )
    normalized = _normalized_question(selected_gap)
    eligible_gaps = [
        gap
        for gap in analysis.gaps
        if (
            gap.priority in ("high", "medium")
            and gap.askable
            and gap.status != "EXPLICITLY_UNKNOWN"
        )
    ]
    if not eligible_gaps:
        return None
    priority_rank = {"high": 2, "medium": 1}
    highest_priority = max(priority_rank[gap.priority] for gap in eligible_gaps)
    for gap in analysis.gaps:
        if _normalized_question(gap.topic) != normalized:
            continue
        if (
            gap.priority not in ("high", "medium")
            or not gap.askable
            or gap.status == "EXPLICITLY_UNKNOWN"
            or priority_rank[gap.priority] != highest_priority
        ):
            return None
        return gap
    return None


def _gap_reason_code(gap: GapItem) -> str:
    return {
        "NOT_PROVIDED": "material_incident_fact_missing",
        "AMBIGUOUS": "material_incident_fact_ambiguous",
        "CONFLICTING": "material_incident_fact_conflicting",
        "EXPLICITLY_UNKNOWN": "unresolved_gaps_recorded",
    }[gap.status]


def _coerce_policy_result(
    raw_result: object,
    *,
    elapsed_ms: float,
) -> FollowUpPolicyResult:
    if isinstance(raw_result, FollowUpPolicyResult):
        return FollowUpPolicyResult(
            decision=FollowUpDecision.model_validate(raw_result.decision),
            latency_ms=(
                raw_result.latency_ms
                if raw_result.latency_ms is not None
                else elapsed_ms
            ),
            input_tokens=_safe_token_count(raw_result.input_tokens),
            output_tokens=_safe_token_count(raw_result.output_tokens),
            provider=raw_result.provider,
            model=raw_result.model,
        )
    return FollowUpPolicyResult(
        decision=FollowUpDecision.model_validate(raw_result),
        latency_ms=elapsed_ms,
    )


def _safe_token_count(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def _followup_failure_code(error: Exception) -> str:
    if isinstance(error, (asyncio.TimeoutError, httpx.TimeoutException)):
        return "policy_timeout"
    if isinstance(error, (json.JSONDecodeError, ValueError, TypeError)):
        return "policy_invalid_output"
    return "policy_error"


def _followup_metadata(
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
    gap_analysis: dict[str, Any] | None = None,
    rag_skipped: bool = True,
    rag_invoked: bool = False,
) -> dict[str, Any]:
    target = resolve_core_llm_target(
        settings.chat_followup_policy_model,
        require_key=False,
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
            "gap_analysis": deepcopy(
                gap_analysis or _empty_gap_analysis_trace()
            ),
            "rag_skipped": rag_skipped,
            "rag_invoked": rag_invoked,
        }
    }


def _mark_followup_rag_invoked(
    outcome: AssistantOutcome,
    metadata_json: dict[str, Any],
) -> AssistantOutcome:
    merged_metadata = _mark_followup_rag_invoked_metadata(metadata_json)
    if not merged_metadata:
        return outcome
    output_metadata = dict(outcome.metadata_json)
    output_metadata["chat_followup"] = merged_metadata["chat_followup"]
    return replace(outcome, metadata_json=output_metadata)


def _mark_followup_rag_invoked_metadata(
    metadata_json: dict[str, Any],
) -> dict[str, Any]:
    trace = metadata_json.get("chat_followup")
    if not isinstance(trace, dict):
        return {}
    return {
        **metadata_json,
        "chat_followup": {
            **trace,
            "rag_skipped": False,
            "rag_invoked": True,
        },
    }


def _normalized_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKC", question)
    normalized = " ".join(normalized.split()).casefold()
    while normalized and unicodedata.category(normalized[-1]).startswith("P"):
        normalized = normalized[:-1].rstrip()
    return normalized
