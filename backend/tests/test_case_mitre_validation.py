import asyncio

from case_mitre_test_support import _fixtures, _gate

from app.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    retrieve_technical_context,
    write_analysis,
)
from app.analysis.technical_context.rag_client import RagCallFailure
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.trace import CaseAnalysisTrace


def test_only_the_row_the_service_tied_to_a_sentence_becomes_an_association():
    _, trace, source_bundle, _, context = _fixtures()

    bound = resolve_case_trace(
        trace.model_copy(update={"retrieval_context_id": "retrieval-case-1"}),
        source_bundle,
        mitre_table=list(context.mitre_table),
    )

    [association] = bound.mitre_associations
    assert association.technique_id == "T1059.001"
    assert association.reason == f"“{source_bundle.sources[0].text}”"
    assert association.claim_ids == []
    assert CaseAnalysisTrace.model_validate(bound.model_dump()) == bound


def test_rag_failure_falls_back_to_case_sources():
    async def exercise():
        _, trace, source_bundle, applicability, _ = _fixtures()

        async def fake_rag(_query):
            raise RagCallFailure("rag_timeout", "RAG service timed out")

        analysis_kwargs = []

        async def fake_analysis(**kwargs):
            analysis_kwargs.append(kwargs)
            return trace

        data = AnalysisInput(sources=source_bundle, response_language="english")
        artifacts = await retrieve_technical_context(
            data, AnalysisArtifacts(), gate=_gate(applicability), rag=fake_rag
        )
        artifacts = await write_analysis(data, artifacts, request=fake_analysis)

        assert len(analysis_kwargs) == 1
        assert analysis_kwargs[0]["technical_context"] is None
        assert artifacts.trace.mitre_associations == []
        assert artifacts.augmentation.status == "failed"
        assert artifacts.augmentation.failure_code == "rag_timeout"

    asyncio.run(exercise())


def test_case_sources_remain_the_only_allowed_claim_source_ids():
    _, trace, source_bundle, _, context = _fixtures()
    outside = CaseAnalysisClaim(
        claim_id="A-02",
        claim_type="reported",
        text="A claim citing external non-case source.",
        epistemic_status="reported",
        supporting_source_ids=["external-mitre-source-id"],
        supporting_citations=[
            CaseSourceCitation(
                source_id="external-mitre-source-id",
                exact_quote="Some quote",
            )
        ],
    )

    bound = resolve_case_trace(
        trace.model_copy(update={"claims": [outside], "retrieval_context_id": "retrieval-case-1"}),
        source_bundle,
        mitre_table=list(context.mitre_table),
    )

    assert bound.claims[0].supporting_source_ids == []
    assert bound.claims[0].supporting_citations == []
    assert bound.grounding.claims_without_citation == 1
    assert bound.grounding.citations_unfound == 1
