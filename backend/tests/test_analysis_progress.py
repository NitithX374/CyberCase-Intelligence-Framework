from __future__ import annotations

import asyncio
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from case_mitre_test_support import _fixtures, _gate, _response
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.analysis import routes as analysis
from app.analysis import stream as streaming
from app.analysis.pipeline import AnalysisArtifacts, AnalysisInput, assess_gaps, bind_to_case
from app.analysis.progress import announce, listening
from app.analysis.stream import progress_events
from app.analysis.technical_context.retrieve import run_case_mitre_augmentation
from app.analysis.write import write_trace
from app.auth.guard import get_current_user
from app.chat import routes as chat
from app.chat.schemas import CaseChatResponse
from app.database import get_db
from app.errors import CaseWorkflowError
from app.llm.settings import AnalysisPipelineConfig
from app.main import app
from app.trace.claims import CaseAssessmentTrace
from app.trace.trace import CaseGroundingReport, CaseProviderJudgement, CaseProviderReading


class Done(BaseModel):
    status: str


def events_of(body: str) -> list[tuple[str, object]]:
    events: list[tuple[str, object]] = []
    for block in body.split("\n\n"):
        lines = block.splitlines()
        if not lines:
            continue
        if lines[0].startswith(":"):
            events.append(("comment", lines[0][1:].strip()))
            continue
        name = next(line.removeprefix("event: ") for line in lines if line.startswith("event: "))
        data = next(line.removeprefix("data: ") for line in lines if line.startswith("data: "))
        events.append((name, json.loads(data)))
    return events


def streamed(work, heartbeat: float = 15.0) -> list[tuple[str, object]]:
    async def collect() -> str:
        return "".join([chunk async for chunk in progress_events(work, heartbeat)])

    return events_of(asyncio.run(collect()))


def steps_heard(exercise) -> list[str]:
    heard: list[str] = []

    async def listened():
        with listening(heard.append):
            await exercise()

    asyncio.run(listened())
    return heard


def test_announcing_a_step_with_no_one_listening_does_nothing():
    announce("read")


def test_the_steps_arrive_in_order_before_the_result():
    async def work():
        announce("assess")
        announce("read")
        return Done(status="completed")

    events = streamed(work)

    assert [name for name, _ in events] == ["step", "step", "result"]
    assert [data["step"] for name, data in events if name == "step"] == ["assess", "read"]
    assert events[-1] == ("result", {"status": "completed"})


def test_a_quiet_stretch_is_filled_with_a_heartbeat():
    async def work():
        await asyncio.sleep(0.05)
        return Done(status="completed")

    events = streamed(work, heartbeat=0.01)

    assert ("comment", "heartbeat") in events
    assert events[-1] == ("result", {"status": "completed"})


def test_a_refusal_arrives_as_an_error_with_its_status_and_code():
    async def work():
        announce("assess")
        raise CaseWorkflowError("case_sources_missing", "Add a source first", 422)

    events = streamed(work)

    assert events[-1] == (
        "error",
        {
            "status": 422,
            "detail": {"code": "case_sources_missing", "message": "Add a source first"},
        },
    )


def test_an_unexpected_failure_arrives_as_a_server_error():
    async def work():
        raise RuntimeError("boom")

    assert streamed(work) == [
        (
            "error",
            {"status": 500, "detail": {"code": "internal_error", "message": "The request failed"}},
        )
    ]


def test_the_work_carries_on_when_the_reader_goes_away():
    async def exercise():
        release = asyncio.Event()
        finished = asyncio.Event()

        async def work():
            announce("read")
            await release.wait()
            finished.set()
            return Done(status="completed")

        stream = progress_events(work)
        first = await anext(stream)
        await stream.aclose()
        release.set()
        await asyncio.wait_for(finished.wait(), 1)
        return first

    assert asyncio.run(exercise()).startswith("event: step")


def failures_logged(caplog) -> list[logging.LogRecord]:
    return [record for record in caplog.records if record.name == streaming.logger.name]


def failing_after_the_reader_left(failure: Exception):
    async def exercise():
        release = asyncio.Event()

        async def work():
            announce("read")
            await release.wait()
            raise failure

        stream = progress_events(work)
        await anext(stream)
        await stream.aclose()
        release.set()
        await asyncio.gather(*list(streaming._unfinished), return_exceptions=True)

    asyncio.run(exercise())


def test_a_refusal_is_logged_with_its_code_after_the_reader_has_gone(caplog):
    refusal = CaseWorkflowError(
        "analysis_provider_down", "The analysis provider is unavailable", 502
    )

    with caplog.at_level(logging.WARNING):
        failing_after_the_reader_left(refusal)

    [record] = failures_logged(caplog)
    assert record.levelno == logging.WARNING
    assert "analysis_provider_down" in record.getMessage()
    assert "502" in record.getMessage()
    assert "The analysis provider is unavailable" in record.getMessage()


def test_an_unexpected_failure_is_logged_with_its_traceback_after_the_reader_has_gone(caplog):
    with caplog.at_level(logging.WARNING):
        failing_after_the_reader_left(RuntimeError("boom"))

    [record] = failures_logged(caplog)
    assert record.levelno == logging.ERROR
    assert record.exc_info is not None
    assert record.exc_info[0] is RuntimeError


def test_a_failure_the_reader_sees_is_logged_once(caplog):
    async def refused():
        raise CaseWorkflowError("case_sources_missing", "Add a source first", 422)

    async def crashed():
        raise RuntimeError("boom")

    with caplog.at_level(logging.WARNING):
        streamed(refused)
        streamed(crashed)

    assert [record.levelno for record in failures_logged(caplog)] == [
        logging.WARNING,
        logging.ERROR,
    ]


def test_a_request_that_finishes_logs_nothing(caplog):
    async def work():
        return Done(status="completed")

    with caplog.at_level(logging.INFO):
        streamed(work)

    assert failures_logged(caplog) == []


def test_the_preflight_and_the_binding_announce_themselves():
    _, trace, bundle, _, _ = _fixtures()
    data = AnalysisInput(sources=bundle)

    async def assessed(**_kwargs):
        return CaseAssessmentTrace(gaps=[])

    async def exercise():
        await assess_gaps(data, request=assessed)
        await bind_to_case(data, AnalysisArtifacts(trace=trace))

    assert steps_heard(exercise) == ["assess", "bind"]


def test_reading_source_binding_and_judgement_announce_in_turn():
    bundle = _fixtures()[2]
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[],
    )
    judgement = CaseProviderJudgement(
        version="case_analysis_trace_v1", summary="Nothing yet.", gaps=[], mitre_associations=[]
    )

    async def request_stage(**kwargs):
        return reading if kwargs["stage"] == "case_reading" else judgement

    async def exercise():
        with patch("app.analysis.write.request_stage", new=request_stage):
            await write_trace(sources=bundle, language="english", config=AnalysisPipelineConfig())

    assert steps_heard(exercise) == ["read", "bind", "views", "judge"]


def test_the_checks_after_a_checked_reading_announce_nothing():
    _, trace, bundle, _, _ = _fixtures()
    checked = trace.model_copy(update={"grounding": CaseGroundingReport()})

    async def exercise():
        await bind_to_case(AnalysisInput(sources=bundle), AnalysisArtifacts(trace=checked))

    assert steps_heard(exercise) == []


@pytest.mark.parametrize(
    ("decision", "reused", "expected"),
    [
        ("RETRIEVE", False, ["gate", "retrieve"]),
        ("RETRIEVE", True, ["gate"]),
        ("SKIP", False, ["gate"]),
    ],
)
def test_retrieval_is_announced_only_when_the_rag_service_is_asked(decision, reused, expected):
    _, _, bundle, applicability, context = _fixtures()
    skip = {"decision": "SKIP", "source_message_ids": [], "trigger_text": []}

    async def rag(_query):
        return _response(context)

    async def exercise():
        await run_case_mitre_augmentation(
            source_bundle=bundle,
            applicability_gate=_gate(applicability if decision == "RETRIEVE" else skip),
            rag_request=rag,
            reused_context=context if reused else None,
        )

    assert steps_heard(exercise) == expected


def _fastapi_app() -> FastAPI:
    application = app
    while not isinstance(application, FastAPI):
        application = application.app
    return application


@pytest.fixture
def client():
    application = _fastapi_app()
    application.dependency_overrides[get_db] = lambda: AsyncMock()
    application.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())
    yield TestClient(app)
    application.dependency_overrides.clear()


def test_an_analysis_asked_for_as_a_stream_sends_its_steps_then_the_plain_result(
    client, monkeypatch
):
    async def run(**_kwargs):
        announce("assess")
        return SimpleNamespace(needs_followup=True)

    monkeypatch.setattr(analysis, "run_case_analysis", run)
    url = f"/api/v1/cases/{uuid4()}/analysis"

    streamed_response = client.post(url, headers={"Accept": "text/event-stream"})
    plain = client.post(url)

    assert streamed_response.headers["content-type"].startswith("text/event-stream")
    events = events_of(streamed_response.text)
    assert [name for name, _ in events] == ["step", "result"]
    assert events[-1] == ("result", plain.json())


def test_a_chat_answer_asked_for_as_a_stream_carries_the_analysis_steps(client, monkeypatch):
    async def send(**_kwargs):
        announce("read")
        announce("judge")
        return CaseChatResponse(messages=[])

    monkeypatch.setattr(chat, "send_case_message", send)
    url = f"/api/v1/cases/{uuid4()}/chat/messages"
    body = {"content": "The finance share", "client_request_id": "key-1"}

    streamed_response = client.post(url, json=body, headers={"Accept": "text/event-stream"})
    plain = client.post(url, json=body)

    events = events_of(streamed_response.text)
    assert [data["step"] for name, data in events if name == "step"] == ["read", "judge"]
    assert events[-1] == ("result", plain.json())


def test_a_refused_analysis_arrives_in_the_stream_with_what_a_plain_request_gets(
    client, monkeypatch
):
    async def refuse(**_kwargs):
        raise CaseWorkflowError("case_sources_missing", "Add a source first", 422)

    monkeypatch.setattr(analysis, "run_case_analysis", refuse)
    url = f"/api/v1/cases/{uuid4()}/analysis"

    streamed_response = client.post(url, headers={"Accept": "text/event-stream"})
    plain = client.post(url)

    assert plain.status_code == 422
    assert events_of(streamed_response.text)[-1] == ("error", {"status": 422, **plain.json()})
