import asyncio
from types import SimpleNamespace
from uuid import uuid4

from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.case_materials import CaseSourceBundle, CaseSourceItem
from app.services.case_analysis.mitre_applicability_gate import (
    MitreApplicabilityRecord,
)
from app.services.clients.rag_client import RagCallFailure
from app.services.workflow.case_mitre_augmentation import (
    CaseRagContextPayload,
    merge_case_mitre_trace,
    run_case_mitre_augmentation,
)


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
        sources=(
            CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),
        ),
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
            run_id=uuid4(),
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
            run_id=uuid4(),
            source_bundle=source_bundle,
            applicability_gate=gate,
            rag_request=rag,
        )
        assert result.status == "retrieved_from_rag"
        assert result.retrieval_context_id == "retrieval-case-1"
        assert result.mitre_table == list(context.mitre_table)
        assert result.associations == ()
        merged = merge_case_mitre_trace(
            trace,
            result,
            source_bundle,
        )
        assert merged.mitre_associations == []
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
            run_id=uuid4(),
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
            run_id=uuid4(),
            source_bundle=source_bundle,
            applicability_gate=_gate(applicability),
            rag_request=rag,
        )
        assert result.status == "failed"
        assert result.failure_code == "rag_timeout"
        assert result.associations == ()

    asyncio.run(exercise())
