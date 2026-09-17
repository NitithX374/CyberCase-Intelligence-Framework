from app.schemas.reports import PRELIMINARY_REPORT_SECTION_IDS, ReportClaim, StructuredReport
from app.services.case_analysis.contracts import CaseProviderAnalysis
from app.services.llm.structured_output import (
    anthropic_json_schema,
    structured_output_schema,
)


def test_report_schema_is_provider_compatible() -> None:
    schema = anthropic_json_schema(StructuredReport)
    assert schema["properties"]["report_version"]["type"] == "string"


def test_report_contract_is_case_evidence_bound() -> None:
    assert "case_evidence" in PRELIMINARY_REPORT_SECTION_IDS
    assert "indicators_found" not in PRELIMINARY_REPORT_SECTION_IDS
    assert "source_message_ids" not in ReportClaim.model_fields


def test_case_provider_analysis_schema_exposes_grounded_claim_roles() -> None:
    for provider in ("anthropic", "openrouter"):
        schema = structured_output_schema(CaseProviderAnalysis, provider=provider)
        assert schema["properties"]["version"]["const"] == "case_analysis_trace_v1"
        assert "involved_parties" in schema["properties"]
        assert "timeline" in schema["properties"]
        assert "impacts" in schema["properties"]
        assert "claims" in schema["properties"]
        assert "gaps" in schema["properties"]
