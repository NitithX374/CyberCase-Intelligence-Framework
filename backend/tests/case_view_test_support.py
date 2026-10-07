from app.analysis.view_schema import DerivedCaseViewsReply
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation


def claim(
    text="Alice transferred $500 to Company A on 12 May 2026.", *, claim_id="A-01", bound=True
):
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        epistemic_status="reported" if bound else "not_confirmed",
        text=text,
        supporting_source_ids=["S1"] if bound else [],
        supporting_citations=[CaseSourceCitation(source_id="S1", exact_quote=text)]
        if bound
        else [],
    )


def reply(**changes):
    return DerivedCaseViewsReply.model_validate(
        {"parties": [], "timeline": [], "impacts": [], **changes}
    )


def transfer_views():
    return reply(
        parties=[
            {"name": "Alice", "role": None, "claim_ids": ["A-01"]},
            {"name": "Company A", "role": None, "claim_ids": ["A-01"]},
        ],
        timeline=[
            {
                "time": "12 May 2026",
                "event": "Alice transferred $500 to Company A.",
                "claim_ids": ["A-01"],
            }
        ],
    )
