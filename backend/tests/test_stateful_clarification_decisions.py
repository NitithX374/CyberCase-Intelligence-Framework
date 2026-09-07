import asyncio
from uuid import uuid4

import pytest

from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    ClarificationExchange,
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)


class Analyzer:
    def __init__(self, gaps: list[GapItem]):
        self.gaps = gaps

    async def analyze(self, **kwargs):
        return GapAnalysisResult(analysis=GapAnalysis(gaps=self.gaps))


class Policy:
    def __init__(self, topic: str, question: str):
        self.topic = topic
        self.question = question
        self.calls = 0

    async def decide(self, **kwargs):
        self.calls += 1
        return FollowUpDecision(
            decision="ask_followup",
            selected_gap=self.topic,
            question=self.question,
        )


def gap(topic: str, status: str) -> GapItem:
    return GapItem(
        topic=topic,
        status=status,
        description=f"{topic} remains unresolved",
        affects="A-01",
        reason=f"{topic} is material",
        priority="high",
        askable=True,
    )


def test_no_gaps_proceeds_without_question_generation() -> None:
    policy = Policy("unused", "This must not be called?")
    result = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="case",
            clarification_exchanges=(),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            gap_analyzer=Analyzer([]),
            policy=policy,
        )
    )

    assert result.question is None
    assert policy.calls == 0
    assert result.metadata_json["chat_followup"]["reason_code"] == (
        "sufficient_case_context"
    )


@pytest.mark.parametrize(
    ("status", "question", "reason_code"),
    [
        (
            "AMBIGUOUS",
            "Can the reported evening period be stated more precisely?",
            "material_incident_fact_ambiguous",
        ),
        (
            "CONFLICTING",
            "Is there more information that can reconcile the two reported times?",
            "material_incident_fact_conflicting",
        ),
    ],
)
def test_ambiguous_and_conflicting_gaps_allow_one_neutral_question(
    status: str,
    question: str,
    reason_code: str,
) -> None:
    topic = "event time"
    policy = Policy(topic, question)
    result = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="case",
            clarification_exchanges=(),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            gap_analyzer=Analyzer([gap(topic, status)]),
            policy=policy,
        )
    )

    assert result.question is not None
    assert result.question == question
    assert result.metadata_json["chat_followup"]["reason_code"] == reason_code


def test_resolved_gap_disappearance_does_not_keep_old_task_active() -> None:
    policy = Policy("identity", "Can the subject be identified?")
    result = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="case",
            clarification_exchanges=(
                ClarificationExchange(
                    question="Can the subject be identified?",
                    answer="A witness identified the subject as Mr A.",
                    gap_topic="identity",
                    gap_key="topic:identity",
                ),
            ),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            gap_analyzer=Analyzer([]),
            policy=policy,
        )
    )

    assert result.question is None
    assert result.gap_analysis is not None
    assert result.gap_analysis.gaps == []
    assert policy.calls == 0
