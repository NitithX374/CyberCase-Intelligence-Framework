from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from app.config import settings
from app.services.case_analysis.contracts import AnalysisGapV3, AnalysisTraceV3
from app.services.followup.contracts import FollowUpResolution
from app.services.followup.gap_stage import GapStageResult, run_gap_analysis_stage
from app.services.followup.policy import AnthropicFollowUpPolicy
from app.services.followup.schemas import (
    ClarificationExchange,
    GapAnalysis,
    GapAnalyzer,
    FollowUpPolicy,
)
from app.services.followup.helpers import (
    _coerce_policy_result as coerce_policy_result,
    _followup_failure_code as followup_failure_code,
    _gap_reason_code as gap_reason_code,
    _invoke_policy_method as invoke_policy_method,
    _normalized_question as normalized_question,
)
from app.services.followup.metadata import empty_gap_analysis_trace, followup_metadata
from app.services.followup.stateful import (
    followup_context,
    normalize_gap_key,
    policy_gap,
    relevant_claim_context,
    select_next_gap,
)

logger = logging.getLogger("app.chat")


async def evaluate_followup_outcome(
    *,
    original_user_content: str,
    clarification_exchanges: Sequence[ClarificationExchange],
    followup_root_ordinal: int,
    source_run_id: UUID,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    raw_evidence: str | None = None,
    analysis_answer: str | None = None,
    analysis_context: Mapping[str, object] | None = None,
    analysis_claims: Sequence[Mapping[str, object]] | None = None,
    canonical_trace: AnalysisTraceV3 | None = None,
    precomputed_gap_stage: GapStageResult | None = None,
    evidence_sha256: str | None = None,
    canonical_state_required: bool = False,
) -> FollowUpResolution:
    round_number = len(clarification_exchanges) + 1
    prior_exchange_count = len(clarification_exchanges)
    gap_trace = empty_gap_analysis_trace()
    canonical_gap_analysis: GapAnalysis | None = None

    def proceed_resolution(
        *,
        reason_code: str,
        stop_reason: str,
        **metadata_kwargs: Any,
    ) -> FollowUpResolution:
        return FollowUpResolution(
            question=None,
            metadata_json=followup_metadata(
                source_run_id=source_run_id,
                followup_root_ordinal=followup_root_ordinal,
                round_number=round_number,
                prior_exchange_count=prior_exchange_count,
                action="proceed",
                question="",
                reason_code=reason_code,
                stop_reason=stop_reason,
                gap_analysis=gap_trace,
                **metadata_kwargs,
            ),
            gap_analysis=canonical_gap_analysis,
        )

    def ask_resolution(
        *,
        selected_gap,
        question: str,
        reason_code: str,
        stop_reason: str,
        decision_source: str,
        policy_decision: str,
        **metadata_kwargs: Any,
    ) -> FollowUpResolution:
        metadata = followup_metadata(
            source_run_id=source_run_id,
            followup_root_ordinal=followup_root_ordinal,
            round_number=round_number,
            prior_exchange_count=prior_exchange_count,
            action="ask_followup",
            question=question,
            reason_code=reason_code,
            stop_reason=stop_reason,
            decision="ask_followup",
            decision_source=decision_source,
            policy_decision=policy_decision,
            selected_gap=selected_gap.topic,
            selected_gap_detail=selected_gap.model_dump(mode="json"),
            followup_context=followup_context(
                selected_gap,
                evidence_sha256=evidence_sha256,
            ),
            gap_analysis=gap_trace,
            rag_skipped=True,
            **metadata_kwargs,
        )
        return FollowUpResolution(
            question=question,
            metadata_json=metadata,
            gap_analysis=canonical_gap_analysis,
        )

    gap_stage = precomputed_gap_stage
    if gap_stage is not None:
        gap_trace = gap_stage.metadata
        canonical_gap_analysis = gap_stage.canonical_analysis
    if canonical_state_required and canonical_trace is None:
        return proceed_resolution(
            reason_code="canonical_state_unavailable",
            stop_reason="canonical_state_unavailable",
        )
    if gap_stage is None:
        gap_stage = await run_gap_analysis_stage(
            original_user_content=original_user_content,
            clarification_exchanges=clarification_exchanges,
            policy=policy,
            gap_analyzer=gap_analyzer,
            raw_evidence=raw_evidence,
            analysis_answer=analysis_answer,
            analysis_context=analysis_context,
            analysis_claims=analysis_claims,
            source_run_id=source_run_id,
        )
    gap_result = gap_stage.policy_input
    gap_trace = gap_stage.metadata
    canonical_gap_analysis = gap_stage.canonical_analysis
    if gap_stage.failure_code is not None:
        return proceed_resolution(
            reason_code="gap_analysis_failed_open",
            stop_reason="gap_analysis_failed_open",
            latency_ms=gap_stage.latency_ms,
            failure_code=gap_stage.failure_code,
        )
    if not settings.chat_followup_policy_enabled:
        return proceed_resolution(
            reason_code="followup_policy_disabled",
            stop_reason="policy_disabled",
        )
    if len(clarification_exchanges) >= settings.chat_followup_max_rounds:
        return proceed_resolution(
            reason_code="max_rounds_reached",
            stop_reason="max_rounds_reached",
        )
    candidate = select_next_gap(
        canonical_trace.gaps
        if canonical_trace is not None
        else gap_result.analysis.gaps,
        clarification_exchanges,
    )
    if candidate is None:
        return proceed_resolution(
            reason_code=(
                "unresolved_gaps_recorded"
                if gap_result.analysis.gaps
                else "sufficient_case_context"
            ),
            stop_reason="no_eligible_canonical_gap",
        )
    selected_gap = policy_gap(candidate)
    selected_gap_analysis = GapAnalysis(gaps=[selected_gap])
    question_context = analysis_context
    question_analysis = analysis_answer
    if canonical_trace is not None and isinstance(candidate, AnalysisGapV3):
        question_context = relevant_claim_context(canonical_trace, candidate)
        question_analysis = canonical_trace.summary
    started = time.perf_counter()
    try:
        active_policy = (
            policy()
            if isinstance(policy, type)
            else (policy or AnthropicFollowUpPolicy())
        )
        policy_kwargs = {
            "original_user_content": original_user_content,
            "clarification_exchanges": clarification_exchanges,
            "gap_analysis": selected_gap_analysis,
            "raw_evidence": raw_evidence,
            "analysis_answer": question_analysis,
            "analysis_context": question_context,
        }
        if hasattr(active_policy, "decide_with_metadata") and callable(
            getattr(active_policy, "decide_with_metadata")
        ):
            raw_result = await invoke_policy_method(
                active_policy.decide_with_metadata,
                policy_kwargs,
            )
        else:
            raw_result = await invoke_policy_method(
                active_policy.decide,
                policy_kwargs,
            )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        result = coerce_policy_result(raw_result, elapsed_ms=elapsed_ms)
        decision = result.decision
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        failure_code = followup_failure_code(exc)
        logger.warning(
            "Chat follow-up policy failed open source_run_id=%s failure_code=%s error=%s",
            source_run_id,
            failure_code,
            exc,
            exc_info=True,
        )
        return proceed_resolution(
            reason_code="policy_failed_open",
            stop_reason="policy_failed_open",
            latency_ms=elapsed_ms,
            failure_code=failure_code,
        )
    if decision.decision == "proceed":
        return proceed_resolution(
            reason_code=decision.reason_code or "unresolved_gaps_recorded",
            stop_reason="question_generation_proceed",
            decision=decision.decision,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            provider=result.provider,
            model=result.model,
        )
    if normalize_gap_key(decision.selected_gap or "") != normalize_gap_key(
        selected_gap.topic
    ):
        return proceed_resolution(
            reason_code="policy_invalid_selection",
            stop_reason="policy_invalid_selection",
            decision="proceed",
            requested_selected_gap=decision.selected_gap,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            provider=result.provider,
            model=result.model,
        )
    normalized_decision_question = normalized_question(decision.question)
    if any(
        normalized_question(exchange.question) == normalized_decision_question
        for exchange in clarification_exchanges
    ):
        return proceed_resolution(
            reason_code="duplicate_question",
            stop_reason="duplicate_question",
            decision="proceed",
            selected_gap=selected_gap.topic,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            provider=result.provider,
            model=result.model,
        )

    return ask_resolution(
        selected_gap=candidate,
        question=decision.question,
        reason_code=decision.reason_code or gap_reason_code(candidate),
        stop_reason="ask_followup",
        decision_source="provider_policy",
        policy_decision=decision.decision,
        latency_ms=result.latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        provider=result.provider,
        model=result.model,
    )


__all__ = ["evaluate_followup_outcome"]
