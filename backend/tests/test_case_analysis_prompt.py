import unittest
from unittest.mock import patch

import httpx
import pytest

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseProviderAnalysis,
    CaseSourceCitation,
)
from app.services.analysis.prompts import case_system_prompt
from app.services.analysis.provider import validate_response_payload
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.analysis.steps.quotes import find_aligned_quote
from app.services.analysis.steps.write import execute_analysis_pipeline
from app.services.sources import CaseSourceBundle, CaseSourceItem


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
    citation = CaseSourceCitation(
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

        async def request_stage(*args, **kwargs):
            observed["content"] = args[4]
            return provider_result(contradicting=False)

        with patch(
            "app.services.analysis.steps.write.request_analysis_stage",
            new=request_stage,
        ):
            await execute_analysis_pipeline(
                CaseSourceBundle(revision=1, sources=(source,)),
                "english",
                AnalysisPipelineConfig(),
                object(),
                receipt={"calls": []},
                mode="case_overview",
            )

        content = observed["content"]
        self.assertEqual(
            content,
            {
                "response_language": "english",
                "analysis_mode": "case_overview",
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
                "question": None,
            },
        )
        self.assertEqual(
            set(content),
            {
                "response_language",
                "analysis_mode",
                "case_sources",
                "followup_history",
                "technical_context",
                "question",
            },
        )

    async def test_a_source_in_both_roles_costs_no_second_provider_call(self) -> None:
        """The analysis used to be sent back to be fixed. Now it is shown.

        A source the model marked as both supporting and contradicting one
        claim is a strange thing to say, but it is what the model said and the
        reader can see both. Nothing here rejects an analysis any more, so
        nothing asks for it a second time.
        """

        source = CaseSourceItem(
            source_id="s1",
            source_kind="narrative",
            text="The report was submitted.",
        )
        calls: list[tuple[str, str]] = []

        async def request_stage(*args, **kwargs):
            calls.append((args[2], args[3]))
            return provider_result(contradicting=len(calls) == 1)

        with patch(
            "app.services.analysis.steps.write.request_analysis_stage",
            new=request_stage,
        ):
            result = await execute_analysis_pipeline(
                CaseSourceBundle(revision=1, sources=(source,)),
                "english",
                AnalysisPipelineConfig(),
                object(),
                receipt={"calls": []},
                mode="case_overview",
            )

        self.assertIsNotNone(result.trace)
        self.assertEqual([stage for stage, _ in calls], ["direct"])
        self.assertNotIn("validation_retry", result.execution_receipt)
        claim = result.trace.claims[0]
        self.assertEqual(claim.supporting_source_ids, ["s1"])
        self.assertEqual(claim.contradicting_source_ids, ["s1"])


@pytest.mark.parametrize(
    ("status_code", "error_code"),
    [(504, "analysis_provider_timeout"), (503, "analysis_provider_down")],
)
def test_provider_status_errors_keep_timeout_specificity(status_code: int, error_code: str) -> None:
    with pytest.raises(CaseAnalysisFailure) as raised:
        validate_response_payload(httpx.Response(status_code, json={"error": "failed"}))

    assert raised.value.code == error_code
