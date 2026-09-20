import asyncio
from types import SimpleNamespace
from uuid import uuid4

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseMitreAssociation,
    CaseProviderAnalysis,
    CaseSourceCitation,
)
from app.services.analysis.mitre_gate.llm import (
    MitreApplicabilityRecord,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    retrieve_technical_context,
    write_analysis,
)
from app.services.analysis.steps.technical_context import (
    CaseRagContextPayload,
    run_case_mitre_augmentation,
)
from app.services.analysis.steps.write import validate_direct_trace
from app.services.clients.rag_client import RagCallFailure
from app.services.sources import CaseSourceBundle, CaseSourceItem
from app.services.workflow import external_context


def _fixtures():
    source_id = str(uuid4())
    text = "พบการใช้ PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23"
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The evidence reports PowerShell network activity.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[
            CaseSourceCitation(
                source_id=source_id,
                exact_quote=text,
            )
        ],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=claim.text,
        claims=[claim],
    )
    source_bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),),
    )
    applicability = MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=[source_id],
        trigger_text=[text],
    )
    context = CaseRagContextPayload(
        retrieval_context_id="retrieval-case-1",
        context="PowerShell execution is external technical context.",
        mitre_table=(
            {
                "technique_id": "T1059.001",
                "name": "PowerShell",
                "description": "Command and scripting interpreter.",
            },
            {
                "technique_id": "S0096",
                "name": "Systeminfo",
                "entity_type": "Software",
                "description": "System information utility.",
            },
        ),
    )
    return source_id, trace, source_bundle, applicability, context


def _gate(record):
    async def evaluate(**kwargs):
        return record

    return evaluate


def _response(context):
    return SimpleNamespace(
        retrieval_context_id=context.retrieval_context_id,
        context=context.context,
        mitre_table=list(context.mitre_table),
    )


def test_nontechnical_case_does_not_call_rag():
    async def exercise():
        _, _, source_bundle, _, _ = _fixtures()
        calls = []

        async def rag(_query):
            calls.append("rag")
            raise AssertionError("nontechnical Case must not call RAG")

        result = await run_case_mitre_augmentation(
            source_bundle=source_bundle,
            applicability_gate=_gate(
                {"decision": "SKIP", "source_message_ids": [], "trigger_text": []}
            ),
            rag_request=rag,
        )
        assert result.status == "not_applicable"
        assert result.retrieval_context_id is None
        assert calls == []

    asyncio.run(exercise())


def test_technical_case_accepts_all_rag_rows_without_mapping_call():
    async def exercise():
        _, trace, source_bundle, applicability, context = _fixtures()
        observed = []

        async def gate(**kwargs):
            observed.append(("gate", kwargs["case_sources"][0].source_id))
            return applicability

        async def rag(query):
            observed.append(("rag", query))
            return _response(context)

        result = await run_case_mitre_augmentation(
            source_bundle=source_bundle,
            applicability_gate=gate,
            rag_request=rag,
        )
        assert result.status == "retrieved_from_rag"
        assert result.retrieval_context_id == "retrieval-case-1"
        assert result.mitre_table == list(context.mitre_table)
        assert result.associations == ()
        assert [item[0] for item in observed] == ["gate", "rag"]

    asyncio.run(exercise())


def test_empty_retrieval_is_insufficient():
    async def exercise():
        _, _, source_bundle, applicability, _ = _fixtures()

        async def rag(_query):
            return SimpleNamespace(
                retrieval_context_id="retrieval-empty", context="", mitre_table=[]
            )

        result = await run_case_mitre_augmentation(
            source_bundle=source_bundle,
            applicability_gate=_gate(applicability),
            rag_request=rag,
        )
        assert result.status == "insufficient_context"

    asyncio.run(exercise())


def test_rag_transport_failure_preserves_failed_augmentation_status():
    async def exercise():
        _, _, source_bundle, applicability, _ = _fixtures()

        async def rag(_query):
            raise RagCallFailure("rag_timeout", "timed out")

        result = await run_case_mitre_augmentation(
            source_bundle=source_bundle,
            applicability_gate=_gate(applicability),
            rag_request=rag,
        )
        assert result.status == "failed"
        assert result.failure_code == "rag_timeout"
        assert result.associations == ()

    asyncio.run(exercise())


def test_workflow_scenario_a_non_cyber_case_gate_skip():
    async def exercise():
        source_id, trace, source_bundle, _, _ = _fixtures()
        rag_calls = []

        async def fake_rag(q):
            rag_calls.append(q)
            return

        analysis_calls = []

        async def fake_analysis(**kwargs):
            analysis_calls.append(kwargs)
            return CaseAnalysisOutput(
                answer="Analysis completed without technical context.",
                trace=trace,
                execution_receipt={"calls": []},
            )

        data = AnalysisInput(sources=source_bundle, response_language="english")
        artifacts = await retrieve_technical_context(
            data,
            AnalysisArtifacts(),
            gate=_gate({"decision": "SKIP", "source_message_ids": [], "trigger_text": []}),
            rag=fake_rag,
        )
        artifacts = await write_analysis(data, artifacts, request=fake_analysis)

        assert rag_calls == []
        assert len(analysis_calls) == 1
        assert analysis_calls[0]["technical_context"] is None
        assert analysis_calls[0]["retrieval_context_id"] is None
        assert artifacts.trace.mitre_associations == []
        assert artifacts.receipt["technical_augmentation"]["status"] == "not_applicable"

    asyncio.run(exercise())


def test_workflow_scenario_b_cyber_case_gate_retrieve_augments_analysis():
    async def exercise():
        source_id, trace, source_bundle, applicability, context = _fixtures()
        call_order = []

        async def fake_gate(**kwargs):
            call_order.append("gate")
            return applicability

        async def fake_rag(q):
            call_order.append("rag")
            return _response(context)

        valid_assoc = CaseMitreAssociation(
            association_id="MA-01",
            technique_id="T1059.001",
            claim_ids=["A-01"],
            reason="PowerShell script execution detected in evidence.",
            status="candidate_only",
            support_role="external_technical_context",
        )
        augmented_trace = trace.model_copy(
            update={
                "mitre_associations": [valid_assoc],
                "retrieval_context_id": "retrieval-case-1",
            }
        )

        async def fake_analysis(**kwargs):
            call_order.append("analysis")
            assert kwargs["technical_context"] == {
                "context": context.context,
                "mitre_table": list(context.mitre_table),
            }
            assert kwargs["retrieval_context_id"] == "retrieval-case-1"
            return CaseAnalysisOutput(
                answer="Analysis with technical context.",
                trace=augmented_trace,
                execution_receipt={"calls": []},
            )

        data = AnalysisInput(sources=source_bundle, response_language="english")
        artifacts = await retrieve_technical_context(
            data, AnalysisArtifacts(), gate=fake_gate, rag=fake_rag
        )
        artifacts = await write_analysis(data, artifacts, request=fake_analysis)

        assert call_order == ["gate", "rag", "analysis"]
        assert len(artifacts.trace.mitre_associations) == 1
        assert artifacts.trace.mitre_associations[0].technique_id == "T1059.001"
        # Whether the retrieved context was used is only knowable once the trace
        # exists, so the stored status is settled at persistence time.
        stored = external_context(artifacts, 1)["technical_augmentation"]
        assert stored["status"] == "retrieved_with_matches"
        assert stored["association_ids"] == ["MA-01"]

    asyncio.run(exercise())


def test_scenario_c_invalid_technique_rejected_by_validation():
    source_id, trace, source_bundle, _, context = _fixtures()
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
    # A technique the retrieval never returned is the model's own invention.
    # It is dropped and counted, the way an invented quotation is.
    trace = validate_direct_trace(
        parsed,
        mode="case_overview",
        source_bundle=source_bundle,
        retrieval_context_id="retrieval-case-1",
        mitre_table=list(context.mitre_table),
    )
    assert trace.mitre_associations == []
    assert trace.grounding.associations_outside_context == 1


def test_workflow_scenario_d_rag_failure_falls_back_to_case_sources():
    async def exercise():
        source_id, trace, source_bundle, applicability, _ = _fixtures()

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


def test_scenario_e_case_sources_remain_only_allowed_source_ids_for_claims():
    source_id, trace, source_bundle, _, context = _fixtures()
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
    # A source id the case does not have is removed from the claim. The claim
    # survives resting on nothing, which claims_without_citation records.
    trace = validate_direct_trace(
        parsed,
        mode="case_overview",
        source_bundle=source_bundle,
        retrieval_context_id="retrieval-case-1",
        mitre_table=list(context.mitre_table),
    )
    assert trace.claims[0].supporting_source_ids == []
    assert trace.grounding.claims_without_citation == 1
