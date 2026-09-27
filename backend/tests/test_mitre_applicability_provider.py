import asyncio
import json
from uuid import uuid4

import httpx
import pytest

from app.services.analysis import provider
from app.services.analysis.mitre_gate.llm import (
    MITRE_APPLICABILITY_SOURCE_MAX_CHARS,
    MITRE_APPLICABILITY_SYSTEM_PROMPT,
    build_mitre_applicability_prompt,
    evaluate_mitre_applicability,
)
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.analysis.technical_context_contracts import MITRE_APPLICABILITY_GATE_VERSION
from app.services.document_ingestion.contracts import (
    DocumentPage,
    ExtractionMethod,
    IngestedDocument,
)
from app.services.llm.core_llm import CoreLlmTarget
from app.services.sources.case_source_bundle import CaseSourceItem
from app.services.sources.source_service import document_provenance


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
    assert captured["max_tokens"] == 1024 + AnalysisPipelineConfig().thinking_tokens
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


def test_the_gate_reads_a_document_once_and_not_again_page_by_page() -> None:
    pages = [f"หน้า {number} " + "ข้อความในเอกสาร " * 200 for number in range(1, 51)]
    ingested = IngestedDocument(
        filename="scan.pdf",
        media_type="application/pdf",
        extraction_method=ExtractionMethod.DOCUMENT_RECOGNITION,
        pages=[
            DocumentPage(
                page_number=number, text=text, text_method="ocr", verification_status="machine_read"
            )
            for number, text in enumerate(pages, 1)
        ],
        full_text="\n\n".join(pages),
    )
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="document",
        text=ingested.full_text,
        document_id=str(uuid4()),
        filename="scan.pdf",
        provenance=document_provenance(ingested),
    )

    prompt = build_mitre_applicability_prompt([source])

    assert len(prompt) < MITRE_APPLICABILITY_SOURCE_MAX_CHARS + 1_000
    assert pages[-1] not in prompt
    [read] = json.loads(prompt.splitlines()[2])["case_sources"]
    assert read["content"] == ingested.full_text[:MITRE_APPLICABILITY_SOURCE_MAX_CHARS]
    [document] = read["document_sources"]
    assert document["pages"] == [
        {"page_number": number, "text_method": "ocr", "verification_status": "machine_read"}
        for number in (1, 2)
    ], "only the pages the gate can see, and only how they were read"


def test_the_gate_still_hears_how_a_page_without_offsets_was_read() -> None:
    ingested = IngestedDocument(
        filename="scan.pdf",
        media_type="application/pdf",
        extraction_method=ExtractionMethod.DOCUMENT_RECOGNITION,
        pages=[
            DocumentPage(
                page_number=1, text="", text_method="ocr", verification_status="needs_review"
            ),
            DocumentPage(
                page_number=2,
                text="A laptop was taken.",
                text_method="ocr",
                verification_status="machine_read",
            ),
        ],
        full_text="A laptop was taken.",
    )
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="document",
        text=ingested.full_text,
        document_id=str(uuid4()),
        filename="scan.pdf",
        provenance=document_provenance(ingested),
    )

    [read] = json.loads(build_mitre_applicability_prompt([source]).splitlines()[2])["case_sources"]

    [document] = read["document_sources"]
    assert document["pages"] == [
        {"page_number": 1, "text_method": "ocr", "verification_status": "needs_review"},
        {"page_number": 2, "text_method": "ocr", "verification_status": "machine_read"},
    ]
