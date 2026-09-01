import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.rag import QueryResponse
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
    GapItem,
)
from app.services.workflow.pipeline_execution import _run_fresh_analysis


def case_value(content: str):
    source_id = uuid4()
    return SimpleNamespace(
        id=uuid4(),
        content=content,
        action="initial_analysis",
        raw_evidence=content,
        evidence_sha256="a" * 64,
        source_message_ids=(source_id,),
        evidence_sources=(RawEvidenceSource(message_id=source_id, content=content),),
        document_source_context=(),
        original_user_content=content,
        clarification_exchanges=(),
        followup_root_ordinal=1,
        analysis_context=None,
    )


def analysis(value, retrieval_id: str | None = None) -> CaseAnalysisResult:
    return CaseAnalysisResult(
        answer="Provisional summary",
        trace=AnalysisTraceV3(
            analysis_mode="case_overview",
            summary="Provisional summary",
            claims=[
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The reported event remains under review.",
                    "epistemic_status": "reported",
                    "supporting_source_message_ids": [str(value.source_message_ids[0])],
                    "contradicting_source_message_ids": [],
                    "reasoning_summary": None,
                }
            ],
            evidence_sha256=value.evidence_sha256,
            retrieval_context_id=retrieval_id,
        ),
    )


class Analyzer:
    def __init__(self, topic: str):
        self.topic = topic
        self.calls = 0

    async def analyze(self, **kwargs):
        self.calls += 1
        return GapAnalysisResult(
            analysis=GapAnalysis(
                gaps=[
                    GapItem(
                        topic=self.topic,
                        status="NOT_PROVIDED",
                        description=f"{self.topic} remains unresolved",
                        affects="A-01",
                        reason=f"{self.topic} is material",
                        priority="high",
                        askable=True,
                    )
                ]
            )
        )


class Policy:
    def __init__(self, topic: str):
        self.topic = topic
        self.calls = 0

    async def decide(self, **kwargs):
        self.calls += 1
        return FollowUpDecision(
            decision="ask_followup",
            selected_gap=self.topic,
            question=f"Can you clarify the {self.topic}?",
        )


async def skip_gate(**kwargs):
    return MitreApplicabilityRecord(decision="SKIP")


@pytest.mark.parametrize(
    ("case_text", "topic"),
    [
        ("A bicycle was taken from outside a shop.", "CCTV subject identity"),
        ("A disputed representation induced a payment.", "representation source"),
        ("Two accounts report different assault times.", "conflicting event time"),
        ("Possession of the property is disputed.", "ownership basis"),
        ("PowerShell connected to 198.51.100.23.", "connection time"),
    ],
)
def test_general_case_domains_select_canonical_gap_without_mitre(
    case_text: str,
    topic: str,
) -> None:
    value = case_value(case_text)
    analyzer = Analyzer(topic)
    policy = Policy(topic)

    async def analysis_request(**kwargs):
        assert "retrieval_context_id" not in kwargs["analysis_context"]
        return analysis(value)

    async def no_rag(query: str):
        raise AssertionError("SKIP must not invoke RAG")

    outcome = asyncio.run(
        _run_fresh_analysis(
            value,
            rag_request=no_rag,
            analysis_request=analysis_request,
            followup_evaluator=evaluate_followup_outcome,
            policy=policy,
            gap_analyzer=analyzer,
            applicability_gate=skip_gate,
        )
    )

    assert outcome.thread_status == "awaiting_followup"
    assert outcome.metadata_json["mitre_applicability"]["decision"] == "SKIP"
    assert outcome.metadata_json["rag_attempt"]["status"] == "no_applicable_context"


@pytest.mark.parametrize("rag_mode", ["unavailable", "used"])
def test_cyber_followup_does_not_depend_on_rag_availability(rag_mode: str) -> None:
    value = case_value("PowerShell connected to 198.51.100.23.")
    analyzer = Analyzer("connection time")
    policy = Policy("connection time")

    async def retrieve_gate(**kwargs):
        source = kwargs["evidence_sources"][0]
        return MitreApplicabilityRecord(
            decision="RETRIEVE",
            source_message_ids=[str(source.message_id)],
            trigger_text=[source.content],
        )

    async def rag_request(query: str):
        if rag_mode == "unavailable":
            raise RagCallFailure("rag_unavailable", "synthetic outage")
        return QueryResponse(
            status="completed",
            retrieval_context_id="ctx-used",
            context="PowerShell technical context",
            mitre_table=[],
        )

    async def analysis_request(**kwargs):
        return analysis(
            value,
            kwargs["analysis_context"].get("retrieval_context_id"),
        )

    outcome = asyncio.run(
        _run_fresh_analysis(
            value,
            rag_request=rag_request,
            analysis_request=analysis_request,
            followup_evaluator=evaluate_followup_outcome,
            policy=policy,
            gap_analyzer=analyzer,
            applicability_gate=retrieve_gate,
        )
    )

    assert outcome.thread_status == "awaiting_followup"
    assert outcome.metadata_json["rag_attempt"]["status"] == rag_mode
    assert analyzer.calls == 1
    assert policy.calls == 1
