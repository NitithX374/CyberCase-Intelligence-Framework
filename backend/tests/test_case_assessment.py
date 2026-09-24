from __future__ import annotations

import asyncio

from app.services.analysis.contracts import CaseAssessmentTrace, CaseFollowupExchange
from app.services.analysis.prompts import (
    GAP_IDENTIFICATION_INSTRUCTIONS,
    case_assessment_prompt,
    case_system_prompt,
)
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.analysis.steps import assess as assess_module
from app.services.analysis.steps.assess import assess_case
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem


def test_assessment_and_full_analysis_share_gap_identity_instructions():
    assert GAP_IDENTIFICATION_INSTRUCTIONS in case_assessment_prompt()
    assert GAP_IDENTIFICATION_INSTRUCTIONS in case_system_prompt()


def test_assessment_uses_its_own_stage_and_only_triage_inputs(monkeypatch):
    captured: dict[str, object] = {}

    async def request_stage(**kwargs):
        captured.update(kwargs)
        return CaseAssessmentTrace(gaps=[])

    monkeypatch.setattr(assess_module, "request_stage", request_stage)
    source = CaseSourceItem(
        source_id="S-01",
        source_kind="narrative",
        text="The service was unavailable.",
    )
    history = (
        CaseFollowupExchange(
            qa_id="QA-01",
            gap_key="incident:time",
            question="When did it happen?",
            answer="Around midnight.",
        ),
    )

    result = asyncio.run(
        assess_case(
            source_bundle=CaseSourceBundle(revision=1, sources=(source,)),
            followup_history=history,
            response_language="english",
            config=AnalysisPipelineConfig(),
            client=object(),
        )
    )

    assert result.gaps == []
    assert captured["stage"] == "assess"
    assert captured["schema"] is CaseAssessmentTrace
    assert captured["content"] == {
        "response_language": "english",
        "case_sources": [
            {
                "source_id": "S-01",
                "source_kind": "narrative",
                "text": "The service was unavailable.",
            }
        ],
        "followup_history": [
            {
                "qa_id": "QA-01",
                "question": "When did it happen?",
                "answer": "Around midnight.",
            }
        ],
    }
