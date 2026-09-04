from app.schemas.reports import StructuredReport
from app.services.case_analysis.contracts import (
    ProviderCaseAnalysis,
    ProviderCaseAnalysisV3,
)
from app.services.llm.structured_output import (
    anthropic_json_schema,
    structured_output_schema,
)


def test_report_schema_is_provider_compatible() -> None:
    schema = anthropic_json_schema(StructuredReport)
    assert schema["properties"]["report_version"]["const"] == (
        "preliminary_analysis_report_v1"
    )


def test_analysis_trace_v2_schema_exposes_source_message_references() -> None:
    schema = anthropic_json_schema(ProviderCaseAnalysis)
    claim = schema["$defs"]["AnalysisClaim"]["properties"]
    assert "source_message_ids" in claim
    assert "entity_ids" not in claim


def test_analysis_trace_v3_provider_schema_exposes_grounded_claim_roles() -> None:
    for provider in ("anthropic", "openrouter"):
        schema = structured_output_schema(ProviderCaseAnalysisV3, provider=provider)
        claim_reference = schema["properties"]["claims"]["items"]["$ref"]
        claim_name = claim_reference.rsplit("/", 1)[-1]
        claim = schema["$defs"][claim_name]["properties"]
        assert schema["properties"]["version"]["const"] == "analysis_trace_v3"
        assert claim["claim_id"]["enum"] == [f"A-{index:02d}" for index in range(1, 65)]
        assert "supporting_source_message_ids" in claim
        assert "contradicting_source_message_ids" in claim
        assert "reasoning_summary" in claim
        assert "gaps" not in schema["properties"]
