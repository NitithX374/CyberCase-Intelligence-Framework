from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.config import settings
from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.followup.contracts import (
    ClarificationExchange,
    FollowUpPolicy,
    FollowUpResolution,
)
from app.services.followup.helpers import (
    coercePolicyResult,
    normalizeQuestion,
    resolveFollowupFailureCode,
    resolveGapReasonCode,
)
from app.services.followup.metadata import followup_metadata
from app.services.followup.policy import AnthropicFollowUpPolicy
from app.services.followup.stateful import (
    apply_clarification_history,
    followup_context,
    normalize_gap_key,
    select_next_gap,
)

logger = logging.getLogger("app.chat")


async def evaluate_followup_outcome(
    *,
    clarification_exchanges: Sequence[ClarificationExchange],
    followup_root_ordinal: int,
    source_run_id: UUID,
    policy: FollowUpPolicy | None = None,
    canonical_trace: CaseAnalysisTrace | None = None,
) -> FollowUpResolution:
    round_number = len(clarification_exchanges) + 1
    prior_exchange_count = len(clarification_exchanges)

    def resolution(
        *,
        action: str,
        reason_code: str,
        stop_reason: str,
        **metadata_kwargs: Any,
    ) -> FollowUpResolution:
        return FollowUpResolution(
            question=metadata_kwargs.pop("question", None),
            metadata_json=followup_metadata(
                source_run_id=source_run_id,
                followup_root_ordinal=followup_root_ordinal,
                round_number=round_number,
                prior_exchange_count=prior_exchange_count,
                action=action,
                question=metadata_kwargs.pop("metadata_question", ""),
                reason_code=reason_code,
                stop_reason=stop_reason,
                **metadata_kwargs,
            ),
        )

    if canonical_trace is None:
        return resolution(
            action="proceed",
            reason_code="canonical_state_unavailable",
            stop_reason="canonical_state_unavailable",
        )

    canonical_gaps = apply_clarification_history(
        canonical_trace.gaps,
        clarification_exchanges,
    )
    if not settings.chat_followup_policy_enabled:
        return resolution(
            action="proceed",
            reason_code="followup_policy_disabled",
            stop_reason="policy_disabled",
        )
    if len(clarification_exchanges) >= settings.chat_followup_max_rounds:
        return resolution(
            action="proceed",
            reason_code="max_rounds_reached",
            stop_reason="max_rounds_reached",
        )

    candidate = select_next_gap(canonical_gaps, clarification_exchanges)
    if candidate is None:
        reason_code = (
            "unresolved_gaps_recorded"
            if canonical_gaps
            else "sufficient_case_context"
        )
        return resolution(
            action="proceed",
            reason_code=reason_code,
            stop_reason="no_eligible_canonical_gap",
        )

    started = time.perf_counter()
    try:
        active_policy = policy() if isinstance(policy, type) else (policy or AnthropicFollowUpPolicy())
        policy_kwargs = {"selected_gap": candidate}
        if hasattr(active_policy, "decide_with_metadata"):
            raw_result = await active_policy.decide_with_metadata(**policy_kwargs)
        else:
            raw_result = await active_policy.decide(**policy_kwargs)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        result = coercePolicyResult(raw_result, elapsed_ms=elapsed_ms)
    except Exception as error:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        failure_code = resolveFollowupFailureCode(error)
        logger.warning(
            "Chat follow-up policy failed open source_run_id=%s failure_code=%s error=%s",
            source_run_id,
            failure_code,
            error,
            exc_info=True,
        )
        return resolution(
            action="proceed",
            reason_code="policy_failed_open",
            stop_reason="policy_failed_open",
            latency_ms=elapsed_ms,
            failure_code=failure_code,
        )

    decision = result.decision
    common_metadata = {
        "decision": decision.decision,
        "latency_ms": result.latency_ms,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "provider": result.provider,
        "model": result.model,
    }
    if decision.decision == "proceed":
        return resolution(
            action="proceed",
            reason_code="unresolved_gaps_recorded",
            stop_reason="question_generation_proceed",
            **common_metadata,
        )
    if normalize_gap_key(decision.selected_gap or "") != normalize_gap_key(candidate.topic):
        return resolution(
            action="proceed",
            reason_code="policy_invalid_selection",
            stop_reason="policy_invalid_selection",
            requested_selected_gap=decision.selected_gap,
            **common_metadata,
        )

    normalized_question = normalizeQuestion(decision.question)
    if any(normalizeQuestion(exchange.question) == normalized_question for exchange in clarification_exchanges):
        return resolution(
            action="proceed",
            reason_code="duplicate_question",
            stop_reason="duplicate_question",
            selected_gap=candidate.topic,
            **common_metadata,
        )

    return resolution(
        action="ask_followup",
        reason_code=resolveGapReasonCode(candidate),
        stop_reason="ask_followup",
        question=decision.question,
        metadata_question=decision.question,
        decision="ask_followup",
        decision_source="provider_question_realizer",
        policy_decision=decision.decision,
        selected_gap=candidate.topic,
        selected_gap_detail=candidate.model_dump(mode="json"),
        followup_context=followup_context(candidate),
        rag_skipped=True,
        **common_metadata,
    )


__all__ = ["evaluate_followup_outcome"]
