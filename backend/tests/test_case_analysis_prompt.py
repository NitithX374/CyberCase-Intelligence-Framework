import re
import unittest
from typing import get_args
from unittest.mock import patch

import httpx
import pytest
from case_mitre_test_support import _fixtures

from app.analysis.prompts import (
    CASE_JUDGEMENT_SYSTEM_PROMPT,
    CASE_READING_JSON_PROMPT,
    CASE_READING_SYSTEM_PROMPT,
    case_assessment_prompt,
)
from app.errors import CaseAnalysisFailure
from app.llm.request import validate_response_payload
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.claims import (
    MAX_CLARIFICATION_QUESTION_CHARS,
    CaseAssessmentTrace,
    CaseProviderCitation,
    CaseProviderClaim,
)
from app.trace.trace import CaseProviderAnalysis, CaseProviderJudgement, CaseProviderReadingReply
from experiments.analysis_arms import write_single_call


@pytest.mark.parametrize(
    ("prompt", "schema"),
    [
        (CASE_READING_SYSTEM_PROMPT, CaseProviderReadingReply),
        (CASE_READING_JSON_PROMPT, CaseProviderReadingReply),
        (CASE_JUDGEMENT_SYSTEM_PROMPT, CaseProviderJudgement),
        (case_assessment_prompt(), CaseAssessmentTrace),
    ],
)
def test_a_prompt_names_only_the_version_its_schema_requires(prompt, schema) -> None:
    [required] = get_args(schema.model_fields["version"].annotation)

    assert set(re.findall(r"[a-z]+(?:_[a-z]+)*_v\d+", prompt)) == {required}


def test_the_judgement_is_asked_for_the_json_it_is_validated_against() -> None:
    assert "Return the requested case_analysis_trace_v1 JSON." in " ".join(
        CASE_JUDGEMENT_SYSTEM_PROMPT.split()
    )


@pytest.mark.parametrize("prompt", [case_assessment_prompt, lambda: CASE_JUDGEMENT_SYSTEM_PROMPT])
def test_the_gap_instructions_state_the_question_limit(prompt) -> None:
    assert f"at most {MAX_CLARIFICATION_QUESTION_CHARS} characters" in " ".join(prompt().split())


@pytest.mark.parametrize(
    "prompt", [case_assessment_prompt, lambda: CASE_JUDGEMENT_SYSTEM_PROMPT]
)
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
    assert (
        "keep the claim at the less-specific wording actually supported by those units"
        in prompt
    )
    # 5. final evidence-completeness check
    assert "Final evidence-completeness check:" in prompt
    assert (
        "add the required Evidence Unit if available, or remove / generalize that unsupported detail from the claim"
        in prompt
    )


def provider_result(*, contradicting: bool) -> CaseProviderAnalysis:
    citation = CaseProviderCitation(
        source_id="s1",
        exact_quote="The report",
    )
    claim = CaseProviderClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The report was submitted.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        contradicting_source_ids=["s1"] if contradicting else [],
        supporting_citations=[citation],
        contradicting_citations=[citation] if contradicting else [],
    )
    return CaseProviderAnalysis(
        version="case_analysis_trace_v1",
        summary="The report was submitted.",
        involved_parties=[],
        timeline=[],
        impacts=[],
        claims=[claim],
    )


class DirectAnalysisCorrectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_request_uses_one_structured_case_source_collection(self) -> None:
        source = CaseSourceItem(
            source_id="s1",
            source_kind="document",
            text="The report was submitted.",
            document_id="d1",
            filename="report.pdf",
            provenance={"verification_status": "machine_read"},
        )
        observed: dict[str, object] = {}

        async def request_stage(**kwargs):
            observed.update(kwargs)
            return provider_result(contradicting=False)

        with patch("experiments.analysis_arms.request_stage", new=request_stage):
            await write_single_call(
                sources=CaseSourceBundle(revision=1, sources=(source,)),
                language="english",
                config=AnalysisPipelineConfig(),
            )

        self.assertEqual(observed["stage"], "case_direct")
        self.assertIs(observed["schema"], CaseProviderAnalysis)
        content = observed["content"]
        self.assertEqual(
            content,
            {
                "response_language": "english",
                "case_sources": [
                    {
                        "source_id": "s1",
                        "source_kind": "document",
                        "text": "The report was submitted.",
                        "document": {
                            "document_id": "d1",
                            "filename": "report.pdf",
                            "verification_status": "machine_read",
                        },
                    }
                ],
                "followup_history": [],
                "technical_context": None,
            },
        )

    async def test_a_source_in_both_roles_costs_no_second_provider_call(self) -> None:
        source = CaseSourceItem(
            source_id="s1",
            source_kind="narrative",
            text="The report was submitted.",
        )
        calls: list[str] = []

        async def request_stage(**kwargs):
            calls.append(kwargs["stage"])
            return provider_result(contradicting=len(calls) == 1)

        with patch("experiments.analysis_arms.request_stage", new=request_stage):
            trace = await write_single_call(
                sources=CaseSourceBundle(revision=1, sources=(source,)),
                language="english",
                config=AnalysisPipelineConfig(),
            )

        self.assertEqual(calls, ["case_direct"])
        claim = trace.claims[0]
        self.assertEqual(claim.supporting_source_ids, ["s1"])
        self.assertEqual(claim.contradicting_source_ids, ["s1"])

    async def test_retrieved_context_is_shown_and_its_id_bound_to_the_trace(self) -> None:
        _, _, bundle, _, context = _fixtures()
        observed: dict[str, object] = {}

        async def request_stage(**kwargs):
            observed.update(kwargs)
            return provider_result(contradicting=False)

        with patch("experiments.analysis_arms.request_stage", new=request_stage):
            trace = await write_single_call(
                sources=bundle,
                language="thai",
                technical_context=context,
                config=AnalysisPipelineConfig(),
            )

        self.assertEqual(observed["content"]["response_language"], "thai")
        self.assertEqual(
            observed["content"]["technical_context"],
            {"context": context.context, "mitre_table": list(context.mitre_table)},
        )
        self.assertEqual(trace.retrieval_context_id, context.retrieval_context_id)


@pytest.mark.parametrize(
    ("status_code", "error_code"),
    [(504, "analysis_provider_timeout"), (503, "analysis_provider_down")],
)
def test_provider_status_errors_keep_timeout_specificity(status_code: int, error_code: str) -> None:
    with pytest.raises(CaseAnalysisFailure) as raised:
        validate_response_payload(httpx.Response(status_code, json={"error": "failed"}))

    assert raised.value.code == error_code
