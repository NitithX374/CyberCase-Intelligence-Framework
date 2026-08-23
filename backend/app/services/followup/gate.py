from app.services.followup.contracts import (
    FollowUpResolution,
    answer_indicates_unavailable as _answer_indicates_unavailable,
)
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.compatibility import resolve_followup_outcome
from app.services.followup.helpers import (
    _coerce_gap_analysis_result,
    _coerce_policy_result,
    _followup_failure_code,
    _gap_reason_code,
    _invoke_policy_method,
    _normalized_question,
    _required_gap_question,
    _required_material_gap,
    _safe_token_count,
    _selected_askable_gap,
)
from app.services.followup.metadata import (
    empty_gap_analysis_trace as _empty_gap_analysis_trace,
    followup_metadata as _followup_metadata,
    gap_analysis_trace as _gap_analysis_trace,
    mark_followup_rag_invoked as _mark_followup_rag_invoked,
    mark_followup_rag_invoked_metadata as _mark_followup_rag_invoked_metadata,
)


__all__ = [
    "FollowUpResolution",
    "_answer_indicates_unavailable",
    "_coerce_gap_analysis_result",
    "_coerce_policy_result",
    "_empty_gap_analysis_trace",
    "_followup_failure_code",
    "_followup_metadata",
    "_gap_analysis_trace",
    "_gap_reason_code",
    "_invoke_policy_method",
    "_mark_followup_rag_invoked",
    "_mark_followup_rag_invoked_metadata",
    "_normalized_question",
    "_required_gap_question",
    "_required_material_gap",
    "_safe_token_count",
    "_selected_askable_gap",
    "evaluate_followup_outcome",
    "resolve_followup_outcome",
]
