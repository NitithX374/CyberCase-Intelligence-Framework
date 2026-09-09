from __future__ import annotations

import asyncio
import json

import unicodedata

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
