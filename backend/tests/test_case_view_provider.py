import json

import httpx
from case_view_test_support import claim, transfer_views

from app.analysis import views
from app.config import settings
from app.llm import request as provider
from app.llm.settings import AnalysisPipelineConfig


async def test_prompt_structured_transport_batches_claims_in_one_non_thinking_request(
    monkeypatch,
):
    posts = []

    def response(request):
        posts.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "content": [{"type": "text", "text": transfer_views().model_dump_json()}],
                "stop_reason": "end_turn",
            },
        )

    monkeypatch.setattr(views, "request_stage", provider.request_stage)
    monkeypatch.setattr(provider, "transport", httpx.MockTransport(response))
    monkeypatch.setattr(settings, "openrouter_cybercase", "test-only")
    config = AnalysisPipelineConfig(providers=("test-provider",))
    result = await views.derive_claim_views(
        [claim(), claim("Company A suspended the account.", claim_id="A-02")], config=config
    )
    assert len(posts) == 1
    payload = posts[0]
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["max_tokens"] == 4096
    assert payload["temperature"] == 0
    assert payload["provider"] == {"order": ["test-provider"], "allow_fallbacks": False}
    assert "output_config" not in payload
    schema = json.loads(
        payload["system"].split("<response_contract>\n")[1].split("\n</response_contract>")[0]
    )
    assert set(schema["required"]) == {"parties", "timeline", "impacts"}
    assert schema["additionalProperties"] is False
    content = json.loads(payload["messages"][0]["content"])
    assert set(content) == {"claims"}
    assert len(content["claims"]) == 2
    assert all(set(item) == {"claim_id", "text"} for item in content["claims"])
    assert result.extraction.status == "completed"


async def test_prompt_schema_failure_yields_empty_views_with_explicit_failure(monkeypatch):
    def response(request):
        return httpx.Response(
            200,
            json={
                "content": [{"type": "text", "text": '{"parties": [], "timeline": []}'}],
                "stop_reason": "end_turn",
            },
        )

    monkeypatch.setattr(views, "request_stage", provider.request_stage)
    monkeypatch.setattr(provider, "transport", httpx.MockTransport(response))
    monkeypatch.setattr(settings, "openrouter_cybercase", "test-only")
    result = await views.derive_claim_views([claim()], config=AnalysisPipelineConfig())
    assert result.extraction.status == "failed"
    assert result.extraction.warning == "case_views_invalid"
    assert result.parties == result.timeline == result.impacts == []
