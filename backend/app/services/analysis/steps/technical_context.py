from __future__ import annotations

import logging
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass

from pydantic import ValidationError

from app.schemas.rag import LegalReferenceResult, QueryResponse
from app.services.analysis.contracts import CaseFollowupExchange, CaseMitreAssociation
from app.services.analysis.mitre_gate import mitre_gate
from app.services.analysis.mitre_gate.llm import (
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.services.clients.rag_client import RagCallFailure, request_rag
from app.services.sources.case_source_bundle import CaseSourceBundle, build_rag_query

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


CASE_MITRE_AUGMENTATION_VERSION = "case_mitre_augmentation_v1"
CaseMitreAugmentationStatus = str


@dataclass(frozen=True)
class CaseRagContextPayload:
    retrieval_context_id: str
    context: str
    mitre_table: tuple[dict[str, object], ...]
    legal_relevance: LegalReferenceResult


@dataclass(frozen=True)
class CaseMitreAugmentation:
    status: CaseMitreAugmentationStatus
    applicability: MitreApplicabilityRecord
    context: CaseRagContextPayload | None
    associations: tuple[CaseMitreAssociation, ...]
    failure_code: str | None = None
    reused: bool = False

    @property
    def retrieval_context_id(self) -> str | None:
        return self.context.retrieval_context_id if self.context else None

    @property
    def mitre_table(self) -> list[dict[str, object]]:
        return list(self.context.mitre_table) if self.context else []

    def to_metadata(self) -> dict[str, object]:
        metadata: dict[str, object] = {
            "version": CASE_MITRE_AUGMENTATION_VERSION,
            "status": self.status,
            "applicability": self.applicability.model_dump(mode="json"),
            "retrieval_context_id": self.retrieval_context_id,
            "retrieval_context_reused": self.reused,
            "mitre_table": self.mitre_table,
            "association_ids": [item.association_id for item in self.associations],
        }
        if self.failure_code is not None:
            metadata["failure_code"] = self.failure_code
        if self.status == "retrieved_from_rag" and self.context is not None:
            metadata["legal_relevance"] = self.context.legal_relevance.model_dump(mode="json")
        return metadata


async def run_case_mitre_augmentation(
    *,
    source_bundle: CaseSourceBundle,
    applicability_gate=mitre_gate,
    rag_request=request_rag,
    on_rag_validated=None,
    reused_context: CaseRagContextPayload | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseMitreAugmentation:
    applicability = await evaluate_gate(source_bundle.sources, applicability_gate)
    if applicability.failure_code is not None:
        return failed_augmentation(applicability.failure_code, applicability)
    if applicability.decision == "SKIP":
        return CaseMitreAugmentation("not_applicable", applicability, None, ())

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
        except (ValueError, ValidationError):
            return failed_augmentation("rag_invalid_response", applicability)
        except Exception:
            logger.exception("Case MITRE retrieval failed")
            return failed_augmentation("rag_service_error", applicability)

        if on_rag_validated is not None:
            try:
                try:
                    await on_rag_validated(context, rag_query)
                except TypeError:
                    await on_rag_validated(context)
            except Exception:
                logger.exception("Case MITRE early persistence callback failed")

    if not context.retrieval_context_id or not context.mitre_table:
        return CaseMitreAugmentation(
            "insufficient_context", applicability, context, (), reused=is_reused
        )
    return CaseMitreAugmentation(
        "retrieved_from_rag",
        applicability,
        context,
        (),
        reused=is_reused,
    )


async def evaluate_gate(case_sources, gate):
    try:
        result = await gate(case_sources=case_sources)
        return MitreApplicabilityRecord.model_validate(result)
    except Exception:
        logger.exception("Case MITRE applicability failed")
        return skipped_mitre_applicability("mitre_applicability_provider_error")


def failed_augmentation(
    code: str,
    applicability: MitreApplicabilityRecord | str,
    context: CaseRagContextPayload | None = None,
) -> CaseMitreAugmentation:
    record = (
        applicability
        if isinstance(applicability, MitreApplicabilityRecord)
        else skipped_mitre_applicability(code)
    )
    return CaseMitreAugmentation("failed", record, context, (), code)


def validated_case_rag_context(response: QueryResponse) -> CaseRagContextPayload:
    retrieval_id = response.retrieval_context_id
    context = response.context
    mitre_table = response.mitre_table
    if not isinstance(retrieval_id, str) or not retrieval_id.strip():
        raise ValueError("RAG response has no retrieval context identifier")
    if not isinstance(context, str):
        raise ValueError("RAG response context is invalid")
    if not isinstance(mitre_table, list):
        raise ValueError("RAG response MITRE table is invalid")
    normalized_rows = [
        row if isinstance(row, dict) else row.model_dump(mode="json") for row in mitre_table
    ]
    return CaseRagContextPayload(
        retrieval_context_id=retrieval_id.strip(),
        context=context,
        mitre_table=tuple(deepcopy(normalized_rows)),
        legal_relevance=response.legal_reference,
    )


__all__ = [
    "CASE_MITRE_AUGMENTATION_VERSION",
    "CaseMitreAugmentation",
    "CaseRagContextPayload",
    "run_case_mitre_augmentation",
    "validated_case_rag_context",
]
