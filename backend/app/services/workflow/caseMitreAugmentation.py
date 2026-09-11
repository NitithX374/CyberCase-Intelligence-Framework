from __future__ import annotations

import hashlib
import logging
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

import httpx
from pydantic import ValidationError

from app.schemas.rag import QueryResponse
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseMitreAssociation,
    CaseProviderMitreMapping,
)
from app.services.case_analysis.mitreApplicabilityGate import (
    MitreApplicabilityRecord,
    evaluate_mitre_applicability,
    skipped_mitre_applicability,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.providerStage import request_stage, resolve_target
from app.services.case_analysis.prompts import CASE_MITRE_MAPPING_PROMPT
from app.services.case_analysis.validation import validate_case_trace
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.clients.ragClient import RagCallFailure, request_rag


logger = logging.getLogger("app.case_workflow")
CASE_MITRE_AUGMENTATION_VERSION = "case_mitre_augmentation_v1"
CaseMitreAugmentationStatus = str


@dataclass(frozen=True)
class CaseRagContextPayload:
    retrieval_context_id: str
    context: str
    mitre_table: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class CaseMitreAugmentation:
    status: CaseMitreAugmentationStatus
    applicability: MitreApplicabilityRecord
    context: CaseRagContextPayload | None
    associations: tuple[NativeMitreAssociation, ...]
    failure_code: str | None = None

    @property
    def retrieval_context_id(self) -> str | None:
        return self.context.retrieval_context_id if self.context else None

    @property
    def mitre_table(self) -> list[dict[str, object]]:
        return list(self.context.mitre_table) if self.context else []

    def to_metadata(self, query: str) -> dict[str, object]:
        metadata: dict[str, object] = {
            "version": CASE_MITRE_AUGMENTATION_VERSION,
            "status": self.status,
            "applicability": self.applicability.model_dump(mode="json"),
            "retrieval_context_id": self.retrieval_context_id,
            "mitre_table": self.mitre_table,
            "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
            "association_ids": [item.association_id for item in self.associations],
        }
        if self.failure_code is not None:
            metadata["failure_code"] = self.failure_code
        return metadata


async def run_case_mitre_augmentation(
    *,
    run_id: UUID,
    input_text: str,
    manifest: Sequence[Mapping[str, object]],
    base_trace: CaseAnalysisTrace,
    document_context: object,
    config: AnalysisPipelineConfig,
    applicability_gate=evaluate_mitre_applicability,
    rag_request=request_rag,
    mapping_request=None,
    calls: list[dict[str, object]] | None = None,
) -> CaseMitreAugmentation:
    try:
        evidence_sources = _case_evidence_sources(manifest)
    except ValueError as error:
        return _failed("case_source_invalid", str(error))

    applicability = await _evaluate_gate(
        run_id,
        evidence_sources,
        applicability_gate,
    )
    if applicability.failure_code is not None:
        return _failed(applicability.failure_code, applicability)
    if applicability.decision == "SKIP":
        return CaseMitreAugmentation("not_applicable", applicability, None, ())

    try:
        response = await rag_request(input_text)
        context = validated_case_rag_context(response)
    except RagCallFailure as error:
        return _failed(error.code, applicability)
    except (ValueError, ValidationError):
        return _failed("rag_invalid_response", applicability)
    except Exception:
        logger.exception("Case MITRE retrieval failed run_id=%s", run_id)
        return _failed("rag_service_error", applicability)

    technique_rows = _technique_rows(context.mitre_table)
    if not context.retrieval_context_id or not technique_rows:
        return CaseMitreAugmentation("insufficient_context", applicability, context, ())

    try:
        associations = await (mapping_request or request_case_mitre_mapping)(
            claims=base_trace.claims,
            applicability=applicability,
            context=context,
            config=config,
            calls=calls if calls is not None else [],
        )
        valid_associations = _validate_associations(
            associations,
            base_trace.claims,
            applicability,
            technique_rows,
        )
    except (CaseAnalysisFailure, ValidationError, ValueError):
        return _failed("mitre_mapping_invalid", applicability, context)
    except Exception:
        logger.exception("Case MITRE mapping failed run_id=%s", run_id)
        return _failed("mitre_mapping_error", applicability, context)

    status = "retrieved_with_matches" if valid_associations else "retrieved_without_supported_match"
    return CaseMitreAugmentation(
        status,
        applicability,
        context,
        tuple(valid_associations),
    )


def merge_case_mitre_trace(
    trace: CaseAnalysisTrace,
    augmentation: CaseMitreAugmentation,
    sources: tuple[CaseAdmittedSource, ...],
    document_context: object,
) -> CaseAnalysisTrace:
    merged = trace.model_copy(
        update={
            "mitre_associations": list(augmentation.associations),
            "retrieval_context_id": augmentation.retrieval_context_id,
        }
    )
    return validate_case_trace(
        merged,
        sources,
        document_context,
        mitre_table=augmentation.mitre_table,
    )


async def request_case_mitre_mapping(
    *,
    claims: Sequence[CaseAnalysisClaim],
    applicability: MitreApplicabilityRecord,
    context: CaseRagContextPayload,
    config: AnalysisPipelineConfig,
    calls: list[dict[str, object]],
    client: httpx.AsyncClient | None = None,
) -> tuple[CaseMitreAssociation, ...]:
    content = {
        "case_claims": [
            {
                "claim_id": claim.claim_id,
                "text": claim.text,
                "claim_type": claim.claim_type,
                "epistemic_status": claim.epistemic_status,
                "supporting_source_ids": claim.supporting_source_ids,
                "contradicting_source_ids": claim.contradicting_source_ids,
            }
            for claim in claims
        ],
        "applicability": applicability.model_dump(mode="json"),
        "external_mitre_table": list(context.mitre_table),
    }
    if client is not None:
        parsed = await _request_mapping(client, config, content, calls)
    else:
        async with httpx.AsyncClient() as owned_client:
            parsed = await _request_mapping(owned_client, config, content, calls)
    return tuple(parsed.associations)


async def _request_mapping(
    client: httpx.AsyncClient,
    config: AnalysisPipelineConfig,
    content: dict[str, object],
    calls: list[dict[str, object]],
) -> CaseProviderMitreMapping:
    return await request_stage(
        client=client,
        target=resolve_target(config),
        config=config,
        stage="case_mitre_mapping",
        system=CASE_MITRE_MAPPING_PROMPT,
        content=content,
        schema=CaseProviderMitreMapping,
        calls=calls,
    )


async def _evaluate_gate(run_id, sources, gate):
    try:
        result = await gate(source_run_id=run_id, evidence_sources=sources)
        return MitreApplicabilityRecord.model_validate(result)
    except Exception:
        logger.exception("Case MITRE applicability failed run_id=%s", run_id)
        return skipped_mitre_applicability("mitre_applicability_provider_error")


def _case_evidence_sources(
    manifest: Sequence[Mapping[str, object]],
) -> tuple[RawEvidenceSource, ...]:
    sources: list[RawEvidenceSource] = []
    for entry in manifest:
        source_id = entry.get("source_id")
        text = entry.get("exact_text")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("Case evidence source ID is missing")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Case evidence source text is missing")
        try:
            message_id = UUID(source_id)
        except ValueError as error:
            raise ValueError("Case evidence source ID is not canonical") from error
        sources.append(
            RawEvidenceSource(
                message_id=message_id,
                content=text,
                document_sources=tuple(_document_source_metadata(entry)),
            )
        )
    if not sources:
        raise ValueError("Case evidence source registry is empty")
    return tuple(sources)


def _document_source_metadata(entry: Mapping[str, object]) -> list[dict[str, object]]:
    document_id = entry.get("document_id")
    filename = entry.get("filename")
    provenance = entry.get("provenance")
    if not all(isinstance(value, str) and value.strip() for value in (document_id, filename)):
        return []
    pages = provenance.get("pages") if isinstance(provenance, Mapping) else []
    return [{"document_id": document_id, "filename": filename, "page_spans": pages if isinstance(pages, list) else []}]


def _technique_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        dict(row)
        for row in rows
        if isinstance(row, Mapping)
        and isinstance(row.get("technique_id"), str)
        and _is_technique_id(row["technique_id"])
    ]


def _validate_associations(
    associations: Sequence[NativeMitreAssociation],
    claims: Sequence[NativeCaseAnalysisClaim],
    applicability: MitreApplicabilityRecord,
    rows: Sequence[Mapping[str, object]],
) -> list[NativeMitreAssociation]:
    known_claims = {claim.claim_id: claim for claim in claims}
    technique_ids = {str(row["technique_id"]) for row in rows}
    cited_sources = set(applicability.source_message_ids)
    seen_ids: set[str] = set()
    validated: list[NativeMitreAssociation] = []
    for association in associations:
        if association.association_id in seen_ids:
            raise ValueError("MITRE association identifiers must be unique")
        if association.technique_id not in technique_ids:
            raise ValueError("MITRE association technique is outside retrieved context")
        if not set(association.claim_ids).issubset(known_claims):
            raise ValueError("MITRE association claim is outside Case analysis")
        if not any(
            set(known_claims[claim_id].supporting_source_ids) & cited_sources
            for claim_id in association.claim_ids
        ):
            raise ValueError("MITRE association has no cited Case claim support")
        seen_ids.add(association.association_id)
        validated.append(association)
    return validated


def _is_technique_id(value: str) -> bool:
    if len(value) not in {5, 9} or not value.startswith("T"):
        return False
    if len(value) == 5:
        return value[1:].isdigit()
    return value[1:5].isdigit() and value[5] == "." and value[6:].isdigit()


def _failed(
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


mergeCaseMitreTrace = merge_case_mitre_trace
requestCaseMitreMapping = request_case_mitre_mapping
runCaseMitreAugmentation = run_case_mitre_augmentation


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
        row if isinstance(row, dict) else row.model_dump(mode="json")
        for row in mitre_table
    ]
    return CaseRagContextPayload(
        retrieval_context_id=retrieval_id.strip(),
        context=context,
        mitre_table=tuple(deepcopy(normalized_rows)),
    )


validatedCaseRagContext = validated_case_rag_context

__all__ = [
    "CASE_MITRE_AUGMENTATION_VERSION",
    "CaseMitreAugmentation",
    "CaseRagContextPayload",
    "mergeCaseMitreTrace",
    "merge_case_mitre_trace",
    "requestCaseMitreMapping",
    "request_case_mitre_mapping",
    "runCaseMitreAugmentation",
    "run_case_mitre_augmentation",
    "validatedCaseRagContext",
    "validated_case_rag_context",
]
