import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.rag import MitreTableRow, QueryResponse
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.followup.contracts import FollowUpResolution
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
        original_user_content="Initial",
        clarification_exchanges=(),
        followup_root_ordinal=1,
        analysis_context={
            "retrieved_context": "existing context",
            "retrieval_context_id": "ctx-existing",
            "mitre_table": [{"technique_id": "T1190"}],
        },
    )


@pytest.mark.parametrize("action", ["initial_analysis", "add_case_info"])
def test_initial_and_added_information_run_fresh_rag_on_raw_evidence(action: str) -> None:
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
        return FollowUpResolution(outcome=None, metadata_json={"chat_followup": {}})

    outcome = asyncio.run(_run_fresh_analysis(
        value,
        rag_request=rag_request,
        analysis_request=analysis_request,
        followup_evaluator=followup_evaluator,
        policy=None,
        gap_analyzer=None,
    ))
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
