import asyncio
import hashlib
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from typing import cast

import httpx
from pydantic import ValidationError

from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.claim_anchored.assembly import assemble_trace
from app.services.case_analysis.claim_anchored.binder import bind_claims
from app.services.case_analysis.claim_anchored.contracts import (
    ExtractedClaims,
    GeneratedSummary,
    SemanticVerifier,
)
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.claim_anchored.prompts import (
    EXTRACTION_PROMPT,
    GENERATION_PROMPT,
    generation_input,
)
from app.services.case_analysis.claim_anchored.provider import (
    input_budget,
    request_stage,
    resolve_target,
    stage_payload,
    token_count,
)
from app.services.case_analysis.claim_anchored.selector import select_claims
from app.services.case_analysis.claim_anchored.source_registry import (
    build_source_registry,
)
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.case_analysis.personalization import resolve_response_language
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
)


async def analyze_claim_anchored(
    *,
    raw_evidence: str,
    analysis_context: dict[str, object],
    user_message: object,
    config: AnalysisPipelineConfig,
    client: httpx.AsyncClient | None = None,
    verifier: SemanticVerifier | None = None,
) -> CaseAnalysisResult:
    receipt: dict[str, object] = {
        "configuration": config.model_dump(mode="json"),
        "calls": [],
        "semantic_verification": "not_performed" if verifier is None else "requested",
    }
    try:
        if client is None:
            async with httpx.AsyncClient() as owned:
                return await _analyze(
                    raw_evidence,
                    analysis_context,
                    user_message,
                    config,
                    owned,
                    verifier,
                    receipt,
                )
        return await _analyze(
            raw_evidence,
            analysis_context,
            user_message,
            config,
            client,
            verifier,
            receipt,
        )
    except (
        CaseAnalysisFailure,
        ValidationError,
        AnalysisTraceProvenanceError,
        AnalysisTraceStructureError,
    ) as error:
        code = getattr(error, "code", "claim_anchored_invalid")
        receipt["failure_code"] = code
        message = (
            error.message
            if isinstance(error, CaseAnalysisFailure)
            else "Attribute-first validation failed"
        )
        raise ClaimAnchoredFailure(code, message, receipt) from error


async def _analyze(
    raw_evidence: str,
    context: dict[str, object],
    user_message: object,
    config: AnalysisPipelineConfig,
    client: httpx.AsyncClient,
    verifier: SemanticVerifier | None,
    receipt: dict[str, object],
) -> CaseAnalysisResult:
    calls: list[dict[str, object]] = []
    receipt["calls"] = calls

    async def checkpoint() -> None:
        callback = context.get("_execution_checkpoint")
        if callback is not None:
            if not callable(callback):
                raise ClaimAnchoredFailure(
                    "claim_checkpoint_invalid", "Execution checkpoint is invalid"
                )
            await cast(Callable[[dict[str, object]], Awaitable[None]], callback)(
                receipt
            )

    sources = build_source_registry(context)
    digest = hashlib.sha256(raw_evidence.strip().encode("utf-8")).hexdigest()
    if context.get("_evidence_sha256", digest) != digest:
        raise ClaimAnchoredFailure(
            "claim_evidence_stale", "Evidence snapshot hash changed"
        )
    receipt["evidence_sha256"] = digest
    receipt["sources"] = [
        {"source_message_id": source.source_message_id, "sha256": source.content_sha256}
        for source in sources
    ]
    language = resolve_response_language(user_message)
    target = resolve_target(config)
    extracted = await request_stage(
        client=client,
        target=target,
        config=config,
        stage="extraction",
        system=EXTRACTION_PROMPT,
        content={
            "sources": [asdict(source) for source in sources],
            "response_language": language,
        },
        schema=ExtractedClaims,
        calls=calls,
        checkpoint=checkpoint,
    )
    receipt["extracted_claim_count"] = len(extracted.claims)
    bound = bind_claims(extracted, sources, context.get("document_source_context", []))
    receipt["bound_claims"] = [value.model_dump(mode="json") for value in bound]
    if verifier is not None:
        await verifier.check_claims(
            tuple(value.model_copy(deep=True) for value in bound)
        )
    selection = await asyncio.to_thread(
        select_claims,
        bound,
        source_ids=tuple(source.source_message_id for source in sources),
        max_claims=config.max_claims,
        fits=lambda values: (
            token_count(
                stage_payload(
                    config,
                    GENERATION_PROMPT,
                    generation_input(values, language),
                    GeneratedSummary,
                )
            )
            <= min(input_budget(config), config.selection_tokens)
        ),
    )
    receipt["selection_policy"] = "stable_source_coverage_v1"
    receipt["omissions"] = list(selection.omissions)
    receipt["selected_claims"] = [
        value.model_dump(mode="json") for value in selection.claims
    ]
    generated = await request_stage(
        client=client,
        target=target,
        config=config,
        stage="generation",
        system=GENERATION_PROMPT,
        content=generation_input(selection.claims, language),
        schema=GeneratedSummary,
        calls=calls,
        checkpoint=checkpoint,
    )
    trace = assemble_trace(
        generated,
        selection.claims,
        digest,
        {source.source_message_id for source in sources},
    )
    if verifier is not None:
        await verifier.check_summary(
            generated.model_copy(deep=True),
            tuple(value.model_copy(deep=True) for value in selection.claims),
        )
        receipt["semantic_verification"] = "completed"
    receipt["units"] = generated.model_dump(mode="json")["units"]
    await checkpoint()
    return CaseAnalysisResult(
        answer=trace.summary, trace=trace, execution_receipt=receipt
    )
