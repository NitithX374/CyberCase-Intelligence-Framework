import asyncio
import json
from uuid import uuid4

import httpx
import pytest

from app.services.analysis import provider
from app.services.analysis.mitre_gate.llm import (
    MITRE_APPLICABILITY_GATE_VERSION,
    MITRE_APPLICABILITY_SOURCE_MAX_CHARS,
    MITRE_APPLICABILITY_SYSTEM_PROMPT,
    build_mitre_applicability_prompt,
    evaluate_mitre_applicability,
)
from app.services.llm.core_llm import CoreLlmTarget
from app.services.sources.case_source_bundle import CaseSourceItem


@pytest.fixture
def resolved_models(monkeypatch) -> list[str]:
    models: list[str] = []

    def resolve_target(model):
        models.append(model)
        return CoreLlmTarget(
            model=model,
            messages_url="https://provider.test/messages",
            headers={"Authorization": "Bearer test-key"},
        )

    monkeypatch.setattr(provider, "resolve_core_llm_target", resolve_target)
    monkeypatch.setattr(provider, "TRANSPORT_RETRY_DELAY_SECONDS", 0)
    return models


def gate_answering(monkeypatch, handler, *sources: CaseSourceItem):
    monkeypatch.setattr(provider, "transport", httpx.MockTransport(handler))
    return asyncio.run(evaluate_mitre_applicability(case_sources=list(sources)))


def narrative(text: str) -> CaseSourceItem:
    return CaseSourceItem(source_id=str(uuid4()), source_kind="narrative", text=text)


def test_gate_uses_fixed_prompt_strict_schema_and_deterministic_options(
    monkeypatch, resolved_models
) -> None:
    captured = {}
    source = narrative("PowerShell downloaded a remote script.")

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        output = {
            "decision": "RETRIEVE",
            "source_message_ids": [source.source_id],
            "trigger_text": ["PowerShell downloaded a remote script"],
        }
        return httpx.Response(200, json={"output_text": json.dumps(output)})

    monkeypatch.setattr(
        "app.services.analysis.settings.settings.case_analysis_model",
        "openrouter/vendor/custom-model",
    )
    result = gate_answering(monkeypatch, handler, source)

    assert result.decision == "RETRIEVE"
    assert resolved_models == ["vendor/custom-model"]
    assert captured["model"] == "vendor/custom-model"
    assert captured["system"] == MITRE_APPLICABILITY_SYSTEM_PROMPT
    assert captured["temperature"] == 0.0
    assert captured["max_tokens"] == 1024
    assert captured["messages"][0]["content"] == build_mitre_applicability_prompt([source])
    schema = captured["output_config"]["format"]["schema"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "decision",
        "source_message_ids",
        "trigger_text",
    }
    assert MITRE_APPLICABILITY_GATE_VERSION == "mitre_applicability_v1"


def test_malformed_provider_output_fails_closed(monkeypatch, resolved_models) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"output_text": "```json\n{}\n```"})

    result = gate_answering(monkeypatch, handler, narrative("PowerShell executed"))

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_invalid_output"


@pytest.mark.parametrize("status", [401, 429, 500, 503])
def test_provider_error_fails_closed(monkeypatch, resolved_models, status) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "unavailable"})

    result = gate_answering(monkeypatch, handler, narrative("PowerShell executed"))

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_provider_error"


def test_a_connection_that_stays_down_fails_closed_as_a_provider_error(
    monkeypatch, resolved_models
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection reset", request=request)

    result = gate_answering(monkeypatch, handler, narrative("PowerShell executed"))

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_provider_error"


@pytest.mark.parametrize(
    "body",
    [
        {"stop_reason": "max_tokens", "output_text": "{"},
        {"content": 42},
    ],
)
def test_an_incomplete_answer_fails_closed_as_invalid_output(
    monkeypatch, resolved_models, body
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    result = gate_answering(monkeypatch, handler, narrative("PowerShell executed"))

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_invalid_output"


def test_a_dropped_connection_is_retried_like_every_other_stage(
    monkeypatch, resolved_models
) -> None:
    attempts = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        if len(attempts) == 1:
            raise httpx.ConnectError("connection reset", request=request)
        output = {"decision": "SKIP", "source_message_ids": [], "trigger_text": []}
        return httpx.Response(200, json={"output_text": json.dumps(output)})

    result = gate_answering(monkeypatch, handler, narrative("A laptop was taken."))

    assert len(attempts) == 2
    assert result.decision == "SKIP"
    assert result.failure_code is None


def test_a_timeout_fails_closed_with_the_stage_code(monkeypatch, resolved_models) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    result = gate_answering(monkeypatch, handler, narrative("PowerShell executed"))

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_timeout"


def test_the_record_says_when_the_gate_read_only_part_of_a_source(
    monkeypatch, resolved_models
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        output = {"decision": "SKIP", "source_message_ids": [], "trigger_text": []}
        return httpx.Response(200, json={"output_text": json.dumps(output)})

    def evaluated(text: str):
        return gate_answering(monkeypatch, handler, narrative(text))

    assert evaluated("A laptop was taken.").input_truncated is False
    long_source = "A laptop was taken. " + "x" * MITRE_APPLICABILITY_SOURCE_MAX_CHARS
    assert evaluated(long_source).input_truncated is True
