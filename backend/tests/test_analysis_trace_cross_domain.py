import pytest

from app.services.case_analysis.contracts import AnalysisTraceV3
from app.services.case_analysis.validation import validate_analysis_trace_v3


DOMAIN_CASES = [
    ("theft", "The owner reported that a bicycle was missing."),
    ("fraud", "The customer reported an unauthorized invoice payment."),
    ("assault", "The complainant reported being struck outside a shop."),
    ("property", "The tenant reported damage to a boundary fence."),
    ("cybercrime", "The account holder reported unauthorized account access."),
]


@pytest.mark.parametrize(("domain", "claim_text"), DOMAIN_CASES)
def test_v3_contract_is_domain_neutral(domain: str, claim_text: str) -> None:
    source_message_id = f"{domain}-message"
    trace = AnalysisTraceV3.model_validate(
        {
            "version": "analysis_trace_v3",
            "validation_status": "validated",
            "analysis_mode": "case_overview",
            "summary": f"Evidence-bound overview for the {domain} case.",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": claim_text,
                    "epistemic_status": "reported",
                    "supporting_source_message_ids": [source_message_id],
                    "contradicting_source_message_ids": [],
                    "reasoning_summary": None,
                }
            ],
            "gaps": [],
            "mitre_associations": [],
            "evidence_sha256": "c" * 64,
            "retrieval_context_id": None,
        }
    )

    validated = validate_analysis_trace_v3(
        trace,
        source_message_ids={source_message_id},
    )

    assert validated.mitre_associations == []
    assert validated.claims[0].supporting_source_message_ids == [source_message_id]
