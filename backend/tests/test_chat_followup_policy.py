import asyncio
from uuid import uuid4

import pytest

from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)


class Analyzer:
    async def analyze(self, **kwargs):
        assert kwargs["raw_evidence"] == "raw evidence"
        return GapAnalysisResult(
            analysis=GapAnalysis(
                gaps=[
                    GapItem(
                        topic="affected account",
                        status="NOT_PROVIDED",
                        description="The affected account is missing",
                        affects="scope",
                        reason="It defines the target",
                        priority="high",
                        askable=True,
                    )
                ]
            )
        )


class Policy:
    async def decide(self, **kwargs):
        assert kwargs["raw_evidence"] == "raw evidence"
        return FollowUpDecision(
            decision="ask_followup",
            selected_gap="affected account",
            question="Which account was affected?",
        )


def test_followup_consumes_raw_evidence_without_case_state() -> None:
    result = asyncio.run(evaluate_followup_outcome(
        original_user_content="Initial",
        clarification_exchanges=(),
        followup_root_ordinal=1,
        source_run_id=uuid4(),
        raw_evidence="raw evidence",
        analysis_answer="analysis",
        analysis_context={"mitre_table": []},
        gap_analyzer=Analyzer(),
        policy=Policy(),
    ))
    assert result.outcome is not None
    assert result.outcome.thread_status == "awaiting_followup"
    assert result.outcome.content == "Which account was affected?"
