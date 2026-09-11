from __future__ import annotations

import asyncio
import json
import unicodedata

import httpx

from collections.abc import Mapping

_VISIBLE_TEXT_BLOCK_TYPES = frozenset(
    {"text", "output_text", "message", "thought_text"}
)


def _extract_text_value(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_extract_text_value(item) for item in value)
    if not isinstance(value, Mapping):
        return ""

    block_type = value.get("type")
    if block_type in {"thinking", "redacted_thinking", "reasoning"}:
        return ""
    if block_type in _VISIBLE_TEXT_BLOCK_TYPES:
        text = value.get("text")
        if isinstance(text, str):
            return text

    text = value.get("text")
    if isinstance(text, str) and block_type in {None, "message", "output_text"}:
        return text

    nested_content = value.get("content")
    if nested_content is not None:
        nested = _extract_text_value(nested_content)
        if nested:
            return nested

    message = value.get("message")
    if message is not None:
        return _extract_text_value(message)

    return ""


def _extract_llm_text(payload: Mapping[str, object] | object) -> str:
    """Extract raw text across supported provider response shapes (Anthropic, OpenRouter, etc.)."""
    if not isinstance(payload, Mapping):
        return ""

    direct_output = payload.get("output_text")
    if isinstance(direct_output, str) and direct_output.strip():
        return direct_output

    content = payload.get("content")
    if content is not None:
        extracted = _extract_text_value(content)
        if extracted.strip():
            return extracted

    choices = payload.get("choices")
    if isinstance(choices, list):
        extracted = _extract_text_value(choices)
        if extracted.strip():
            return extracted

    output = payload.get("output")
    if output is not None:
        extracted = _extract_text_value(output)
        if extracted.strip():
            return extracted

    return ""


def _extract_llm_json(raw: str) -> dict[str, object]:
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("LLM response text is empty")
    candidates = [cleaned]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start and cleaned[start : end + 1] != cleaned:
        candidates.append(cleaned[start : end + 1])
    errors: list[ValueError] = []
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except ValueError as error:
            errors.append(error)
            continue
        if not isinstance(data, dict):
            raise ValueError("LLM structured response must be an object")
        return data
    raise ValueError("Could not parse valid JSON object from LLM response") from errors[
        -1
    ]


extractLlmText = _extract_llm_text
extractLlmJson = _extract_llm_json
from app.services.followup.contracts import (
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
    FollowUpDecision,
    FollowUpPolicyResult,
)


def coerceGapAnalysisResult(
    raw_result: object,
    *,
    elapsed_ms: float,
) -> GapAnalysisResult:
    if isinstance(raw_result, GapAnalysisResult):
        return GapAnalysisResult(
            analysis=normalizeGapAnalysisSemantics(
                GapAnalysis.model_validate(raw_result.analysis)
            ),
            latency_ms=(
                raw_result.latency_ms
                if raw_result.latency_ms is not None
                else elapsed_ms
            ),
            input_tokens=countTokensSafely(raw_result.input_tokens),
            output_tokens=countTokensSafely(raw_result.output_tokens),
            provider=raw_result.provider,
            model=raw_result.model,
        )
    return GapAnalysisResult(
        analysis=normalizeGapAnalysisSemantics(
            GapAnalysis.model_validate(raw_result)
        ),
        latency_ms=elapsed_ms,
    )


def normalizeGapAnalysisSemantics(analysis: GapAnalysis) -> GapAnalysis:
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


def resolveGapReasonCode(gap: GapItem) -> str:
    return {
        "NOT_PROVIDED": "material_incident_fact_missing",
        "AMBIGUOUS": "material_incident_fact_ambiguous",
        "CONFLICTING": "material_incident_fact_conflicting",
        "EXPLICITLY_UNKNOWN": "unresolved_gaps_recorded",
    }[gap.status]


def coercePolicyResult(
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
            input_tokens=countTokensSafely(raw_result.input_tokens),
            output_tokens=countTokensSafely(raw_result.output_tokens),
            provider=raw_result.provider,
            model=raw_result.model,
        )
    return FollowUpPolicyResult(
        decision=FollowUpDecision.model_validate(raw_result),
        latency_ms=elapsed_ms,
    )


def countTokensSafely(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def resolveFollowupFailureCode(error: Exception) -> str:
    if isinstance(error, (asyncio.TimeoutError, httpx.TimeoutException)):
        return "policy_timeout"
    if isinstance(error, (json.JSONDecodeError, ValueError, TypeError)):
        return "policy_invalid_output"
    return "policy_error"


def normalizeQuestion(question: str) -> str:
    normalized = unicodedata.normalize("NFKC", question)
    return " ".join(normalized.strip().split())


# Backward compatibility aliases
_coerce_gap_analysis_result = coerceGapAnalysisResult
_normalize_gap_analysis_semantics = normalizeGapAnalysisSemantics
_gap_reason_code = resolveGapReasonCode
_coerce_policy_result = coercePolicyResult
_safe_token_count = countTokensSafely
_followup_failure_code = resolveFollowupFailureCode
_normalized_question = normalizeQuestion

__all__ = [
    "_extract_llm_json",
    "_extract_llm_text",
    "coerceGapAnalysisResult",
    "coercePolicyResult",
    "countTokensSafely",
    "extractLlmJson",
    "extractLlmText",
    "normalizeGapAnalysisSemantics",
    "normalizeQuestion",
    "resolveFollowupFailureCode",
    "resolveGapReasonCode",
]
