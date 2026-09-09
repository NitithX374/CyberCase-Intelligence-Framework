import asyncio
import hashlib
import json

import httpx
import pytest
from app.config import settings
from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_analysis.case_analysis_executor import request_case_analysis
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig
from app.services.followup.decision import evaluate_followup_outcome
from app.services.workflow.chat_run_completion import _serialize_analysis_trace
from app.services.workflow.pipeline_execution import _run_fresh_analysis
from test_claim_anchored_binding import extraction
from test_claim_anchored_pipeline import envelope
from test_stateful_clarification_pipeline import Analyzer, Policy, claimed, gap


async def forbidden(**kwargs):
    raise AssertionError("Phase 1 must never invoke technical retrieval or gate")


def test_followup_keeps_receipt_and_case_only_gap_input(monkeypatch):
    monkeypatch.setattr(settings, "openrouter_cybercase", "test")
    value = claimed("A bicycle was reported missing.")
    value.evidence_sha256 = hashlib.sha256(value.raw_evidence.encode()).hexdigest()
    value.analysis_pipeline = AnalysisPipelineConfig(
        pipeline="claim_anchored"
    ).model_dump()
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        result = (
            extraction(value.content, str(value.source_message_ids[0])).model_dump(
                mode="json"
            )
            if len(requests) == 1
            else {"units": [{"text": value.content, "claim_ids": ["A-01"]}]}
        )
        return httpx.Response(200, json=envelope(result))

    class CaseAnalyzer(Analyzer):
        async def analyze(self, **kwargs):
            assert "retrieved_context" not in kwargs["analysis_context"]
            assert "_analysis_pipeline" not in kwargs["analysis_context"]
            assert kwargs["raw_evidence"] == value.raw_evidence
            return await super().analyze(**kwargs)

    async def exercise():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:

            async def analyze(**kwargs):
                return await request_case_analysis(**kwargs, client=client)

            return await _run_fresh_analysis(
                value,
                rag_request=forbidden,
                analysis_request=analyze,
                applicability_gate=forbidden,
                followup_evaluator=evaluate_followup_outcome,
                policy=Policy("Identity", "Who saw the bicycle?"),
                gap_analyzer=CaseAnalyzer([gap("Identity")]),
            )

    outcome = asyncio.run(exercise())
    assert outcome.thread_status == "awaiting_followup"
    assert outcome.metadata_json["chat_action"]["prompt_version"] == "claim_anchored_v1"
    assert outcome.metadata_json["analysis_execution"]["units"][0]["claim_ids"] == [
        "A-01"
    ]
    assert (
        outcome.metadata_json["technical_augmentation"]["status"] == "disabled_phase1"
    )
    assert len(outcome.analysis_trace_draft.gaps) == 1
    persisted = serialize_message_metadata(
        {**outcome.metadata_json, "analysis_trace": _serialize_analysis_trace(outcome)}
    )
    assert persisted["analysis_trace"]["summary"] == value.content
    assert (
        persisted["analysis_execution"]["configuration"]["pipeline"] == "claim_anchored"
    )


def test_gap_failure_cannot_publish_attribute_first_without_trace():
    from app.services.case_analysis.contracts import CaseAnalysisResult
    from app.services.workflow.analysis_pipeline_context import bind_pipeline_outcome
    from app.services.workflow.outcome import AssistantOutcome

    result = CaseAnalysisResult(
        answer="text", trace=None, execution_receipt={"calls": ["completed"]}
    )
    with pytest.raises(ClaimAnchoredFailure) as error:
        bind_pipeline_outcome(
            AssistantOutcome("text", None, {}, "answered"),
            result,
            AnalysisPipelineConfig(pipeline="claim_anchored").model_dump(),
        )
    assert error.value.receipt == result.execution_receipt
