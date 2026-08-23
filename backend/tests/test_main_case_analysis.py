import json

import pytest

from app.services.case_analysis.case_analysis_prompt_builder import (
    _validate_analysis_request,
    build_case_analysis_prompt,
)
from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure


def payload_from_prompt(prompt: str) -> dict[str, object]:
    return json.loads(prompt.split("<case_context_json>\n", 1)[1].split("\n</case_context_json>", 1)[0])


def test_analysis_prompt_uses_raw_evidence_and_separates_external_context() -> None:
    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence="[INITIAL CASE NARRATIVE]\nA server was compromised.",
        analysis_context={
            "retrieved_context": "MITRE external knowledge",
            "source_message_ids": ["message-1"],
        },
        question=None,
        response_language="english",
    )
    payload = payload_from_prompt(prompt)
    assert payload["raw_user_case_evidence"].startswith("[INITIAL CASE NARRATIVE]")
    assert payload["external_analysis_context"] == {
        "retrieved_context": "MITRE external knowledge",
        "source_message_ids": ["message-1"],
    }
    assert "case_state" not in json.dumps(payload).lower()


def test_question_mode_requires_a_question() -> None:
    with pytest.raises(CaseAnalysisFailure):
        _validate_analysis_request("question_answer", None)


def test_overview_rejects_a_question() -> None:
    with pytest.raises(CaseAnalysisFailure):
        _validate_analysis_request("case_overview", "Why?")
