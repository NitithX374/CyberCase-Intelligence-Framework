import hashlib

import pytest

from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisGap,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
    CaseGeneratedUnit,
    CaseProviderAnalysis,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_analysis.evidenceQuoteResolver import (
    find_aligned_quote,
    resolve_document_locator,
)
from app.services.document_ingestion.provenance import bind_exact_page_spans


def _source(source_id: str, content: str) -> CaseAdmittedSource:
    return CaseAdmittedSource(
        source_id=source_id,
        revision=1,
        content=content,
        content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )


def _trace(claim: CaseAnalysisClaim, content: str) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=claim.text,
        claims=[claim],
        evidence_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )


@pytest.mark.parametrize("role", ["supporting", "contradicting"])
def test_case_validation_requires_exact_citation_for_each_declared_role(role):
    content = "The witness reported a blue vehicle."
    supporting_ids = ["s1"]
    supporting_citations = [
        CaseEvidenceCitation(
            source_id="s1",
            source_revision=1,
            exact_quote=content,
        )
    ] if role == "contradicting" else []
    contradicting_ids = ["s2"] if role == "contradicting" else []
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The witness reported a vehicle.",
        epistemic_status="reported",
        supporting_source_ids=supporting_ids,
        supporting_citations=supporting_citations,
        contradicting_source_ids=contradicting_ids,
    )
    trace = _trace(claim, content)
    with pytest.raises(CaseAnalysisFailure) as error:
        validate_case_trace(trace, (_source("s1", content), _source("s2", "A different account.")), [])
    assert error.value.code == "case_trace_role_citation_missing"


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
    assert pages[0]["text_sha256"] == hashlib.sha256(content[: pages[0]["end_offset"]].encode()).hexdigest()
    context = [{
        "source_id": "s1",
        "documents": [{
            "document_id": "d1",
            "filename": "case.pdf",
            "page_spans": pages,
        }],
    }]
    locator = resolve_document_locator("s1", "page\n\nsecond", content, context)
    assert locator["page_numbers"] == [1, 2]

    repeated = "same\n\nsame"
    repeated_pages = bind_exact_page_spans(
        {"pages": [{"page_number": 1, "merged_text": "same"}, {"page_number": 2, "merged_text": "same"}]},
        repeated,
    )["pages"]
    repeated_locator = resolve_document_locator(
        "s1",
        "same",
        repeated,
        [{"source_id": "s1", "documents": [{"document_id": "d1", "filename": "case.pdf", "page_spans": repeated_pages}]}],
    )
    assert repeated_locator["page_numbers"] == []
    edited_locator = resolve_document_locator("s1", "second page", "edited page\n\nsecond page", context)
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
        "answer": "Grounded answer text.",
        "summary": "Summary text.",
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


def test_case_generated_unit_and_gap_identifier_normalization():
    unit = CaseGeneratedUnit(
        text="A single generated summary unit.",
        claim_ids=("C1", "claim-2", "A-03"),
    )
    assert unit.claim_ids == ("A-01", "A-02", "A-03")

    gap = CaseAnalysisGap(
        gap_id="gap1",
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


def test_unwrap_exception_handles_nested_exception_group():
    from app.services.workflow.caseRunExecution import _unwrap_exception

    domain_error = CaseAnalysisFailure("test_code", "Test message")
    group = ExceptionGroup("outer", [ExceptionGroup("inner", [domain_error])])
    unwrapped = _unwrap_exception(group)
    assert unwrapped is domain_error
    assert unwrapped.code == "test_code"


def test_case_evidence_citation_normalizes_partial_document_locators():
    # Scenario from LLM: filename provided from header, but document_id null and pages empty
    citation_partial = CaseEvidenceCitation.model_validate({
        "source_id": "493c59ed-a9ea-48c3-a498-281d17e3030f",
        "source_revision": 1,
        "exact_quote": "ผู้ต้องหาหลบหนี",
        "filename": "ลำดับ01 รายงานการสอบสวน.pdf",
        "page_numbers": [],
    })
    assert citation_partial.document_id is None
    assert citation_partial.filename is None
    assert citation_partial.page_numbers == []

    # Complete locator is preserved
    citation_complete = CaseEvidenceCitation.model_validate({
        "source_id": "493c59ed-a9ea-48c3-a498-281d17e3030f",
        "source_revision": 1,
        "exact_quote": "ผู้ต้องหาหลบหนี",
        "document_id": "doc-01",
        "filename": "ลำดับ01 รายงานการสอบสวน.pdf",
        "page_numbers": [1, 2],
    })
    assert citation_complete.document_id == "doc-01"
    assert citation_complete.filename == "ลำดับ01 รายงานการสอบสวน.pdf"
    assert citation_complete.page_numbers == [1, 2]


def test_find_aligned_quote_handles_markdown_and_whitespace():
    content = "Header\n\n**Witness** Statement\n\nThe witness saw \"red car\"."
    assert find_aligned_quote(content, "Witness Statement") == "**Witness** Statement"
    assert find_aligned_quote(content, 'witness saw "red car"') == 'witness saw "red car"'
    assert find_aligned_quote(content, "witness saw “red car”") == 'witness saw "red car"'
    assert find_aligned_quote(content, "Nonexistent Statement") is None


def test_validate_case_trace_allows_same_page_multiple_occurrences():
    content = "report\n\npage one fact repeated\n\nfact repeated"
    provenance = bind_exact_page_spans({"pages": [{"page_number": 1, "merged_text": content}]}, content)
    context = [{"source_id": "s1", "documents": [{"document_id": "d1", "filename": "report.pdf", "page_spans": provenance["pages"]}]}]
    claim = CaseAnalysisClaim(
        claim_id="A-01", claim_type="reported", text="Fact was reported.", epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[CaseEvidenceCitation(source_id="s1", source_revision=1, exact_quote="fact repeated")],
    )
    validated = validate_case_trace(_trace(claim, content), (_source("s1", content),), context)
    assert validated.claims[0].supporting_citations[0].page_numbers == [1]
