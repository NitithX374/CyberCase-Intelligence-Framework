from uuid import UUID

import pytest

import app.models  # noqa: F401
from app.models.analysis_result import CaseAnalysisResult
from app.models.case import Case
from app.models.source import CaseSource
from app.sources.bundle import CaseSourceBundle, CaseSourceItem, case_source_bundle_for_analysis
from app.sources.evidence import evidence_units
from app.sources.ingestion.contracts import DocumentPage, ExtractionMethod, IngestedDocument
from app.sources.ingestion.provenance import bind_exact_page_spans
from app.sources.service import document_provenance
from app.trace.bind import resolve_case_trace
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseSourceCitation,
)
from app.trace.quotes import find_document_locator
from app.trace.trace import CaseAnalysisTrace, CaseProviderJudgement


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
                {"page_number": 1, "text": "first page"},
                {"page_number": 2, "text": "second page"},
            ]
        },
        content,
    )
    pages = provenance["pages"]
    assert pages[0]["start_offset"] == 0
    assert pages[0]["end_offset"] == pages[1]["start_offset"]
    assert "text_sha256" not in pages[0]
    doc = {"document_id": "d1", "filename": "case.pdf", "page_spans": pages}
    locator = find_document_locator(
        doc, content, [content.index("page\n\nsecond")], len("page\n\nsecond")
    )
    assert locator is not None
    assert locator[2] == (1, 2)

    repeated = "same\n\nsame"
    repeated_pages = bind_exact_page_spans(
        {
            "pages": [
                {"page_number": 1, "text": "same"},
                {"page_number": 2, "text": "same"},
            ]
        },
        repeated,
    )["pages"]
    doc_repeated = {"document_id": "d1", "filename": "case.pdf", "page_spans": repeated_pages}
    assert find_document_locator(doc_repeated, repeated, [0, 6], 4) is None
    assert find_document_locator(doc, "edited page\n\nsecond page", [13], 11) is None


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


def test_judgement_gaps_are_normalized_instead_of_rejected():
    parsed = CaseProviderJudgement.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "summary": "Files were encrypted [A-01].",
            "gaps": [
                gap_payload(
                    gap_key="incident\ntime",
                    topic="Incident\r\ntime",
                    affected_claim_ids=["A-01", "A-1"],
                    clarification_question="When did\nit happen?",
                ),
                gap_payload(gap_id="G-02", clarification_question="x" * 301),
            ],
        }
    )

    assert parsed.gaps[0].gap_key == "incident time"
    assert parsed.gaps[0].topic == "Incident time"
    assert parsed.gaps[0].affected_claim_ids == ["A-01"]
    assert parsed.gaps[0].clarification_question == "When did it happen?"
    assert parsed.gaps[1].clarification_question is None


def test_a_passage_spanning_more_pages_than_a_citation_holds_gets_no_page_locator():
    lines = [f"line {number}" for number in range(1, 11)]
    content = "\n\n".join(lines)
    pages = bind_exact_page_spans(
        {"pages": [{"page_number": number, "text": line} for number, line in enumerate(lines, 1)]},
        content,
    )["pages"]
    document = {"document_id": "d1", "filename": "report.pdf", "page_spans": pages}

    eight_pages = find_document_locator(document, content, [0], len("\n\n".join(lines[:8])))
    nine_pages = find_document_locator(document, content, [0], len("\n\n".join(lines[:9])))

    assert eight_pages[2] == tuple(range(1, 9))
    assert nine_pages is None


def test_a_blank_page_does_not_cost_the_pages_after_it_their_numbers():
    ingested = IngestedDocument(
        filename="scan.pdf",
        media_type="application/pdf",
        extraction_method=ExtractionMethod.DOCUMENT_RECOGNITION,
        pages=[
            DocumentPage(
                page_number=number, text=text, text_method="ocr", verification_status=status
            )
            for number, text, status in (
                (1, "first page", "machine_read"),
                (2, "", "needs_review"),
                (3, "third page", "machine_read"),
            )
        ],
        full_text="first page\n\nthird page",
    )
    source = CaseSourceItem(
        source_id="s1",
        source_kind="document",
        text=ingested.full_text,
        document_id="d1",
        filename="scan.pdf",
        provenance=document_provenance(ingested),
    )
    first_page, third_page = evidence_units(source)
    claims = [
        CaseAnalysisClaim(
            claim_id=claim_id,
            claim_type="reported",
            text="A page was quoted.",
            epistemic_status="reported",
            supporting_source_ids=["s1"],
            supporting_citations=[
                CaseSourceCitation(source_id="s1", evidence_unit_ids=[unit.unit_id])
            ],
        )
        for claim_id, unit in (("A-01", first_page), ("A-02", third_page))
    ]

    validated = resolve_case_trace(
        CaseAnalysisTrace(analysis_mode="case_overview", summary="Pages.", claims=claims),
        CaseSourceBundle(revision=1, sources=(source,)),
    )

    first, third = (claim.supporting_citations[0] for claim in validated.claims)
    assert (first.document_id, first.page_numbers) == ("d1", [1])
    assert (third.document_id, third.page_numbers) == ("d1", [3])


def test_gap_identifier_normalization():
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


def test_a_stored_claim_with_a_reasoning_summary_reads_without_it():
    claim = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "Valid factual claim text",
            "epistemic_status": "reported",
            "supporting_source_ids": ["s1"],
            "reasoning_summary": "Written by an earlier reader.",
        }
    )
    assert claim.text == "Valid factual claim text"
    assert "reasoning_summary" not in claim.model_dump()


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


def narrative(source_id: str) -> CaseSource:
    return CaseSource(
        id=UUID(source_id), source_kind="narrative", exact_text=f"Narrative {source_id}"
    )


def test_a_report_reads_exactly_the_sources_its_analysis_recorded_in_that_order():
    first = narrative("00000000-0000-0000-0000-000000000001")
    second = narrative("00000000-0000-0000-0000-000000000002")
    never_read = narrative("00000000-0000-0000-0000-000000000003")
    case = Case(source_revision=3, sources=[first, second, never_read])
    recorded = [str(second.id), str(first.id)]

    bundle = case_source_bundle_for_analysis(case, CaseAnalysisResult(source_revision=2), recorded)

    assert bundle.revision == 2
    assert [source.source_id for source in bundle.sources] == recorded


def test_a_recorded_source_that_no_longer_exists_is_an_error():
    case = Case(source_revision=1, sources=[])

    with pytest.raises(ValueError):
        case_source_bundle_for_analysis(
            case, CaseAnalysisResult(source_revision=1), ["00000000-0000-0000-0000-00000000000d"]
        )
