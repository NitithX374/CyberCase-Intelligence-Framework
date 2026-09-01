from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from app.config import settings
from app.services.followup.schemas import ClarificationExchange, GapAnalysis
from app.services.llm.token_budget import (
    estimate_json_tokens,
    estimate_tokens,
    get_safe_input_token_budget,
    log_context_budget_diagnostics,
)


def build_bounded_context(
    *,
    original_user_content: str,
    clarification_exchanges: Sequence[ClarificationExchange],
    raw_evidence: str | None = None,
    analysis_answer: str | None = None,
    analysis_context: Mapping[str, object] | None = None,
    gap_analysis: GapAnalysis | Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build the context payload for Gap Analysis and Follow-up Policy.

    Preserves 100% of authoritative case evidence and clarification history
    whenever the full payload fits within the safe model token budget (~100k tokens).
    """
    exchanges = [
        {
            "workflow_context": {
                key: value
                for key, value in {
                    "requested_gap_id": exchange.gap_id,
                    "requested_gap_topic": exchange.gap_topic,
                    "requested_gap_key": exchange.gap_key,
                    "question_evidence_sha256": exchange.evidence_sha256,
                    "question_message_id": exchange.question_message_id,
                }.items()
                if value is not None
            },
            "assistant_question": exchange.question,
            "user_answer": exchange.answer,
        }
        for exchange in clarification_exchanges
        if exchange.question or exchange.answer
    ]

    normalized_gap_analysis: Any = None
    if isinstance(gap_analysis, GapAnalysis):
        normalized_gap_analysis = gap_analysis.model_dump(mode="json")
    elif gap_analysis is not None:
        normalized_gap_analysis = gap_analysis

    payload: dict[str, object] = {
        "original_user_content": original_user_content,
        "clarification_exchanges": exchanges,
    }
    if normalized_gap_analysis is not None:
        payload["gap_analysis"] = normalized_gap_analysis
    if raw_evidence is not None:
        payload["raw_evidence"] = raw_evidence
    if analysis_answer is not None:
        payload["main_case_analysis"] = analysis_answer
    if analysis_context is not None:
        payload["retrieved_mitre_context"] = dict(analysis_context)

    token_budget = get_safe_input_token_budget()
    estimated_tokens = estimate_json_tokens(payload)

    if estimated_tokens <= token_budget:
        log_context_budget_diagnostics(
            feature="followup_bounded_context",
            estimated_input_tokens=estimated_tokens,
            configured_input_token_budget=token_budget,
            raw_evidence=raw_evidence or original_user_content,
            external_context=analysis_context,
            context_truncated=False,
            retained_evidence_ratio=1.0,
            retained_external_context_ratio=1.0,
        )
        return payload

    # Overflow path: apply prioritized reduction
    return _build_overflow_followup_context(
        original_user_content=original_user_content,
        exchanges=exchanges,
        raw_evidence=raw_evidence,
        gap_analysis=normalized_gap_analysis,
        analysis_answer=analysis_answer,
        analysis_context=analysis_context,
        token_budget=token_budget,
    )


def _build_overflow_followup_context(
    *,
    original_user_content: str,
    exchanges: list[dict[str, object]],
    raw_evidence: str | None,
    gap_analysis: Any,
    analysis_answer: str | None,
    analysis_context: Mapping[str, object] | None,
    token_budget: int,
) -> dict[str, object]:
    """Reduce optional context before authoritative evidence during overflow."""
    base_payload: dict[str, object] = {
        "original_user_content": original_user_content,
        "clarification_exchanges": exchanges,
        "context_truncated": True,
    }
    if gap_analysis is not None:
        base_payload["gap_analysis"] = gap_analysis
    if raw_evidence is not None:
        base_payload["raw_evidence"] = raw_evidence

    # Attempt 1: Full evidence + gap analysis + main_case_analysis (no external MITRE context)
    candidate = dict(base_payload)
    if analysis_answer is not None:
        candidate["main_case_analysis"] = analysis_answer

    if estimate_json_tokens(candidate) <= token_budget:
        # Full evidence fits! Squeeze as much retrieved MITRE context as possible.
        if analysis_context:
            context_dict = dict(analysis_context)
            candidate["retrieved_mitre_context"] = _bounded_mapping(
                context_dict,
                limit=max(100, (token_budget - estimate_json_tokens(candidate)) * 4),
            )
        log_context_budget_diagnostics(
            feature="followup_bounded_context_overflow",
            estimated_input_tokens=estimate_json_tokens(candidate),
            configured_input_token_budget=token_budget,
            raw_evidence=raw_evidence or original_user_content,
            external_context=candidate.get("retrieved_mitre_context"),
            context_truncated=True,
            retained_evidence_ratio=1.0,
            retained_external_context_ratio=0.5,
        )
        return candidate

    # Attempt 2: Full evidence + gap analysis (no analysis_answer, no external context)
    if estimate_json_tokens(base_payload) <= token_budget:
        log_context_budget_diagnostics(
            feature="followup_bounded_context_overflow",
            estimated_input_tokens=estimate_json_tokens(base_payload),
            configured_input_token_budget=token_budget,
            raw_evidence=raw_evidence or original_user_content,
            external_context=None,
            context_truncated=True,
            retained_evidence_ratio=1.0,
            retained_external_context_ratio=0.0,
        )
        return base_payload

    # Attempt 3: Evidence itself must be reduced (last resort)
    evidence_text = raw_evidence or original_user_content
    low, high = 0, len(evidence_text)
    best_candidate = dict(base_payload)
    if raw_evidence is not None:
        best_candidate["raw_evidence"] = ""
    else:
        best_candidate["original_user_content"] = ""

    while low <= high:
        mid = (low + high) // 2
        test = dict(base_payload)
        if raw_evidence is not None:
            test["raw_evidence"] = evidence_text[:mid]
        else:
            test["original_user_content"] = evidence_text[:mid]
        if estimate_json_tokens(test) <= token_budget:
            best_candidate = test
            low = mid + 1
        else:
            high = mid - 1

    log_context_budget_diagnostics(
        feature="followup_bounded_context_overflow",
        estimated_input_tokens=estimate_json_tokens(best_candidate),
        configured_input_token_budget=token_budget,
        raw_evidence=str(best_candidate.get("raw_evidence") or best_candidate.get("original_user_content")),
        external_context=None,
        context_truncated=True,
        retained_evidence_ratio=len(str(best_candidate.get("raw_evidence") or best_candidate.get("original_user_content"))) / max(1, len(evidence_text)),
        retained_external_context_ratio=0.0,
    )
    return best_candidate


def _bounded(value: str, limit: int) -> str:
    return value[: max(0, limit)]


def _bounded_mapping(
    value: Mapping[str, object],
    limit: int,
) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, item in value.items():
        if isinstance(item, str):
            output[str(key)] = _bounded(item, max(1, limit // 4))
        elif isinstance(item, Mapping):
            output[str(key)] = _bounded_mapping(item, max(1, limit // 2))
        elif isinstance(item, list):
            output[str(key)] = [
                _bounded_mapping(entry, max(1, limit // 4))
                if isinstance(entry, Mapping)
                else (
                    _bounded(entry, max(1, limit // 4))
                    if isinstance(entry, str)
                    else entry
                )
                for entry in item[:32]
            ]
        else:
            output[str(key)] = item

    serialized = json.dumps(output, ensure_ascii=False, default=str)
    if len(serialized) <= limit:
        return output
    return {
        "truncated": True,
        "serialized_context": serialized[: max(1, limit - 32)],
    }


__all__ = ["build_bounded_context"]
