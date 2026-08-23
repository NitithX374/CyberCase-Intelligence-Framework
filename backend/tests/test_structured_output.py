from app.schemas.reports import StructuredReport
from app.services.case_analysis.contracts import ProviderCaseAnalysis
from app.services.llm.structured_output import anthropic_json_schema


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
