from app.services.analysis.contracts import CaseProviderAnalysis
from app.services.llm.structured_output import structured_output_schema


def test_case_provider_analysis_schema_exposes_grounded_claim_roles() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    assert schema["properties"]["version"]["const"] == "case_analysis_trace_v1"
    for section in ("involved_parties", "timeline", "impacts", "claims", "gaps"):
        assert section in schema["properties"]
    assert set(schema["required"]) == set(schema["properties"])


def test_the_provider_is_not_asked_for_document_locators() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    citation = schema["$defs"]["CaseProviderCitation"]
    assert set(citation["properties"]) == {"source_id", "exact_quote"}
