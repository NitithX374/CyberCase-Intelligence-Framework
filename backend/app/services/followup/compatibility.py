from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from app.services.followup.contracts import FollowUpResolution
from app.services.followup.schemas import ClarificationExchange, GapAnalyzer, FollowUpPolicy
from app.services.followup.decision import evaluate_followup_outcome

if TYPE_CHECKING:
    from app.services.workflow.outcome import AssistantOutcome

async def resolve_followup_outcome(
    *,
    original_user_content: str,
    clarification_exchanges: Sequence[ClarificationExchange],
    followup_root_ordinal: int,
    source_run_id: UUID,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    case_state: Mapping[str, object] | None = None,
    analysis_answer: str | None = None,
    analysis_context: Mapping[str, object] | None = None,
) -> AssistantOutcome | None:
    """Compatibility wrapper returning only the pending assistant outcome."""

    resolution = await evaluate_followup_outcome(
        original_user_content=original_user_content,
        clarification_exchanges=clarification_exchanges,
        followup_root_ordinal=followup_root_ordinal,
        source_run_id=source_run_id,
        policy=policy,
        gap_analyzer=gap_analyzer,
        case_state=case_state,
        analysis_answer=analysis_answer,
        analysis_context=analysis_context,
    )
    return resolution.outcome
