import hashlib

from app.services.case_analysis.contracts import AnalysisClaimV3
from app.services.case_analysis.source_citations import bind_analysis_claim_citations
from app.services.chat.document_provenance import validated_document_source_payloads
from app.schemas.chat import CaseNarrativeDocumentSource
from app.services.document_ingestion.contracts import DocumentPage


def document_source(content: str) -> CaseNarrativeDocumentSource:
    return CaseNarrativeDocumentSource.model_validate(
        {
            "document_id": "DOC-1",
            "filename": "statement.pdf",
            "extraction_method": "native_pdf",
            "page_count": 2,
            "verification_status": "native",
            "confidence_status": "not_applicable",
            "minimum_confidence": None,
            "warnings": [],
            "page_spans": [
                {
                    "page_number": 1,
                    "start_offset": 0,
                    "end_offset": len(content),
                    "text_sha256": hashlib.sha256(content.encode()).hexdigest(),
                }
            ],
        }
    )


def multi_page_source(
    pages: list[tuple[int, str]],
) -> tuple[str, CaseNarrativeDocumentSource]:
    content = "\n\n".join(text for _, text in pages)
    offset = 0
    spans = []
    for page_number, text in pages:
        spans.append(
            {
                "page_number": page_number,
                "start_offset": offset,
                "end_offset": offset + len(text),
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            }
        )
        offset += len(text) + 2
    source = CaseNarrativeDocumentSource.model_validate(
        {
            "document_id": "DOC-1",
            "filename": "statement.pdf",
            "extraction_method": "native_pdf",
            "page_count": max(page for page, _ in pages),
            "verification_status": "native",
            "confidence_status": "not_applicable",
            "minimum_confidence": None,
            "warnings": [],
            "page_spans": spans,
        }
    )
    return content, source


def claim(source_id: str, quote: str) -> AnalysisClaimV3:
    return AnalysisClaimV3.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "The submitted statement reports a transfer.",
            "epistemic_status": "reported",
            "supporting_source_message_ids": [source_id],
            "contradicting_source_message_ids": [],
            "supporting_citations": [
                {
                    "source_message_id": source_id,
                    "exact_quote": quote,
                }
            ],
            "contradicting_citations": [],
            "reasoning_summary": None,
        }
    )


def test_valid_quote_binds_to_validated_document_page() -> None:
    source_id = "message-1"
    content = "The complainant transferred 25,000 baht."
    source = document_source(content).model_dump(mode="json")
    bound = bind_analysis_claim_citations(
        [claim(source_id, "transferred 25,000 baht")],
        {
            "_source_text_by_message_id": {source_id: content},
            "document_source_context": [
                {"source_message_id": source_id, "documents": [source]}
            ],
        },
    )
    citation = bound[0].supporting_citations[0]
    assert citation.filename == "statement.pdf"
    assert citation.page_numbers == [1]


def test_narrative_only_quote_remains_message_level() -> None:
    source_id = "message-1"
    content = "The witness reported seeing a blue vehicle."
    bound = bind_analysis_claim_citations(
        [claim(source_id, "seeing a blue vehicle")],
        {"_source_text_by_message_id": {source_id: content}},
    )
    citation = bound[0].supporting_citations[0]
    assert citation.filename is None
    assert citation.page_numbers == []


def test_invalid_quote_is_not_persisted_as_a_citation() -> None:
    source_id = "message-1"
    bound = bind_analysis_claim_citations(
        [claim(source_id, "paraphrased text")],
        {"_source_text_by_message_id": {source_id: "Exact source text"}},
    )
    assert bound[0].supporting_citations == []


def test_edited_narrative_drops_stale_page_span() -> None:
    source = document_source("Original page text")
    payload = validated_document_source_payloads("Edited page text", [source])
    assert payload[0]["page_spans"] == []


def test_edited_early_page_drops_later_page_spans() -> None:
    content, source = multi_page_source([(1, "Original first page"), (2, "Second page")])
    edited = content.replace("Original first page", "Reviewed first page")
    payload = validated_document_source_payloads(edited, [source])
    assert payload[0]["page_spans"] == []


def test_quote_spanning_pages_binds_all_touched_pages() -> None:
    content, source = multi_page_source([(4, "The transfer was recorded"), (5, "in the bank ledger")])
    bound = bind_analysis_claim_citations(
        [claim("message-1", "recorded\n\nin the")],
        {
            "_source_text_by_message_id": {"message-1": content},
            "document_source_context": [
                {"source_message_id": "message-1", "documents": [source.model_dump(mode="json")]}
            ],
        },
    )
    citation = bound[0].supporting_citations[0]
    assert citation.filename == "statement.pdf"
    assert citation.page_numbers == [4, 5]


def test_quote_spanning_non_consecutive_pages_keeps_safe_page_list() -> None:
    content, source = multi_page_source([(4, "The transfer was recorded"), (7, "in the bank ledger")])
    bound = bind_analysis_claim_citations(
        [claim("message-1", "recorded\n\nin the")],
        {
            "_source_text_by_message_id": {"message-1": content},
            "document_source_context": [
                {"source_message_id": "message-1", "documents": [source.model_dump(mode="json")]}
            ],
        },
    )
    assert bound[0].supporting_citations[0].page_numbers == [4, 7]


def test_stale_page_hash_drops_document_locator() -> None:
    content = "The transfer appears on this page."
    document = document_source(content).model_dump(mode="json")
    document["page_spans"] = [{
        "page_number": 4,
        "start_offset": 0,
        "end_offset": len(content),
        "text_sha256": "0" * 64,
    }]
    bound = bind_analysis_claim_citations(
        [claim("message-1", "transfer appears")],
        {
            "_source_text_by_message_id": {"message-1": content},
            "document_source_context": [
                {"source_message_id": "message-1", "documents": [document]}
            ],
        },
    )
    citation = bound[0].supporting_citations[0]
    assert citation.filename is None
    assert citation.page_numbers == []


def test_duplicate_quote_on_different_pages_does_not_guess_a_page() -> None:
    source_id = "message-1"
    content = "same phrase\n\nsame phrase"
    page_text = "same phrase"
    page_hash = hashlib.sha256(page_text.encode()).hexdigest()
    document = document_source(page_text).model_dump(mode="json")
    document["page_spans"] = [
        {
            "page_number": 1,
            "start_offset": 0,
            "end_offset": 11,
            "text_sha256": page_hash,
        },
        {
            "page_number": 2,
            "start_offset": 13,
            "end_offset": 24,
            "text_sha256": page_hash,
        },
    ]
    bound = bind_analysis_claim_citations(
        [claim(source_id, page_text)],
        {
            "_source_text_by_message_id": {source_id: content},
            "document_source_context": [
                {"source_message_id": source_id, "documents": [document]}
            ],
        },
    )
    citation = bound[0].supporting_citations[0]
    assert citation.filename is None
    assert citation.page_numbers == []


def test_late_duplicate_quote_on_another_page_does_not_escape_ambiguity_limit() -> None:
    repeated_page = "same phrase\n" * 65
    content, source = multi_page_source([(1, repeated_page), (2, "same phrase")])
    bound = bind_analysis_claim_citations(
        [claim("message-1", "same phrase")],
        {
            "_source_text_by_message_id": {"message-1": content},
            "document_source_context": [
                {"source_message_id": "message-1", "documents": [source.model_dump(mode="json")]}
            ],
        },
    )
    citation = bound[0].supporting_citations[0]
    assert citation.filename is None
    assert citation.page_numbers == []


def test_document_page_response_includes_a_normalized_text_digest() -> None:
    page = DocumentPage(page_number=1, merged_text="  Page text  ")
    expected = hashlib.sha256("Page text".encode()).hexdigest()
    assert page.model_dump(mode="json")["text_sha256"] == expected
