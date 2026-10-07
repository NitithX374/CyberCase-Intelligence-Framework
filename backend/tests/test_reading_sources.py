from dataclasses import replace

import pytest

from app.analysis.reading_sources import ReadingSources
from app.analysis.write import reading_from, reading_request
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import EvidenceIndex, evidence_units
from app.trace.bind import bound_claims, followup_registry_items
from app.trace.claims import CaseFollowupExchange
from app.trace.trace import CaseProviderReadingReply

FIRST = CaseSourceItem(
    "S1", "document", "John sent an email.\nJane received it.", "D1", "email.pdf"
)
SECOND = CaseSourceItem("S2", "document", "The bank froze an account.", "D2", "bank.pdf")
BUNDLE = CaseSourceBundle(4, (FIRST, SECOND))


def reply_for(citations, contradicting=()):
    return CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "epistemic_status": "reported",
                    "text": "The supplied sources describe an email and an account freeze.",
                    "supporting_citations": citations,
                    "contradicting_citations": list(contradicting),
                }
            ],
        }
    )


def citation(source_id, *unit_ids):
    return {"source_id": source_id, "evidence_unit_ids": list(unit_ids)}


@pytest.mark.parametrize(
    "text",
    [
        FIRST.text,
        "ผู้เสียหายแจ้งเหตุ\nโอนเงิน 25,000 บาท\n",
        "\r\n  • 13:00 ERROR\nบัญชี 12O-456\t\n",
        " \r\n\t",
        "",
    ],
)
def test_compact_payload_preserves_every_source_character_and_stable_local_ids(text):
    source = replace(FIRST, text=text)
    first, second = ReadingSources((source,)), ReadingSources((source,))
    assert first.payloads == second.payloads
    payload = first.payloads[0]
    assert payload["source_id"] == "S1"
    assert payload["document"] == {"document_id": "D1", "filename": "email.pdf"}
    assert "text" not in payload
    assert "".join(unit["text"] for unit in payload["evidence_units"]) == text
    for number, unit in enumerate(payload["evidence_units"], 1):
        assert set(unit) == {"unit_id", "text"}
        assert unit["unit_id"] == f"U{number:03d}"
        canonical = first.canonical_id("S1", unit["unit_id"])
        resolved, reason = EvidenceIndex((source,)).resolve("S1", canonical)
        if text.strip():
            assert reason is None
            assert resolved.text == source.text[resolved.start : resolved.end] == unit["text"]


def test_local_unit_numbers_are_source_scoped_and_a_claim_can_select_multiple_documents():
    sources = ReadingSources(BUNDLE.sources)
    original = reply_for([citation("S1", "U001", "U002"), citation("S2", "U001")])
    reading, grounding = bound_claims(reading_from(original, reading_sources=sources), BUNDLE)
    [claim] = reading.claims
    assert claim.supporting_source_ids == ["S1", "S2"]
    assert [item.document_id for item in claim.supporting_citations] == ["D1", "D1", "D2"]
    assert [item.exact_quote for item in claim.supporting_citations] == [
        FIRST.text[: evidence_units(FIRST)[0].end],
        "Jane received it.",
        SECOND.text,
    ]
    assert len({item.evidence_unit_ids[0] for item in claim.supporting_citations}) == 3
    assert grounding.evidence_ids_claimed == grounding.evidence_ids_resolved == 3
    assert original.claims[0].supporting_citations[0].evidence_unit_ids == ["U001", "U002"]


@pytest.mark.parametrize(
    "source_id,unit_id,reason",
    [
        ("missing", "U001", "unknown_source"),
        ("S1", "U999", "unknown_unit"),
        ("S1", "U000", "malformed_id"),
        ("S1", "U01", "malformed_id"),
        ("S1", "U0001", "malformed_id"),
        ("S1", " U001", "malformed_id"),
        ("S1", "U001x", "malformed_id"),
        ("S1", "U" + "9" * 239, "malformed_id"),
        ("S1", evidence_units(SECOND)[0].unit_id, "cross_source"),
        ("S1", "S1:U001-0000000000000000", "stale_id"),
    ],
)
def test_invalid_addresses_keep_existing_binding_diagnostics(source_id, unit_id, reason):
    sources = ReadingSources(BUNDLE.sources)
    reply = reply_for([citation(source_id, unit_id)])
    reading, grounding = bound_claims(reading_from(reply, reading_sources=sources), BUNDLE)
    [claim] = reading.claims
    assert claim.supporting_citations == []
    assert claim.invalid_evidence[0].reason == reason
    assert claim.epistemic_status == "not_confirmed"
    assert grounding.evidence_ids_invalid == 1


def test_duplicates_are_diagnosed_after_alias_decoding_including_canonical_duplicates():
    sources = ReadingSources(BUNDLE.sources)
    canonical = evidence_units(FIRST)[0].unit_id
    reply = reply_for([citation("S1", "U001", "U001", canonical), citation("S2", "U001")])
    reading, grounding = bound_claims(reading_from(reply, reading_sources=sources), BUNDLE)
    [claim] = reading.claims
    assert len(claim.supporting_citations) == 2
    assert [item.reason for item in claim.invalid_evidence] == ["duplicate_id", "duplicate_id"]
    assert grounding.evidence_ids_claimed == 4
    assert grounding.evidence_ids_resolved == grounding.evidence_ids_invalid == 2


def test_decoding_uses_the_request_revision_and_cannot_rebind_a_reply_to_changed_source_text():
    request_sources = ReadingSources(BUNDLE.sources)
    reply = reply_for([citation("S1", "U001")])
    updated = replace(FIRST, text="John did not send an email.")
    changed = CaseSourceBundle(5, (updated, SECOND))
    reading, grounding = bound_claims(reading_from(reply, reading_sources=request_sources), changed)
    assert reading.claims[0].supporting_citations == []
    assert reading.claims[0].invalid_evidence[0].reason == "stale_id"
    assert grounding.evidence_ids_resolved == 0


def test_canonical_historical_ids_still_resolve_without_a_transport_address_book():
    reply = reply_for([citation("S1", evidence_units(FIRST)[0].unit_id)])
    historical, _ = bound_claims(reading_from(reply), BUNDLE)
    decoded, _ = bound_claims(
        reading_from(reply, reading_sources=ReadingSources(BUNDLE.sources)), BUNDLE
    )
    assert historical == decoded
    assert historical.claims[0].supporting_citations[0].pointer_state == "direct"


def test_contradicting_unit_ids_are_decoded_without_changing_their_role():
    sources = ReadingSources(BUNDLE.sources)
    reply = reply_for([citation("S1", "U001")], [citation("S2", "U001")])
    reading, grounding = bound_claims(reading_from(reply, reading_sources=sources), BUNDLE)
    assert reading.claims[0].contradicting_source_ids == ["S2"]
    assert reading.claims[0].contradicting_citations[0].evidence_unit_ids == [
        evidence_units(SECOND)[0].unit_id
    ]
    assert grounding.evidence_ids_resolved == 2


def test_followup_answers_share_local_addressing_and_preserve_source_revision():
    history = (
        CaseFollowupExchange("QA-03", "affected", "Who?", "John is the victim."),
        CaseFollowupExchange("QA-04", "when", "When?", None),
    )
    sources = ReadingSources((*BUNDLE.sources, *followup_registry_items(history)))
    payload = reading_request(BUNDLE, "english", history, reading_sources=sources)
    assert [item["source_id"] for item in payload["case_sources"]] == ["S1", "S2", "QA-03"]
    assert payload["source_revision"] == 4
    assert payload["case_sources"][2]["evidence_units"] == [
        {"unit_id": "U001", "text": "John is the victim."}
    ]
    reply = reply_for([citation("QA-03", "U001")])
    reading, grounding = bound_claims(reading_from(reply, reading_sources=sources), BUNDLE, history)
    assert reading.claims[0].supporting_citations[0].source_id == "QA-03"
    assert grounding.evidence_ids_resolved == 1


def test_compact_ocr_payload_retains_provenance_and_resolved_page_location():
    source = replace(
        FIRST,
        provenance={
            "extraction_method": "document_recognition",
            "verification_status": "needs_review",
            "warnings": ["OCR uncertainty"],
            "pages": [{"page_number": 2, "start_offset": 0, "end_offset": len(FIRST.text)}],
        },
    )
    bundle = CaseSourceBundle(4, (source,))
    sources = ReadingSources(bundle.sources)
    assert sources.payloads[0]["document"] == {
        "document_id": "D1",
        "filename": "email.pdf",
        "extraction_method": "document_recognition",
        "verification_status": "needs_review",
        "warnings": ["OCR uncertainty"],
    }
    reply = reply_for([citation("S1", "U002")])
    reading, _ = bound_claims(reading_from(reply, reading_sources=sources), bundle)
    [resolved] = reading.claims[0].supporting_citations
    assert resolved.page_numbers == [2]
    assert resolved.exact_quote == source.text[resolved.start : resolved.end] == "Jane received it."


def test_duplicate_source_identity_is_refused_before_requesting_the_reader():
    with pytest.raises(ValueError, match="identities must be unique"):
        ReadingSources((FIRST, replace(SECOND, source_id="S1")))
