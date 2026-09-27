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
from app.trace.trace import CaseAnalysisTrace, CaseMitreAssociation


def association(technique_id: str, claim_ids: list[str]) -> CaseMitreAssociation:
    return CaseMitreAssociation(
        association_id="MA-01",
        technique_id=technique_id,
        claim_ids=claim_ids,
        reason="PowerShell reached an external address.",
        status="candidate_only",
        support_role="external_technical_context",
    )


def bound_with(*associations: CaseMitreAssociation) -> CaseAnalysisTrace:
    _, trace, source_bundle, _, context = _fixtures()
    return resolve_case_trace(
        trace.model_copy(
            update={
                "mitre_associations": list(associations),
                "retrieval_context_id": "retrieval-case-1",
            }
        ),
        source_bundle,
        mitre_table=list(context.mitre_table),
    )


def test_a_technique_outside_the_retrieved_table_is_dropped_and_counted():
    trace = bound_with(association("T9999", ["A-01"]))

    assert trace.mitre_associations == []
    assert trace.grounding.associations_outside_context == 1


def test_a_table_row_that_is_not_a_technique_is_dropped_and_counted():
    trace = bound_with(association("S0096", ["A-01"]))

    assert trace.mitre_associations == []
    assert trace.grounding.associations_outside_context == 1


def test_an_association_whose_claims_are_all_unknown_is_dropped_and_counted():
    trace = bound_with(association("T1059.001", ["A-07"]))

    assert trace.mitre_associations == []
    assert trace.grounding.associations_without_claim == 1
    assert trace.grounding.associations_outside_context == 0
    assert CaseAnalysisTrace.model_validate(trace.model_dump()).mitre_associations == []


def test_an_association_keeps_only_the_claims_that_exist():
    trace = bound_with(association("T1059.001", ["A-01", "A-07"]))

    assert [item.claim_ids for item in trace.mitre_associations] == [["A-01"]]
    assert trace.grounding.associations_without_claim == 0
    assert CaseAnalysisTrace.model_validate(trace.model_dump()) == trace


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
