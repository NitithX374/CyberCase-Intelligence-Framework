from app.schemas.reports import StructuredReport
from app.services.case_analysis.contracts import CaseProviderAnalysis
from app.services.llm.structuredOutput import (
    anthropic_json_schema,
    structured_output_schema,
)


def test_report_schema_is_provider_compatible() -> None:
    schema = anthropic_json_schema(StructuredReport)
    assert schema["properties"]["report_version"]["const"] == (
        "preliminary_analysis_report_v1"
    )


def test_case_provider_analysis_schema_exposes_grounded_claim_roles() -> None:
    for provider in ("anthropic", "openrouter"):
        schema = structured_output_schema(CaseProviderAnalysis, provider=provider)
        assert schema["properties"]["version"]["const"] == "case_analysis_trace_v1"
        assert "involved_parties" in schema["properties"]
        assert "timeline" in schema["properties"]
        assert "impacts" in schema["properties"]
        assert "claims" in schema["properties"]
        assert "gaps" in schema["properties"]
