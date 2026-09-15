import unittest
from unittest.mock import patch

import httpx
import pytest

from app.services.case_analysis.caseAnalysis import execute_raw_direct_pipeline
from app.services.case_analysis.contracts import (
    CaseEvidenceSource,
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseEvidenceCitation,
    CaseProviderAnalysis,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.prompts import case_system_prompt
from app.services.case_analysis.evidenceQuoteResolver import find_aligned_quote
from app.services.case_analysis.caseAnalysisResponseParser import validate_response_payload


def test_direct_analysis_prompt_keeps_source_roles_disjoint_per_claim() -> None:
    prompt = case_system_prompt()

    assert "a source ID may appear in only one role" in prompt
    assert "create separate attributed claims or a conflict gap" in prompt


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
    citation = CaseEvidenceCitation(
        source_id="s1",
        exact_quote="The report",
    )
    claim = CaseAnalysisClaim(
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
        answer="The report was submitted.",
        summary="The report was submitted.",
        involved_parties=[],
        timeline=[],
        impacts=[],
        claims=[claim],
    )


class DirectAnalysisCorrectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_provenance_failure_gets_one_corrective_provider_pass(self) -> None:
        source = CaseEvidenceSource(
            source_id="s1",
            content="The report was submitted.",
        )
        calls: list[tuple[str, str]] = []

        async def request_stage(*args, **kwargs):
            calls.append((args[2], args[3]))
            return provider_result(contradicting=len(calls) == 1)

        raw_evidence = "[SOURCE s1]\nThe report was submitted."
        with patch(
            "app.services.case_analysis.caseAnalysis.request_analysis_stage",
            new=request_stage,
        ):
            result = await execute_raw_direct_pipeline(
                raw_evidence,
                {
                    "document_source_context": [],
                },
                "english",
                AnalysisPipelineConfig(),
                (source,),
                object(),
                receipt={"calls": []},
                mode="case_overview",
            )

        self.assertIsNotNone(result.trace)
        self.assertEqual(
            [stage for stage, _ in calls], ["direct", "direct_correction"]
        )
        self.assertIn("CORRECTION REQUIREMENTS", calls[1][1])
        self.assertEqual(
            result.execution_receipt["validation_retry"],
            {"reason": "case_trace_conflicting_source_role"},
        )


@pytest.mark.parametrize(
    ("status_code", "error_code"),
    [(504, "analysis_provider_timeout"), (503, "analysis_provider_down")],
)
def test_provider_status_errors_keep_timeout_specificity(status_code: int, error_code: str) -> None:
    with pytest.raises(CaseAnalysisFailure) as raised:
        validate_response_payload(httpx.Response(status_code, json={"error": "failed"}))

    assert raised.value.code == error_code
