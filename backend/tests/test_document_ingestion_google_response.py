import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services.document_ingestion.contracts import OCRWord
from app.services.document_ingestion.errors import (
    RecognitionProviderError,
    RecognitionResponseError,
)
from app.services.document_ingestion.recognition.google_vision_response import (
    minimum_word_confidence,
    normalize_response,
)

FIXTURE = Path(__file__).parent / "fixtures/google_vision_synthetic.json"


def sample():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def provider_words(payload):
    return payload["responses"][0]["fullTextAnnotation"]["pages"][0]["blocks"][0][
        "paragraphs"
    ][0]["words"]


def test_synthetic_receipt_matches_text_thai_words_reading_order_boxes_and_minimum():
    fixture = sample()
    text, words = normalize_response(fixture["provider_response"])
    assert {
        "text": text,
        "recognition_confidence": minimum_word_confidence(words),
        "words": [word.model_dump() for word in words],
    } == fixture["normalized"]
    assert isinstance(words[0].confidence, float)
    assert words[3].confidence is None
    assert words[0].bbox is None


@pytest.mark.parametrize("confidence", [0, 1, 0.1234, None])
def test_confidence_preserves_real_zero_and_missing_values(confidence):
    payload = sample()["provider_response"]
    provider_words(payload)[0]["confidence"] = confidence
    _, words = normalize_response(payload)
    assert words[0].confidence == confidence
    if confidence is not None:
        assert isinstance(words[0].confidence, float)


@pytest.mark.parametrize(
    "confidence", [-0.1, 1.01, float("nan"), float("inf"), True, "0.9"]
)
def test_invalid_confidence_fails_without_clamping_or_fabricating(confidence):
    payload = sample()["provider_response"]
    provider_words(payload)[0]["confidence"] = confidence
    with pytest.raises(RecognitionResponseError):
        normalize_response(payload)
    with pytest.raises(ValidationError):
        OCRWord(text="test", confidence=confidence)


@pytest.mark.parametrize(
    "polygon", [None, {}, {"vertices": []}, {"vertices": [{"x": 4}]}]
)
def test_missing_polygon_or_coordinates_produce_no_box(polygon):
    payload = sample()["provider_response"]
    provider_words(payload)[0]["boundingBox"] = polygon
    _, words = normalize_response(payload)
    assert words[0].bbox is None


def test_incomplete_four_vertex_polygon_does_not_invent_coordinates():
    payload = sample()["provider_response"]
    provider_words(payload)[2]["boundingBox"]["vertices"][0].pop("x")
    assert normalize_response(payload)[1][2].bbox is None


def test_multiple_paragraphs_blocks_pages_keep_provider_order_and_page_formatting():
    payload = sample()["provider_response"]
    annotation = payload["responses"][0]["fullTextAnnotation"]
    annotation["pages"] *= 2
    annotation["pages"][0]["blocks"] *= 2
    annotation["pages"][0]["blocks"][0]["paragraphs"] *= 2
    text, words = normalize_response(payload)
    assert text == annotation["text"]
    assert [word.text for word in words] == ["นาย", "ก.", "52,000", "บาท"] * 8


@pytest.mark.parametrize("annotation", [None, {}, {"text": ""}, {"text": " \n "}])
def test_empty_annotation_is_safe_response_error(annotation):
    with pytest.raises(RecognitionResponseError):
        normalize_response({"responses": [{"fullTextAnnotation": annotation}]})


@pytest.mark.parametrize(
    "payload", [{}, None, {"responses": []}, {"responses": [{}, {}]}]
)
def test_malformed_envelope_is_safe_response_error(payload):
    with pytest.raises(RecognitionResponseError):
        normalize_response(payload)


def test_provider_error_is_sanitized():
    with pytest.raises(RecognitionProviderError) as raised:
        normalize_response(
            {"responses": [{"error": {"code": 7, "message": "private"}}]}
        )
    assert "private" not in str(raised.value)


def test_aggregate_uses_only_reported_words_and_never_page_confidence():
    payload = sample()["provider_response"]
    payload["responses"][0]["fullTextAnnotation"]["pages"][0]["confidence"] = 0.99
    for word in provider_words(payload):
        word.pop("confidence", None)
    _, words = normalize_response(payload)
    assert minimum_word_confidence(words) is None
    assert minimum_word_confidence([]) is None
    assert minimum_word_confidence([OCRWord(text="zero", confidence=0), *words]) == 0
