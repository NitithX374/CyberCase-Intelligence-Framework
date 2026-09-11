import hashlib

import pytest
from app.services.case_analysis.claim_anchored import bind_claims
from app.services.case_analysis.claim_anchored.contracts import (
    ClaimAnchoredFailure,
    ExtractedClaims,
    build_source_registry,
)


def source_context(text="พยานไม่เห็นผู้ต้องหา", source_id="message-1"):
    return {
        "source_message_ids": [source_id],
        "_source_text_by_message_id": {source_id: text},
    }


def extraction(quote="พยานไม่เห็นผู้ต้องหา", source_id="message-1", **updates):
    claim = {
        "text": quote,
        "claim_type": "reported",
        "epistemic_status": "reported",
        "evidence": [
            {"source_message_id": source_id, "exact_quote": quote, "role": "supporting"}
        ],
        "reasoning_summary": None,
    }
    claim.update(updates)
    return ExtractedClaims.model_validate({"claims": [claim]})


def bind(text, quote, documents=None):
    return bind_claims(
        extraction(quote), build_source_registry(source_context(text)), documents or []
    )


def page(text, start, end, number):
    return {
        "page_number": number,
        "start_offset": start,
        "end_offset": end,
        "text_sha256": hashlib.sha256(text[start:end].encode()).hexdigest(),
    }


def documents(spans):
    return [
        {
            "source_message_id": "message-1",
            "documents": [
                {
                    "document_id": "doc-1",
                    "filename": "case.pdf",
                    "page_spans": spans,
                }
            ],
        }
    ]


def test_thai_offsets_preserve_exact_original_text():
    text = "ข้อความนำ😀 พยานไม่เห็นผู้ต้องหา ข้อความท้าย"
    bound = bind(text, "พยานไม่เห็นผู้ต้องหา")[0]
    span = bound.spans[0]
    assert text[span.start_offset : span.end_offset] == span.citation.exact_quote
    assert span.start_offset == text.index("พยาน")
    assert span.source_text_sha256 == hashlib.sha256(text.encode()).hexdigest()
    assert span.locator_status == "narrative_only"


@pytest.mark.parametrize(
    "text,quote,code",
    [
        ("transfer 5000", "transfer 500", ""),
        ("transfer 5000", "transfer 6000", "claim_quote_absent"),
        ("same same", "same", "claim_quote_ambiguous"),
        ("พยานไม่เห็น", "พยานเห็น", "claim_quote_absent"),
    ],
)
def test_literal_binding_does_not_claim_semantic_support(text, quote, code):
    if code:
        with pytest.raises(ClaimAnchoredFailure, match=".") as error:
            bind(text, quote)
        assert error.value.code == code
    else:
        assert bind(text, quote)[0].spans[0].citation.exact_quote == quote


def test_repeated_quote_on_one_page_remains_ambiguous():
    text = "same same"
    with pytest.raises(ClaimAnchoredFailure) as error:
        bind(text, "same", documents([page(text, 0, len(text), 1)]))
    assert error.value.code == "claim_quote_ambiguous"


def test_unknown_source_and_same_source_opposing_roles_fail():
    registry = build_source_registry(source_context())
    with pytest.raises(ClaimAnchoredFailure) as error:
        bind_claims(extraction(source_id="external-rag"), registry, [])
    assert error.value.code == "claim_source_unknown"
    value = extraction()
    claim = value.claims[0]
    opposing = claim.evidence[0].model_copy(update={"role": "contradicting"})
    value = value.model_copy(
        update={
            "claims": (
                claim.model_copy(update={"evidence": (*claim.evidence, opposing)}),
            )
        }
    )
    with pytest.raises(ClaimAnchoredFailure) as error:
        bind_claims(value, registry, [])
    assert error.value.code == "claim_source_roles_overlap"


def test_cross_page_binding_and_stale_provenance():
    text = "first page second page"
    spans = [page(text, 0, 11, 1), page(text, 11, len(text), 2)]
    assert bind(text, "page second", documents(spans))[0].spans[
        0
    ].citation.page_numbers == [1, 2]
    spans[0]["text_sha256"] = "a" * 64
    span = bind(text, "page second", documents(spans))[0].spans[0]
    assert span.citation.page_numbers == []
    assert span.locator_status == "narrative_only"


def test_registry_requires_exact_admitted_source_set():
    context = source_context()
    context["_source_text_by_message_id"]["rag"] = "untrusted external text"
    with pytest.raises(ClaimAnchoredFailure):
        build_source_registry(context)


def test_uncovered_text_between_pages_cannot_gain_a_page_locator():
    text = "first UNMAPPED second"
    spans = [page(text, 0, 5, 1), page(text, 15, len(text), 2)]
    bound = bind(text, text, documents(spans))[0]
    assert bound.spans[0].locator_status == "narrative_only"
    assert bound.spans[0].citation.page_numbers == []
