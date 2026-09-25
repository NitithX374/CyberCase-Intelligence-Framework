from __future__ import annotations

from uuid import uuid4

from app.services.analysis.steps.write import provider_source_payload
from app.services.sources.case_source_bundle import CaseSourceItem


def test_a_document_still_carries_its_extraction_quality():
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="document",
        text="Received statement",
        document_id=str(uuid4()),
        filename="statement.pdf",
        provenance={"extraction_method": "native", "warnings": []},
    )
    payload = provider_source_payload(source)
    assert payload["document"]["filename"] == "statement.pdf"
    assert payload["document"]["extraction_method"] == "native"


def test_a_document_sends_only_what_its_provenance_records():
    document_id = str(uuid4())
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="document",
        text="Scanned statement",
        document_id=document_id,
        filename="scan.pdf",
        provenance={
            "pages": [{"page_number": 1, "text": "Scanned statement"}],
            "extraction_method": "document_recognition",
            "verification_status": "needs_review",
            "warnings": ["Page 1: native text was not usable."],
            "provider": "document_recognition",
            "confidence_status": "unknown",
            "minimum_confidence": None,
        },
    )
    assert provider_source_payload(source)["document"] == {
        "document_id": document_id,
        "filename": "scan.pdf",
        "extraction_method": "document_recognition",
        "verification_status": "needs_review",
        "warnings": ["Page 1: native text was not usable."],
    }
