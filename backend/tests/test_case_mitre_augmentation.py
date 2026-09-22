import asyncio
from types import SimpleNamespace

from case_mitre_test_support import _fixtures, _gate, _response

from app.schemas.rag import LegalReferenceResult
from app.services.analysis.contracts import (
    CaseAnalysisOutput,
    CaseMitreAssociation,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    retrieve_technical_context,
    write_analysis,
)
from app.services.analysis.steps.technical_context import (
    run_case_mitre_augmentation,
)
from app.services.clients.rag_client import RagCallFailure
from app.services.workflow import external_context


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
        assert list(result.context.mitre_table) == list(context.mitre_table)
        assert result.context.legal_relevance == context.legal_relevance
        assert result.associations == ()
        assert [item[0] for item in observed] == ["gate", "rag"]

    asyncio.run(exercise())


def test_empty_retrieval_is_insufficient():
    async def exercise():
        _, _, source_bundle, applicability, _ = _fixtures()

        async def rag(_query):
            return SimpleNamespace(
                retrieval_context_id="retrieval-empty",
                context="",
                mitre_table=[],
                legal_reference=LegalReferenceResult(),
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
