from __future__ import annotations

import asyncio
import logging
import threading

from fastapi import status

from app.errors import CaseAnalysisFailure
from app.trace.claim_validation import unverified_claims, usable_claims, validate_claims
from app.trace.nli_model import NliUnavailable
from app.trace.summary import summary_pieces
from app.trace.trace import CaseGroundingReport, CaseProviderJudgement, CaseProviderReading

logger = logging.getLogger("app.case_analysis")


async def checked_claim_support(
    reading: CaseProviderReading, grounding: CaseGroundingReport
) -> tuple[CaseProviderReading, CaseGroundingReport]:
    stop = threading.Event()
    try:
        claims, counts = await asyncio.to_thread(validate_claims, reading.claims, stop=stop)
    except asyncio.CancelledError:
        stop.set()
        raise
    except NliUnavailable as error:
        logger.error("Claim support verifier unavailable, claims not assessed: %s", error.reason)
        claims, counts = unverified_claims(reading.claims)
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


def usable_reading(reading: CaseProviderReading) -> CaseProviderReading:
    return reading.model_copy(update={"claims": usable_claims(reading.claims)})


def check_judgement_references(
    judgement: CaseProviderJudgement, reading: CaseProviderReading
) -> None:
    allowed = {claim.claim_id for claim in reading.claims}
    references = {
        claim_id for _, claim_ids in summary_pieces(judgement.summary) for claim_id in claim_ids
    }
    references.update(claim_id for gap in judgement.gaps for claim_id in gap.affected_claim_ids)
    if references - allowed:
        raise CaseAnalysisFailure(
            "case_judgement_invalid_claim",
            "Judgement referenced a Claim that was not given to it",
            status.HTTP_502_BAD_GATEWAY,
        )
