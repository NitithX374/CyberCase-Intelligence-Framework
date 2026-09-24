from datetime import UTC

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisTrace,
    CaseGeneratedUnit,
    CaseProviderAnalysis,
    CaseSourceCitation,
)
from app.services.analysis.steps.bind import resolve_case_trace
from app.services.analysis.steps.quotes import (
    find_aligned_quote,
    resolve_document_locator,
)
from app.services.document_ingestion.provenance import bind_exact_page_spans
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem


def _source(
    source_id: str,
    content: str,
    provenance: dict[str, object] | None = None,
) -> CaseSourceItem:
    return CaseSourceItem(
        source_id=source_id,
        source_kind="narrative",
        text=content,
        provenance=provenance or {},
    )


def _trace(claim: CaseAnalysisClaim, content: str) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=claim.text,
        claims=[claim],
    )


def test_case_validation_allows_sources_without_exact_citations():
    content = "The witness reported a blue vehicle."
    supporting_ids = ["s1"]
    contradicting_ids = ["s2"]
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The witness reported a vehicle.",
        epistemic_status="reported",
        supporting_source_ids=supporting_ids,
        supporting_citations=[],
        contradicting_source_ids=contradicting_ids,
        contradicting_citations=[],
    )
    trace = _trace(claim, content)
    validated = resolve_case_trace(
        trace,
        CaseSourceBundle(
            revision=1,
            sources=(_source("s1", content), _source("s2", "A different account.")),
        ),
        [],
    )
    assert validated.claims[0].claim_id == "A-01"
    assert validated.claims[0].supporting_source_ids == ["s1"]
    assert validated.claims[0].contradicting_source_ids == ["s2"]


def test_exact_page_spans_are_contiguous_and_fail_closed_for_repeated_or_edited_text():
    content = "first page\n\nsecond page"
    provenance = bind_exact_page_spans(
        {
            "pages": [
                {"page_number": 1, "merged_text": "first page"},
                {"page_number": 2, "merged_text": "second page"},
            ]
        },
        content,
    )
    pages = provenance["pages"]
    assert pages[0]["start_offset"] == 0
    assert pages[0]["end_offset"] == pages[1]["start_offset"]
    assert "text_sha256" not in pages[0]
    context = [
        {
            "source_id": "s1",
            "documents": [
                {
                    "document_id": "d1",
                    "filename": "case.pdf",
                    "page_spans": pages,
                }
            ],
        }
    ]
    locator = resolve_document_locator("s1", "page\n\nsecond", content, context)
    assert locator["page_numbers"] == [1, 2]

    repeated = "same\n\nsame"
    repeated_pages = bind_exact_page_spans(
        {
            "pages": [
                {"page_number": 1, "merged_text": "same"},
                {"page_number": 2, "merged_text": "same"},
            ]
        },
        repeated,
    )["pages"]
    repeated_locator = resolve_document_locator(
        "s1",
        "same",
        repeated,
        [
            {
                "source_id": "s1",
                "documents": [
                    {"document_id": "d1", "filename": "case.pdf", "page_spans": repeated_pages}
                ],
            }
        ],
    )
    assert repeated_locator["page_numbers"] == []
    edited_locator = resolve_document_locator(
        "s1", "second page", "edited page\n\nsecond page", context
    )
    assert edited_locator["page_numbers"] == []


def test_case_claim_normalizes_c_and_claim_identifier_aliases():
    claim1 = CaseAnalysisClaim(
        claim_id="C1",
        claim_type="reported",
        text="The witness reported an incident.",
        epistemic_status="reported",
    )
    assert claim1.claim_id == "A-01"

    claim2 = CaseAnalysisClaim(
        claim_id="claim-2",
        claim_type="reported",
        text="A second report was filed.",
        epistemic_status="reported",
    )
    assert claim2.claim_id == "A-02"

    claim3 = CaseAnalysisClaim(
        claim_id="c_09",
        claim_type="reported",
        text="A ninth report was filed.",
        epistemic_status="reported",
    )
    assert claim3.claim_id == "A-09"

    claim_canonical = CaseAnalysisClaim(
        claim_id="A-03",
        claim_type="reported",
        text="Third report.",
        epistemic_status="reported",
    )
    assert claim_canonical.claim_id == "A-03"


def test_case_provider_analysis_normalizes_model_claim_ids_from_json():
    raw_payload = """{
        "version": "case_analysis_trace_v1",
        "summary": "Summary text.",
        "involved_parties": [],
        "timeline": [],
        "impacts": [],
        "claims": [
            {
                "claim_id": "C1",
                "claim_type": "reported",
                "text": "First claim text.",
                "epistemic_status": "reported",
                "supporting_source_ids": ["s1"],
                "contradicting_source_ids": [],
                "supporting_citations": [],
                "contradicting_citations": [],
                "reasoning_summary": null
            },
            {
                "claim_id": "C9",
                "claim_type": "reported",
                "text": "Ninth claim text.",
                "epistemic_status": "reported",
                "supporting_source_ids": ["s1"],
                "contradicting_source_ids": [],
                "supporting_citations": [],
                "contradicting_citations": [],
                "reasoning_summary": null
            }
        ],
        "mitre_associations": [
            {
                "association_id": "MA1",
                "technique_id": "T1078",
                "claim_ids": ["C1", "C9"],
                "reason": "Valid technique mapping",
                "status": "candidate_only",
                "support_role": "external_technical_context"
            }
        ]
    }"""
    parsed = CaseProviderAnalysis.model_validate_json(raw_payload)
    assert parsed.claims[0].claim_id == "A-01"
    assert parsed.claims[1].claim_id == "A-09"
    assert parsed.mitre_associations[0].association_id == "MA-01"
    assert parsed.mitre_associations[0].claim_ids == ["A-01", "A-09"]


def gap_payload(**overrides) -> dict[str, object]:
    return {
        "gap_id": "G-01",
        "gap_key": "incident_time",
        "topic": "Incident time",
        "status": "NOT_PROVIDED",
        "description": "The time is not stated.",
        "affected_claim_ids": [],
        "reason": "Timing matters.",
        "priority": "high",
        "askable": True,
        "clarification_question": "When did it happen?",
        **overrides,
    }


def test_provider_output_is_normalized_instead_of_rejected():
    parsed = CaseProviderAnalysis.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "summary": "Files were encrypted.",
            "involved_parties": [
                {"name": "ACME", "role": "Victim", "claim_ids": ["A-01", "A-1", "claim-1"]}
            ],
            "timeline": [],
            "impacts": [],
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "Files were encrypted.",
                    "epistemic_status": "reported",
                    "supporting_source_ids": ["s1"],
                    "contradicting_source_ids": [],
                    "supporting_citations": [
                        {
                            "source_id": "s1",
                            "exact_quote": "Files were encrypted.",
                            "document_id": "d1",
                            "filename": "report.pdf",
                            "page_numbers": list(range(1, 10)),
                        }
                    ],
                    "contradicting_citations": [],
                    "reasoning_summary": "r" * 1_001,
                }
            ],
            "gaps": [
                gap_payload(
                    gap_key="incident\ntime",
                    topic="Incident\r\ntime",
                    affected_claim_ids=["A-01", "A-1"],
                    clarification_question="When did\nit happen?",
                ),
                gap_payload(gap_id="G-02", clarification_question="x" * 301),
            ],
            "mitre_associations": [
                {
                    "association_id": "MA-01",
                    "technique_id": " S0096 ",
                    "claim_ids": ["A-01", "A-1"],
                    "reason": "Copied from the table.",
                    "plain_meaning": "p" * 601,
                    "status": "candidate_only",
                    "support_role": "external_technical_context",
                }
            ],
        }
    )

    assert parsed.involved_parties[0].claim_ids == ["A-01"]
    assert parsed.claims[0].supporting_citations[0].model_dump() == {
        "source_id": "s1",
        "exact_quote": "Files were encrypted.",
    }
    assert parsed.gaps[0].gap_key == "incident time"
    assert parsed.gaps[0].topic == "Incident time"
    assert parsed.gaps[0].affected_claim_ids == ["A-01"]
    assert parsed.gaps[0].clarification_question == "When did it happen?"
    assert parsed.gaps[1].clarification_question is None
    assert parsed.mitre_associations[0].technique_id == "S0096"
    assert parsed.mitre_associations[0].claim_ids == ["A-01"]
    assert parsed.claims[0].reasoning_summary == "r" * 1_000
    assert parsed.mitre_associations[0].plain_meaning == "p" * 600


def test_a_quote_spanning_more_pages_than_a_citation_holds_keeps_no_page_locator():
    lines = [f"line {number}" for number in range(1, 11)]
    content = "\n\n".join(lines)
    provenance = bind_exact_page_spans(
        {
            "pages": [
                {"page_number": number, "merged_text": line} for number, line in enumerate(lines, 1)
            ]
        },
        content,
    )
    quote = "\n\n".join(lines[:9])
    source = CaseSourceItem(
        source_id="s1",
        source_kind="document",
        text=content,
        document_id="d1",
        filename="report.pdf",
        provenance={"pages": provenance["pages"]},
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Nine pages were quoted.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[CaseSourceCitation(source_id="s1", exact_quote=quote)],
    )

    validated = resolve_case_trace(
        _trace(claim, content), CaseSourceBundle(revision=1, sources=(source,)), []
    )

    citation = validated.claims[0].supporting_citations[0]
    assert citation.exact_quote == quote
    assert citation.page_numbers == []


def test_case_provider_analysis_carries_material_gaps_from_main_analysis():
    parsed = CaseProviderAnalysis.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "summary": "A loss was reported, but its timing is not established.",
            "involved_parties": [],
            "timeline": [],
            "impacts": [],
            "claims": [],
            "gaps": [
                {
                    "gap_id": "gap1",
                    "gap_key": "incident_time",
                    "topic": "Incident time",
                    "status": "NOT_PROVIDED",
                    "description": "The supplied material does not state when the incident occurred.",
                    "affected_claim_ids": [],
                    "reason": "Timing affects the case chronology.",
                    "priority": "high",
                    "askable": True,
                }
            ],
            "mitre_associations": [],
        }
    )
    assert parsed.gaps[0].gap_id == "G-01"
    assert parsed.gaps[0].topic == "Incident time"


def test_case_generated_unit_and_gap_identifier_normalization():
    unit = CaseGeneratedUnit(
        text="A single generated summary unit.",
        claim_ids=("C1", "claim-2", "A-03"),
    )
    assert unit.claim_ids == ("A-01", "A-02", "A-03")

    gap = CaseAnalysisGap(
        gap_id="gap1",
        gap_key="financial_loss",
        topic="Financial loss",
        status="NOT_PROVIDED",
        description="Amount of money lost was not stated.",
        affected_claim_ids=["C1", "c2"],
        reason="Missing documentary evidence.",
        priority="high",
        askable=True,
    )
    assert gap.gap_id == "G-01"
    assert gap.affected_claim_ids == ["A-01", "A-02"]


def test_case_evidence_citation_normalizes_partial_document_locators():
    citation_partial = CaseSourceCitation.model_validate(
        {
            "source_id": "493c59ed-a9ea-48c3-a498-281d17e3030f",
            "exact_quote": "ผู้ต้องหาหลบหนี",
            "filename": "ลำดับ01 รายงานการสอบสวน.pdf",
            "page_numbers": [],
        }
    )
    assert citation_partial.document_id is None
    assert citation_partial.filename is None
    assert citation_partial.page_numbers == []

    citation_complete = CaseSourceCitation.model_validate(
        {
            "source_id": "493c59ed-a9ea-48c3-a498-281d17e3030f",
            "exact_quote": "ผู้ต้องหาหลบหนี",
            "document_id": "doc-01",
            "filename": "ลำดับ01 รายงานการสอบสวน.pdf",
            "page_numbers": [1, 2],
        }
    )
    assert citation_complete.document_id == "doc-01"
    assert citation_complete.filename == "ลำดับ01 รายงานการสอบสวน.pdf"
    assert citation_complete.page_numbers == [1, 2]


def test_find_aligned_quote_handles_markdown_and_whitespace():
    content = 'Header\n\n**Witness** Statement\n\nThe witness saw "red car".'
    assert find_aligned_quote(content, "Witness Statement") == "**Witness** Statement"
    assert find_aligned_quote(content, 'witness saw "red car"') == 'witness saw "red car"'
    assert find_aligned_quote(content, "witness saw “red car”") == 'witness saw "red car"'
    assert find_aligned_quote(content, "Nonexistent Statement") is None


def test_resolve_case_trace_allows_same_page_multiple_occurrences():
    content = "report\n\npage one fact repeated\n\nfact repeated"
    provenance = bind_exact_page_spans(
        {"pages": [{"page_number": 1, "merged_text": content}]}, content
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Fact was reported.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[CaseSourceCitation(source_id="s1", exact_quote="fact repeated")],
    )
    source = CaseSourceItem(
        source_id="s1",
        source_kind="document",
        text=content,
        document_id="d1",
        filename="report.pdf",
        provenance={"pages": provenance["pages"]},
    )
    validated = resolve_case_trace(
        _trace(claim, content),
        CaseSourceBundle(revision=1, sources=(source,)),
        [],
    )
    assert validated.claims[0].supporting_citations[0].page_numbers == [1]


def test_claim_reasoning_summary_empty_and_whitespace_normalized():
    claim_empty = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "Valid factual claim text",
            "epistemic_status": "reported",
            "supporting_source_ids": ["s1"],
            "reasoning_summary": "",
        }
    )
    assert claim_empty.reasoning_summary is None

    claim_whitespace = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-02",
            "claim_type": "reported",
            "text": "Valid factual claim text",
            "epistemic_status": "reported",
            "supporting_source_ids": ["s1"],
            "reasoning_summary": "   ",
        }
    )
    assert claim_whitespace.reasoning_summary is None


def test_claim_malformed_raw_citations_dropped_without_failing_claim():
    claim = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "Valid factual claim text",
            "epistemic_status": "reported",
            "supporting_source_ids": ["s1"],
            "supporting_citations": [
                {"source_id": "s1", "exact_quote": ""},
                {"source_id": "", "exact_quote": "some quote"},
                {
                    "source_id": "s1",
                    "exact_quote": "valid quote",
                    "document_id": "doc-01",
                    "filename": "doc.pdf",
                    "page_numbers": [1, 1, 999, -5],
                },
            ],
        }
    )
    assert len(claim.supporting_citations) == 1
    assert claim.supporting_citations[0].exact_quote == "valid quote"
    assert claim.supporting_citations[0].page_numbers == [1]


def test_case_reference_lists_drop_invalid_entries_without_rejecting_claim():
    claim = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "Valid factual claim text",
            "epistemic_status": "reported",
            "supporting_source_ids": ["s1", "s1", "", 17],
            "supporting_citations": [
                {"source_id": "s1", "exact_quote": "valid quote"},
                {"source_id": "s2", "exact_quote": "x" * 2_001},
                {"source_id": "s3", "exact_quote": "another quote", "filename": 42},
            ],
        }
    )

    assert claim.supporting_source_ids == ["s1"]
    assert [citation.source_id for citation in claim.supporting_citations] == ["s1", "s3"]
    assert claim.supporting_citations[1].filename is None


def narrative_written_at(source_id: str, created_at, *, archived_at=None):
    from types import SimpleNamespace

    return SimpleNamespace(
        id=source_id,
        source_kind="narrative",
        exact_text=f"Narrative {source_id}",
        document_id=None,
        provenance_json={},
        created_at=created_at,
        archived_at=archived_at,
        source_metadata_json={},
        document=None,
        filename=None,
    )


def analysis_citing(created_at, *cited: str):
    from types import SimpleNamespace

    return SimpleNamespace(
        created_at=created_at,
        source_revision=2,
        trace_json={
            "claims": [
                {"claim_id": f"A-{index:02d}", "supporting_source_ids": [source_id]}
                for index, source_id in enumerate(cited, 1)
            ]
        },
    )


def test_a_report_reads_the_sources_its_analysis_recorded_in_that_order():
    from datetime import datetime, timedelta
    from types import SimpleNamespace

    from app.services.sources.case_source_bundle import case_source_bundle_for_analysis

    written = datetime.now(UTC)
    first = narrative_written_at("00000000-0000-0000-0000-000000000001", written)
    archived_later = narrative_written_at(
        "00000000-0000-0000-0000-000000000002",
        written,
        archived_at=written + timedelta(days=1),
    )
    never_read = narrative_written_at("00000000-0000-0000-0000-000000000003", written)
    case = SimpleNamespace(source_revision=3, sources=[first, archived_later, never_read])
    result = analysis_citing(written + timedelta(minutes=5), first.id)

    bundle = case_source_bundle_for_analysis(case, result, [archived_later.id, first.id])

    assert bundle.revision == 2
    assert [source.source_id for source in bundle.sources] == [archived_later.id, first.id]


def test_a_report_reads_the_recorded_sources_whatever_the_claims_cite():
    from datetime import datetime, timedelta
    from types import SimpleNamespace

    from app.services.sources.case_source_bundle import case_source_bundle_for_analysis

    written = datetime.now(UTC)
    narrative = narrative_written_at("00000000-0000-0000-0000-00000000000a", written)
    case = SimpleNamespace(source_revision=1, sources=[narrative])
    result = analysis_citing(written + timedelta(minutes=5), "QA-01", "QA-02")

    bundle = case_source_bundle_for_analysis(case, result, [narrative.id])

    assert [source.source_id for source in bundle.sources] == [narrative.id]


def test_a_source_added_while_the_analysis_ran_is_not_in_its_report():
    from datetime import datetime, timedelta
    from types import SimpleNamespace

    from app.services.sources.case_source_bundle import case_source_bundle_for_analysis

    written = datetime.now(UTC)
    read = narrative_written_at("00000000-0000-0000-0000-00000000000b", written)
    raced = narrative_written_at("00000000-0000-0000-0000-00000000000c", written)
    case = SimpleNamespace(source_revision=1, sources=[read, raced])
    result = analysis_citing(written + timedelta(minutes=5), read.id)

    bundle = case_source_bundle_for_analysis(case, result, [read.id])

    assert [source.source_id for source in bundle.sources] == [read.id], (
        "a source whose timestamp is older than the analysis is still not one it read"
    )


def test_a_recorded_source_that_no_longer_exists_is_an_error():
    from datetime import datetime, timedelta
    from types import SimpleNamespace

    import pytest

    from app.services.sources.case_source_bundle import case_source_bundle_for_analysis

    written = datetime.now(UTC)
    case = SimpleNamespace(source_revision=1, sources=[])
    result = analysis_citing(written + timedelta(minutes=5))

    with pytest.raises(ValueError):
        case_source_bundle_for_analysis(case, result, ["00000000-0000-0000-0000-00000000000d"])
