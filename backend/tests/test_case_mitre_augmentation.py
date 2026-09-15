import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import httpx

from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseSourceCitation,
    CaseMitreAssociation,
)
from app.services.case_materials import CaseSourceBundle, CaseSourceItem
from app.services.case_analysis.mitre_applicability_gate import (
    MitreApplicabilityRecord,
)
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig
from app.services.clients.rag_client import RagCallFailure
from app.services.workflow.case_mitre_augmentation import (
    CaseRagContextPayload,
    merge_case_mitre_trace,
    request_case_mitre_mapping,
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


def _association():
    return CaseMitreAssociation(
        association_id="MA-01",
        technique_id="T1059.001",
        claim_ids=["A-01"],
        reason="The external technique describes the reported PowerShell behavior.",
        status="candidate_only",
        support_role="external_technical_context",
    )


def test_nontechnical_case_does_not_call_rag_or_mapping():
    async def exercise():
        _, trace, source_bundle, _, _ = _fixtures()
        calls = []

        async def rag(_query):
            calls.append("rag")
            raise AssertionError("nontechnical Case must not call RAG")

        async def mapping(**_kwargs):
            calls.append("mapping")
            raise AssertionError("nontechnical Case must not map MITRE")

        result = await run_case_mitre_augmentation(
            run_id=uuid4(),
            source_bundle=source_bundle,
            base_trace=trace,
            config=AnalysisPipelineConfig(),
            applicability_gate=_gate(
                {"decision": "SKIP", "source_message_ids": [], "trigger_text": []}
            ),
            rag_request=rag,
            mapping_request=mapping,
        )
        assert result.status == "not_applicable"
        assert result.retrieval_context_id is None
        assert calls == []

    asyncio.run(exercise())


def test_technical_case_calls_rag_and_persists_case_claim_mapping():
    async def exercise():
        source_id, trace, source_bundle, applicability, context = _fixtures()
        observed = []

        async def gate(**kwargs):
            observed.append(("gate", kwargs["case_sources"][0].source_id))
            return applicability

        async def rag(query):
            observed.append(("rag", query))
            return _response(context)

        async def mapping(**kwargs):
            observed.append(("mapping", kwargs["context"].retrieval_context_id))
            assert kwargs["claims"][0].supporting_source_ids == [source_id]
            return [_association()]

        result = await run_case_mitre_augmentation(
            run_id=uuid4(),
            source_bundle=source_bundle,
            base_trace=trace,
            config=AnalysisPipelineConfig(),
            applicability_gate=gate,
            rag_request=rag,
            mapping_request=mapping,
        )
        assert result.status == "retrieved_with_matches"
        assert result.retrieval_context_id == "retrieval-case-1"
        assert result.associations == (_association(),)
        merged = merge_case_mitre_trace(
            trace,
            result,
            source_bundle,
        )
        assert merged.mitre_associations[0].technique_id == "T1059.001"
        assert [item[0] for item in observed] == ["gate", "rag", "mapping"]

    asyncio.run(exercise())


def test_empty_retrieval_is_insufficient_without_mapping():
    async def exercise():
        _, trace, source_bundle, applicability, _ = _fixtures()
        called = False

        async def rag(_query):
            return SimpleNamespace(retrieval_context_id="retrieval-empty", context="", mitre_table=[])

        async def mapping(**_kwargs):
            nonlocal called
            called = True
            return []

        result = await run_case_mitre_augmentation(
            run_id=uuid4(),
            source_bundle=source_bundle,
            base_trace=trace,
            config=AnalysisPipelineConfig(),
            applicability_gate=_gate(applicability),
            rag_request=rag,
            mapping_request=mapping,
        )
        assert result.status == "insufficient_context"
        assert not called

    asyncio.run(exercise())


def test_rag_transport_failure_preserves_failed_augmentation_status():
    async def exercise():
        _, trace, source_bundle, applicability, _ = _fixtures()

        async def rag(_query):
            raise RagCallFailure("rag_timeout", "timed out")

        result = await run_case_mitre_augmentation(
            run_id=uuid4(),
            source_bundle=source_bundle,
            base_trace=trace,
            config=AnalysisPipelineConfig(),
            applicability_gate=_gate(applicability),
            rag_request=rag,
        )
        assert result.status == "failed"
        assert result.failure_code == "rag_timeout"
        assert result.associations == ()

    asyncio.run(exercise())


def test_mapping_http_boundary_uses_existing_core_provider(monkeypatch):
    async def exercise():
        source_id, trace, _, applicability, context = _fixtures()
        captured = {}

        class Client:
            async def post(self, url, *, headers, json, timeout):
                captured.update({"url": url, "json": json})
                return httpx.Response(
                    200,
                    json={
                        "content": [
                            {
                                "type": "text",
                                "text": json_module.dumps(
                                    {
                                        "version": "case_mitre_mapping_v1",
                                        "associations": [_association().model_dump(mode="json")],
                                    }
                                ),
                            }
                        ]
                    },
                )

        monkeypatch.setattr(
            "app.services.workflow.case_mitre_augmentation.resolve_target",
            lambda _config: SimpleNamespace(
                model="test-model",
                provider="anthropic",
                messages_url="https://provider.invalid/messages",
                headers={},
            ),
        )
        calls = []
        associations = await request_case_mitre_mapping(
            claims=trace.claims,
            applicability=applicability,
            context=context,
            config=AnalysisPipelineConfig(provider="anthropic", model="test-model"),
            calls=calls,
            client=Client(),
        )
        assert associations == (_association(),)
        assert captured["url"] == "https://provider.invalid/messages"
        assert captured["json"]["output_config"]["format"]["type"] == "json_schema"
        assert calls[0]["stage"] == "case_mitre_mapping"
        assert source_id in json_module.dumps(captured["json"])

    json_module = json
    asyncio.run(exercise())
