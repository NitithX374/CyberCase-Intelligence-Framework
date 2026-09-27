from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, replace

from app.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    bind_to_case,
    bound_trace,
    retrieve_technical_context,
    write_analysis,
)
from app.analysis.prompts import case_system_prompt
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.analysis.write import write_request, write_trace, written_trace
from app.errors import CaseAnalysisFailure
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig, configured_pipeline
from app.services.sources.case_source_bundle import CaseSourceBundle
from app.trace.claims import CaseFollowupExchange
from app.trace.trace import CaseAnalysisTrace, CaseProviderAnalysis
from experiments.split_analysis import (
    CaseProviderReading,
    request_case_judgement,
    request_case_reading,
)

CASE_TRACE_REVISION_PROMPT = """
GROUNDING CORRECTION

Your previous analysis is below, together with every quotation in it that could
not be found in the source it names. Re-emit the complete JSON object.

For each quotation listed:
- If the claim is supported by the source, replace exact_quote with the sentence
  as it appears there, copied character for character.
- If nothing in the sources supports the claim, say so through the claim's
  epistemic status or record it as a gap.

Do not delete a claim merely because its quotation was wrong. A claim the
sources do support is worth keeping with a corrected quotation, and an analysis
that says less is not a better one.

Change nothing else. Every other claim, party, moment, impact, gap and
association must come back as it was.
""".strip()


@dataclass(frozen=True)
class ArmArtifacts(AnalysisArtifacts):
    reading: CaseProviderReading | None = None
    calls: tuple[dict[str, object], ...] = ()
    rounds: tuple[dict[str, object], ...] = ()


Arm = Callable[[AnalysisInput], Awaitable[AnalysisArtifacts]]


async def direct(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    return await write_analysis(data, artifacts)


async def verify(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    artifacts = await write_analysis(data, artifacts)
    return await bind_to_case(data, artifacts)


async def write_revision(
    *,
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange] = (),
    technical_context: CaseRagContextPayload | None = None,
    config: AnalysisPipelineConfig,
    revision: str | None = None,
) -> CaseAnalysisTrace:
    if revision is None:
        return await write_trace(
            sources=sources,
            language=language,
            followup_history=followup_history,
            technical_context=technical_context,
            config=config,
        )
    parsed = await request_stage(
        config=config,
        stage="case_direct_revision",
        system=f"{case_system_prompt()}\n\n{revision}",
        content=write_request(sources, language, followup_history, technical_context),
        schema=CaseProviderAnalysis,
    )
    return written_trace(parsed, technical_context)


async def revise(
    data: AnalysisInput,
    *,
    max_revisions: int = 1,
    request: Callable = write_revision,
) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    artifacts = await write_analysis(data, artifacts, request=request)
    written = artifacts.trace

    trace = bound_trace(data, artifacts, written)
    rounds = [grounding_record(0, trace)]

    for attempt in range(1, max_revisions + 1):
        unbound = unbound_citations(written, trace)
        if not unbound:
            break
        revised = await request(
            sources=data.sources,
            language=data.response_language,
            followup_history=data.followup_history,
            technical_context=artifacts.technical_context,
            config=configured_pipeline(),
            revision=revision_note(unbound),
        )
        trace = bound_trace(data, artifacts, revised)
        rounds.append(grounding_record(attempt, trace))

    return replace(artifacts, trace=trace, rounds=tuple(rounds))


async def split(
    data: AnalysisInput,
    *,
    reading_request: Callable = request_case_reading,
    judgement_request: Callable = request_case_judgement,
) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    artifacts = await read_sources(data, artifacts, request=reading_request)
    artifacts = await judge_reading(data, artifacts, request=judgement_request)
    return await bind_to_case(data, artifacts)


async def read_sources(
    data: AnalysisInput,
    so_far: ArmArtifacts,
    *,
    request: Callable = request_case_reading,
) -> ArmArtifacts:
    output = await request(
        sources=data.sources,
        language=data.response_language,
        config=configured_pipeline(),
        followup_history=data.followup_history,
    )
    return replace(so_far, reading=output.reading, calls=(*so_far.calls, *output.calls))


async def judge_reading(
    data: AnalysisInput,
    so_far: ArmArtifacts,
    *,
    request: Callable = request_case_judgement,
) -> ArmArtifacts:
    if so_far.reading is None:
        raise CaseAnalysisFailure("analysis_reading_missing", "Judgement needs a reading to judge")
    output = await request(
        sources=data.sources,
        language=data.response_language,
        config=configured_pipeline(),
        reading=so_far.reading,
        technical_context=so_far.technical_context,
        followup_history=data.followup_history,
    )
    return replace(so_far, trace=output.trace, calls=(*so_far.calls, *output.calls))


def grounding_record(attempt: int, trace: CaseAnalysisTrace) -> dict[str, object]:
    grounding = trace.grounding
    return {
        "attempt": attempt,
        "claims": grounding.claims if grounding else 0,
        "citations_verified": grounding.citations_verified if grounding else 0,
        "citations_unfound": grounding.citations_unfound if grounding else 0,
        "sources_cited": grounding.sources_cited if grounding else 0,
    }


def unbound_citations(
    written: CaseAnalysisTrace | None, bound: CaseAnalysisTrace
) -> list[tuple[str, str]]:
    if written is None:
        return []
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
    listing = "\n".join(f'- {claim_id}: "{quote}"' for claim_id, quote in unbound)
    return (
        f"{CASE_TRACE_REVISION_PROMPT}\n\nQuotations not found in the source they name:\n{listing}"
    )


ARMS: dict[str, Arm] = {
    "direct": direct,
    "verify": verify,
    "revise": revise,
    "split": split,
}


__all__ = [
    "ARMS",
    "Arm",
    "ArmArtifacts",
    "CASE_TRACE_REVISION_PROMPT",
    "direct",
    "grounding_record",
    "judge_reading",
    "read_sources",
    "revise",
    "revision_note",
    "split",
    "unbound_citations",
    "verify",
    "write_revision",
]
