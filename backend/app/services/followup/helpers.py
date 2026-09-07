from __future__ import annotations

import asyncio
import inspect
import json
import re
import unicodedata
from typing import Any

import httpx

from app.services.followup.response_content import (
    _extract_llm_text as _extract_llm_text,
    _extract_llm_json as _extract_llm_json,
)
from app.services.followup.schemas import (
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
    FollowUpDecision,
    FollowUpPolicyResult,
)


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


def _normalized_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKC", question)
    normalized = " ".join(normalized.split()).casefold()
    while normalized and unicodedata.category(normalized[-1]).startswith("P"):
        normalized = normalized[:-1].rstrip()
    return normalized
