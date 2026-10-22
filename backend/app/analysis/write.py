from __future__ import annotations

import asyncio
import logging
import math
from collections.abc import Sequence

from fastapi import status
from pydantic import ValidationError

from app.analysis.claim_gate import check_judgement_references, checked_claim_support
from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_READING_JSON_PROMPT
from app.analysis.reading_sources import ReadingSources
from app.analysis.stream import announce
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.analysis.views import DerivedCaseViews, derive_claim_views
from app.errors import CaseAnalysisFailure
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle
from app.trace.bind import followup_registry_items
from app.trace.claim_validation import usable_claims
from app.trace.claims import (
    CLAIM_FIELDS_FOR_JUDGEMENT,
    CaseAnalysisClaim,
    CaseFollowupExchange,
    followup_payload,
)
from app.trace.trace import CaseAnalysisTrace, CaseProviderJudgement, CaseProviderReadingReply

logger = logging.getLogger("app.case_analysis")

SUMMARY_CLAIMS_PER_SENTENCE = 3
SUMMARY_MIN_SENTENCES = 2
SUMMARY_MAX_SENTENCES = 8


async def write_trace(
    *,
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange] = (),
    technical_context: CaseRagContextPayload | None = None,
    config: AnalysisPipelineConfig,
) -> CaseAnalysisTrace:
    announce("read")
    reading_sources = await asyncio.to_thread(
        ReadingSources, (*sources.sources, *followup_registry_items(followup_history))
    )
    reply = await request_stage(
        config=config.for_reading(),
        stage="case_reading",
        system=CASE_READING_JSON_PROMPT,
        content=reading_request(reading_sources, language, followup_history),
        schema=CaseProviderReadingReply,
    )
    announce("bind")
    claims = await checked_reading(reply, reading_sources)
    judged = usable_claims(claims)
    if not judged:
        announce("verify")
        claims = await checked_claim_support(claims)
        judgement = CaseProviderJudgement(
            summary=(
                "ไม่มีข้อค้นพบที่ผ่านการตรวจการอ้างอิง Source จึงยังไม่สร้างบทสรุปคดี"
                if language == "thai"
                else "No finding passed the Source citation checks; no case summary was generated."
            ),
        )
        return joined_trace(claims, judgement, technical_context)
    announce("verify")
    verify_task = asyncio.create_task(checked_claim_support(claims))
    announce("views")
    view_task = asyncio.create_task(derive_claim_views(judged, config=config))
    announce("judge")
    judge_task = asyncio.create_task(
        request_stage(
            config=config.for_judgement(),
            stage="case_judgement",
            system=CASE_JUDGEMENT_SYSTEM_PROMPT,
            content=judgement_request(judged, language, followup_history),
            schema=CaseProviderJudgement,
        )
    )
    tasks = (judge_task, view_task, verify_task)
    try:
        judgement, views, claims = await asyncio.gather(*tasks)
        check_judgement_references(judgement, judged)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    judged_ids = {claim.claim_id for claim in judged}
    views.extraction = views.extraction.model_copy(
        update={
            "excluded_claim_ids": [
                claim.claim_id for claim in claims if claim.claim_id not in judged_ids
            ]
        }
    )
    return joined_trace(claims, judgement, technical_context, views=views)


async def checked_reading(
    reply: CaseProviderReadingReply, reading_sources: ReadingSources
) -> list[CaseAnalysisClaim]:
    try:
        return await asyncio.to_thread(reading_sources.bound_claims, reply)
    except ValidationError as error:
        logger.exception("Checking the reading against the case built an invalid trace")
        raise CaseAnalysisFailure(
            "case_bind_invalid",
            "The analysis could not be bound to the case sources",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error


def reading_request(
    reading_sources: ReadingSources,
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
) -> dict[str, object]:
    return {
        "response_language": language,
        "case_sources": list(reading_sources.payloads),
        "followup_history": followup_payload(followup_history),
    }


def summary_sentence_limit(claim_count: int) -> int:
    return max(
        SUMMARY_MIN_SENTENCES,
        min(SUMMARY_MAX_SENTENCES, math.ceil(claim_count / SUMMARY_CLAIMS_PER_SENTENCE)),
    )


def judgement_request(
    claims: list[CaseAnalysisClaim],
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
) -> dict[str, object]:
    return {
        "response_language": language,
        "summary_sentence_limit": summary_sentence_limit(len(claims)),
        "followup_history": [
            {"qa_id": item.qa_id, "gap_key": item.gap_key, "answered": True}
            for item in followup_history
            if item.is_answered
        ],
        "reading": reading_payload(claims),
    }


def reading_payload(claims: list[CaseAnalysisClaim]) -> dict[str, object]:
    return {
        "claims": [
            claim.model_dump(mode="json", include=CLAIM_FIELDS_FOR_JUDGEMENT) for claim in claims
        ],
    }


def joined_trace(
    claims: list[CaseAnalysisClaim],
    judgement: CaseProviderJudgement,
    technical_context: CaseRagContextPayload | None = None,
    *,
    views: DerivedCaseViews | None = None,
) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=judgement.summary,
        claims=claims,
        involved_parties=views.parties if views is not None else [],
        timeline=views.timeline if views is not None else [],
        impacts=views.impacts if views is not None else [],
        view_extraction=views.extraction if views is not None else None,
        gaps=judgement.gaps,
        retrieval_context_id=(
            technical_context.retrieval_context_id if technical_context is not None else None
        ),
    )


__all__ = [
    "checked_reading",
    "joined_trace",
    "judgement_request",
    "reading_payload",
    "reading_request",
    "summary_sentence_limit",
    "write_trace",
]
