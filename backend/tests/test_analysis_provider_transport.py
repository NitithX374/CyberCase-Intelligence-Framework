import json

import httpx
import pytest
from pydantic import BaseModel

from app.services.analysis import provider
from app.services.analysis.contracts import CaseAnalysisFailure
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.llm.core_llm import CoreLlmTarget


class Probe(BaseModel):
    ok: bool


def answered() -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [{"type": "text", "text": json.dumps({"ok": True})}],
            "stop_reason": "end_turn",
        },
    )


@pytest.fixture(autouse=True)
def quick(monkeypatch) -> None:
    monkeypatch.setattr(provider, "TRANSPORT_RETRY_DELAY_SECONDS", 0)
    monkeypatch.setattr(provider, "token_count", lambda payload: 1)
    monkeypatch.setattr(
        provider,
        "resolve_core_llm_target",
        lambda model: CoreLlmTarget(
            model=model,
            messages_url="https://provider.test/v1/messages",
            headers={"Authorization": "Bearer test-key"},
        ),
    )


async def run_stage(monkeypatch, handler, calls: list[dict[str, object]], **options) -> Probe:
    monkeypatch.setattr(provider, "transport", httpx.MockTransport(handler))
    return await provider.request_stage(
        config=AnalysisPipelineConfig(model="test/model"),
        stage="probe",
        system="system",
        content={"case": "text"},
        schema=Probe,
        calls=calls,
        **options,
    )


async def test_a_dropped_connection_is_tried_once_more(monkeypatch) -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        if len(attempts) == 1:
            raise httpx.ConnectError("connection reset", request=request)
        return answered()

    calls: list[dict[str, object]] = []
    result = await run_stage(monkeypatch, handler, calls)

    assert result == Probe(ok=True)
    assert len(attempts) == 2
    assert calls[0]["status"] == "completed"


async def test_a_second_transport_error_fails_the_stage(monkeypatch, caplog) -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        raise httpx.RemoteProtocolError("Server disconnected", request=request)

    calls: list[dict[str, object]] = []
    with pytest.raises(CaseAnalysisFailure) as failure:
        await run_stage(monkeypatch, handler, calls)

    assert failure.value.code == "probe_transport"
    assert len(attempts) == provider.TRANSPORT_ATTEMPTS
    assert calls[0]["status"] == "failed"
    assert "RemoteProtocolError" in caplog.text


async def test_a_timeout_is_not_retried(monkeypatch) -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(CaseAnalysisFailure) as failure:
        await run_stage(monkeypatch, handler, [])

    assert failure.value.code == "probe_timeout"
    assert len(attempts) == 1


async def test_the_stage_asks_for_what_its_config_says(monkeypatch) -> None:
    sent: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return answered()

    await run_stage(monkeypatch, handler, [])
    await run_stage(monkeypatch, handler, [], temperature=0.0)

    assert sent[0]["model"] == "test/model"
    assert sent[0]["max_tokens"] == AnalysisPipelineConfig().output_tokens
    assert "temperature" not in sent[0]
    assert sent[1]["temperature"] == 0.0
    assert json.loads(sent[0]["messages"][0]["content"]) == {"case": "text"}
