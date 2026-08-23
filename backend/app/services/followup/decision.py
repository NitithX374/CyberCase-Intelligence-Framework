from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from app.config import settings
from app.services.followup.contracts import FollowUpResolution, answer_indicates_unavailable
from app.services.followup.gap_analysis import AnthropicGapAnalysis
from app.services.followup.policy import AnthropicFollowUpPolicy
from app.services.followup.schemas import (
    ClarificationExchange, GapAnalysis, GapAnalysisResult, GapAnalyzer, GapItem, FollowUpDecision, FollowUpPolicy, FollowUpPolicyResult,
)
from app.services.followup.helpers import (
    _coerce_gap_analysis_result as coerce_gap_analysis_result,
    _coerce_policy_result as coerce_policy_result,
    _followup_failure_code as followup_failure_code,
    _gap_reason_code as gap_reason_code,
    _invoke_policy_method as invoke_policy_method,
    _normalized_question as normalized_question,
    _required_gap_question as required_gap_question,
    _required_material_gap as required_material_gap,
    _selected_askable_gap as selected_askable_gap,
)
from app.services.followup.metadata import empty_gap_analysis_trace, followup_metadata, gap_analysis_trace

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
) -> FollowUpResolution:
    round_number = len(clarification_exchanges) + 1
    prior_exchange_count = len(clarification_exchanges)
    gap_trace = empty_gap_analysis_trace()

    def proceed_resolution(
        *,
        reason_code: str,
        stop_reason: str,
        **metadata_kwargs: Any,
    ) -> FollowUpResolution:
        return FollowUpResolution(
            outcome=None,
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
        )

    def ask_resolution(
        *,
        selected_gap: GapItem,
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
            gap_analysis=gap_trace,
            rag_skipped=True,
            **metadata_kwargs,
        )
        from app.services.workflow.outcome import AssistantOutcome

        return FollowUpResolution(
            outcome=AssistantOutcome(
                content=question,
                retrieval_context_id=None,
                metadata_json=metadata,
                thread_status="awaiting_followup",
            ),
            metadata_json={},
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
    if clarification_exchanges and answer_indicates_unavailable(
        clarification_exchanges[-1].answer
    ):
        return proceed_resolution(
            reason_code="answer_unavailable",
            stop_reason="answer_unavailable",
        )

    compatibility_gap_analysis = gap_analyzer is None and policy is not None
    if compatibility_gap_analysis:
        gap_result = GapAnalysisResult(analysis=GapAnalysis(gaps=[]))
        gap_trace = empty_gap_analysis_trace(status="compatibility_skipped")
    else:
        gap_started = time.perf_counter()
        try:
            active_gap_analyzer = (
                gap_analyzer()
                if isinstance(gap_analyzer, type)
                else (gap_analyzer or AnthropicGapAnalysis())
            )
            gap_kwargs = {
                "original_user_content": original_user_content,
                "clarification_exchanges": clarification_exchanges,
                "raw_evidence": raw_evidence,
                "analysis_answer": analysis_answer,
                "analysis_context": analysis_context,
            }
            raw_gap_result = await invoke_policy_method(
                active_gap_analyzer.analyze,
                gap_kwargs,
            )
            gap_result = coerce_gap_analysis_result(
                raw_gap_result,
                elapsed_ms=round((time.perf_counter() - gap_started) * 1000, 3),
            )
            gap_trace = gap_analysis_trace(gap_result)
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - gap_started) * 1000, 3)
            failure_code = followup_failure_code(exc)
            gap_trace = empty_gap_analysis_trace(
                status="failed",
                latency_ms=elapsed_ms,
                failure_code=failure_code,
            )
            logger.warning(
                "Chat gap analysis failed open source_run_id=%s failure_code=%s",
                source_run_id,
                failure_code,
            )
            return proceed_resolution(
                reason_code="gap_analysis_failed_open",
                stop_reason="gap_analysis_failed_open",
                latency_ms=elapsed_ms,
                failure_code=failure_code,
            )

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
            "gap_analysis": gap_result.analysis,
            "raw_evidence": raw_evidence,
            "analysis_answer": analysis_answer,
            "analysis_context": analysis_context,
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
            "Chat follow-up policy failed open source_run_id=%s failure_code=%s",
            source_run_id,
            failure_code,
        )
        return proceed_resolution(
            reason_code="policy_failed_open",
            stop_reason="policy_failed_open",
            latency_ms=elapsed_ms,
            failure_code=failure_code,
        )

    required_gap = required_material_gap(gap_result.analysis)
    if decision.decision == "proceed" and required_gap is not None:
        return ask_resolution(
            selected_gap=required_gap,
            question=required_gap_question(original_user_content, required_gap),
            reason_code=gap_reason_code(required_gap),
            stop_reason="required_material_gap_guard",
            decision_source="deterministic_material_gap_guard",
            policy_decision=decision.decision,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            provider=result.provider,
            model=result.model,
        )

    if decision.decision == "proceed":
        reason_code = decision.reason_code or (
            "unresolved_gaps_recorded"
            if gap_result.analysis.gaps
            else "sufficient_case_context"
        )
        return proceed_resolution(
            reason_code=reason_code,
            stop_reason="policy_proceed",
            decision=decision.decision,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            provider=result.provider,
            model=result.model,
        )

    selected_gap = selected_askable_gap(
        gap_result.analysis,
        decision.selected_gap,
        compatibility=compatibility_gap_analysis,
    )
    if selected_gap is None:
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
        selected_gap=selected_gap,
        question=decision.question,
        reason_code=decision.reason_code or gap_reason_code(selected_gap),
        stop_reason="ask_followup",
        decision_source="provider_policy",
        policy_decision=decision.decision,
        latency_ms=result.latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        provider=result.provider,
        model=result.model,
    )
