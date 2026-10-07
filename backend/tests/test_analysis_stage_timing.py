import logging

import httpx
import pytest
from pydantic import BaseModel
from test_analysis_provider_transport import thought_and_answered

from app.errors import CaseAnalysisFailure
from app.llm import request as provider
from app.llm.openrouter import CoreLlmTarget
from app.llm.settings import AnalysisPipelineConfig


class Result(BaseModel):
    ok: bool


@pytest.fixture
def local_transport(monkeypatch):
    monkeypatch.setattr(provider, "token_count", lambda payload: 123)
    monkeypatch.setattr(
        provider,
        "resolve_core_llm_target",
        lambda model: CoreLlmTarget(
            model=model,
            messages_url="https://provider.test/messages",
            headers={"Authorization": "Bearer secret-test-key"},
        ),
    )


async def test_normal_stage_logs_elapsed_time_without_a_receipt_collector(
    monkeypatch, caplog, local_transport
):
    caplog.set_level(logging.INFO, logger="app.case_analysis")
    monkeypatch.setattr(
        provider, "transport", httpx.MockTransport(lambda request: thought_and_answered())
    )
    result = await provider.request_stage(
        config=AnalysisPipelineConfig(model="test/model"),
        stage="probe",
        system="sensitive-system-text",
        content="sensitive-case-text",
        schema=Result,
    )
    assert result.ok is True
    final = [record.message for record in caplog.records if "finished status=" in record.message]
    assert len(final) == 1
    assert "status=completed elapsed_ms=" in final[0]
    assert "estimated_input_tokens=123 output_tokens=90 thinking_tokens=70" in final[0]
    assert not any(
        text in caplog.text
        for text in ("sensitive-system-text", "sensitive-case-text", "secret-test-key")
    )


async def test_failed_stage_logs_failure_without_changing_timeout_semantics(
    monkeypatch, caplog, local_transport
):
    caplog.set_level(logging.INFO, logger="app.case_analysis")

    def timeout(request):
        raise httpx.ReadTimeout("network idle", request=request)

    monkeypatch.setattr(provider, "transport", httpx.MockTransport(timeout))
    with pytest.raises(CaseAnalysisFailure) as caught:
        await provider.request_stage(
            config=AnalysisPipelineConfig(model="test/model"),
            stage="probe",
            system="system",
            content="case",
            schema=Result,
        )
    assert caught.value.code == "probe_timeout"
    assert "finished status=failed elapsed_ms=" in caplog.text
    assert "output_tokens=None thinking_tokens=None" in caplog.text
