from __future__ import annotations

import pytest

from app.analysis.write import reading_from
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseProviderClaim, CaseSourceCitation
from app.trace.trace import CaseAnalysisTrace, CaseProviderReadingReply

FIRST = CaseSourceItem(
    "S1",
    "document",
    "John reported that the server was encrypted.\nThe report was received at 13:00.",
    document_id="D1",
    filename="statement.pdf",
    provenance={
        "extraction_method": "ocr",
        "verification_status": "machine_read",
        "warnings": ["uncertain digits"],
    },
)
SECOND = CaseSourceItem(
    "S2",
    "document",
    "The server logs record encryption at 13:00.",
    document_id="D2",
    filename="logs.pdf",
)
BUNDLE = CaseSourceBundle(4, (FIRST, SECOND))


def claim(citations, claim_id="A-01"):
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text="The server was encrypted at 13:00.",
        epistemic_status="reported",
        supporting_citations=[CaseSourceCitation(**c) for c in citations],
    )


def resolved(citations, bundle=BUNDLE):
    return resolve_case_trace(
        CaseAnalysisTrace(
            analysis_mode="case_overview",
            summary="An incident occurred. [A-01]",
            claims=[claim(citations)],
        ),
        bundle,
    )


def reference(source, *ids):
    return {
        "source_id": source.source_id,
        "evidence_unit_ids": list(ids) or [evidence_units(source)[0].unit_id],
    }


def test_valid_ids_resolve_original_spans_without_any_quote_search():
    trace = resolved([reference(FIRST)])
    [citation] = trace.claims[0].supporting_citations
    assert citation.pointer_state == "direct"
    assert citation.exact_quote == FIRST.text[citation.start : citation.end]
    assert citation.evidence_unit_ids == [evidence_units(FIRST)[0].unit_id]
    assert (citation.document_id, citation.filename, citation.page_numbers) == (
        "D1",
        "statement.pdf",
        [],
    )
    assert trace.grounding.evidence_ids_claimed == trace.grounding.evidence_ids_resolved == 1
    assert trace.grounding.evidence_ids_invalid == 0
    assert trace.grounding.evidence_id_resolution_rate == 1.0
    assert trace.grounding.claims_with_direct_evidence == 1
    assert trace.grounding.claims_with_recovered_evidence == 0
    assert trace.grounding.claims_without_resolved_evidence == 0
    assert FIRST.provenance["warnings"] == ["uncertain digits"]


@pytest.mark.parametrize(
    ("source_id", "unit_id", "reason"),
    [
        ("missing", evidence_units(FIRST)[0].unit_id, "unknown_source"),
        ("S1", evidence_units(FIRST)[0].unit_id.replace("U001", "U999"), "unknown_unit"),
        ("S1", "U001", "malformed_id"),
        ("S1", "", "malformed_id"),
        ("S1", evidence_units(FIRST)[0].unit_id + " ", "malformed_id"),
        ("S1", evidence_units(FIRST)[0].unit_id.replace("U001", "U000"), "malformed_id"),
        ("S1", evidence_units(SECOND)[0].unit_id, "cross_source"),
        ("S1", "S1:U001-0000000000000000", "stale_id"),
    ],
)
def test_invalid_ids_do_not_become_supporting_citations(source_id, unit_id, reason):
    trace = resolved([{"source_id": source_id, "evidence_unit_ids": [unit_id]}])
    [item] = trace.claims
    assert item.supporting_citations == []
    assert item.epistemic_status == "not_confirmed"
    assert item.invalid_evidence[0].reason == reason
    assert item.invalid_evidence[0].pointer_state == "unresolved"
    assert trace.grounding.evidence_ids_claimed == trace.grounding.evidence_ids_invalid == 1
    assert trace.grounding.evidence_ids_resolved == 0
    assert trace.grounding.evidence_id_resolution_rate == 0
    assert trace.grounding.claims_without_resolved_evidence == 1


def test_duplicate_ids_are_counted_and_never_duplicate_materialized_evidence():
    unit = evidence_units(FIRST)[0].unit_id
    trace = resolved([reference(FIRST, unit, unit), reference(FIRST, unit)])
    assert len(trace.claims[0].supporting_citations) == 1
    assert [item.reason for item in trace.claims[0].invalid_evidence] == [
        "duplicate_id",
        "duplicate_id",
    ]
    assert trace.grounding.evidence_ids_claimed == 3
    assert trace.grounding.evidence_ids_resolved == 1
    assert trace.grounding.evidence_ids_invalid == 2
    assert trace.grounding.evidence_id_resolution_rate == 1 / 3


def test_one_claim_can_resolve_multiple_units_from_multiple_documents():
    first_units = evidence_units(FIRST)
    assert len(first_units) == 2
    trace = resolved([reference(FIRST, *(u.unit_id for u in first_units)), reference(SECOND)])
    citations = trace.claims[0].supporting_citations
    assert [c.source_id for c in citations] == ["S1", "S1", "S2"]
    assert [c.document_id for c in citations] == ["D1", "D1", "D2"]
    assert all(c.pointer_state == "direct" for c in citations)
    assert trace.claims[0].supporting_source_ids == ["S1", "S2"]
    assert trace.grounding.evidence_ids_resolved == 3
    assert trace.grounding.sources_cited == trace.grounding.sources_total == 2
    assert CaseAnalysisTrace.model_validate_json(trace.model_dump_json()) == trace


def test_one_unit_can_support_different_claims_and_counts_each_reference():
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Reported encryption.",
        claims=[claim([reference(FIRST)], "A-01"), claim([reference(FIRST)], "A-02")],
    )
    trace = resolve_case_trace(trace, BUNDLE)
    assert trace.grounding.evidence_ids_claimed == trace.grounding.evidence_ids_resolved == 2


def test_provider_ids_survive_conversion_without_provider_generated_locations():
    reply = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "epistemic_status": "reported",
                    "text": "Reported encryption.",
                    "supporting_citations": [reference(FIRST)],
                }
            ],
        }
    )
    [citation] = reading_from(reply).claims[0].supporting_citations
    assert citation.evidence_unit_ids == reference(FIRST)["evidence_unit_ids"]
    assert citation.exact_quote == "" and citation.start is None
    assert citation.pointer_state == "unresolved"


def test_resolved_unit_expansion_survives_trace_storage_without_truncation():
    source = CaseSourceItem("S1", "document", "\n".join(f"Record {i}." for i in range(65)))
    units = evidence_units(source)
    assert len(units) == 65
    trace = resolved(
        [reference(source, *(u.unit_id for u in units[:64])), reference(source, units[64].unit_id)],
        CaseSourceBundle(1, (source,)),
    )
    stored = CaseAnalysisTrace.model_validate_json(trace.model_dump_json())
    assert len(stored.claims[0].supporting_citations) == 65
    assert stored.grounding.evidence_ids_resolved == 65


def test_provider_does_not_silently_discard_excess_reference_groups():
    with pytest.raises(ValueError, match="at most 64"):
        CaseProviderClaim.model_validate(
            {
                "claim_id": "A-01",
                "claim_type": "reported",
                "epistemic_status": "reported",
                "text": "Reported encryption.",
                "supporting_citations": [reference(FIRST) for _ in range(65)],
            }
        )


@pytest.mark.parametrize(
    "citation",
    [
        {"source_id": "S1", "evidence_unit_ids": []},
        {"source_id": "S1", "evidence_unit_ids": None},
        {"source_id": "  ", "evidence_unit_ids": ["bad"]},
        {"source_id": "S1"},
    ],
)
def test_provider_invalid_reference_shapes_fail_instead_of_disappearing(citation):
    with pytest.raises(ValueError):
        CaseProviderClaim.model_validate(
            {
                "claim_id": "A-01",
                "claim_type": "reported",
                "epistemic_status": "reported",
                "text": "Reported encryption.",
                "supporting_citations": [citation],
            }
        )


def test_pointer_state_remains_optional_for_stored_legacy_api_citations():
    schema = CaseSourceCitation.model_json_schema()
    assert "pointer_state" not in schema.get("required", [])
    assert "default" not in schema["properties"]["pointer_state"]
    assert (
        CaseSourceCitation(source_id="S1", exact_quote="Legacy text").pointer_state == "recovered"
    )


def test_duplicate_source_identity_fails_before_analysis_binding():
    with pytest.raises(ValueError, match="must be unique"):
        resolved([reference(FIRST)], CaseSourceBundle(1, (FIRST, FIRST)))


def test_invalid_references_stay_visible_alongside_valid_evidence():
    trace = resolved([reference(FIRST), reference(FIRST, "not-an-id")])
    assert trace.claims[0].epistemic_status == "reported"
    assert len(trace.claims[0].supporting_citations) == 1
    assert trace.claims[0].invalid_evidence[0].reason == "malformed_id"
    assert trace.grounding.evidence_id_resolution_rate == 0.5


def test_repeated_document_text_uses_the_selected_offset_for_its_page():
    text = "John reported the server outage.\nJohn reported the server outage."
    cut = text.index("\n") + 1
    source = CaseSourceItem(
        "S1",
        "document",
        text,
        "D1",
        "statement.pdf",
        {
            "pages": [
                {"page_number": 1, "start_offset": 0, "end_offset": cut},
                {"page_number": 2, "start_offset": cut, "end_offset": len(text)},
            ]
        },
    )
    [_, selected] = evidence_units(source)
    trace = resolved([reference(source, selected.unit_id)], CaseSourceBundle(1, (source,)))
    assert trace.claims[0].supporting_citations[0].page_numbers == [2]
    assert trace.claims[0].supporting_citations[0].start == cut
