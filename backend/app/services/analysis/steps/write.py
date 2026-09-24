from __future__ import annotations

from collections.abc import Sequence

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseProviderAnalysis,
    followup_payload,
)
from app.services.analysis.prompts import case_system_prompt
from app.services.analysis.provider import request_stage
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.analysis.steps.technical_context import CaseRagContextPayload
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem


async def write_trace(
    *,
    sources: CaseSourceBundle,
    language: str,
    followup_history: Sequence[CaseFollowupExchange] = (),
    technical_context: CaseRagContextPayload | None = None,
    config: AnalysisPipelineConfig,
) -> CaseAnalysisTrace:
    parsed = await request_stage(
        config=config,
        stage="case_direct",
        system=case_system_prompt(),
        content=write_request(sources, language, followup_history, technical_context),
        schema=CaseProviderAnalysis,
    )
    return written_trace(parsed, technical_context)


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
        for quality_key in (
            "extraction_method",
            "provider",
            "verification_status",
            "confidence_status",
            "minimum_confidence",
            "warnings",
        ):
            if quality_key in source.provenance:
                document[quality_key] = source.provenance[quality_key]
        payload["document"] = document
    return payload


def written_trace(
    parsed: CaseProviderAnalysis,
    technical_context: CaseRagContextPayload | None,
) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=parsed.summary,
        involved_parties=parsed.involved_parties,
        timeline=parsed.timeline,
        claims=[CaseAnalysisClaim.model_validate(claim.model_dump()) for claim in parsed.claims],
        impacts=parsed.impacts,
        gaps=parsed.gaps,
        mitre_associations=parsed.mitre_associations,
        retrieval_context_id=(
            technical_context.retrieval_context_id if technical_context is not None else None
        ),
    )


__all__ = [
    "provider_source_payload",
    "write_request",
    "write_trace",
    "written_trace",
]
