from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from uuid import UUID

from app.services.followup.gap_analysis import AnthropicGapAnalysis
from app.services.followup.helpers import (
    _coerce_gap_analysis_result,
    _followup_failure_code,
    _invoke_policy_method,
)
from app.services.followup.metadata import (
    empty_gap_analysis_trace,
    gap_analysis_trace,
)
from app.services.followup.schemas import (
    ClarificationExchange,
    FollowUpPolicy,
    GapAnalysis,
    GapAnalysisResult,
    GapAnalyzer,
)
from app.services.followup.stateful import apply_clarification_history


logger = logging.getLogger("app.chat")


@dataclass(frozen=True)
class GapStageResult:
    policy_input: GapAnalysisResult
    canonical_analysis: GapAnalysis | None
    metadata: dict[str, object]
    failure_code: str | None = None
    latency_ms: float | None = None


async def run_gap_analysis_stage(
    *,
    original_user_content: str,
    clarification_exchanges: Sequence[ClarificationExchange],
    policy: FollowUpPolicy | None,
    gap_analyzer: GapAnalyzer | None,
    raw_evidence: str | None,
    analysis_answer: str | None,
    analysis_context: Mapping[str, object] | None,
    analysis_claims: Sequence[Mapping[str, object]] | None,
    source_run_id: UUID,
) -> GapStageResult:
    if gap_analyzer is None and policy is not None:
        empty = GapAnalysisResult(analysis=GapAnalysis(gaps=[]))
        return GapStageResult(
            policy_input=empty,
            canonical_analysis=None,
            metadata=empty_gap_analysis_trace(status="compatibility_skipped"),
        )

    started = time.perf_counter()
    try:
        active_analyzer = (
            gap_analyzer()
            if isinstance(gap_analyzer, type)
            else (gap_analyzer or AnthropicGapAnalysis())
        )
        raw_result = await _invoke_policy_method(
            active_analyzer.analyze,
            {
                "original_user_content": original_user_content,
                "clarification_exchanges": clarification_exchanges,
                "raw_evidence": raw_evidence,
                "analysis_answer": analysis_answer,
                "analysis_context": analysis_context,
                "analysis_claims": analysis_claims,
            },
        )
        result = _coerce_gap_analysis_result(
            raw_result,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 3),
        )
        result = GapAnalysisResult(
            analysis=apply_clarification_history(
                result.analysis,
                clarification_exchanges,
            ),
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            provider=result.provider,
            model=result.model,
        )
        return GapStageResult(
            policy_input=result,
            canonical_analysis=result.analysis,
            metadata=gap_analysis_trace(result),
        )
    except Exception as error:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        failure_code = _followup_failure_code(error)
        logger.warning(
            "Chat gap analysis failed open source_run_id=%s failure_code=%s error=%s",
            source_run_id,
            failure_code,
            error,
            exc_info=True,
        )
        return GapStageResult(
            policy_input=GapAnalysisResult(analysis=GapAnalysis(gaps=[])),
            canonical_analysis=None,
            metadata=empty_gap_analysis_trace(
                status="failed",
                latency_ms=elapsed_ms,
                failure_code=failure_code,
            ),
            failure_code=failure_code,
            latency_ms=elapsed_ms,
        )


__all__ = ["GapStageResult", "run_gap_analysis_stage"]
