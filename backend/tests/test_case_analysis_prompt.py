import re

import httpx
import pytest

from app.analysis.prompts import (
    CASE_JUDGEMENT_SYSTEM_PROMPT,
    CASE_READING_JSON_PROMPT,
    CASE_READING_SYSTEM_PROMPT,
    case_assessment_prompt,
)
from app.errors import CaseAnalysisFailure
from app.llm.request import decode_response
from app.trace.claims import MAX_CLARIFICATION_QUESTION_CHARS


@pytest.mark.parametrize(
    "prompt",
    [
        CASE_READING_SYSTEM_PROMPT,
        CASE_READING_JSON_PROMPT,
        CASE_JUDGEMENT_SYSTEM_PROMPT,
        case_assessment_prompt(),
    ],
)
def test_no_prompt_names_a_version(prompt) -> None:
    assert re.findall(r"[a-z]+(?:_[a-z]+)*_v\d+", prompt) == []


@pytest.mark.parametrize(
    ("prompt", "sentence"),
    [
        (CASE_READING_SYSTEM_PROMPT, "Return only the requested JSON."),
        (CASE_JUDGEMENT_SYSTEM_PROMPT, "Return the requested JSON."),
        (case_assessment_prompt(), "Return only the requested JSON."),
    ],
)
def test_each_call_is_asked_for_the_json_it_is_validated_against(prompt, sentence) -> None:
    assert sentence in " ".join(prompt.split())


@pytest.mark.parametrize("prompt", [case_assessment_prompt, lambda: CASE_JUDGEMENT_SYSTEM_PROMPT])
def test_the_gap_instructions_state_the_question_limit(prompt) -> None:
    assert f"at most {MAX_CLARIFICATION_QUESTION_CHARS} characters" in " ".join(prompt().split())


@pytest.mark.parametrize("prompt", [case_assessment_prompt, lambda: CASE_JUDGEMENT_SYSTEM_PROMPT])
def test_the_gap_instructions_keep_the_topic_in_words(prompt) -> None:
    assert "It is never the gap_key." in " ".join(prompt().split())


def test_reader_prompt_enforces_complete_evidence_attribution() -> None:
    prompt = " ".join(CASE_READING_SYSTEM_PROMPT.split())
    # 1. all material claim details must be supported by cited evidence
    assert (
        "Every claim's supporting citations must collectively support every material element stated in the claim without relying on uncited case context."
        in prompt
    )
    # 2. minimum sufficient evidence set
    assert (
        "Select the minimum sufficient evidence set, not merely the unit containing the main action"
        in prompt
    )
    # 3. named-entity resolution requires citation of the identity-establishing unit
    assert (
        "When resolving a role, pronoun, alias, or generic reference into a specific named entity, cite both the unit establishing the identity"
        in prompt
    )
    # 4. unsupported specificity must be removed/generalized
    assert "keep the claim at the less-specific wording actually supported by those units" in prompt
    # 5. final evidence-completeness check
    assert "Final evidence-completeness check:" in prompt
    assert (
        "add the required Evidence Unit if available, or remove / generalize that unsupported detail from the claim"
        in prompt
    )


@pytest.mark.parametrize(
    ("status_code", "error_code"),
    [(504, "analysis_provider_timeout"), (503, "analysis_provider_down")],
)
def test_provider_status_errors_keep_timeout_specificity(status_code: int, error_code: str) -> None:
    with pytest.raises(CaseAnalysisFailure) as raised:
        decode_response(httpx.Response(status_code, json={"error": "failed"}))

    assert raised.value.code == error_code
