import asyncio
import json
from uuid import uuid4

import httpx

from app.services.case_analysis.mitre_applicability_contracts import (
    MITRE_APPLICABILITY_GATE_VERSION,
)
from app.services.case_analysis.mitre_applicability_gate import (
    MitreApplicabilityGate,
    evaluate_mitre_applicability,
)
from app.services.case_analysis.mitre_applicability_prompt import (
    MITRE_APPLICABILITY_SYSTEM_PROMPT,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.llm.core_llm import CoreLlmTarget


def target() -> CoreLlmTarget:
    return CoreLlmTarget(
        provider="openrouter",
        model="test-model",
        api_key="test-key",
        base_url="https://provider.test",
        messages_url="https://provider.test/messages",
        headers={"Authorization": "Bearer test-key"},
    )


def test_gate_uses_fixed_prompt_strict_schema_and_deterministic_options(
    monkeypatch,
) -> None:
    captured = {}
    source = RawEvidenceSource(
        message_id=uuid4(),
        content="PowerShell downloaded a remote script.",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        output = {
            "decision": "RETRIEVE",
            "source_message_ids": [str(source.message_id)],
            "trigger_text": ["PowerShell downloaded a remote script"],
        }
        return httpx.Response(200, json={"output_text": json.dumps(output)})

    monkeypatch.setattr(
        "app.services.case_analysis.mitre_applicability_gate.resolve_core_llm_target",
        lambda model: target(),
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(MitreApplicabilityGate(client=client).evaluate([source]))
    asyncio.run(client.aclose())

    assert result.decision == "RETRIEVE"
    assert captured["system"] == MITRE_APPLICABILITY_SYSTEM_PROMPT
    assert captured["temperature"] == 0.0
    assert captured["max_tokens"] == 1024
    assert str(source.message_id) in captured["messages"][0]["content"]
    schema = captured["output_config"]["format"]["schema"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "decision",
        "source_message_ids",
        "trigger_text",
    }
    assert MITRE_APPLICABILITY_GATE_VERSION == "mitre_applicability_v1"


def test_malformed_provider_output_fails_closed(monkeypatch) -> None:
    source = RawEvidenceSource(message_id=uuid4(), content="PowerShell executed")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"output_text": "```json\n{}\n```"})

    monkeypatch.setattr(
        "app.services.case_analysis.mitre_applicability_gate.resolve_core_llm_target",
        lambda model: target(),
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(
        evaluate_mitre_applicability(
            source_run_id=uuid4(),
            evidence_sources=[source],
            gate=MitreApplicabilityGate(client=client),
        )
    )
    asyncio.run(client.aclose())

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_invalid_output"


def test_provider_error_fails_closed(monkeypatch) -> None:
    source = RawEvidenceSource(message_id=uuid4(), content="PowerShell executed")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "unavailable"})

    monkeypatch.setattr(
        "app.services.case_analysis.mitre_applicability_gate.resolve_core_llm_target",
        lambda model: target(),
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(
        evaluate_mitre_applicability(
            source_run_id=uuid4(),
            evidence_sources=[source],
            gate=MitreApplicabilityGate(client=client),
        )
    )
    asyncio.run(client.aclose())

    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_provider_error"
