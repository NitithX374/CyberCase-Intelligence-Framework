import asyncio
from uuid import uuid4

from app.models.chat import ChatMessage
from app.services.case_analysis.contracts import AnalysisTraceV3, CaseAnalysisResult
from app.services.case_analysis.state_selector import (
    select_latest_canonical_case_overview,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.workflow.pipeline_execution import _run_question


def claim(claim_id: str, text: str) -> dict[str, object]:
    return {
        "claim_id": claim_id,
        "claim_type": "reported",
        "text": text,
        "epistemic_status": "reported",
        "supporting_source_message_ids": ["message-1"],
        "contradicting_source_message_ids": [],
        "reasoning_summary": None,
    }


def trace_payload(
    mode: str,
    *,
    summary: str,
    gaps: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "version": "analysis_trace_v3",
        "validation_status": "validated",
        "analysis_mode": mode,
        "summary": summary,
        "claims": [claim("A-01", summary)],
        "gaps": gaps,
        "mitre_associations": [],
        "evidence_sha256": "a" * 64,
        "retrieval_context_id": None,
    }


def gap_payload() -> dict[str, object]:
    return {
        "gap_id": "G-01",
        "topic": "Missing receipt",
        "status": "NOT_PROVIDED",
        "description": "The receipt is absent.",
        "affected_claim_ids": ["A-01"],
        "reason": "It constrains the payment finding.",
        "priority": "high",
        "askable": True,
    }


def message(ordinal: int, trace: dict[str, object]) -> ChatMessage:
    return ChatMessage(
        id=uuid4(),
        thread_id=uuid4(),
        ordinal=ordinal,
        role="assistant",
        content=f"analysis {ordinal}",
        metadata_json={"analysis_trace": trace, "mitre_table": []},
    )


def test_qa_trace_cannot_replace_canonical_case_overview() -> None:
    overview = message(
        2,
        trace_payload(
            "case_overview",
            summary="Canonical overview",
            gaps=[gap_payload()],
        ),
    )
    qa = message(
        4,
        trace_payload(
            "question_answer",
            summary="Response-scoped answer",
            gaps=[],
        ),
    )
    selected = select_latest_canonical_case_overview(
        [overview, qa],
        evidence_sha256="a" * 64,
        source_message_ids={"message-1"},
    )
    assert selected is not None
    assert selected.message.id == overview.id
    assert selected.trace.gaps[0].gap_id == "G-01"


def test_invalid_main_trace_with_gap_metadata_is_not_canonical_state() -> None:
    invalid = ChatMessage(
        id=uuid4(),
        thread_id=uuid4(),
        ordinal=2,
        role="assistant",
        content="A follow-up question",
        metadata_json={
            "analysis_state_scope": "canonical_case_overview",
            "analysis_trace_failure": {
                "version": "analysis_trace_v3",
                "validation_status": "unavailable",
                "failure_code": "analysis_trace_structure_invalid",
            },
            "chat_followup": {"gap_analysis": {"gaps": [gap_payload()]}},
            "mitre_table": [],
        },
    )
    selected = select_latest_canonical_case_overview(
        [invalid],
        evidence_sha256="a" * 64,
        source_message_ids={"message-1"},
    )
    assert selected is None


def test_invalid_later_main_trace_cannot_replace_valid_canonical_gaps() -> None:
    overview = message(
        2,
        trace_payload(
            "case_overview",
            summary="Canonical overview",
            gaps=[gap_payload()],
        ),
    )
    invalid = ChatMessage(
        id=uuid4(),
        thread_id=overview.thread_id,
        ordinal=4,
        role="assistant",
        content="Invalid replacement",
        metadata_json={
            "analysis_state_scope": "canonical_case_overview",
            "analysis_trace_failure": {
                "version": "analysis_trace_v3",
                "validation_status": "unavailable",
                "failure_code": "analysis_trace_structure_invalid",
            },
            "chat_followup": {"gap_analysis": {"gaps": [gap_payload()]}},
            "mitre_table": [],
        },
    )
    selected = select_latest_canonical_case_overview(
        [overview, invalid],
        evidence_sha256="a" * 64,
        source_message_ids={"message-1"},
    )
    assert selected is not None
    assert selected.message.id == overview.id
    assert selected.trace.gaps[0].gap_id == "G-01"


def test_question_answer_is_response_scoped_and_runs_main_analysis_once() -> None:
    source_id = uuid4()
    claimed = type(
        "Claimed",
        (),
        {
            "content": "What does the evidence establish?",
            "raw_evidence": "[INITIAL CASE NARRATIVE]\nA payment was reported.",
            "evidence_sha256": "a" * 64,
            "source_message_ids": (source_id,),
            "evidence_sources": (
                RawEvidenceSource(
                    message_id=source_id,
                    content="A payment was reported.",
                ),
            ),
            "document_source_context": (),
            "analysis_context": {"mitre_table": [], "previous_analysis": "overview"},
        },
    )()
    calls = 0

    async def analysis_request(**kwargs):
        nonlocal calls
        calls += 1
        assert kwargs["mode"] == "question_answer"
        return CaseAnalysisResult(
            answer="The payment is reported but not independently verified.",
            trace=AnalysisTraceV3.model_validate(
                {
                    "analysis_mode": "question_answer",
                    "summary": "Direct answer",
                    "claims": [
                        {
                            **claim("A-01", "The payment was reported."),
                            "supporting_source_message_ids": [str(source_id)],
                        }
                    ],
                    "gaps": [],
                    "mitre_associations": [],
                    "evidence_sha256": "a" * 64,
                    "retrieval_context_id": None,
                }
            ),
        )

    outcome = asyncio.run(_run_question(claimed, analysis_request))
    assert calls == 1
    assert outcome.analysis_trace_draft is not None
    assert outcome.analysis_trace_draft.analysis_mode == "question_answer"
    assert outcome.analysis_trace_draft.gaps == []
    assert outcome.metadata_json["analysis_state_scope"] == "response_scoped"
    assert outcome.metadata_json["canonical_case_state"] is False
    assert outcome.retrieval_context_id is None
