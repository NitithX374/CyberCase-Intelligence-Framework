from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from app.schemas.rag import QueryResponse
from app.services.analysis.mitre_gate import mitre_gate
from app.services.analysis.technical_context_contracts import (
    CaseRagContextPayload,
    CaseTechnicalAugmentation,
    CaseTechnicalAugmentationStatus,
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.services.clients.rag_client import RagCallFailure, request_rag
from app.services.sources.case_source_bundle import CaseSourceBundle, build_rag_query
from app.trace.claims import CaseFollowupExchange

logger = logging.getLogger(__name__)


def technical_context_key(
    source_revision: int,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> dict[str, int]:
    return {
        "source_revision": source_revision,
        "followup_answers": sum(1 for item in followup_history if item.is_answered),
    }


def retrieval_query(
    source_bundle: CaseSourceBundle,
    trigger_text: Sequence[str],
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> str:
    query = ("\n".join(trigger_text).strip() if trigger_text else "") or build_rag_query(
        source_bundle
    )
    answers = [
        f"{item.question.strip()} {item.answer.strip()}"
        for item in followup_history
        if item.is_answered
    ]
    if not answers:
        return query
    return "\n".join([query, *answers])


@dataclass(frozen=True)
class CaseMitreAugmentation:
    status: CaseTechnicalAugmentationStatus
    applicability: MitreApplicabilityRecord
    context: CaseRagContextPayload | None
    failure_code: str | None = None
    reused: bool = False

    @property
    def retrieval_context_id(self) -> str | None:
        return self.context.retrieval_context_id if self.context else None

    def recorded(self, association_ids: list[str]) -> CaseTechnicalAugmentation:
        matched = self.status == "retrieved_from_rag" and bool(association_ids)
        return CaseTechnicalAugmentation(
            status="retrieved_with_matches" if matched else self.status,
            applicability=self.applicability,
            retrieval_context_id=self.retrieval_context_id,
            retrieval_context_reused=self.reused,
            mitre_table=list(self.context.mitre_table) if self.context else [],
            association_ids=association_ids,
            failure_code=self.failure_code,
        )


async def run_case_mitre_augmentation(
    *,
    source_bundle: CaseSourceBundle,
    applicability_gate=mitre_gate,
    rag_request=request_rag,
    reused_context: CaseRagContextPayload | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseMitreAugmentation:
    applicability = await evaluate_gate(source_bundle.sources, applicability_gate)
    if applicability.failure_code is not None:
        return failed_augmentation(applicability.failure_code, applicability)
    if applicability.decision == "SKIP":
        return CaseMitreAugmentation("not_applicable", applicability, None)

    is_reused = False
    if reused_context is not None:
        context = reused_context
        is_reused = True
    else:
        rag_query = retrieval_query(source_bundle, applicability.trigger_text, followup_history)
        try:
            response = await rag_request(rag_query)
            context = validated_case_rag_context(response)
        except RagCallFailure as error:
            return failed_augmentation(error.code, applicability)
        except Exception:
            logger.exception("Case MITRE retrieval failed")
            return failed_augmentation("rag_service_error", applicability)

    if not context.retrieval_context_id or not context.mitre_table:
        return CaseMitreAugmentation(
            "insufficient_context", applicability, context, reused=is_reused
        )
    return CaseMitreAugmentation("retrieved_from_rag", applicability, context, reused=is_reused)


async def evaluate_gate(case_sources, gate):
    try:
        result = await gate(case_sources=case_sources)
        return MitreApplicabilityRecord.model_validate(result)
    except Exception:
        logger.exception("Case MITRE applicability failed")
        return skipped_mitre_applicability("mitre_applicability_provider_error")


def failed_augmentation(
    code: str, applicability: MitreApplicabilityRecord
) -> CaseMitreAugmentation:
    return CaseMitreAugmentation("failed", applicability, None, code)


def validated_case_rag_context(response: QueryResponse) -> CaseRagContextPayload:
    return CaseRagContextPayload(
        retrieval_context_id=(response.retrieval_context_id or "").strip() or None,
        context=response.context,
        mitre_table=tuple(row.model_dump(mode="json") for row in response.mitre_table),
        legal_relevance=response.legal_reference,
    )


__all__ = [
    "CaseMitreAugmentation",
    "run_case_mitre_augmentation",
    "validated_case_rag_context",
]
