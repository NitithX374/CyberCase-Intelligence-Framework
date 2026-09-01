import asyncio
from types import SimpleNamespace
from uuid import uuid4

from app.services.case_analysis.contracts import AnalysisTraceV3, CaseAnalysisResult
from app.services.case_analysis.mitre_applicability_contracts import (
    MitreApplicabilityRecord,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    ClarificationExchange,
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)
from app.services.followup.stateful import normalize_gap_key
from app.services.workflow.pipeline_execution import _run_fresh_analysis


def claimed(
    content: str,
    *,
    exchanges: tuple[ClarificationExchange, ...] = (),
):
    source_ids = tuple(uuid4() for _ in range(1 + len(exchanges)))
    return SimpleNamespace(
        id=uuid4(),
        content=content,
        action="add_case_info" if exchanges else "initial_analysis",
        raw_evidence=content,
        evidence_sha256="a" * 64,
        source_message_ids=source_ids,
        evidence_sources=tuple(
            RawEvidenceSource(message_id=source_id, content=content)
            for source_id in source_ids
        ),
        document_source_context=(),
        original_user_content=content,
        clarification_exchanges=exchanges,
        followup_root_ordinal=1,
        analysis_context=None,
    )


def analysis(value, retrieval_context_id: str | None = None) -> CaseAnalysisResult:
    return CaseAnalysisResult(
        answer="Current evidence supports a provisional case summary.",
        trace=AnalysisTraceV3(
            analysis_mode="case_overview",
            summary="Current evidence supports a provisional case summary.",
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
            gaps=[],
            mitre_associations=[],
            evidence_sha256=value.evidence_sha256,
            retrieval_context_id=retrieval_context_id,
        ),
    )


def gap(topic: str, *, priority: str = "high") -> GapItem:
    return GapItem(
        topic=topic,
        status="NOT_PROVIDED",
        description=f"{topic} remains unresolved",
        affects="A-01",
        reason=f"{topic} affects the current interpretation",
        priority=priority,
        askable=True,
    )


async def skip_gate(**kwargs):
    return MitreApplicabilityRecord(decision="SKIP")


class Analyzer:
    def __init__(self, gaps: list[GapItem]):
        self.gaps = gaps
        self.calls = 0

    async def analyze(self, **kwargs):
        self.calls += 1
        return GapAnalysisResult(analysis=GapAnalysis(gaps=self.gaps))


class Policy:
    def __init__(self, topic: str, question: str):
        self.topic = topic
        self.question = question
        self.calls = 0

    async def decide(self, **kwargs):
        self.calls += 1
        assert [entry.topic for entry in kwargs["gap_analysis"].gaps] == [self.topic]
        assert set(kwargs["analysis_context"]) == {"relevant_claims"}
        return FollowUpDecision(
            decision="ask_followup",
            selected_gap=self.topic,
            question=self.question,
        )


def test_valid_v3_pipeline_uses_one_gap_call_and_one_question_call() -> None:
    value = claimed("A bicycle was reported missing.")
    analyzer = Analyzer([gap("CCTV subject identity")])
    policy = Policy(
        "CCTV subject identity",
        "Is there information that identifies the CCTV subject?",
    )
    analysis_calls = 0

    async def analysis_request(**kwargs):
        nonlocal analysis_calls
        analysis_calls += 1
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

    assert analysis_calls == 1
    assert analyzer.calls == 1
    assert policy.calls == 1
    assert outcome.thread_status == "awaiting_followup"
    assert outcome.analysis_trace_draft is not None
    assert outcome.analysis_trace_draft.gaps[0].gap_id == "G-01"
    context = outcome.metadata_json["chat_followup"]["followup_context"]
    assert context == {
        "gap_topic": "CCTV subject identity",
        "gap_key": normalize_gap_key("CCTV subject identity"),
        "gap_id": "G-01",
        "evidence_sha256": value.evidence_sha256,
    }


def test_invalid_main_trace_never_runs_gap_or_followup_provider() -> None:
    value = claimed("A bicycle was reported missing.")
    analyzer = Analyzer([gap("identity")])
    policy = Policy("identity", "Can the subject be identified?")

    async def analysis_request(**kwargs):
        return CaseAnalysisResult(answer="Safe prose fallback", trace=None)

    outcome = asyncio.run(
        _run_fresh_analysis(
            value,
            rag_request=lambda query: None,
            analysis_request=analysis_request,
            followup_evaluator=evaluate_followup_outcome,
            policy=policy,
            gap_analyzer=analyzer,
            applicability_gate=skip_gate,
        )
    )

    assert outcome.content == "Safe prose fallback"
    assert outcome.analysis_trace_draft is None
    assert analyzer.calls == 0
    assert policy.calls == 0
    assert (
        outcome.metadata_json["chat_followup"]["stop_reason"]
        == "canonical_state_unavailable"
    )


def test_short_unknown_reruns_analysis_and_gap_once_then_selects_next_topic() -> None:
    history = (
        ClarificationExchange(
            question="ทราบเวลาที่เกิดเหตุหรือไม่?",
            answer="ไม่ทราบ",
            gap_id="G-09",
            gap_topic="เวลาที่เกิดเหตุ",
            gap_key=normalize_gap_key("เวลาที่เกิดเหตุ"),
        ),
    )
    value = claimed("ไม่ทราบ", exchanges=history)
    analyzer = Analyzer([gap("เวลาเกิดเหตุ"), gap("ตัวบุคคลในภาพกล้อง", priority="medium")])
    policy = Policy(
        "ตัวบุคคลในภาพกล้อง",
        "มีข้อมูลเพิ่มเติมที่ช่วยยืนยันตัวบุคคลในภาพกล้องหรือไม่?",
    )
    analysis_calls = 0

    async def analysis_request(**kwargs):
        nonlocal analysis_calls
        analysis_calls += 1
        return analysis(value)

    outcome = asyncio.run(
        _run_fresh_analysis(
            value,
            rag_request=lambda query: None,
            analysis_request=analysis_request,
            followup_evaluator=evaluate_followup_outcome,
            policy=policy,
            gap_analyzer=analyzer,
            applicability_gate=skip_gate,
        )
    )

    assert analysis_calls == 1
    assert analyzer.calls == 1
    assert policy.calls == 1
    assert outcome.analysis_trace_draft is not None
    assert outcome.analysis_trace_draft.gaps[0].status == "EXPLICITLY_UNKNOWN"
    assert outcome.analysis_trace_draft.gaps[0].askable is False
    assert outcome.metadata_json["chat_followup"]["followup_context"]["gap_id"] == (
        "G-02"
    )
