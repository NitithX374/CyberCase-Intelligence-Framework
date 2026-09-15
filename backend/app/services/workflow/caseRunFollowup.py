from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.followup.decision import evaluate_followup_outcome
from app.services.workflow.caseRunErrors import CaseRunExecutionError


async def attachCaseFollowup(
    output,
    claimed,
    clarification_exchanges,
):
    if not isinstance(output.trace, CaseAnalysisTrace):
        return output
    resolution = await evaluate_followup_outcome(
        clarification_exchanges=clarification_exchanges,
        followup_root_ordinal=1,
        source_run_id=claimed.id,
        canonical_trace=output.trace,
    )
    if resolution.question is None:
        return output
    metadata = deepcopy(resolution.metadata_json)
    followup = metadata.get("chat_followup")
    if not isinstance(followup, dict):
        raise CaseRunExecutionError(
            "clarification_metadata_missing",
            "Case clarification metadata is missing",
        )
    detail = followup.get("selected_gap_detail")
    detail = detail if isinstance(detail, dict) else {}
    context = followup.get("followup_context")
    context = context if isinstance(context, dict) else {}
    topic = detail.get("topic") or followup.get("selected_gap")
    gap_key = context.get("gap_key")
    gap_id = detail.get("gap_id") or context.get("gap_id") or gap_key
    if not all(isinstance(value, str) and value.strip() for value in (gap_id, topic, gap_key)):
        raise CaseRunExecutionError(
            "clarification_metadata_missing",
            "Case clarification has no stable gap identity",
        )
    metadata.update({"gap_id": gap_id, "topic": topic, "gap_key": gap_key})
    return replace(
        output,
        followup_question=resolution.question,
        followup_metadata=metadata,
    )


__all__ = ["attachCaseFollowup"]
