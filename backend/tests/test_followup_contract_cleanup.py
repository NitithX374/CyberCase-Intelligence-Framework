from __future__ import annotations

import asyncio
from uuid import uuid4
import pytest
from pydantic import ValidationError

from app.services.followup.contracts import (
    ClarificationExchange,
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
)
from app.services.followup.gapAnalysis import run_gap_analysis_stage


def test_followup_decision_rejects_legacy_action_shape() -> None:
    # Legacy payload with "action" instead of "decision" must fail validation
    with pytest.raises(ValidationError):
        FollowUpDecision.model_validate(
            {
                "action": "ask_followup",
                "question": "What IP was affected?",
                "selected_gap": "attacker IP",
            }
        )


def test_followup_decision_requires_selected_gap() -> None:
    # Without selected_gap, ask_followup must be rejected even with reason_code
    with pytest.raises(ValidationError):
        FollowUpDecision.model_validate(
            {
                "decision": "ask_followup",
                "question": "What IP was affected?",
                "reason_code": "material_incident_fact_missing",
            }
        )


def test_followup_decision_attributes_are_clean() -> None:
    decision = FollowUpDecision.model_validate(
        {
            "decision": "ask_followup",
            "selected_gap": "attacker IP",
            "question": "What IP was affected?",
        }
    )
    assert decision.decision == "ask_followup"
    assert decision.selected_gap == "attacker IP"
    assert decision.question == "What IP was affected?"
    assert not hasattr(decision, "reason_code")
    assert not hasattr(decision, "action")


def test_retired_followup_helpers_are_removed() -> None:
    import app.services.followup.helpers as helpers

    assert not hasattr(helpers, "_invoke_policy_method")
    assert not hasattr(helpers, "_required_material_gap")
    assert not hasattr(helpers, "_required_gap_question")
    assert not hasattr(helpers, "_selected_askable_gap")


def test_retired_prompt_builder_helpers_are_removed() -> None:
    import app.services.case_analysis.prompts as builder

    assert not hasattr(builder, "_bounded_json")


def test_gap_stage_invokes_analyzer_directly() -> None:
    class MockAnalyzer:
        def __init__(self) -> None:
            self.invoked = False

        async def analyze(
            self,
            *,
            original_user_content: str,
            clarification_exchanges: list[ClarificationExchange],
            raw_evidence: str | None,
            analysis_answer: str | None,
            analysis_context: dict[str, object] | None,
            analysis_claims: list[dict[str, object]] | None,
        ) -> GapAnalysisResult:
            self.invoked = True
            return GapAnalysisResult(
                analysis=GapAnalysis(gaps=[]),
                latency_ms=10.0,
            )

    analyzer = MockAnalyzer()
    res = asyncio.run(
        run_gap_analysis_stage(
            original_user_content="incident",
            clarification_exchanges=[],
            gap_analyzer=analyzer,
            raw_evidence="incident",
            analysis_answer="summary",
            analysis_context={},
            analysis_claims=[],
            source_run_id=uuid4(),
        )
    )
    assert analyzer.invoked is True
    assert res.failure_code is None
