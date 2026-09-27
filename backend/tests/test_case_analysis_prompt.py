import unittest
from unittest.mock import patch

import httpx
import pytest
from case_mitre_test_support import _fixtures

from app.analysis.prompts import case_assessment_prompt, case_system_prompt
from app.analysis.write import write_trace
from app.errors import CaseAnalysisFailure
from app.llm.request import validate_response_payload
from app.llm.settings import AnalysisPipelineConfig
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem
from app.trace.claims import (
    MAX_CLARIFICATION_QUESTION_CHARS,
    CaseProviderCitation,
    CaseProviderClaim,
)
from app.trace.quotes import find_aligned_quote
from app.trace.trace import CaseProviderAnalysis


def test_direct_analysis_prompt_keeps_source_roles_disjoint_per_claim() -> None:
    prompt = case_system_prompt()

    assert "a source ID may appear in only one role" in prompt
    assert "create separate attributed claims or a conflict gap" in prompt


@pytest.mark.parametrize("prompt", [case_assessment_prompt, case_system_prompt])
def test_the_gap_instructions_state_the_question_limit(prompt) -> None:
    assert f"at most {MAX_CLARIFICATION_QUESTION_CHARS} characters" in " ".join(prompt().split())


def test_ellipsis_citation_is_expanded_to_one_exact_source_span() -> None:
    content = "Prefix before\nfirst quoted statement\n omitted middle\nlast quoted statement\nSuffix after"

    assert find_aligned_quote(content, "first quoted statement ... last quoted statement") == (
        "first quoted statement\n omitted middle\nlast quoted statement"
    )


def test_ellipsis_alignment_requires_each_retained_segment() -> None:
    content = "first quoted statement\n omitted middle\nlast quoted statement"

    assert (
        find_aligned_quote(
            content,
            "first quoted statement ... absent segment ... last quoted statement",
        )
        is None
    )


def test_quote_alignment_preserves_source_text_when_ocr_wraps_a_word() -> None:
    content = "คำร้องขอ\nหมายจับผู้ต้องหา"

    assert find_aligned_quote(content, "คำร้องขอหมายจับผู้ต้องหา") == content


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

        with patch("app.analysis.write.request_stage", new=request_stage):
            await write_trace(
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

        with patch("app.analysis.write.request_stage", new=request_stage):
            trace = await write_trace(
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

        with patch("app.analysis.write.request_stage", new=request_stage):
            trace = await write_trace(
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
