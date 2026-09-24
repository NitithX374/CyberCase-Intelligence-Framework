from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace

from app.services.analysis.clarification import (
    FollowupDecision,
    Proceed,
    decide_followup,
)
from app.services.analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseAssessmentTrace,
    CaseFollowupExchange,
    CaseProviderReading,
)
from app.services.analysis.mitre_gate import mitre_gate
from app.services.analysis.settings import AnalysisPipelineConfig, configured_pipeline
from app.services.analysis.steps.assess import assess_case
from app.services.analysis.steps.bind import resolve_case_trace
from app.services.analysis.steps.technical_context import (
    CaseRagContextPayload,
    run_case_mitre_augmentation,
)
from app.services.analysis.steps.write import request_case_analysis
from app.services.clients.rag_client import request_rag
from app.services.sources.case_source_bundle import CaseSourceBundle


@dataclass(frozen=True)
class AnalysisInput:
    sources: CaseSourceBundle
    response_language: str = "english"
    mode: str = "case_overview"
    question: str | None = None
    followup_history: tuple[CaseFollowupExchange, ...] = ()
    reused_context: CaseRagContextPayload | None = None
    asked_gap_keys: frozenset[str] = frozenset()
    rounds_spent: int = 1
    max_rounds: int = 3
    gaps_per_round: int = 3


@dataclass(frozen=True)
class AnalysisArtifacts:
    answer: str = ""
    trace: CaseAnalysisTrace | None = None
    reading: CaseProviderReading | None = None
    technical_context: dict[str, object] | None = None
    retrieval_context_id: str | None = None
    receipt: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisAdvance:
    assessment: CaseAssessmentTrace
    decision: FollowupDecision
    artifacts: AnalysisArtifacts | None = None


async def advance_case(data: AnalysisInput) -> AnalysisAdvance:
    assessment = await assess_gaps(data)
    decision = decide_followup(
        gaps=assessment.gaps,
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


async def assess_gaps(
    data: AnalysisInput,
    *,
    request: Callable = assess_case,
    config: Callable[[], AnalysisPipelineConfig] = configured_pipeline,
) -> CaseAssessmentTrace:
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
    receipt = {**so_far.receipt, "technical_augmentation": augmentation.to_metadata()}
    if augmentation.status != "retrieved_from_rag":
        return replace(so_far, receipt=receipt)
    return replace(
        so_far,
        technical_context={
            "context": augmentation.context.context,
            "mitre_table": list(augmentation.context.mitre_table),
        },
        retrieval_context_id=augmentation.retrieval_context_id,
        receipt=receipt,
    )


async def write_analysis(
    data: AnalysisInput,
    so_far: AnalysisArtifacts,
    *,
    request: Callable = request_case_analysis,
    config: Callable[[], AnalysisPipelineConfig] = configured_pipeline,
) -> AnalysisArtifacts:
    output = await request(
        source_bundle=data.sources,
        pipeline_config=config().model_dump(mode="json"),
        question=data.question,
        user_message=analysis_instruction(data.response_language),
        mode=data.mode,
        technical_context=so_far.technical_context,
        retrieval_context_id=so_far.retrieval_context_id,
        followup_history=data.followup_history,
    )
    if not isinstance(output.trace, CaseAnalysisTrace):
        raise CaseAnalysisFailure(
            "analysis_trace_missing", "Case analysis did not produce a validated trace"
        )
    return replace(
        so_far,
        answer=output.answer.strip(),
        trace=output.trace,
        receipt=merged_receipt(so_far.receipt, output.execution_receipt),
    )


async def bind_to_case(data: AnalysisInput, so_far: AnalysisArtifacts) -> AnalysisArtifacts:
    trace = bound_trace(data, so_far, so_far.trace)
    return replace(
        so_far,
        trace=trace,
        answer=trace.summary,
        receipt={**so_far.receipt, "verification": {"rounds": [grounding_record(0, trace)]}},
    )


def bound_trace(
    data: AnalysisInput, so_far: AnalysisArtifacts, trace: CaseAnalysisTrace | None
) -> CaseAnalysisTrace:
    if trace is None:
        raise CaseAnalysisFailure(
            "analysis_trace_missing", "Verification needs an analysis to check"
        )
    table = (so_far.technical_context or {}).get("mitre_table") or []
    return resolve_case_trace(
        trace,
        data.sources,
        mitre_table=list(table),
        followup_history=data.followup_history,
    )


def merged_receipt(
    so_far: dict[str, object], produced: dict[str, object] | None
) -> dict[str, object]:
    produced = produced or {}
    merged = {**so_far, **produced}
    calls = [*(so_far.get("calls") or []), *(produced.get("calls") or [])]
    if calls:
        merged["calls"] = calls
    return merged


def grounding_record(attempt: int, trace: CaseAnalysisTrace) -> dict[str, object]:
    grounding = trace.grounding
    return {
        "attempt": attempt,
        "claims": grounding.claims if grounding else 0,
        "citations_verified": grounding.citations_verified if grounding else 0,
        "citations_unfound": grounding.citations_unfound if grounding else 0,
        "sources_cited": grounding.sources_cited if grounding else 0,
    }


def analysis_instruction(response_language: str) -> str:
    return "วิเคราะห์คดีนี้" if response_language == "thai" else "Analyze this case."


__all__ = [
    "AnalysisAdvance",
    "AnalysisArtifacts",
    "AnalysisInput",
    "advance_case",
    "assess_gaps",
    "analysis_instruction",
    "bind_to_case",
    "bound_trace",
    "grounding_record",
    "merged_receipt",
    "retrieve_technical_context",
    "write_analysis",
]
