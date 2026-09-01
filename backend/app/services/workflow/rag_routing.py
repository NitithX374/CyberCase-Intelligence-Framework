from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.case_analysis.mitre_applicability_contracts import (
    MITRE_APPLICABILITY_GATE_VERSION,
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.services.clients.rag_client import RagCallFailure
from app.services.workflow.outcome import (
    RagAttemptStatus,
    RagContextPayload,
    validated_rag_context_payload,
)


logger = logging.getLogger("app.chat")


@dataclass(frozen=True)
class RagAttempt:
    status: RagAttemptStatus
    context: RagContextPayload | None
    failure_code: str | None = None


async def attempt_mitre_applicability(
    claimed,
    applicability_gate,
) -> MitreApplicabilityRecord:
    try:
        return MitreApplicabilityRecord.model_validate(
            await applicability_gate(
                source_run_id=claimed.id,
                evidence_sources=claimed.evidence_sources,
            )
        )
    except Exception:
        logger.warning(
            "MITRE applicability failed closed gate_version=%s source_run_id=%s "
            "failure_code=%s",
            MITRE_APPLICABILITY_GATE_VERSION,
            claimed.id,
            "mitre_applicability_provider_error",
        )
        return skipped_mitre_applicability("mitre_applicability_provider_error")


async def attempt_optional_rag(claimed, rag_request) -> RagAttempt:
    try:
        response = await rag_request(claimed.raw_evidence)
    except RagCallFailure as error:
        logger.warning(
            "Optional RAG unavailable source_run_id=%s failure_code=%s error=%s",
            claimed.id,
            error.code,
            error.message,
        )
        return RagAttempt(
            status="unavailable",
            context=None,
            failure_code=error.code,
        )
    if response.retrieval_context_id is None or (
        not response.context.strip() and not response.mitre_table
    ):
        return RagAttempt(status="no_applicable_context", context=None)
    try:
        context = validated_rag_context_payload(response)
    except ValueError as error:
        logger.warning(
            "Optional RAG invalid source_run_id=%s failure_code=%s error=%s",
            claimed.id,
            "rag_invalid_response",
            error,
        )
        return RagAttempt(
            status="unavailable",
            context=None,
            failure_code="rag_invalid_response",
        )
    return RagAttempt(status="used", context=context)


__all__ = ["RagAttempt", "attempt_mitre_applicability", "attempt_optional_rag"]
