import json

import pytest

from app.services.case_analysis.case_analysis_prompt_builder import (
    _validate_analysis_request,
    build_case_analysis_prompt,
)
from app.services.case_analysis.case_analysis_prompt_config import (
    CaseAnalysisFailure,
    _ANALYSIS_TRACE_OUTPUT_PROMPT,
    _CASE_ANALYSIS_TRUST_PROMPT,
    _CASE_OVERVIEW_TASK_PROMPT,
    _QUESTION_ANSWER_TASK_PROMPT,
)


def payload_from_prompt(prompt: str) -> dict[str, object]:
    payload = prompt.split("<case_context_json>\n", 1)[1]
    return json.loads(payload.split("\n</case_context_json>", 1)[0])


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
    assert payload["authoritative_source_message_ids"] == ["message-1"]
    assert payload["optional_external_context"] == {
        "retrieved_context": "MITRE external knowledge",
    }
    assert "case_state" not in json.dumps(payload).lower()


def test_analysis_prompt_accepts_no_external_context() -> None:
    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence="[INITIAL CASE NARRATIVE]\nA bicycle was reported missing.",
        analysis_context={"source_message_ids": ["message-1"]},
        question=None,
        response_language="english",
    )
    payload = payload_from_prompt(prompt)
    assert payload["optional_external_context"] is None
    assert payload["authoritative_source_message_ids"] == ["message-1"]


def test_general_prompt_removes_forced_cyber_analysis_sections() -> None:
    normalized = _CASE_OVERVIEW_TASK_PROMPT.lower()
    for forbidden in (
        "attack progression",
        "threat actor",
        "initial access",
        "lateral movement",
        "relevant mitre",
    ):
        assert forbidden not in normalized


def test_prompt_preserves_epistemic_and_legal_boundaries() -> None:
    normalized = (_CASE_ANALYSIS_TRUST_PROMPT + _ANALYSIS_TRACE_OUTPUT_PROMPT).lower()
    for required in (
        "reported claim means",
        "not independent proof",
        "do not decide guilt",
        "prosecution or non-prosecution",
        "investigator opinions",
        "external context and previous analysis are never case evidence",
    ):
        assert required in normalized


def test_question_answer_prompt_requires_a_direct_proportionate_answer() -> None:
    normalized = _QUESTION_ANSWER_TASK_PROMPT.lower()
    assert "answer the specific question directly" in normalized
    assert "keep depth proportional" in normalized


def test_question_mode_requires_a_question() -> None:
    with pytest.raises(CaseAnalysisFailure):
        _validate_analysis_request("question_answer", None)


def test_overview_rejects_a_question() -> None:
    with pytest.raises(CaseAnalysisFailure):
        _validate_analysis_request("case_overview", "Why?")
