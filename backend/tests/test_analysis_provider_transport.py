import json
import logging

import httpx
import pytest
from pydantic import BaseModel

from app.errors import CaseAnalysisFailure
from app.llm import request as provider
from app.llm.openrouter import CoreLlmTarget
from app.llm.settings import AnalysisPipelineConfig


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


def thought_and_answered() -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [
                {"type": "thinking", "thinking": "weighing the case"},
                {"type": "text", "text": json.dumps({"ok": True})},
            ],
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 120,
                "output_tokens": 90,
                "output_tokens_details": {"thinking_tokens": 70},
            },
        },
    )


def lost_in_whitespace() -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [{"type": "text", "text": '{"ok": true' + " \n" * 2_000}],
            "stop_reason": "max_tokens",
            "usage": {"input_tokens": 120, "output_tokens": 40_800},
        },
    )


def cut_off_while_thinking(stop_reason: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [{"type": "thinking", "thinking": "still weighing"}],
            "stop_reason": stop_reason,
            "usage": {
                "input_tokens": 120,
                "output_tokens": 300,
                "output_tokens_details": {"thinking_tokens": 300},
            },
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


async def run_stage(
    monkeypatch,
    handler,
    calls: list[dict[str, object]],
    config: AnalysisPipelineConfig | None = None,
    **options,
) -> Probe:
    monkeypatch.setattr(provider, "transport", httpx.MockTransport(handler))
    return await provider.request_stage(
        config=config or AnalysisPipelineConfig(model="test/model"),
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


async def test_an_answer_lost_in_whitespace_is_asked_once_more(monkeypatch) -> None:
    replies = [lost_in_whitespace(), answered()]
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        return replies[len(attempts) - 1]

    calls: list[dict[str, object]] = []
    result = await run_stage(monkeypatch, handler, calls)

    assert result == Probe(ok=True)
    assert len(attempts) == 2
    assert calls[0]["status"] == "completed"
    assert calls[0]["runaway_output_tokens"] == 40_800


async def test_a_second_runaway_fails_the_stage(monkeypatch) -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        return lost_in_whitespace()

    with pytest.raises(CaseAnalysisFailure) as failure:
        await run_stage(monkeypatch, handler, [])

    assert failure.value.code == "probe_incomplete"
    assert len(attempts) == provider.RUNAWAY_ATTEMPTS


async def test_the_stage_asks_for_what_its_config_says(monkeypatch) -> None:
    sent: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return answered()

    config = AnalysisPipelineConfig(model="test/model", thinking_tokens=4_096)
    await run_stage(monkeypatch, handler, [], config=config)
    await run_stage(monkeypatch, handler, [], temperature=0.0)
    await run_stage(
        monkeypatch,
        handler,
        [],
        config=AnalysisPipelineConfig(model="test/model", thinking_tokens=0),
    )

    assert sent[0]["model"] == "test/model"
    assert sent[0]["max_tokens"] == config.output_tokens + config.thinking_tokens
    assert sent[0]["thinking"] == {"type": "enabled", "budget_tokens": config.thinking_tokens}
    assert "temperature" not in sent[0]
    assert sent[1]["temperature"] == 0.0
    assert sent[2]["thinking"] == {"type": "disabled"}
    assert sent[2]["max_tokens"] == config.output_tokens
    assert json.loads(sent[0]["messages"][0]["content"]) == {"case": "text"}


async def test_pinned_providers_are_the_only_ones_asked(monkeypatch) -> None:
    sent: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return answered()

    pinned = ("parasail/fp8", "coreweave/fp8")
    await run_stage(
        monkeypatch,
        handler,
        [],
        config=AnalysisPipelineConfig(model="test/model", providers=pinned),
    )
    await run_stage(
        monkeypatch, handler, [], config=AnalysisPipelineConfig(model="test/model", providers=())
    )

    assert sent[0]["provider"] == {"order": list(pinned), "allow_fallbacks": False}
    assert "provider" not in sent[1]


async def test_the_receipt_records_what_the_provider_counted(monkeypatch) -> None:
    calls: list[dict[str, object]] = []
    result = await run_stage(monkeypatch, lambda request: thought_and_answered(), calls)

    assert result == Probe(ok=True)
    assert calls[0]["input_tokens"] == 120
    assert calls[0]["output_tokens"] == 90
    assert calls[0]["thinking_tokens"] == 70


async def test_a_count_the_provider_leaves_out_is_none(monkeypatch) -> None:
    calls: list[dict[str, object]] = []
    await run_stage(monkeypatch, lambda request: answered(), calls)

    assert calls[0]["input_tokens"] is None
    assert calls[0]["thinking_tokens"] is None


@pytest.mark.parametrize(
    ("stop_reason", "status_code"),
    [("max_tokens", 502), ("refusal", 409)],
)
async def test_a_reply_that_stops_early_is_named_after_its_stage(
    monkeypatch, caplog, stop_reason, status_code
) -> None:
    caplog.set_level(logging.INFO, logger="app.case_analysis")
    calls: list[dict[str, object]] = []
    with pytest.raises(CaseAnalysisFailure) as failure:
        await run_stage(monkeypatch, lambda request: cut_off_while_thinking(stop_reason), calls)

    assert failure.value.code == "probe_incomplete"
    assert failure.value.status_code == status_code
    assert calls[0]["status"] == "failed"
    assert calls[0]["thinking_tokens"] == 300
    assert "'thinking_tokens': 300" in caplog.text
