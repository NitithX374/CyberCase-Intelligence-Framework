from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

from fastapi import status
from pydantic import ValidationError

from app.analysis.prompts import case_assessment_prompt
from app.analysis.stream import announce
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.analysis.technical_context.gate import mitre_gate
from app.analysis.technical_context.rag_client import request_rag
from app.analysis.technical_context.retrieve import (
    CaseMitreAugmentation,
    run_case_mitre_augmentation,
)
from app.analysis.write import provider_source_payload, write_trace
from app.errors import CaseAnalysisFailure
from app.followup.clarification import (
    FollowupDecision,
    Proceed,
    decide_followup,
    rounds_are_spent,
)
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig, configured_pipeline
from app.sources.bundle import CaseSourceBundle
from app.trace.bind import bound_references, resolve_case_trace
from app.trace.claims import CaseAssessmentTrace, CaseFollowupExchange, followup_payload
from app.trace.trace import CaseAnalysisTrace

logger = logging.getLogger("app.case_analysis")


@dataclass(frozen=True)
class AnalysisInput:
    sources: CaseSourceBundle
    response_language: str = "english"
    followup_history: tuple[CaseFollowupExchange, ...] = ()
    reused_context: CaseRagContextPayload | None = None
    asked_gap_keys: frozenset[str] = frozenset()
    rounds_spent: int = 1
    max_rounds: int = 3
    gaps_per_round: int = 3


@dataclass(frozen=True)
class AnalysisArtifacts:
    trace: CaseAnalysisTrace | None = None
    augmentation: CaseMitreAugmentation | None = None

    @property
    def technical_context(self) -> CaseRagContextPayload | None:
        if self.augmentation is None or self.augmentation.status != "retrieved_from_rag":
            return None
        return self.augmentation.context


@dataclass(frozen=True)
class AnalysisAdvance:
    assessment: CaseAssessmentTrace | None
    decision: FollowupDecision
    artifacts: AnalysisArtifacts | None = None


async def advance_case(data: AnalysisInput) -> AnalysisAdvance:
    assessment = (
        None if rounds_are_spent(data.rounds_spent, data.max_rounds) else await assess_gaps(data)
    )
    decision = decide_followup(
        gaps=() if assessment is None else assessment.gaps,
        asked_gap_keys=data.asked_gap_keys,
        asked_this_round=0,
        rounds_spent=data.rounds_spent,
        max_rounds=data.max_rounds,
        gaps_per_round=data.gaps_per_round,
    )
    if not isinstance(decision, Proceed):
        return AnalysisAdvance(assessment=assessment, decision=decision)

    artifacts = AnalysisArtifacts()
    artifacts = await retrieve_technical_context(data, artifacts)
    artifacts = await write_analysis(data, artifacts)
    artifacts = await bind_to_case(data, artifacts)
    return AnalysisAdvance(
        assessment=assessment,
        decision=decision,
        artifacts=artifacts,
    )


async def assess_case(
    *,
    source_bundle: CaseSourceBundle,
    followup_history: Sequence[CaseFollowupExchange],
    response_language: str,
    config: AnalysisPipelineConfig,
) -> CaseAssessmentTrace:
    return await request_stage(
        config=config,
        stage="assess",
        system=case_assessment_prompt(),
        content={
            "response_language": response_language,
            "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
            "followup_history": followup_payload(followup_history),
        },
        schema=CaseAssessmentTrace,
    )


async def assess_gaps(
    data: AnalysisInput,
    *,
    request: Callable = assess_case,
    config: Callable[[], AnalysisPipelineConfig] = configured_pipeline,
) -> CaseAssessmentTrace:
    announce("assess")
    return await request(
        source_bundle=data.sources,
        followup_history=data.followup_history,
        response_language=data.response_language,
        config=config(),
    )


async def retrieve_technical_context(
    data: AnalysisInput,
    so_far: AnalysisArtifacts,
    *,
    gate: Callable = mitre_gate,
    rag: Callable = request_rag,
) -> AnalysisArtifacts:
    augmentation = await run_case_mitre_augmentation(
        source_bundle=data.sources,
        applicability_gate=gate,
        rag_request=rag,
        reused_context=data.reused_context,
        followup_history=data.followup_history,
    )
    return replace(so_far, augmentation=augmentation)


async def write_analysis(
    data: AnalysisInput,
    so_far: AnalysisArtifacts,
    *,
    request: Callable = write_trace,
    config: Callable[[], AnalysisPipelineConfig] = configured_pipeline,
) -> AnalysisArtifacts:
    trace = await request(
        sources=data.sources,
        language=data.response_language,
        followup_history=data.followup_history,
        technical_context=so_far.technical_context,
        config=config(),
    )
    return replace(so_far, trace=trace)


async def bind_to_case(data: AnalysisInput, so_far: AnalysisArtifacts) -> AnalysisArtifacts:
    if so_far.trace.grounding is None:
        announce("bind")
    try:
        trace = await asyncio.to_thread(bound_trace, data, so_far, so_far.trace)
    except ValidationError as error:
        logger.exception("Binding the analysis to the case built an invalid trace")
        raise CaseAnalysisFailure(
            "case_bind_invalid",
            "The analysis could not be bound to the case sources",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error
    return replace(so_far, trace=trace)


def bound_trace(
    data: AnalysisInput, so_far: AnalysisArtifacts, trace: CaseAnalysisTrace
) -> CaseAnalysisTrace:
    context = so_far.technical_context
    mitre_table = list(context.mitre_table) if context is not None else []
    if trace.grounding is not None:
        return bound_references(trace, mitre_table)
    return resolve_case_trace(
        trace,
        data.sources,
        mitre_table=mitre_table,
        followup_history=data.followup_history,
    )


__all__ = [
    "AnalysisAdvance",
    "AnalysisArtifacts",
    "AnalysisInput",
    "advance_case",
    "assess_case",
    "assess_gaps",
    "bind_to_case",
    "bound_trace",
    "retrieve_technical_context",
    "write_analysis",
]
