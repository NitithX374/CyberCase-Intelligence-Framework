from app.services.case_analysis.claim_anchored.contracts import (
    BoundClaim,
    GeneratedSummary,
)
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.contracts import AnalysisTraceV3
from app.services.case_analysis.validation import validate_analysis_trace_v3


def assemble_trace(
    generated: GeneratedSummary,
    claims: tuple[BoundClaim, ...],
    evidence_sha256: str,
    source_ids: set[str],
) -> AnalysisTraceV3:
    known = {bound.claim.claim_id for bound in claims}
    referenced: set[str] = set()
    for unit in generated.units:
        if (
            len(unit.claim_ids) != len(set(unit.claim_ids))
            or not set(unit.claim_ids) <= known
        ):
            raise ClaimAnchoredFailure(
                "claim_generation_unknown_id", "Generated unit cites invalid claim IDs"
            )
        referenced.update(unit.claim_ids)
    if referenced != known:
        raise ClaimAnchoredFailure(
            "claim_generation_mapping_loss", "Generation omitted selected claims"
        )
    return validate_analysis_trace_v3(
        AnalysisTraceV3(
            analysis_mode="case_overview",
            summary="\n\n".join(unit.text for unit in generated.units),
            claims=[bound.claim.model_copy(deep=True) for bound in claims],
            evidence_sha256=evidence_sha256,
            retrieval_context_id=None,
        ),
        source_message_ids=source_ids,
        mitre_table=[],
    )
