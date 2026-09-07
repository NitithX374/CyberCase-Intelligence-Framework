import asyncio
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.config import settings
from app.services.case_analysis.contracts import AnalysisGapV3
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.gap_stage import run_gap_analysis_stage
from app.services.followup.schemas import (
    ClarificationExchange,
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)
from app.services.followup.stateful import (
    apply_clarification_history,
    normalize_gap_key,
    select_next_gap,
)


def item(
    topic: str,
    *,
    status: str = "NOT_PROVIDED",
    priority: str = "high",
    askable: bool = True,
    affects: str = "A-01",
) -> GapItem:
    return GapItem(
        topic=topic,
        status=status,
        description=f"{topic} remains unresolved",
        affects=affects,
        reason=f"{topic} is material",
        priority=priority,
        askable=askable,
    )


def canonical_gap(
    gap_id: str,
    topic: str,
    *,
    status: str = "NOT_PROVIDED",
    priority: str = "high",
    askable: bool = True,
    claims: list[str] | None = None,
) -> AnalysisGapV3:
    return AnalysisGapV3(
        gap_id=gap_id,
        topic=topic,
        status=status,
        description=f"{topic} remains unresolved",
        affected_claim_ids=claims if claims is not None else ["A-01"],
        reason=f"{topic} is material",
        priority=priority,
        askable=askable,
    )


def exchange(
    topic: str,
    answer: str,
    *,
    gap_id: str = "G-01",
) -> ClarificationExchange:
    return ClarificationExchange(
        question=f"Please clarify {topic}?",
        answer=answer,
        gap_id=gap_id,
        gap_topic=topic,
        gap_key=normalize_gap_key(topic),
        evidence_sha256="a" * 64,
        question_message_id=str(uuid4()),
        answer_message_id=str(uuid4()),
    )


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (" Incident Time ", "incident-time"),
        ("เวลาที่เกิดเหตุ", "เวลาเกิดเหตุ"),
        ("ช่วงเวลาของเหตุการณ์", "เวลาที่เกิดเหตุ"),
        ("CCTV subject identity", "identity of CCTV subject"),
        ("ตัวบุคคลในภาพกล้อง", "การระบุตัวบุคคลในภาพกล้อง"),
    ],
)
def test_gap_key_normalization_is_bounded_and_cross_revision(
    left: str,
    right: str,
) -> None:
    assert normalize_gap_key(left) == normalize_gap_key(right)


def test_priority_claim_link_and_stable_order_select_next_gap() -> None:
    gaps = [
        canonical_gap("G-01", "medium", priority="medium"),
        canonical_gap("G-02", "case-level", claims=[]),
        canonical_gap("G-03", "claim-linked"),
        canonical_gap("G-04", "same-rank-second"),
    ]

    selected = select_next_gap(gaps, ())

    assert selected is not None
    assert selected.gap_id == "G-03"


def test_no_gaps_unknown_low_or_unaskable_proceed_without_candidate() -> None:
    assert select_next_gap([], ()) is None
    assert (
        select_next_gap(
            [
                canonical_gap(
                    "G-01",
                    "unknown",
                    status="EXPLICITLY_UNKNOWN",
                    askable=False,
                ),
                canonical_gap("G-02", "optional", priority="low"),
            ],
            (),
        )
        is None
    )


def test_answered_gap_key_survives_gap_and_claim_ordinal_changes() -> None:
    history = (exchange("incident time", "unknown", gap_id="G-09"),)
    gaps = [
        canonical_gap("G-01", "เวลาที่เกิดเหตุ", claims=["A-64"]),
        canonical_gap("G-02", "CCTV subject identity", priority="medium"),
    ]

    selected = select_next_gap(gaps, history)

    assert selected is not None
    assert selected.gap_id == "G-02"


@pytest.mark.parametrize(
    "answer",
    ["ไม่ทราบ", "ไม่มีข้อมูลเพิ่มเติม", "unknown", "not available"],
)
def test_unavailable_answer_transitions_missing_topic_to_explicit_unknown(
    answer: str,
) -> None:
    result = apply_clarification_history(
        GapAnalysis(gaps=[item("incident time")]),
        (exchange("incident time", answer),),
    )

    assert result.gaps[0].status == "EXPLICITLY_UNKNOWN"
    assert result.gaps[0].askable is False


@pytest.mark.parametrize("status", ["AMBIGUOUS", "CONFLICTING"])
def test_exhausted_ambiguous_or_conflicting_gap_preserves_status(status: str) -> None:
    result = apply_clarification_history(
        GapAnalysis(gaps=[item("event account", status=status)]),
        (exchange("event account", "ไม่มีข้อมูลเพิ่มเติม"),),
    )

    assert result.gaps[0].status == status
    assert result.gaps[0].askable is False


def test_gap_stage_applies_short_answer_topic_context_once() -> None:
    calls = 0

    class Analyzer:
        async def analyze(self, **kwargs):
            nonlocal calls
            calls += 1
            assert kwargs["clarification_exchanges"][0].answer == "ไม่ทราบ"
            return GapAnalysisResult(analysis=GapAnalysis(gaps=[item("เวลาที่เกิดเหตุ")]))

    result = asyncio.run(
        run_gap_analysis_stage(
            original_user_content="ทรัพย์สินสูญหาย",
            clarification_exchanges=(exchange("เวลาที่เกิดเหตุ", "ไม่ทราบ"),),
            policy=None,
            gap_analyzer=Analyzer(),
            raw_evidence="ไม่ทราบ",
            analysis_answer="analysis",
            analysis_context={},
            analysis_claims=[],
            source_run_id=uuid4(),
        )
    )

    assert calls == 1
    assert result.canonical_analysis is not None
    assert result.canonical_analysis.gaps[0].status == "EXPLICITLY_UNKNOWN"


def test_followup_round_limit_prevents_question_generation(monkeypatch) -> None:
    calls = 0

    class Analyzer:
        async def analyze(self, **kwargs):
            return GapAnalysisResult(
                analysis=GapAnalysis(gaps=[item("distinct identity")])
            )

    class Policy:
        async def decide(self, **kwargs):
            nonlocal calls
            calls += 1
            return FollowUpDecision(
                decision="ask_followup",
                selected_gap="distinct identity",
                question="Can the subject be identified?",
            )

    monkeypatch.setattr(settings, "chat_followup_max_rounds", 1)
    result = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="case",
            clarification_exchanges=(exchange("incident time", "unknown"),),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            gap_analyzer=Analyzer(),
            policy=Policy(),
        )
    )

    assert result.question is None
    assert calls == 0
    assert result.metadata_json["chat_followup"]["stop_reason"] == "max_rounds_reached"


def test_one_question_contract_rejects_compound_questions() -> None:
    with pytest.raises(ValidationError):
        FollowUpDecision(
            decision="ask_followup",
            selected_gap="identity",
            question="Who is shown, and when did they arrive?",
        )
