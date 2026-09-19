from app.schemas.reports import PRELIMINARY_REPORT_SECTION_IDS, ReportClaim, StructuredReport
from app.services.case_analysis.contracts import CaseProviderAnalysis
from app.services.llm.structured_output import structured_output_schema


def test_report_schema_is_provider_compatible() -> None:
    schema = structured_output_schema(StructuredReport)
    assert schema["properties"]["report_version"]["const"] == ("preliminary_analysis_report_v1")


def test_report_contract_is_case_evidence_bound() -> None:
    assert "case_evidence" in PRELIMINARY_REPORT_SECTION_IDS
    assert "indicators_found" not in PRELIMINARY_REPORT_SECTION_IDS
    assert "source_message_ids" not in ReportClaim.model_fields


def test_case_provider_analysis_schema_exposes_grounded_claim_roles() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    assert schema["properties"]["version"]["const"] == "case_analysis_trace_v1"
    for section in ("involved_parties", "timeline", "impacts", "claims", "gaps"):
        assert section in schema["properties"]
    # Every property is required, so the model cannot quietly omit a section.
    assert set(schema["required"]) == set(schema["properties"])
