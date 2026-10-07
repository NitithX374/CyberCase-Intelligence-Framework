from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from time import perf_counter

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.analysis.prompts import CASE_VIEWS_SYSTEM_PROMPT
from app.errors import CaseAnalysisFailure
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig
from app.trace.bind import item_support
from app.trace.claims import CaseAnalysisClaim
from app.trace.trace import (
    CaseImpactItem,
    CaseInvolvedParty,
    CaseTimelineItem,
    CaseViewExtraction,
    ProviderImpactItem,
    ProviderParty,
    ProviderTimelineItem,
)

logger = logging.getLogger("app.case_analysis")


class DerivedParty(ProviderParty):
    role: str | None = Field(min_length=1, max_length=500)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("name", "role")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return None if value is None else super().normalize_text(value)


class DerivedTimelineEvent(ProviderTimelineItem):
    time: str | None = Field(min_length=1, max_length=500)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("time", "event")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return None if value is None else super().normalize_text(value)


class DerivedImpact(ProviderImpactItem):
    claim_ids: list[str] = Field(min_length=1, max_length=64)


class DerivedCaseViewsReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parties: list[DerivedParty] = Field(max_length=64)
    timeline: list[DerivedTimelineEvent] = Field(max_length=64)
    impacts: list[DerivedImpact] = Field(max_length=64)


@dataclass
class DerivedCaseViews:
    parties: list[CaseInvolvedParty]
    timeline: list[CaseTimelineItem]
    impacts: list[CaseImpactItem]
    extraction: CaseViewExtraction


def view_request(claims: Sequence[CaseAnalysisClaim]) -> dict[str, object]:
    return {
        "claims": [{"claim_id": claim.claim_id, "text": claim.text} for claim in claims],
    }


def materialize_views(
    reply: DerivedCaseViewsReply, claims: Sequence[CaseAnalysisClaim]
) -> tuple[list[CaseInvolvedParty], list[CaseTimelineItem], list[CaseImpactItem], int]:
    claims_by_id = {claim.claim_id: claim for claim in claims}
    dropped = 0

    def rows(candidates, model, kind):
        nonlocal dropped
        accepted = []
        for index, candidate in enumerate(candidates):
            invalid = [claim_id for claim_id in candidate.claim_ids if claim_id not in claims_by_id]
            if invalid:
                dropped += 1
                logger.warning(
                    "Case views dropped %s item %d with unknown Claim IDs %s", kind, index, invalid
                )
                continue
            claim_ids = list(dict.fromkeys(candidate.claim_ids))
            accepted.append(
                model.model_validate(
                    {
                        **candidate.model_dump(),
                        "claim_ids": claim_ids,
                        "support": item_support(claim_ids, claims_by_id),
                    }
                )
            )
        return accepted

    parties = rows(reply.parties, CaseInvolvedParty, "party")
    timeline = rows(reply.timeline, CaseTimelineItem, "timeline")
    impacts = rows(reply.impacts, CaseImpactItem, "impact")
    return parties, timeline, impacts, dropped


async def derive_claim_views(
    claims: Sequence[CaseAnalysisClaim], *, config: AnalysisPipelineConfig
) -> DerivedCaseViews:
    started = perf_counter()
    view_config = config.for_views()
    extraction = CaseViewExtraction(
        method="llm",
        model=view_config.model,
        input_claim_ids=[claim.claim_id for claim in claims],
        excluded_claim_ids=[],
        duration_ms=0,
    )
    parties, timeline, impacts = [], [], []
    if not claims:
        extraction.status = "skipped"
    else:
        try:
            async with asyncio.timeout(view_config.timeout_seconds):
                reply = await request_stage(
                    config=view_config,
                    stage="case_views",
                    system=CASE_VIEWS_SYSTEM_PROMPT,
                    content=view_request(claims),
                    schema=DerivedCaseViewsReply,
                    temperature=0,
                )
            parties, timeline, impacts, extraction.items_dropped = materialize_views(reply, claims)
        except Exception as error:
            extraction.status = "failed"
            extraction.warning = (
                error.code if isinstance(error, CaseAnalysisFailure) else "case_views_failed"
            )
            logger.warning(
                "Case views unavailable: code=%s error_type=%s; Judgement continues independently",
                extraction.warning,
                type(error).__name__,
                exc_info=True,
            )
    extraction.duration_ms = (perf_counter() - started) * 1000
    return DerivedCaseViews(parties, timeline, impacts, extraction)
