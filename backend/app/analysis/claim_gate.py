from __future__ import annotations

import asyncio
import logging

from fastapi import status

from app.errors import CaseAnalysisFailure
from app.trace.claim_validation import admitted_claims, validate_claims
from app.trace.nli_model import NliUnavailable
from app.trace.summary import summary_pieces
from app.trace.trace import CaseGroundingReport, CaseProviderJudgement, CaseProviderReading

logger = logging.getLogger("app.case_analysis")


async def checked_claim_support(
    reading: CaseProviderReading, grounding: CaseGroundingReport
) -> tuple[CaseProviderReading, CaseGroundingReport]:
    try:
        claims, counts = await asyncio.to_thread(validate_claims, reading.claims)
    except NliUnavailable as error:
        logger.error("Claim support verifier unavailable: %s", error.reason)
        raise CaseAnalysisFailure(
            "case_claim_verifier_unavailable",
            f"Claim support verification is unavailable: {error.reason}",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error
    logger.info(
        "Claim support: %d supported, %d not supported, %d unassessed; %d calls in %.1f ms",
        counts.supported,
        counts.not_supported,
        counts.unassessed,
        counts.calls,
        counts.duration_ms,
    )
    return reading.model_copy(update={"claims": claims}), grounding.model_copy(
        update=counts.grounding()
    )


def admitted_reading(reading: CaseProviderReading) -> CaseProviderReading:
    return reading.model_copy(update={"claims": admitted_claims(reading.claims)})


def check_judgement_references(
    judgement: CaseProviderJudgement, reading: CaseProviderReading
) -> None:
    allowed = {claim.claim_id for claim in reading.claims}
    references = {
        claim_id for _, claim_ids in summary_pieces(judgement.summary) for claim_id in claim_ids
    }
    references.update(claim_id for gap in judgement.gaps for claim_id in gap.affected_claim_ids)
    references.update(
        claim_id
        for association in judgement.mitre_associations
        for claim_id in association.claim_ids
    )
    if references - allowed:
        raise CaseAnalysisFailure(
            "case_judgement_invalid_claim",
            "Judgement referenced a Claim that was not admitted after Source support verification",
            status.HTTP_502_BAD_GATEWAY,
        )
