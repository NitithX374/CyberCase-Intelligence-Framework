"""The analysis pipeline as an ordered list of stages.

Production runs every stage. An ablation runs this same code with one stage
left out, so what the experiment measures is the system rather than a second
implementation of it that drifts away from the first.

No stage touches the database. Each one is handed what it needs and returns
what it produced, which is what lets the same pipeline run over a case row or
over a dataset file.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Protocol

from app.config import settings
from app.services.case_analysis import request_case_analysis
from app.services.case_analysis.contracts import CaseAnalysisFailure, CaseAnalysisTrace
from app.services.case_analysis.mitre_gate import mitre_gate
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig, configured_pipeline
from app.services.case_analysis.prompts import CASE_TRACE_REVISION_PROMPT
from app.services.case_analysis.validation import resolve_case_trace
from app.services.clients.rag_client import request_rag
from app.services.sources import CaseSourceBundle
from app.services.technical_context.mitre_augmentation import run_case_mitre_augmentation


@dataclass(frozen=True)
class AnalysisInput:
    """Everything the pipeline reads. The caller assembles it; no stage adds to it."""

    sources: CaseSourceBundle
    response_language: str = "english"
    mode: str = "case_overview"
    question: str | None = None


@dataclass(frozen=True)
class AnalysisArtifacts:
    """What the stages have produced. Each stage returns the next version of it."""

    answer: str = ""
    trace: CaseAnalysisTrace | None = None
    technical_context: dict[str, object] | None = None
    retrieval_context_id: str | None = None
    receipt: dict[str, object] = field(default_factory=dict)


class Stage(Protocol):
    """One step of the pipeline, named so an ablation can drop it by name."""

    name: str

    async def run(self, data: AnalysisInput, so_far: AnalysisArtifacts) -> AnalysisArtifacts: ...


@dataclass(frozen=True)
class TechnicalContextStage:
    """Retrieve MITRE ATT&CK context, when the gate says the case calls for it.

    Every failure inside the augmentation comes back as a status, so a RAG
    service that is unreachable costs the analysis its technical context and
    nothing else.
    """

    name: str = "technical_context"
    applicability_gate: Callable = mitre_gate
    rag_request: Callable = request_rag

    async def run(self, data: AnalysisInput, so_far: AnalysisArtifacts) -> AnalysisArtifacts:
        augmentation = await run_case_mitre_augmentation(
            source_bundle=data.sources,
            applicability_gate=self.applicability_gate,
            rag_request=self.rag_request,
        )
        receipt = {**so_far.receipt, "technical_augmentation": augmentation.to_metadata()}
        if augmentation.status != "retrieved_from_rag":
            return replace(so_far, receipt=receipt)
        return replace(
            so_far,
            technical_context={
                "context": augmentation.context.context,
                "mitre_table": augmentation.mitre_table,
            },
            retrieval_context_id=augmentation.retrieval_context_id,
            receipt=receipt,
        )


@dataclass(frozen=True)
class AnalysisStage:
    """The one model call that reads the sources and writes the trace."""

    name: str = "analysis"
    analysis_request: Callable = request_case_analysis
    config: Callable[[], AnalysisPipelineConfig] = configured_pipeline

    async def run(self, data: AnalysisInput, so_far: AnalysisArtifacts) -> AnalysisArtifacts:
        output = await self.analysis_request(
            source_bundle=data.sources,
            pipeline_config=self.config().model_dump(mode="json"),
            question=data.question,
            user_message=analysis_instruction(data.response_language),
            mode=data.mode,
            technical_context=so_far.technical_context,
            retrieval_context_id=so_far.retrieval_context_id,
        )
        if not isinstance(output.trace, CaseAnalysisTrace):
            raise CaseAnalysisFailure(
                "analysis_trace_missing", "Case analysis did not produce a validated trace"
            )
        return replace(
            so_far,
            answer=output.answer.strip(),
            trace=output.trace,
            receipt={**so_far.receipt, **(output.execution_receipt or {})},
        )


@dataclass(frozen=True)
class VerifyStage:
    """Bind the analysis to the case, and optionally ask it to fix what missed.

    Verifying and revising are separate settings because they answer different
    questions. Verifying alone drops a quotation that is in no source and
    records the loss. Revising hands those quotations back and asks for them
    again, which costs a model call and may simply delete the claims instead —
    which is why the report counts what was kept as well as what was bound.

    max_revisions = 0 verifies and stops. That is the arm the product ships.
    """

    name: str = "verify"
    max_revisions: int = 0
    analysis_request: Callable = request_case_analysis
    config: Callable[[], AnalysisPipelineConfig] = configured_pipeline

    async def run(self, data: AnalysisInput, so_far: AnalysisArtifacts) -> AnalysisArtifacts:
        if so_far.trace is None:
            raise CaseAnalysisFailure(
                "analysis_trace_missing", "Verification needs an analysis to check"
            )
        table = (so_far.technical_context or {}).get("mitre_table") or []
        trace = resolve_case_trace(so_far.trace, data.sources, mitre_table=list(table))
        rounds: list[dict[str, object]] = [grounding_record(0, trace)]

        for attempt in range(1, self.max_revisions + 1):
            unbound = unbound_citations(so_far.trace, trace)
            if not unbound:
                break
            output = await self.analysis_request(
                source_bundle=data.sources,
                pipeline_config=self.config().model_dump(mode="json"),
                question=data.question,
                user_message=analysis_instruction(data.response_language),
                mode=data.mode,
                technical_context=so_far.technical_context,
                retrieval_context_id=so_far.retrieval_context_id,
                revision=revision_note(unbound),
            )
            if not isinstance(output.trace, CaseAnalysisTrace):
                break
            trace = resolve_case_trace(output.trace, data.sources, mitre_table=list(table))
            rounds.append(grounding_record(attempt, trace))

        return replace(
            so_far,
            trace=trace,
            answer=trace.summary,
            receipt={**so_far.receipt, "verification": {"rounds": rounds}},
        )


def unbound_citations(
    written: CaseAnalysisTrace, bound: CaseAnalysisTrace
) -> list[tuple[str, str]]:
    """The quotations the model wrote that no source turned out to contain."""

    survived = {
        (c.source_id, c.exact_quote)
        for claim in bound.claims
        for c in claim.supporting_citations + claim.contradicting_citations
    }
    return [
        (claim.claim_id, citation.exact_quote)
        for claim in written.claims
        for citation in claim.supporting_citations + claim.contradicting_citations
        if (citation.source_id, citation.exact_quote) not in survived
    ]


def revision_note(unbound: list[tuple[str, str]]) -> str:
    """The correction, naming each quotation that missed and the claim it was for."""

    listing = "\n".join(f'- {claim_id}: "{quote}"' for claim_id, quote in unbound)
    return (
        f"{CASE_TRACE_REVISION_PROMPT}\n\nQuotations not found in the source they name:\n{listing}"
    )


def grounding_record(attempt: int, trace: CaseAnalysisTrace) -> dict[str, object]:
    grounding = trace.grounding
    return {
        "attempt": attempt,
        "claims": grounding.claims if grounding else 0,
        "citations_verified": grounding.citations_verified if grounding else 0,
        "citations_unfound": grounding.citations_unfound if grounding else 0,
        "sources_cited": grounding.sources_cited if grounding else 0,
    }


def analysis_stages(arm: str | None = None) -> tuple[Stage, ...]:
    """The stages one arm of the experiment runs.

    A and B differ by one stage, which is the whole point: the comparison is
    the same code with a step added, not a second implementation.
    """

    chosen = arm or settings.case_analysis_arm
    if chosen == "direct":
        return (TechnicalContextStage(), AnalysisStage())
    if chosen == "revise":
        return (
            TechnicalContextStage(),
            AnalysisStage(),
            VerifyStage(max_revisions=settings.case_analysis_max_revisions),
        )
    return (TechnicalContextStage(), AnalysisStage(), VerifyStage())


CASE_ANALYSIS_STAGES: tuple[Stage, ...] = (
    TechnicalContextStage(),
    AnalysisStage(),
    VerifyStage(),
)


async def run_pipeline(
    data: AnalysisInput,
    stages: tuple[Stage, ...] = CASE_ANALYSIS_STAGES,
) -> AnalysisArtifacts:
    artifacts = AnalysisArtifacts()
    for stage in stages:
        artifacts = await stage.run(data, artifacts)
    return artifacts


def without(*names: str, stages: tuple[Stage, ...] = CASE_ANALYSIS_STAGES) -> tuple[Stage, ...]:
    """The pipeline minus some stages — how an ablation condition is written."""

    return tuple(stage for stage in stages if stage.name not in names)


def analysis_instruction(response_language: str) -> str:
    return "วิเคราะห์คดีนี้" if response_language == "thai" else "Analyze this case."


__all__ = [
    "CASE_ANALYSIS_STAGES",
    "AnalysisArtifacts",
    "AnalysisInput",
    "AnalysisStage",
    "VerifyStage",
    "analysis_stages",
    "Stage",
    "TechnicalContextStage",
    "analysis_instruction",
    "run_pipeline",
    "without",
]
