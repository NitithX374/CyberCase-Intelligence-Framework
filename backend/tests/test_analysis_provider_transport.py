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


def target() -> CoreLlmTarget:
    return CoreLlmTarget(
        model="test/model",
        messages_url="https://provider.test/v1/messages",
        headers={"Authorization": "Bearer test-key"},
    )


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


async def run_stage(handler, calls: list[dict[str, object]]) -> Probe:
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        return await provider.request_stage(
            client=client,
            target=target(),
            config=AnalysisPipelineConfig(model="test/model"),
            stage="probe",
            system="system",
            content={"case": "text"},
            schema=Probe,
            calls=calls,
        )


async def test_a_dropped_connection_is_tried_once_more() -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        if len(attempts) == 1:
            raise httpx.ConnectError("connection reset", request=request)
        return answered()

    calls: list[dict[str, object]] = []
    result = await run_stage(handler, calls)

    assert result == Probe(ok=True)
    assert len(attempts) == 2
    assert calls[0]["status"] == "completed"


async def test_a_second_transport_error_fails_the_stage(caplog) -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        raise httpx.RemoteProtocolError("Server disconnected", request=request)

    calls: list[dict[str, object]] = []
    with pytest.raises(CaseAnalysisFailure) as failure:
        await run_stage(handler, calls)

    assert failure.value.code == "probe_transport"
    assert len(attempts) == provider.TRANSPORT_ATTEMPTS
    assert calls[0]["status"] == "failed"
    assert "RemoteProtocolError" in caplog.text


async def test_a_timeout_is_not_retried() -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(CaseAnalysisFailure) as failure:
        await run_stage(handler, [])

    assert failure.value.code == "probe_timeout"
    assert len(attempts) == 1
