"""The analysis, as the product runs it.

Three steps in a fixed order. There is no arm switch here and no stage list to
assemble: what an analysis does is what ``analyse_case`` does, readable top to
bottom. The alternative compositions the thesis measures live in
``experiments/analysis_arms.py`` and call these same step functions, so an
ablation measures this code rather than a second copy of it that drifts.

No step touches the database. Each is handed what it needs and returns what it
produced, which is what lets the same steps run over a case row or over a
dataset file.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace

from app.services.analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseProviderReading,
)
from app.services.analysis.mitre_gate import mitre_gate
from app.services.analysis.settings import AnalysisPipelineConfig, configured_pipeline
from app.services.analysis.steps.bind import resolve_case_trace
from app.services.analysis.steps.technical_context import (
    CaseRagContextPayload,
    run_case_mitre_augmentation,
)
from app.services.analysis.steps.write import request_case_analysis
from app.services.clients.rag_client import request_rag
from app.services.sources import CaseSourceBundle


@dataclass(frozen=True)
class AnalysisInput:
    """Everything the pipeline reads. The caller assembles it; no step adds to it."""

    sources: CaseSourceBundle
    response_language: str = "english"
    mode: str = "case_overview"
    question: str | None = None
    # What the reader has already been asked and answered. Conversation, not
    # case sources, so it is versioned by nothing and carried separately.
    followup_history: tuple[CaseFollowupExchange, ...] = ()
    # The context a previous analysis of this same input already retrieved.
    # The caller decides whether it still applies -- the steps hold no history
    # and read no rows, so they cannot know. None means retrieve.
    reused_context: CaseRagContextPayload | None = None


@dataclass(frozen=True)
class AnalysisArtifacts:
    """What the steps have produced. Each step returns the next version of it."""

    answer: str = ""
    trace: CaseAnalysisTrace | None = None
    # Only the split arm fills this: what its reading call wrote, on its way to
    # its judgement call. The production path has no halfway point to hold.
    reading: CaseProviderReading | None = None
    technical_context: dict[str, object] | None = None
    retrieval_context_id: str | None = None
    receipt: dict[str, object] = field(default_factory=dict)


async def analyse_case(data: AnalysisInput) -> AnalysisArtifacts:
    """One analysis, start to finish."""

    artifacts = AnalysisArtifacts()
    artifacts = await retrieve_technical_context(data, artifacts)
    artifacts = await write_analysis(data, artifacts)
    artifacts = await bind_to_case(data, artifacts)
    # RET504 would fold this into the line above. The three steps read as one
    # list precisely because they are written the same way.
    return artifacts  # noqa: RET504


# -- the steps ----------------------------------------------------------------


async def retrieve_technical_context(
    data: AnalysisInput,
    so_far: AnalysisArtifacts,
    *,
    gate: Callable = mitre_gate,
    rag: Callable = request_rag,
) -> AnalysisArtifacts:
    """MITRE ATT&CK context, when the gate says the case calls for it.

    Every failure inside the augmentation comes back as a status, so a RAG
    service that is unreachable costs the analysis its technical context and
    nothing else.

    A retrieval the caller has already paid for is used as given. The gate
    still runs either way: whether ATT&CK applies is cheap to ask and is what
    the analysis records about itself.
    """

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
            "mitre_table": augmentation.mitre_table,
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
    """The one model call that reads the sources and writes the trace."""

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
    """Bind what the model wrote to what the case actually holds.

    A quotation in no source is dropped and counted rather than raised on, so
    one bad citation costs its claim its support and not the whole analysis.
    Asking the model to fix what missed is the revise arm's business, not this
    step's.
    """

    trace = bound_trace(data, so_far, so_far.trace)
    return replace(
        so_far,
        trace=trace,
        answer=trace.summary,
        receipt={**so_far.receipt, "verification": {"rounds": [grounding_record(0, trace)]}},
    )


# -- what the steps and the arms share ----------------------------------------


def bound_trace(
    data: AnalysisInput, so_far: AnalysisArtifacts, trace: CaseAnalysisTrace | None
) -> CaseAnalysisTrace:
    """One binding pass. The revise arm runs several; production runs one."""

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
    """Two model calls, one receipt, and every call still in it.

    A plain merge would let the second call's ``calls`` list replace the
    first's, which is how an arm that costs two calls comes to look like it
    cost one.
    """

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
    "AnalysisArtifacts",
    "AnalysisInput",
    "analyse_case",
    "analysis_instruction",
    "bind_to_case",
    "bound_trace",
    "grounding_record",
    "merged_receipt",
    "retrieve_technical_context",
    "write_analysis",
]
