from app.llm.schema import structured_output_schema
from app.trace.trace import CaseProviderAnalysis


def test_case_provider_analysis_schema_exposes_grounded_claim_roles() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    assert schema["properties"]["version"]["const"] == "case_analysis_trace_v1"
    for section in ("involved_parties", "timeline", "impacts", "claims", "gaps"):
        assert section in schema["properties"]
    assert set(schema["required"]) == set(schema["properties"])


def test_claims_are_written_before_the_fields_that_point_at_them() -> None:
    order = list(structured_output_schema(CaseProviderAnalysis)["properties"])
    assert order[:2] == ["version", "claims"]
    for pointing in ("summary", "involved_parties", "timeline", "impacts"):
        assert order.index(pointing) > order.index("claims")


def test_the_provider_is_not_asked_for_document_locators() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    citation = schema["$defs"]["CaseProviderCitation"]
    assert set(citation["properties"]) == {"source_id", "exact_quote"}
