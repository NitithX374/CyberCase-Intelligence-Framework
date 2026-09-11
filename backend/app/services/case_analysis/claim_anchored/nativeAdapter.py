from __future__ import annotations

import asyncio
from dataclasses import asdict

import httpx

from app.services.case_analysis.caseBinding import bind_case_claims, select_case_claims
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisResult,
    CaseAnalysisTrace,
    CaseExtractedClaims,
    CaseGeneratedSummary,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.legacyPrompts import (
    CASE_EXTRACTION_PROMPT,
    CASE_GENERATION_PROMPT,
    case_generation_input,
)
from app.services.case_analysis.providerStage import (
    input_budget,
    request_stage,
    resolve_target,
    token_count,
)
from app.services.case_analysis.validation import validate_case_trace


async def execute_claim_anchored_case_pipeline(
    *,
    raw_evidence: str,
    context: dict[str, object],
    language: str,
    config: AnalysisPipelineConfig,
    sources: tuple[CaseAdmittedSource, ...],
    client: httpx.AsyncClient,
    evidence_sha256: str,
    receipt: dict[str, object],
) -> CaseAnalysisResult:
    calls = receipt.get("calls")
    if not isinstance(calls, list):
        raise CaseAnalysisFailure("case_receipt_invalid", "Case analysis receipt is invalid")
    extracted = await request_stage(
        client=client,
        target=resolve_target(config),
        config=config,
        stage="case_extraction",
        system=CASE_EXTRACTION_PROMPT,
        content={
            "response_language": language,
            "sources": [asdict(source) for source in sources],
        },
        schema=CaseExtractedClaims,
        calls=calls,
    )
    bound = bind_case_claims(extracted, sources, context.get("document_source_context", []))
    selection = await asyncio.to_thread(
        select_case_claims,
        bound,
        source_ids=tuple(source.source_id for source in sources),
        max_claims=config.max_claims,
        fits=lambda values: token_count(
            {"system": CASE_GENERATION_PROMPT, "content": case_generation_input(values, language)}
        )
        <= min(input_budget(config), config.selection_tokens),
    )
    receipt["selection_policy"] = "stable_case_source_coverage_v1"
    receipt["omissions"] = list(selection.omissions)
    generated = await request_stage(
        client=client,
        target=resolve_target(config),
        config=config,
        stage="case_generation",
        system=CASE_GENERATION_PROMPT,
        content=case_generation_input(selection.claims, language),
        schema=CaseGeneratedSummary,
        calls=calls,
    )
    known = {claim.claim.claim_id for claim in selection.claims}
    referenced = {claim_id for unit in generated.units for claim_id in unit.claim_ids}
    if referenced != known:
        raise CaseAnalysisFailure(
            "case_generation_mapping_loss",
            "Case generation omitted or changed selected claims",
        )
    trace = validate_case_trace(
        CaseAnalysisTrace(
            analysis_mode="case_overview",
            summary="\n\n".join(unit.text for unit in generated.units),
            claims=[bound_claim.claim for bound_claim in selection.claims],
            evidence_sha256=evidence_sha256,
        ),
        sources,
        context.get("document_source_context", []),
    )
    return CaseAnalysisResult(answer=trace.summary, trace=trace, execution_receipt=receipt)


__all__ = ["execute_claim_anchored_case_pipeline"]
