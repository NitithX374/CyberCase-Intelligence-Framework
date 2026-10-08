from app.analysis.write import judgement_request
from app.trace.claims import CaseAnalysisClaim, CaseClaimGrounding, CaseSourceCitation
from app.trace.trace import CaseAnalysisTrace, CaseProviderReading


def citation(source_id: str, text: str) -> CaseSourceCitation:
    return CaseSourceCitation(
        source_id=source_id,
        evidence_unit_ids=[f"{source_id}:U001-0123456789abcdef"],
        exact_quote=text,
        pointer_state="direct",
        start=0,
        end=len(text),
        document_id=f"document-{source_id}",
        filename=f"{source_id}.pdf",
        page_numbers=[2],
    )


def reading() -> CaseProviderReading:
    return CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="Alice reported losing 25,000 baht.",
                epistemic_status="reported",
                supporting_source_ids=["S1", "S2"],
                supporting_citations=[
                    citation("S1", "Alice reported the incident."),
                    citation("S2", "The reported loss was 25,000 baht."),
                ],
                contradicting_source_ids=["S3"],
                contradicting_citations=[citation("S3", "The loss was disputed.")],
                reasoning_summary="Private verifier explanation.",
            )
        ],
    )


def test_judgement_keeps_claim_ids_and_source_text_without_source_locators():
    original = reading()
    payload = judgement_request(original, "en", (), None)

    assert payload["reading"]["claims"] == [
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "Alice reported losing 25,000 baht.",
            "epistemic_status": "reported",
            "supporting_citations": [
                {"exact_quote": "Alice reported the incident."},
                {"exact_quote": "The reported loss was 25,000 baht."},
            ],
            "contradicting_citations": [{"exact_quote": "The loss was disputed."}],
        }
    ]


def test_judgement_serialization_preserves_original_grounding_and_saved_trace():
    original = reading()
    claim = original.claims[0]
    claim.semantic_grounding = CaseClaimGrounding(
        verdict="supported",
        reason="lr_supported",
        threshold=0.5,
        selected_evidence_unit_ids=[claim.supporting_citations[0].evidence_unit_ids[0]],
    )
    before = original.model_dump(mode="json")

    judgement_request(original, "en", (), None)

    assert original.model_dump(mode="json") == before
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Alice reported losing 25,000 baht [A-01].",
        claims=original.claims,
    )
    [saved] = trace.model_dump(mode="json")["claims"]
    assert saved["supporting_source_ids"] == ["S1", "S2"]
    assert saved["contradicting_source_ids"] == ["S3"]
    assert saved["supporting_citations"] == before["claims"][0]["supporting_citations"]
    assert saved["contradicting_citations"] == before["claims"][0]["contradicting_citations"]
    assert saved["semantic_grounding"] == before["claims"][0]["semantic_grounding"]
