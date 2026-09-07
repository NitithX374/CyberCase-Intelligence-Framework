import asyncio
from uuid import uuid4

from app.models.chat import ChatMessage
from app.services.chat.clarification_chain import reconstruct_clarification_chain
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    ClarificationExchange,
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)


def gap(
    topic: str,
    *,
    priority: str = "high",
    status: str = "NOT_PROVIDED",
) -> GapItem:
    return GapItem(
        topic=topic,
        status=status,
        description=f"{topic} remains unresolved",
        affects="A-01",
        reason=f"{topic} affects the current interpretation",
        priority=priority,
        askable=True,
    )


class StaticAnalyzer:
    def __init__(self, gaps: list[GapItem]):
        self.gaps = gaps

    async def analyze(self, **kwargs):
        return GapAnalysisResult(analysis=GapAnalysis(gaps=self.gaps))


class StaticPolicy:
    def __init__(self, topic: str, question: str):
        self.topic = topic
        self.question = question

    async def decide(self, **kwargs):
        return FollowUpDecision(
            decision="ask_followup",
            selected_gap=self.topic,
            question=self.question,
        )


def test_unavailable_answer_exhausts_only_its_topic() -> None:
    resolution = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="A bicycle was reported missing.",
            clarification_exchanges=(
                ClarificationExchange(
                    question="Do you know the incident time?",
                    answer="unknown",
                    gap_topic="incident time",
                    gap_key="topic:incident-time",
                ),
            ),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            raw_evidence="unknown",
            gap_analyzer=StaticAnalyzer(
                [
                    gap("incident time", status="EXPLICITLY_UNKNOWN"),
                    gap("CCTV subject identity", priority="medium"),
                ]
            ),
            policy=StaticPolicy(
                "CCTV subject identity",
                "Is there information that identifies the CCTV subject?",
            ),
        )
    )

    assert resolution.question is not None
    assert resolution.question == (
        "Is there information that identifies the CCTV subject?"
    )


def test_same_topic_is_not_reasked_with_different_wording() -> None:
    resolution = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="A bicycle was reported missing.",
            clarification_exchanges=(
                ClarificationExchange(
                    question="When did the incident occur?",
                    answer="I cannot determine the time.",
                    gap_topic="incident time",
                    gap_key="topic:incident-time",
                ),
            ),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            raw_evidence="I cannot determine the time.",
            gap_analyzer=StaticAnalyzer([gap("incident time")]),
            policy=StaticPolicy(
                "incident time",
                "What was the approximate time of the incident?",
            ),
        )
    )

    assert resolution.question is None


def test_clarification_chain_retains_structural_gap_context() -> None:
    thread_id = uuid4()
    question_id = uuid4()
    messages = [
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=1,
            role="user",
            content="A bicycle was reported missing.",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=question_id,
            thread_id=thread_id,
            ordinal=2,
            role="assistant",
            content="ทราบเวลาที่เกิดเหตุหรือไม่?",
            metadata_json={
                "chat_followup": {
                    "kind": "clarification",
                    "root_ordinal": 1,
                    "followup_context": {
                        "gap_id": "G-02",
                        "gap_topic": "เวลาที่เกิดเหตุ",
                        "gap_key": "incident-time",
                        "evidence_sha256": "a" * 64,
                    },
                }
            },
        ),
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=3,
            role="user",
            content="ไม่ทราบ",
            metadata_json={
                "evidence_kind": "clarification_answer",
                "clarification_context": {
                    "question_message_id": str(question_id),
                    "answered_gap_topic": "เวลาที่เกิดเหตุ",
                    "answered_gap_key": "incident-time",
                },
            },
        ),
    ]

    chain = reconstruct_clarification_chain(messages, root_ordinal=1)

    assert chain is not None
    assert chain.exchanges[0].gap_topic == "เวลาที่เกิดเหตุ"
    assert chain.exchanges[0].gap_key == "incident-time"
    assert chain.exchanges[0].question_message_id == str(question_id)


def test_asked_question_metadata_carries_gap_identity() -> None:
    resolution = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="A bicycle was reported missing.",
            clarification_exchanges=(),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            raw_evidence="A bicycle was reported missing.",
            gap_analyzer=StaticAnalyzer([gap("CCTV subject identity")]),
            policy=StaticPolicy(
                "CCTV subject identity",
                "Is there information that identifies the CCTV subject?",
            ),
        )
    )

    assert resolution.question is not None
    context = resolution.metadata_json["chat_followup"]["followup_context"]
    assert context["gap_topic"] == "CCTV subject identity"
    assert context["gap_key"]
