import unittest
from unittest.mock import patch

import analysis_arms
from analysis_arms import write_single_call
from case_mitre_test_support import _fixtures

from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.citations import CaseProviderCitation
from app.trace.claims import CaseProviderClaim
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseProviderAnalysis,
    CaseTimelineItem,
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

        with patch.object(analysis_arms, "request_stage", new=request_stage):
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

        with patch.object(analysis_arms, "request_stage", new=request_stage):
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

        with patch.object(analysis_arms, "request_stage", new=request_stage):
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

    async def test_direct_pipeline_populates_parties_timeline_and_impacts(self) -> None:
        raw_text = "On Monday, company ACME was targeted by unauthorized access."
        source = CaseSourceItem(
            source_id="s1",
            source_kind="narrative",
            text=raw_text,
        )
        citation = CaseProviderCitation(
            source_id="s1",
            exact_quote=raw_text,
        )
        claim = CaseProviderClaim(
            claim_id="A-01",
            claim_type="reported",
            text="Company ACME was targeted by unauthorized access on Monday.",
            epistemic_status="reported",
            supporting_source_ids=["s1"],
            supporting_citations=[citation],
        )
        provider_output = CaseProviderAnalysis(
            version="case_analysis_trace_v1",
            summary="Case overview summary",
            involved_parties=[CaseInvolvedParty(name="ACME", role="Victim", claim_ids=["A-01"])],
            timeline=[
                CaseTimelineItem(time="Monday", event="Unauthorized access", claim_ids=["A-01"])
            ],
            claims=[claim],
            impacts=[
                CaseImpactItem(description="Unauthorized access to systems", claim_ids=["A-01"])
            ],
        )

        async def fake_request_stage(**kwargs):
            return provider_output

        with patch.object(analysis_arms, "request_stage", new=fake_request_stage):
            trace = await write_single_call(
                sources=CaseSourceBundle(revision=1, sources=(source,)),
                language="english",
                config=AnalysisPipelineConfig(),
            )

        assert isinstance(trace, CaseAnalysisTrace)
        assert trace.analysis_mode == "case_overview"
        assert trace.retrieval_context_id is None
        assert len(trace.involved_parties) == 1
        assert trace.involved_parties[0].name == "ACME"
        assert trace.involved_parties[0].claim_ids == ["A-01"]
        assert len(trace.timeline) == 1
        assert trace.timeline[0].event == "Unauthorized access"
        assert len(trace.impacts) == 1
        assert trace.impacts[0].description == "Unauthorized access to systems"
