import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.rag import MitreTableRow, QueryResponse
from app.services.case_analysis.mitre_applicability_contracts import (
    MitreApplicabilityRecord,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.case_analysis.contracts import (
    AnalysisTraceDraft,
    AnalysisTraceV3,
    CaseAnalysisResult,
)
from app.services.followup.contracts import FollowUpResolution
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)
from app.services.workflow.chat_run_completion import _serialize_analysis_trace
from app.services.workflow.outcome import AssistantOutcome
from app.services.workflow.pipeline_execution import _run_fresh_analysis, _run_question


def claimed(action: str):
    source_id = uuid4()
    return SimpleNamespace(
        id=uuid4(),
        content="new information" if action != "ask" else "What happened?",
        action=action,
        raw_evidence="[INITIAL CASE NARRATIVE]\nInitial\n\n[ADDED CASE INFORMATION #1]\nNew",
        evidence_sha256="a" * 64,
        source_message_ids=(source_id,),
        evidence_sources=(RawEvidenceSource(message_id=source_id, content="Initial"),),
        document_source_context=(),
        original_user_content="Initial",
        clarification_exchanges=(),
        followup_root_ordinal=1,
        analysis_context={
            "retrieved_context": "existing context",
            "retrieval_context_id": "ctx-existing",
            "mitre_table": [{"technique_id": "T1190"}],
        },
    )


async def retrieve_gate(**kwargs):
    source = kwargs["evidence_sources"][0]
    return MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=[str(source.message_id)],
        trigger_text=[source.content],
    )


@pytest.mark.parametrize("action", ["initial_analysis", "add_case_info"])
def test_initial_and_added_information_run_fresh_rag_on_raw_evidence(
    action: str,
) -> None:
    value = claimed(action)
    calls: list[str] = []

    async def rag_request(query: str):
        calls.append(query)
        return QueryResponse(
            status="completed",
            retrieval_context_id=f"ctx-{action}",
            context="external context",
            mitre_table=[
                MitreTableRow(
                    technique_id="T1190",
                    name="Exploit Public-Facing Application",
                )
            ],
        )

    async def analysis_request(**kwargs):
        assert kwargs["raw_evidence"] == value.raw_evidence
        assert kwargs["analysis_context"]["source_message_ids"] == [
            str(value.source_message_ids[0])
        ]
        return CaseAnalysisResult(answer="analysis", trace=None)

    async def followup_evaluator(**kwargs):
        assert kwargs["raw_evidence"] == value.raw_evidence
        return FollowUpResolution(question=None, metadata_json={"chat_followup": {}})

    outcome = asyncio.run(
        _run_fresh_analysis(
            value,
            rag_request=rag_request,
            analysis_request=analysis_request,
            followup_evaluator=followup_evaluator,
            policy=None,
            gap_analyzer=None,
            applicability_gate=retrieve_gate,
        )
    )
    assert calls == [value.raw_evidence]
    assert outcome.rag_context_payload is not None
    assert outcome.metadata_json["chat_action"]["rag_invoked"] is True


def test_ask_reuses_context_and_does_not_create_rag_payload() -> None:
    value = claimed("ask")

    async def analysis_request(**kwargs):
        assert kwargs["question"] == "What happened?"
        assert kwargs["analysis_context"]["retrieval_context_id"] == "ctx-existing"
        return CaseAnalysisResult(answer="answer", trace=None)

    outcome = asyncio.run(_run_question(value, analysis_request))
    assert outcome.rag_context_payload is None
    assert outcome.retrieval_context_id == "ctx-existing"
    assert outcome.metadata_json["chat_action"]["rag_invoked"] is False


def test_v3_trace_persists_without_a_retrieval_context() -> None:
    trace = AnalysisTraceV3.model_validate(
        {
            "analysis_mode": "case_overview",
            "summary": "A bicycle was reported missing.",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The owner reported a missing bicycle.",
                    "epistemic_status": "reported",
                    "supporting_source_message_ids": ["S1"],
                    "contradicting_source_message_ids": [],
                    "reasoning_summary": None,
                }
            ],
            "evidence_sha256": "a" * 64,
            "retrieval_context_id": None,
        }
    )
    outcome = AssistantOutcome(
        content="Grounded overview",
        retrieval_context_id=None,
        metadata_json={},
        thread_status="answered",
        analysis_trace_draft=trace,
        evidence_sha256="a" * 64,
    )
    serialized = _serialize_analysis_trace(outcome)
    assert serialized is not None
    assert serialized["version"] == "analysis_trace_v3"
    assert serialized["retrieval_context_id"] is None


def test_v2_trace_persistence_remains_backward_compatible() -> None:
    trace = AnalysisTraceDraft.model_validate(
        {
            "analysis_mode": "case_overview",
            "claims": [],
            "mitre_associations": [],
        }
    )
    outcome = AssistantOutcome(
        content="Legacy grounded overview",
        retrieval_context_id="ctx-v2",
        metadata_json={},
        thread_status="answered",
        analysis_trace_draft=trace,
        evidence_sha256="b" * 64,
    )
    serialized = _serialize_analysis_trace(outcome)
    assert serialized is not None
    assert serialized["version"] == "analysis_trace_v2"
    assert serialized["retrieval_context_id"] == "ctx-v2"


def test_fresh_pipeline_uses_one_analysis_and_one_gap_result_for_both_surfaces() -> (
    None
):
    value = claimed("initial_analysis")
    analysis_calls = 0
    gap_calls = 0

    async def rag_request(query: str):
        return QueryResponse(
            status="completed",
            retrieval_context_id="ctx-canonical",
            context="Relevant external context",
            mitre_table=[],
        )

    async def analysis_request(**kwargs):
        nonlocal analysis_calls
        analysis_calls += 1
        return CaseAnalysisResult(
            answer="The property association remains provisional.",
            trace=AnalysisTraceV3.model_validate(
                {
                    "analysis_mode": "case_overview",
                    "summary": "A property association is under review.",
                    "claims": [
                        {
                            "claim_id": "A-01",
                            "claim_type": "reported",
                            "text": "The suspect may possess the missing property.",
                            "epistemic_status": "reported",
                            "supporting_source_message_ids": [
                                str(value.source_message_ids[0])
                            ],
                            "contradicting_source_message_ids": [],
                            "reasoning_summary": None,
                        }
                    ],
                    "gaps": [],
                    "mitre_associations": [],
                    "evidence_sha256": value.evidence_sha256,
                    "retrieval_context_id": "ctx-canonical",
                }
            ),
        )

    class CountingGapAnalyzer:
        async def analyze(self, **kwargs):
            nonlocal gap_calls
            gap_calls += 1
            assert kwargs["analysis_claims"][0]["claim_id"] == "A-01"
            return GapAnalysisResult(
                analysis=GapAnalysis(
                    gaps=[
                        GapItem(
                            topic="Property identity",
                            status="AMBIGUOUS",
                            description="The object has not been independently identified.",
                            affects="A-01 — suspect possession of the missing property",
                            reason="Identification constrains the property association.",
                            priority="medium",
                            askable=True,
                        )
                    ]
                )
            )

    class AskPolicy:
        async def decide(self, **kwargs):
            return FollowUpDecision(
                decision="ask_followup",
                selected_gap="Property identity",
                question="Can you identify the property shown in the footage?",
            )

    outcome = asyncio.run(
        _run_fresh_analysis(
            value,
            rag_request=rag_request,
            analysis_request=analysis_request,
            followup_evaluator=evaluate_followup_outcome,
            policy=AskPolicy(),
            gap_analyzer=CountingGapAnalyzer(),
            applicability_gate=retrieve_gate,
        )
    )

    assert analysis_calls == 1
    assert gap_calls == 1
    assert outcome.thread_status == "awaiting_followup"
    assert outcome.analysis_trace_draft is not None
    assert outcome.analysis_trace_draft.gaps[0].affected_claim_ids == ["A-01"]
    legacy_gaps = outcome.metadata_json["chat_followup"]["gap_analysis"]["gaps"]
    assert legacy_gaps[0]["status"] == "AMBIGUOUS"
    assert legacy_gaps[0]["affects"].startswith("A-01")
