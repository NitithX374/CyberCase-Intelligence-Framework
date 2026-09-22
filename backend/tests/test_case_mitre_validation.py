import asyncio

from case_mitre_test_support import _fixtures, _gate

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisOutput,
    CaseMitreAssociation,
    CaseProviderAnalysis,
    CaseSourceCitation,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    retrieve_technical_context,
    write_analysis,
)
from app.services.analysis.steps.write import validate_direct_trace
from app.services.clients.rag_client import RagCallFailure


def test_invalid_technique_is_rejected_by_validation():
    _, trace, source_bundle, _, context = _fixtures()
    invalid_assoc = CaseMitreAssociation(
        association_id="MA-01",
        technique_id="T9999",
        claim_ids=["A-01"],
        reason="Invented technique.",
        status="candidate_only",
        support_role="external_technical_context",
    )
    parsed = CaseProviderAnalysis(
        version="case_analysis_trace_v1",
        summary="Summary",
        involved_parties=[],
        timeline=[],
        claims=list(trace.claims),
        impacts=[],
        gaps=[],
        mitre_associations=[invalid_assoc],
    )
    trace = validate_direct_trace(
        parsed,
        mode="case_overview",
        source_bundle=source_bundle,
        retrieval_context_id="retrieval-case-1",
        mitre_table=list(context.mitre_table),
    )
    assert trace.mitre_associations == []
    assert trace.grounding.associations_outside_context == 1


def test_rag_failure_falls_back_to_case_sources():
    async def exercise():
        _, trace, source_bundle, applicability, _ = _fixtures()

        async def fake_rag(_query):
            raise RagCallFailure("rag_timeout", "RAG service timed out")

        analysis_kwargs = []

        async def fake_analysis(**kwargs):
            analysis_kwargs.append(kwargs)
            return CaseAnalysisOutput(
                answer="Analysis without RAG context.",
                trace=trace,
                execution_receipt={"calls": []},
            )

        data = AnalysisInput(sources=source_bundle, response_language="english")
        artifacts = await retrieve_technical_context(
            data, AnalysisArtifacts(), gate=_gate(applicability), rag=fake_rag
        )
        artifacts = await write_analysis(data, artifacts, request=fake_analysis)

        assert len(analysis_kwargs) == 1
        assert analysis_kwargs[0]["technical_context"] is None
        assert analysis_kwargs[0]["retrieval_context_id"] is None
        assert artifacts.trace.mitre_associations == []
        augmentation = artifacts.receipt["technical_augmentation"]
        assert augmentation["status"] == "failed"
        assert augmentation["failure_code"] == "rag_timeout"

    asyncio.run(exercise())


def test_case_sources_remain_the_only_allowed_claim_source_ids():
    _, _, source_bundle, _, context = _fixtures()
    invalid_claim = CaseAnalysisClaim(
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
    parsed = CaseProviderAnalysis(
        version="case_analysis_trace_v1",
        summary="Summary",
        involved_parties=[],
        timeline=[],
        claims=[invalid_claim],
        impacts=[],
        gaps=[],
        mitre_associations=[],
    )
    trace = validate_direct_trace(
        parsed,
        mode="case_overview",
        source_bundle=source_bundle,
        retrieval_context_id="retrieval-case-1",
        mitre_table=list(context.mitre_table),
    )
    assert trace.claims[0].supporting_source_ids == []
    assert trace.grounding.claims_without_citation == 1
