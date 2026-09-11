import asyncio
import hashlib
import json

import httpx
import pytest
from app.config import settings
from app.services.case_analysis.claim_anchored.service import analyze_claim_anchored
from app.services.case_analysis.claim_anchored.contracts import ClaimAnchoredFailure
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from test_claim_anchored_binding import extraction, source_context


def envelope(value):
    return {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
        "usage": {"input_tokens": 100, "output_tokens": 30},
        "model": "test-model",
    }


def run_pipeline(
    monkeypatch, *, quote="พยานไม่เห็นผู้ต้องหา", config=None, generated=None, status=200
):
    monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
    config = config or AnalysisPipelineConfig(pipeline="claim_anchored")
    context = source_context()
    context.update(
        {
            "retrieved_context": "EXTERNAL_POISON",
            "mitre_table": [{"text": "EXTERNAL_POISON"}],
            "_analysis_pipeline": config.model_dump(),
            "previous_analysis": "EXTERNAL_POISON",
        }
    )
    raw = "[INITIAL CASE NARRATIVE]\nพยานไม่เห็นผู้ต้องหา"
    context["_evidence_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
    requests = []

    def handler(request):
        payload = json.loads(request.content)
        requests.append(payload)
        if len(requests) == 1:
            response = extraction(quote).model_dump(mode="json")
        else:
            response = generated or {
                "units": [{"text": "พยานระบุว่าไม่เห็นผู้ต้องหา", "claim_ids": ["A-01"]}]
            }
        assert "EXTERNAL_POISON" not in request.content.decode()
        return httpx.Response(
            status if len(requests) == 2 else 200, json=envelope(response)
        )

    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await analyze_claim_anchored(
                raw_evidence=raw,
                analysis_context=context,
                user_message="thai",
                config=config,
                client=client,
            )

    return execute, requests, context


def test_two_stage_pipeline_is_source_isolated_and_compatible(monkeypatch):
    execute, requests, context = run_pipeline(monkeypatch)
    result = asyncio.run(execute())
    assert len(requests) == 2
    assert result.answer == result.trace.summary
    assert (
        result.trace.claims[0].supporting_citations[0].exact_quote == "พยานไม่เห็นผู้ต้องหา"
    )
    assert result.trace.evidence_sha256 == context["_evidence_sha256"]
    receipt = result.execution_receipt
    assert receipt["semantic_verification"] == "not_performed"
    assert [call["status"] for call in receipt["calls"]] == ["completed", "completed"]
    assert receipt["calls"][0]["usage"]["input_tokens"] == 100
    generation = json.loads(requests[1]["messages"][0]["content"])
    assert set(generation) == {"selected_claims", "response_language"}
    assert (
        generation["selected_claims"][0]["evidence"][0]["exact_quote"]
        == "พยานไม่เห็นผู้ต้องหา"
    )


def test_invalid_quote_fails_before_generation_without_legacy_fallback(monkeypatch):
    execute, requests, _ = run_pipeline(monkeypatch, quote="พยานเห็นผู้ต้องหา")
    with pytest.raises(ClaimAnchoredFailure) as error:
        asyncio.run(execute())
    assert error.value.code == "claim_quote_absent"
    assert len(requests) == 1
    assert error.value.receipt["calls"][0]["status"] == "completed"


def test_generation_failure_keeps_extraction_receipt(monkeypatch):
    execute, requests, _ = run_pipeline(monkeypatch, status=503)
    with pytest.raises(ClaimAnchoredFailure) as error:
        asyncio.run(execute())
    assert len(requests) == 2
    assert len(error.value.receipt["selected_claims"]) == 1
    assert error.value.receipt["calls"][-1]["status"] == "failed"


def test_input_budget_fails_before_any_provider_call(monkeypatch):
    execute, requests, _ = run_pipeline(
        monkeypatch,
        config=AnalysisPipelineConfig(pipeline="claim_anchored", input_tokens=10),
    )
    with pytest.raises(ClaimAnchoredFailure) as error:
        asyncio.run(execute())
    assert error.value.code == "claim_extraction_budget_exceeded"
    assert requests == []


def test_generator_cannot_rewrite_citations_or_claim_metadata(monkeypatch):
    generated = {
        "units": [
            {"text": "Summary", "claim_ids": ["A-01"], "epistemic_status": "reported"}
        ]
    }
    execute, _, _ = run_pipeline(monkeypatch, generated=generated)
    with pytest.raises(ClaimAnchoredFailure) as error:
        asyncio.run(execute())
    assert error.value.code == "claim_generation_invalid"
