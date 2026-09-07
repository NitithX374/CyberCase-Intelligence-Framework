import asyncio
from types import SimpleNamespace
from uuid import uuid4

from app.schemas.rag import QueryResponse
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.case_analysis.mitre_applicability_contracts import (
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.clients.rag_client import RagCallFailure
from app.services.followup.contracts import FollowUpResolution
from app.services.workflow.pipeline_execution import _run_fresh_analysis, _run_question


def claimed(content: str, *, action: str = "initial_analysis"):
    source_id = uuid4()
    return SimpleNamespace(
        id=uuid4(),
        content=content,
        action=action,
        raw_evidence=f"[INITIAL CASE NARRATIVE]\n{content}",
        evidence_sha256="a" * 64,
        source_message_ids=(source_id,),
        evidence_sources=(RawEvidenceSource(message_id=source_id, content=content),),
        document_source_context=(),
        original_user_content=content,
        clarification_exchanges=(),
        followup_root_ordinal=1,
        analysis_context={
            "retrieved_context": "existing",
            "retrieval_context_id": "ctx-existing",
            "mitre_table": [],
        },
    )


async def run_fresh(value, gate, rag_request):
    counts = {"analysis": 0, "gap": 0}

    async def analysis_request(**kwargs):
        counts["analysis"] += 1
        return CaseAnalysisResult(answer="Main analysis completed", trace=None)

    async def followup_evaluator(**kwargs):
        counts["gap"] += 1
        return FollowUpResolution(question=None, metadata_json={"chat_followup": {}})

    outcome = await _run_fresh_analysis(
        value,
        rag_request=rag_request,
        analysis_request=analysis_request,
        followup_evaluator=followup_evaluator,
        policy=None,
        gap_analyzer=None,
        applicability_gate=gate,
    )
    return outcome, counts


def test_skip_avoids_rag_and_main_analysis_continues() -> None:
    value = claimed("A bicycle was stolen.")
    rag_calls = 0

    async def gate(**kwargs):
        return skipped_mitre_applicability()

    async def rag_request(query: str):
        nonlocal rag_calls
        rag_calls += 1

    outcome, counts = asyncio.run(run_fresh(value, gate, rag_request))
    assert rag_calls == 0
    assert counts == {"analysis": 1, "gap": 1}
    assert outcome.metadata_json["rag_attempt"] == {"status": "no_applicable_context"}
    assert outcome.metadata_json["chat_action"]["rag_invoked"] is False
    assert outcome.metadata_json["mitre_applicability"]["decision"] == "SKIP"
    assert outcome.retrieval_context_id is None


def test_retrieve_invokes_rag_once_before_main_analysis() -> None:
    value = claimed("PowerShell downloaded a remote script.")
    rag_calls = 0

    async def gate(**kwargs):
        source = kwargs["evidence_sources"][0]
        return MitreApplicabilityRecord(
            decision="RETRIEVE",
            source_message_ids=[str(source.message_id)],
            trigger_text=["PowerShell downloaded a remote script"],
        )

    async def rag_request(query: str):
        nonlocal rag_calls
        rag_calls += 1
        return QueryResponse(
            status="completed",
            retrieval_context_id="ctx-cyber",
            context="External ATT&CK context",
            mitre_table=[],
        )

    outcome, counts = asyncio.run(run_fresh(value, gate, rag_request))
    assert rag_calls == 1
    assert counts == {"analysis": 1, "gap": 1}
    assert outcome.metadata_json["rag_attempt"] == {"status": "used"}
    assert outcome.metadata_json["chat_action"]["rag_invoked"] is True


def test_gate_failure_fails_closed_without_blocking_analysis() -> None:
    value = claimed("PowerShell may have run.")
    rag_calls = 0

    async def gate(**kwargs):
        raise RuntimeError("provider unavailable")

    async def rag_request(query: str):
        nonlocal rag_calls
        rag_calls += 1

    outcome, counts = asyncio.run(run_fresh(value, gate, rag_request))
    assert rag_calls == 0
    assert counts == {"analysis": 1, "gap": 1}
    applicability = outcome.metadata_json["mitre_applicability"]
    assert applicability["decision"] == "SKIP"
    assert applicability["failure_code"] == "mitre_applicability_provider_error"


def test_rag_failure_after_retrieve_does_not_block_analysis() -> None:
    value = claimed("PowerShell downloaded a remote script.")

    async def gate(**kwargs):
        source = kwargs["evidence_sources"][0]
        return MitreApplicabilityRecord(
            decision="RETRIEVE",
            source_message_ids=[str(source.message_id)],
            trigger_text=["PowerShell downloaded a remote script"],
        )

    async def rag_request(query: str):
        raise RagCallFailure("rag_timeout", "RAG timed out")

    outcome, counts = asyncio.run(run_fresh(value, gate, rag_request))
    assert counts == {"analysis": 1, "gap": 1}
    assert outcome.metadata_json["rag_attempt"] == {
        "status": "unavailable",
        "failure_code": "rag_timeout",
    }
    assert outcome.retrieval_context_id is None


def test_ask_does_not_rerun_gate_or_rag() -> None:
    value = claimed("What technique applies?", action="ask")
    analysis_calls = 0

    async def analysis_request(**kwargs):
        nonlocal analysis_calls
        analysis_calls += 1
        return CaseAnalysisResult(answer="Scoped answer", trace=None)

    outcome = asyncio.run(_run_question(value, analysis_request))
    assert analysis_calls == 1
    assert outcome.metadata_json["chat_action"]["rag_invoked"] is False
    assert outcome.metadata_json["chat_action"]["retrieval_context_reused"] is True


def test_new_evidence_reevaluates_gate() -> None:
    gate_calls = 0

    async def gate(**kwargs):
        nonlocal gate_calls
        gate_calls += 1
        return skipped_mitre_applicability()

    async def rag_request(query: str):
        raise AssertionError("RAG must not run for SKIP")

    async def scenario():
        first = claimed("A phone was stolen.")
        added = claimed("A receipt was recovered.", action="add_case_info")
        await run_fresh(first, gate, rag_request)
        await run_fresh(added, gate, rag_request)

    asyncio.run(scenario())
    assert gate_calls == 2
