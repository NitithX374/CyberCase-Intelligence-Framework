from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence

from fastapi import status
from pydantic import ValidationError

from app.analysis.progress import announce
from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_READING_JSON_PROMPT
from app.analysis.reading_sources import ReadingSources
from app.analysis.source_payload import provider_source_payload
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.analysis.views import DerivedCaseViews, derive_claim_views
from app.errors import CaseAnalysisFailure
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle
from app.trace.bind import bound_claims, followup_registry_items
from app.trace.claims import (
    CLAIM_FIELDS_HIDDEN_FROM_JUDGEMENT,
    CaseAnalysisClaim,
    CaseFollowupExchange,
    followup_payload,
)
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseGroundingReport,
    CaseProviderJudgement,
    CaseProviderReading,
    CaseProviderReadingReply,
)

logger = logging.getLogger("app.case_analysis")


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
        content=reading_request(
            sources, language, followup_history, reading_sources=reading_sources
        ),
        schema=CaseProviderReadingReply,
        grammar=False,
    )
    announce("bind")
    reading, grounding = await checked_reading(
        reading_from(reply, reading_sources=reading_sources), sources, followup_history
    )
    announce("views")
    view_task = asyncio.create_task(derive_claim_views(reading.claims, config=config))
    try:
        announce("judge")
        judgement = await request_stage(
            config=config,
            stage="case_judgement",
            system=CASE_JUDGEMENT_SYSTEM_PROMPT,
            content=judgement_request(reading, language, followup_history, technical_context),
            schema=CaseProviderJudgement,
        )
        views = await view_task
    except BaseException:
        view_task.cancel()
        await asyncio.gather(view_task, return_exceptions=True)
        raise
    return joined_trace(reading, judgement, technical_context, grounding, views=views)


async def checked_reading(
    reading: CaseProviderReading,
    sources: CaseSourceBundle,
    followup_history: Sequence[CaseFollowupExchange],
) -> tuple[CaseProviderReading, CaseGroundingReport]:
    try:
        return await asyncio.to_thread(bound_claims, reading, sources, followup_history)
    except ValidationError as error:
        logger.exception("Checking the reading against the case built an invalid trace")
        raise CaseAnalysisFailure(
            "case_bind_invalid",
            "The analysis could not be bound to the case sources",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error


def reading_from(
    reply: CaseProviderReadingReply, *, reading_sources: ReadingSources | None = None
) -> CaseProviderReading:
    if reading_sources is not None:
        reply = reading_sources.canonical_reply(reply)
    return CaseProviderReading(
        version=reply.version,
        claims=[
            CaseAnalysisClaim.model_validate(
                {
                    **claim.model_dump(),
                    "supporting_source_ids": list(
                        dict.fromkeys(citation.source_id for citation in claim.supporting_citations)
                    ),
                    "contradicting_source_ids": list(
                        dict.fromkeys(
                            citation.source_id for citation in claim.contradicting_citations
                        )
                    ),
                }
            )
            for claim in reply.claims
        ],
    )


def reading_request(
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
    *,
    reading_sources: ReadingSources | None = None,
) -> dict[str, object]:
    if reading_sources is None:
        reading_sources = ReadingSources(
            (*sources.sources, *followup_registry_items(followup_history))
        )
    return {
        "response_language": language,
        "source_revision": sources.revision,
        "case_sources": list(reading_sources.payloads),
        "followup_history": followup_payload(followup_history),
    }


def write_request(
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
    technical_context: CaseRagContextPayload | None,
) -> dict[str, object]:
    return {
        "response_language": language,
        "case_sources": [provider_source_payload(source) for source in sources.sources],
        "followup_history": followup_payload(followup_history),
        "technical_context": technical_context_payload(technical_context),
    }


def judgement_request(
    reading: CaseProviderReading,
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
    technical_context: CaseRagContextPayload | None,
) -> dict[str, object]:
    return {
        "response_language": language,
        "followup_history": followup_payload(followup_history),
        "technical_context": technical_context_payload(technical_context),
        "reading": reading_payload(reading),
    }


def technical_context_payload(
    technical_context: CaseRagContextPayload | None,
) -> dict[str, object] | None:
    if technical_context is None:
        return None
    return {
        "context": technical_context.context,
        "mitre_table": list(technical_context.mitre_table),
    }


def reading_payload(reading: CaseProviderReading) -> dict[str, object]:
    return {
        "claims": [
            claim.model_dump(mode="json", exclude=CLAIM_FIELDS_HIDDEN_FROM_JUDGEMENT)
            for claim in reading.claims
        ],
    }


def joined_trace(
    reading: CaseProviderReading,
    judgement: CaseProviderJudgement,
    technical_context: CaseRagContextPayload | None = None,
    grounding: CaseGroundingReport | None = None,
    *,
    views: DerivedCaseViews | None = None,
) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=judgement.summary,
        claims=reading.claims,
        involved_parties=views.parties if views is not None else [],
        timeline=views.timeline if views is not None else [],
        impacts=views.impacts if views is not None else [],
        view_extraction=views.extraction if views is not None else None,
        gaps=judgement.gaps,
        mitre_associations=judgement.mitre_associations,
        retrieval_context_id=(
            technical_context.retrieval_context_id if technical_context is not None else None
        ),
        grounding=grounding,
    )


__all__ = [
    "checked_reading",
    "joined_trace",
    "judgement_request",
    "provider_source_payload",
    "reading_from",
    "reading_payload",
    "reading_request",
    "write_request",
    "write_trace",
]
