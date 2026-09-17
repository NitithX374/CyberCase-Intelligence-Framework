import asyncio
import json
from unittest.mock import Mock

import httpx
import pytest
from pydantic import ValidationError

from app.config import settings
from app.services.case_analysis import case_analysis
from app.services.case_analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisOutput,
    CaseQuestionAnswerOutput,
    CaseQuestionAnswerResponse,
)
from app.services.case_analysis.pipeline_config import configured_pipeline
from app.services.case_analysis.prompts import CASE_REASONING_SYSTEM_PROMPT, case_system_prompt
from app.services.case_materials import CaseSourceBundle, CaseSourceItem
from app.services.case_materials.case_source_bundle import (
    build_case_reasoning_payload,
    provider_source_payload,
)


def source_bundle() -> CaseSourceBundle:
    return CaseSourceBundle(revision=2, sources=(
        CaseSourceItem(
            source_id="6ccca6b3-0d99-4c68-bf5a-36bb712997fd",
            source_kind="document",
            text="ผู้เสียหายชื่อสมชาย",
            document_id="document-id",
            filename="case.pdf",
            provenance={
                "extraction_method": "ocr",
                "provider": "typhoon",
                "verification_status": "needs_review",
                "warnings": ["OCR uncertainty"],
            },
        ),
        CaseSourceItem(
            source_id="followup-source-id",
            source_kind="followup_answer",
            text="22:30",
            provenance={
                "gap_id": "G-03",
                "gap_key": "incident_time",
                "topic": "เวลาเกิดเหตุ",
                "clarification_question": "เหตุเกิดเวลาประมาณเท่าใด?",
                "source_analysis_id": "historical-analysis-id",
                "source_revision": 1,
                "question_message_id": "historical-question-id",
            },
        ),
    ))


def provider_overview(bundle: CaseSourceBundle) -> dict[str, object]:
    source = bundle.sources[0]
    return {
        "version": "case_analysis_trace_v1",
        "answer": source.text,
        "summary": source.text,
        "involved_parties": [],
        "timeline": [],
        "impacts": [],
        "claims": [{
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": source.text,
            "epistemic_status": "reported",
            "supporting_source_ids": [source.source_id],
            "supporting_citations": [{
                "source_id": source.source_id,
                "exact_quote": source.text,
            }],
        }],
    }


def provider_response(payload: dict[str, object]) -> httpx.Response:
    return httpx.Response(200, json={
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
    })


def test_both_production_modes_share_payload_sources_identity_and_generation(monkeypatch):
    bundle = source_bundle()
    observed = []
    history = [{"role": "user", "content": f"historical message {i}"} for i in range(15)]
    technical_context = {"context": "external knowledge", "mitre_table": [{"technique_id": "T1059"}]}
    analysis_context = {
        "analysis_id": "analysis-id",
        "freshness": "current",
        "summary": "The persisted analysis summary",
    }
    active_clarification = {
        "status": "current",
        "question_message_id": "question-id",
        "gap_id": "G-01",
    }
    monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")

    def provider(request):
        wire = json.loads(request.content)
        content = json.loads(wire["messages"][0]["content"])
        observed.append((wire, content))
        if content["analysis_mode"] == "case_overview":
            return provider_response(provider_overview(bundle))
        return provider_response({
            "answer": f"ผู้เสียหายชื่อสมชาย [{bundle.sources[0].source_id}]",
            "cited_source_ids": [bundle.sources[0].source_id],
            "clarification_question": "  บัญชีใดที่คุณหมายถึง?  ",
        })

    async def exercise():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            overview = await case_analysis.request_case_analysis(
                mode="case_overview", source_bundle=bundle,
                pipeline_config=configured_pipeline().model_dump(mode="json"),
                question=None, user_message="วิเคราะห์คดี", client=client,
                technical_context=technical_context, retrieval_context_id="retrieval-id",
            )
            answer = await case_analysis.request_case_reasoning(
                mode="question_answer", source_bundle=bundle,
                pipeline_config=configured_pipeline().model_dump(mode="json"),
                question="ผู้เสียหายชื่ออะไร", user_message="ผู้เสียหายชื่ออะไร",
                conversation_history=history, technical_context=technical_context,
                analysis_context=analysis_context, active_clarification=active_clarification,
                current_evidence_revision=3, analysis_evidence_revision=3, client=client,
            )
            assert isinstance(overview, CaseAnalysisOutput)
            assert overview.trace.claims[0].supporting_citations[0].exact_quote == bundle.sources[0].text
            assert isinstance(answer, CaseQuestionAnswerOutput)
            assert answer.cited_source_ids == (bundle.sources[0].source_id,)
            assert answer.clarification_question == "บัญชีใดที่คุณหมายถึง?"
            assert not hasattr(answer, "trace")
            assert overview.execution_receipt["calls"][0]["stage"] == "case_direct"
            assert answer.execution_receipt["calls"][0]["stage"] == "case_question_answer"

    asyncio.run(exercise())
    overview_wire, overview_payload = observed[0]
    answer_wire, answer_payload = observed[1]
    expected_sources = [provider_source_payload(source) for source in bundle.sources]
    assert overview_payload["case_sources"] == answer_payload["case_sources"] == expected_sources
    assert overview_payload["technical_context"] == answer_payload["technical_context"] == technical_context
    assert overview_payload["conversation_history"] == []
    assert answer_payload["conversation_history"] == history[-12:]
    assert answer_payload["response_language"] == overview_payload["response_language"] == "thai"
    assert "analysis_context" not in overview_payload
    assert answer_payload["analysis_context"] == analysis_context
    assert answer_payload["active_clarification"] == active_clarification
    assert answer_payload["current_evidence_revision"] == 3
    assert answer_payload["analysis_evidence_revision"] == 3
    assert overview_wire["system"].startswith(CASE_REASONING_SYSTEM_PROMPT)
    assert answer_wire["system"].startswith(CASE_REASONING_SYSTEM_PROMPT)
    assert overview_wire["model"] == answer_wire["model"]
    assert "claims" in overview_wire["output_config"]["format"]["schema"]["properties"]
    assert set(answer_wire["output_config"]["format"]["schema"]["properties"]) == {
        "answer", "cited_source_ids", "clarification_question",
    }


def test_followup_context_is_bounded_provenance_not_source_text():
    source = source_bundle().sources[1]
    assert provider_source_payload(source) == {
        "source_id": source.source_id,
        "source_kind": "followup_answer",
        "text": "22:30",
        "followup_context": {
            "gap_id": "G-03", "gap_key": "incident_time", "topic": "เวลาเกิดเหตุ",
            "clarification_question": "เหตุเกิดเวลาประมาณเท่าใด?",
        },
    }


def test_overview_excludes_conversation_history_even_when_supplied():
    payload = build_case_reasoning_payload(
        source_bundle=source_bundle(), response_language="english", mode="case_overview",
        question=None, conversation_history=[{"role": "assistant", "content": "Old analytical claim"}],
    )
    assert payload["conversation_history"] == []
    assert set(payload) == {
        "response_language", "analysis_mode", "case_sources", "technical_context", "question", "conversation_history",
    }


@pytest.mark.parametrize("citations", [[], ["does-not-exist"], [source_bundle().sources[0].source_id]])
def test_qa_validates_citations_without_trace_construction_or_correction(monkeypatch, citations):
    bundle = source_bundle()
    forbidden = Mock(side_effect=AssertionError("Ordinary Q&A must not construct or validate an analysis trace"))
    for name in ("validate_direct_trace", "validate_case_trace", "CaseAnalysisTrace"):
        monkeypatch.setattr(case_analysis, name, forbidden)
    monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
    requests = []

    def provider(request):
        requests.append(request)
        return provider_response({"answer": "ข้อมูลปัจจุบัน", "cited_source_ids": citations})

    async def exercise():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            return await case_analysis.request_case_reasoning(
                mode="question_answer", source_bundle=bundle,
                pipeline_config=configured_pipeline().model_dump(mode="json"),
                question="ผู้เสียหายชื่ออะไร", user_message="ผู้เสียหายชื่ออะไร", client=client,
            )

    if citations == ["does-not-exist"]:
        with pytest.raises(CaseAnalysisFailure) as error:
            asyncio.run(exercise())
        assert error.value.code == "case_question_answer_unknown_source"
    else:
        assert asyncio.run(exercise()).cited_source_ids == tuple(citations)
    assert len(requests) == 1
    forbidden.assert_not_called()


@pytest.mark.parametrize("payload", [
    {"answer": ""}, {"answer": " \n\t "}, {"answer": "x" * 24_001},
    {"answer": "answer", "cited_source_ids": ["s"] * 65},
    {"answer": "answer", "gaps": []}, {"answer": "answer", "gap_id": "G-01"},
    {"answer": "answer", "clarification_question": ""},
    {"answer": "answer", "clarification_question": " \n\t "},
])
def test_qa_contract_rejects_empty_answers_and_formal_analysis_fields(payload):
    with pytest.raises(ValidationError):
        CaseQuestionAnswerResponse.model_validate(payload)


def test_qa_contract_accepts_and_strips_optional_clarification():
    response = CaseQuestionAnswerResponse.model_validate({
        "answer": "answer",
        "cited_source_ids": [],
        "clarification_question": "  Which account do you mean?  ",
    })
    assert response.clarification_question == "Which account do you mean?"


def test_qa_prompt_has_no_overview_requirements():
    prompt = case_system_prompt("question_answer")
    assert "only the user's current question" in prompt
    assert "not Case evidence" in prompt
    assert "Do not invent a formal gap" in prompt
    assert "Do not repeat a clarification already answered" in prompt
    assert "analysis_context" in prompt
    assert "active_clarification" in prompt
    assert "freshness" in prompt
    assert "Case Structure:" not in prompt
    assert "Use sequential gap IDs" not in prompt
