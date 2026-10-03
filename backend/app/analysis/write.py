from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence

from fastapi import status
from pydantic import ValidationError

from app.analysis.progress import announce
from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_READING_JSON_PROMPT
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.errors import CaseAnalysisFailure
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import bound_claims
from app.trace.claims import CaseAnalysisClaim, CaseFollowupExchange, followup_payload
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
    reply = await request_stage(
        config=config,
        stage="case_reading",
        system=CASE_READING_JSON_PROMPT,
        content=reading_request(sources, language, followup_history),
        schema=CaseProviderReadingReply,
        grammar=False,
    )
    announce("bind")
    reading, grounding = await checked_reading(reading_from(reply), sources, followup_history)
    announce("judge")
    judgement = await request_stage(
        config=config,
        stage="case_judgement",
        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
        content={
            **write_request(sources, language, followup_history, technical_context),
            "reading": reading_payload(reading),
        },
        schema=CaseProviderJudgement,
    )
    return joined_trace(reading, judgement, technical_context, grounding)


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


def reading_from(reply: CaseProviderReadingReply) -> CaseProviderReading:
    return CaseProviderReading.model_validate(
        {
            **reply.model_dump(),
            "claims": [
                CaseAnalysisClaim.model_validate(claim.model_dump()).model_dump()
                for claim in reply.claims
            ],
        }
    )


def reading_request(
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
) -> dict[str, object]:
    return {
        "response_language": language,
        "case_sources": [provider_source_payload(source) for source in sources.sources],
        "followup_history": followup_payload(followup_history),
    }


def write_request(
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange],
    technical_context: CaseRagContextPayload | None,
) -> dict[str, object]:
    return {
        **reading_request(sources, language, followup_history),
        "technical_context": (
            {
                "context": technical_context.context,
                "mitre_table": list(technical_context.mitre_table),
            }
            if technical_context is not None
            else None
        ),
    }


def provider_source_payload(source: CaseSourceItem) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_id": source.source_id,
        "source_kind": source.source_kind,
        "text": source.text,
    }
    if source.source_kind == "document" or source.document_id or source.filename:
        document: dict[str, object] = {
            "document_id": source.document_id,
            "filename": source.filename,
        }
        for quality_key in ("extraction_method", "verification_status", "warnings"):
            if quality_key in source.provenance:
                document[quality_key] = source.provenance[quality_key]
        payload["document"] = document
    return payload


def reading_payload(reading: CaseProviderReading) -> dict[str, object]:
    return {
        "claims": [
            claim.model_dump(mode="json", exclude={"unverified_citations"})
            for claim in reading.claims
        ],
        "involved_parties": [party.model_dump(mode="json") for party in reading.involved_parties],
        "timeline": [item.model_dump(mode="json") for item in reading.timeline],
        "impacts": [impact.model_dump(mode="json") for impact in reading.impacts],
    }


def joined_trace(
    reading: CaseProviderReading,
    judgement: CaseProviderJudgement,
    technical_context: CaseRagContextPayload | None = None,
    grounding: CaseGroundingReport | None = None,
) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=judgement.summary,
        involved_parties=reading.involved_parties,
        timeline=reading.timeline,
        claims=reading.claims,
        impacts=reading.impacts,
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
    "provider_source_payload",
    "reading_from",
    "reading_payload",
    "reading_request",
    "write_request",
    "write_trace",
]
