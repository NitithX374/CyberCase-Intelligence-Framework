import asyncio
from uuid import uuid4

from app.services.case_analysis.contracts import CaseAnalysisGap, CaseAnalysisTrace
from app.services.followup.contracts import FollowUpExchange
from app.services.followup.decision import (
    evaluate_followup_outcome,
    select_followup_gap,
)


def gap(
    gap_id: str,
    gap_key: str,
    priority: str = "high",
    question: str | None = None,
) -> CaseAnalysisGap:
    return CaseAnalysisGap(
        gap_id=gap_id,
        gap_key=gap_key,
        topic=gap_key.replace("_", " ").title(),
        status="NOT_PROVIDED",
        description=f"{gap_key} is missing.",
        affected_claim_ids=[],
        reason=f"{gap_key} affects the analysis.",
        priority=priority,
        askable=True,
        clarification_question=question or f"What is the confirmed {gap_key.replace('_', ' ').title()}?",
    )


def test_select_followup_gap_returns_one_ranked_high_priority_gap() -> None:
    gaps = (
        gap("G-01", "answered_gap"),
        gap("G-02", "second_gap"),
        gap("G-03", "medium_gap", priority="medium"),
        gap("G-04", "third_gap"),
        gap("G-05", "fourth_gap"),
        gap("G-06", "fifth_gap"),
    )
    exchanges = (
        FollowUpExchange(
            question="What is the confirmed answered gap?",
            answer="Already supplied",
            gap_id="G-01",
            gap_key="answered_gap",
            disposition="answered",
        ),
    )

    selected = select_followup_gap(gaps, exchanges)

    assert selected is not None
    assert selected.gap_id == "G-02"


def test_select_followup_gap_treats_skipped_disposition_as_exhausted() -> None:
    gaps = (
        gap("G-01", "first_gap"),
        gap("G-02", "second_gap"),
    )
    exchanges = (
        FollowUpExchange(
            question="What is the first gap?",
            answer="skipped",
            gap_id="G-01",
            gap_key="first_gap",
            disposition="skipped",
        ),
    )

    selected = select_followup_gap(gaps, exchanges)

    assert selected is not None
    assert selected.gap_id == "G-02"


def test_followup_questions_are_realized_from_main_analysis_gaps(monkeypatch) -> None:
    monkeypatch.setattr("app.services.followup.decision.settings.chat_followup_enabled", True)
    monkeypatch.setattr("app.services.followup.decision.settings.chat_followup_max_rounds", 2)
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The case needs three details.",
        claims=[],
        gaps=[gap("G-01", "incident_time"), gap("G-02", "operator")],
    )

    result = asyncio.run(
        evaluate_followup_outcome(
            followup_exchanges=(),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            source_revision=7,
            canonical_trace=trace,
        )
    )

    assert result.question == "What is the confirmed Incident Time?"
    assert result.metadata_json["action"] == "follow_up"
    followup = result.metadata_json["chat_followup"]
    assert followup["source_revision"] == 7
    assert followup["gap"]["gap_id"] == "G-01"


def test_followup_contract_and_policy_structures() -> None:
    from app.services.followup.contracts import (
        FollowUpDecision,
        FollowUpExchange,
        FollowUpPolicy,
        FollowUpPolicyResult,
        answer_indicates_unavailable,
    )
    from app.services.followup.case_followup import (
        CaseFollowUpError,
    )
    from app.services.followup.policy import (
        AnthropicFollowUpPolicy,
        extract_llm_json,
        extract_llm_text,
    )

    # Protocol compliance
    assert isinstance(AnthropicFollowUpPolicy(), FollowUpPolicy)

    # Policy payload parsing
    decision = FollowUpDecision(decision="ask_followup", selected_gap="G-01", question="Time?")
    result = FollowUpPolicyResult(decision=decision, latency_ms=12.5)
    assert result.decision.decision == "ask_followup"

    parsed_json = extract_llm_json('```json\n{"decision": "proceed", "selected_gap": null, "question": ""}\n```')
    assert parsed_json["decision"] == "proceed"
    assert extract_llm_text({"content": [{"type": "text", "text": "hello"}]}) == "hello"

    # Unavailable answers
    assert answer_indicates_unavailable("ไม่มีข้อมูลครับ") is True
    assert answer_indicates_unavailable("unknown") is True
    assert answer_indicates_unavailable("IP 192.168.1.1") is False

