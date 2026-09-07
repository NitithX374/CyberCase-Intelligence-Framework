import hashlib
import json
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageCreate
from app.services.case_analysis.case_analysis_prompt_builder import (
    build_case_analysis_prompt,
)
from app.services.case_analysis.mitre_applicability_prompt import (
    build_mitre_applicability_prompt,
)
from app.services.chat.chat_run_creation import request_fingerprint as _fingerprint
from app.services.chat.raw_evidence import build_raw_evidence_snapshot


def document_source() -> dict[str, object]:
    return {
        "document_id": "DOC-OCR-1",
        "filename": "statement.pdf",
        "extraction_method": "document_recognition",
        "page_count": 2,
        "verification_status": "needs_review",
        "confidence_status": "not_reported",
        "minimum_confidence": None,
        "warnings": ["OCR provider did not report confidence."],
    }


def test_message_contract_accepts_one_document_source_and_rejects_two() -> None:
    request = ChatMessageCreate(
        content="Merged OCR narrative",
        idempotency_key="handoff-1",
        document_sources=[document_source()],
    )
    assert request.document_sources[0].document_id == "DOC-OCR-1"
    with pytest.raises(ValidationError):
        ChatMessageCreate(
            content="Merged OCR narrative",
            idempotency_key="handoff-2",
            document_sources=[document_source(), document_source()],
        )


def test_document_source_participates_in_idempotency_without_changing_plain_messages() -> (
    None
):
    plain = ChatMessageCreate(content="Narrative", idempotency_key="plain")
    legacy_source = "Narrative\x00"
    assert _fingerprint(plain) == hashlib.sha256(legacy_source.encode()).hexdigest()
    with_document = ChatMessageCreate(
        content="Narrative",
        idempotency_key="with-document",
        document_sources=[document_source()],
    )
    assert _fingerprint(with_document) != _fingerprint(plain)


def test_raw_evidence_keeps_text_authoritative_and_quality_metadata_separate() -> None:
    message_id = uuid4()
    snapshot = build_raw_evidence_snapshot(
        [
            ChatMessage(
                id=message_id,
                thread_id=uuid4(),
                ordinal=1,
                role="user",
                content="Merged OCR narrative",
                metadata_json={
                    "evidence_kind": "initial_case_narrative",
                    "document_sources": [document_source()],
                },
            )
        ]
    )
    assert snapshot.text == "[INITIAL CASE NARRATIVE]\nMerged OCR narrative"
    assert "statement.pdf" not in snapshot.text
    assert snapshot.document_source_context == (
        {
            "source_message_id": str(message_id),
            "documents": [document_source()],
        },
    )


def test_analysis_and_mitre_prompts_receive_quality_as_non_evidence_context() -> None:
    message_id = uuid4()
    message = ChatMessage(
        id=message_id,
        thread_id=uuid4(),
        ordinal=1,
        role="user",
        content="PowerShe11 was observed.",
        metadata_json={
            "evidence_kind": "initial_case_narrative",
            "document_sources": [document_source()],
        },
    )
    snapshot = build_raw_evidence_snapshot([message])
    analysis_prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence=snapshot.text,
        analysis_context={
            "source_message_ids": [str(message_id)],
            "document_source_context": list(snapshot.document_source_context),
        },
        question=None,
        response_language="english",
    )
    analysis_payload = json.loads(
        analysis_prompt.split("<case_context_json>\n", 1)[1].split(
            "\n</case_context_json>", 1
        )[0]
    )
    assert analysis_payload["raw_user_case_evidence"] == snapshot.text
    assert analysis_payload["optional_external_context"]["document_source_context"]
    mitre_prompt = build_mitre_applicability_prompt(snapshot.sources)
    assert '"confidence_status":"not_reported"' in mitre_prompt
    assert '"document_sources"' in mitre_prompt


def test_internal_source_text_map_is_not_serialized_into_the_provider_context() -> None:
    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence="[INITIAL CASE NARRATIVE]\nVisible evidence",
        analysis_context={
            "source_message_ids": ["message-1"],
            "_source_text_by_message_id": {"message-1": "internal duplicate"},
        },
        question=None,
        response_language="english",
    )
    payload = json.loads(
        prompt.split("<case_context_json>\n", 1)[1].split("\n</case_context_json>", 1)[
            0
        ]
    )
    assert payload["optional_external_context"] is None
