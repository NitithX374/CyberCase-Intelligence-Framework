import hashlib
import unittest
from unittest.mock import patch

from app.services.case_analysis.caseAnalysis import executeRawDirectPipeline
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseEvidenceCitation,
    CaseProviderAnalysis,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.prompts import case_system_prompt
from app.services.case_analysis.evidenceQuoteResolver import find_aligned_quote


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
        source_revision=1,
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
        claims=[claim],
    )


class DirectAnalysisCorrectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_provenance_failure_gets_one_corrective_provider_pass(self) -> None:
        source = CaseAdmittedSource(
            source_id="s1",
            revision=1,
            content="The report was submitted.",
            content_sha256=hashlib.sha256(b"The report was submitted.").hexdigest(),
        )
        calls: list[tuple[str, str]] = []

        async def request_stage(*args, **kwargs):
            calls.append((args[2], args[3]))
            return provider_result(contradicting=len(calls) == 1)

        raw_evidence = "[SOURCE s1]\nThe report was submitted."
        digest = hashlib.sha256(raw_evidence.encode()).hexdigest()
        with patch(
            "app.services.case_analysis.caseAnalysis.requestAnalysisStage",
            new=request_stage,
        ):
            result = await executeRawDirectPipeline(
                raw_evidence,
                {
                    "document_source_context": [],
                },
                "english",
                AnalysisPipelineConfig(),
                (source,),
                object(),
                digest,
                {"calls": []},
                "case_overview",
                None,
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
