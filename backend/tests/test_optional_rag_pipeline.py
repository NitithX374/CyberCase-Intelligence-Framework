import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

from app.models.chat import ChatMessage
from app.models.rag_context import RagContext
from app.schemas.rag import MitreTableRow, QueryResponse
from app.services.case_analysis.contracts import AnalysisTraceV3, CaseAnalysisResult
from app.services.case_analysis.mitre_applicability_contracts import (
    MitreApplicabilityRecord,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.clients.rag_client import RagCallFailure
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
)
from app.services.workflow.chat_run_completion import complete_run
from app.services.workflow.pipeline_execution import _run_fresh_analysis


def claimed(case_text: str):
    source_id = uuid4()
    return SimpleNamespace(
        id=uuid4(),
        content=case_text,
        action="initial_analysis",
        raw_evidence=f"[INITIAL CASE NARRATIVE]\n{case_text}",
        evidence_sha256="a" * 64,
        source_message_ids=(source_id,),
        evidence_sources=(RawEvidenceSource(message_id=source_id, content=case_text),),
        document_source_context=(),
        original_user_content=case_text,
        clarification_exchanges=(),
        followup_root_ordinal=1,
    )


def result_for(value, *, retrieval_context_id=None, cyber=False):
    association = []
    if cyber:
        association = [
            {
                "association_id": "MA-01",
                "technique_id": "T1110",
                "claim_ids": ["A-01"],
                "reason": "The admitted context identifies password guessing.",
                "status": "candidate_only",
                "support_role": "external_technical_context",
            }
        ]
    return CaseAnalysisResult(
        answer="Evidence-bound analysis",
        trace=AnalysisTraceV3.model_validate(
            {
                "analysis_mode": "case_overview",
                "summary": "Evidence-bound overview",
                "claims": [
                    {
                        "claim_id": "A-01",
                        "claim_type": "reported",
                        "text": "The incident was reported by the user.",
                        "epistemic_status": "reported",
                        "supporting_source_message_ids": [
                            str(value.source_message_ids[0])
                        ],
                        "contradicting_source_message_ids": [],
                        "reasoning_summary": None,
                    }
                ],
                "gaps": [],
                "mitre_associations": association,
                "evidence_sha256": value.evidence_sha256,
                "retrieval_context_id": retrieval_context_id,
            }
        ),
    )


async def run_overview(value, rag_request, *, cyber=False):
    counts = {"analysis": 0, "gap": 0}

    async def analysis_request(**kwargs):
        counts["analysis"] += 1
        assert kwargs["raw_evidence"] == value.raw_evidence
        retrieval_id = kwargs["analysis_context"].get("retrieval_context_id")
        assert "RAG service request timed out" not in kwargs["raw_evidence"]
        return result_for(
            value,
            retrieval_context_id=retrieval_id,
            cyber=cyber,
        )

    class Analyzer:
        async def analyze(self, **kwargs):
            counts["gap"] += 1
            assert kwargs["analysis_claims"][0]["claim_id"] == "A-01"
            return GapAnalysisResult(analysis=GapAnalysis(gaps=[]))

    class Policy:
        async def decide(self, **kwargs):
            return FollowUpDecision(decision="proceed")

    async def applicability_gate(**kwargs):
        source = kwargs["evidence_sources"][0]
        return MitreApplicabilityRecord(
            decision="RETRIEVE",
            source_message_ids=[str(source.message_id)],
            trigger_text=[source.content],
        )

    outcome = await _run_fresh_analysis(
        value,
        rag_request=rag_request,
        analysis_request=analysis_request,
        followup_evaluator=evaluate_followup_outcome,
        policy=Policy(),
        gap_analyzer=Analyzer(),
        applicability_gate=applicability_gate,
    )
    return outcome, counts


def test_theft_analysis_completes_when_rag_is_unavailable() -> None:
    value = claimed("A bicycle was reported stolen from a shop.")

    async def rag_request(query: str):
        raise RagCallFailure("rag_timeout", "RAG service request timed out")

    outcome, counts = asyncio.run(run_overview(value, rag_request))
    assert counts == {"analysis": 1, "gap": 1}
    assert outcome.analysis_trace_draft is not None
    assert outcome.analysis_trace_draft.retrieval_context_id is None
    assert outcome.analysis_trace_draft.mitre_associations == []
    assert outcome.rag_context_payload is None
    assert outcome.metadata_json["rag_attempt"] == {
        "status": "unavailable",
        "failure_code": "rag_timeout",
    }
    serialized = json.dumps(
        outcome.analysis_trace_draft.model_dump(mode="json"),
        ensure_ascii=False,
    )
    assert "rag_timeout" not in serialized
    assert "RAG service request timed out" not in serialized


def test_fraud_analysis_completes_when_rag_has_no_usable_context() -> None:
    value = claimed("A buyer reported paying for goods that never arrived.")

    async def rag_request(query: str):
        return QueryResponse(
            status="completed",
            retrieval_context_id="ctx-empty",
            context="",
            mitre_table=[],
        )

    outcome, counts = asyncio.run(run_overview(value, rag_request))
    assert counts == {"analysis": 1, "gap": 1}
    assert outcome.retrieval_context_id is None
    assert outcome.rag_context_payload is None
    assert outcome.metadata_json["rag_attempt"] == {"status": "no_applicable_context"}


def test_cyber_analysis_preserves_successful_rag_and_mitre_binding() -> None:
    value = claimed("Repeated failed logins targeted the administrator account.")

    async def rag_request(query: str):
        return QueryResponse(
            status="completed",
            retrieval_context_id="ctx-cyber",
            context="Password guessing is described by ATT&CK T1110.",
            mitre_table=[
                MitreTableRow(
                    technique_id="T1110",
                    name="Brute Force",
                )
            ],
        )

    outcome, counts = asyncio.run(run_overview(value, rag_request, cyber=True))
    assert counts == {"analysis": 1, "gap": 1}
    assert outcome.retrieval_context_id == "ctx-cyber"
    assert outcome.rag_context_payload is not None
    assert outcome.rag_context_payload.retrieval_context_id == "ctx-cyber"
    assert outcome.analysis_trace_draft is not None
    assert outcome.analysis_trace_draft.mitre_associations[0].technique_id == "T1110"
    assert outcome.metadata_json["rag_attempt"] == {"status": "used"}


class Transaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class CompletionDb:
    def __init__(self):
        self.added = []

    def begin(self):
        return Transaction()

    def add(self, value):
        self.added.append(value)

    async def flush(self):
        return None


def test_rag_failure_does_not_persist_a_fake_rag_context() -> None:
    value = claimed("A bicycle was reported stolen.")

    async def rag_request(query: str):
        raise RagCallFailure("rag_service_error", "RAG service request failed")

    outcome, _ = asyncio.run(run_overview(value, rag_request))
    db = CompletionDb()
    thread = SimpleNamespace(id=uuid4(), next_message_ordinal=2, status="processing")
    run = SimpleNamespace(id=value.id, thread_id=thread.id)

    async def lock_thread(run_id):
        return thread

    async def lock_run(run_id, worker_id):
        return run

    completed = asyncio.run(
        complete_run(
            db,
            value.id,
            "worker",
            outcome,
            lock_run_thread_fn=lock_thread,
            lock_owned_running_run_fn=lock_run,
        )
    )
    assert completed is True
    assert not any(isinstance(item, RagContext) for item in db.added)
    assert any(isinstance(item, ChatMessage) for item in db.added)
