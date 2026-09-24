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
