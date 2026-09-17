from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_materials import CaseSource
from app.models.case_run import CaseAnalysisResult
from app.services.case_materials.material_service import CaseMaterialsError

if TYPE_CHECKING:
    from app.services.case_analysis.contracts import CaseAnalysisMode, ResponseLanguage


@dataclass(frozen=True)
class CaseSourceItem:
    source_id: str
    source_kind: str
    text: str
    document_id: str | None = None
    filename: str | None = None
    provenance: dict[str, object] = field(default_factory=dict)
    source_metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseSourceBundle:
    revision: int
    sources: tuple[CaseSourceItem, ...]


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
            "extraction_method", "provider", "verification_status",
            "confidence_status", "minimum_confidence", "warnings",
        ):
            if quality_key in source.provenance:
                document[quality_key] = source.provenance[quality_key]
        payload["document"] = document
    if source.source_kind == "followup_answer":
        payload["followup_context"] = {
            key: source.provenance[key]
            for key in ("gap_id", "gap_key", "topic", "clarification_question")
            if key in source.provenance
        }
    return payload


def build_case_reasoning_payload(
    *,
    source_bundle: CaseSourceBundle,
    response_language: ResponseLanguage,
    mode: CaseAnalysisMode,
    question: str | None,
    technical_context: dict[str, object] | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    analysis_context: dict[str, object] | None = None,
    active_clarification: dict[str, object] | None = None,
    current_evidence_revision: int | None = None,
    analysis_evidence_revision: int | None = None,
) -> dict[str, object]:
    cleaned_technical_context = None
    if (
        isinstance(technical_context, dict)
        and isinstance(technical_context.get("context"), str)
        and isinstance(technical_context.get("mitre_table"), (list, tuple))
        and technical_context.get("mitre_table")
    ):
        cleaned_technical_context = {
            "context": technical_context["context"],
            "mitre_table": list(technical_context["mitre_table"]),
        }
        for context_id_key in ("retrieval_context_id", "case_run_id"):
            context_id = technical_context.get(context_id_key)
            if isinstance(context_id, str) and context_id.strip():
                cleaned_technical_context[context_id_key] = context_id
    payload: dict[str, object] = {
        "response_language": response_language,
        "analysis_mode": mode,
        "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
        "technical_context": cleaned_technical_context,
        "question": question,
        "conversation_history": list(conversation_history or [])[-12:] if mode == "question_answer" else [],
    }
    if mode == "question_answer":
        payload.update(
            {
                "current_evidence_revision": (
                    current_evidence_revision
                    if current_evidence_revision is not None
                    else source_bundle.revision
                ),
                "analysis_evidence_revision": analysis_evidence_revision,
                "analysis_context": analysis_context,
                "active_clarification": active_clarification,
            }
        )
    return payload


def source_label(source: CaseSourceItem) -> str:
    if source.filename:
        return f"DOCUMENT {source.filename}"
    return {
        "narrative": "CASE NARRATIVE",
        "followup_answer": "FOLLOW-UP ANSWER",
    }.get(source.source_kind, "CASE SOURCE")


def case_source_item(source: CaseSource) -> CaseSourceItem:
    return CaseSourceItem(
        source_id=str(source.id),
        source_kind=source.source_kind,
        text=source.exact_text,
        document_id=str(source.document_id) if source.document_id else None,
        filename=source.document.filename if source.document else None,
        provenance=source.provenance_json,
        source_metadata=source.source_metadata_json,
    )


def case_source_bundle_from_case(case: Case) -> CaseSourceBundle:
    active_sources = sorted(
        (source for source in case.sources if source.archived_at is None),
        key=lambda source: (source.created_at, str(source.id)),
    )
    return CaseSourceBundle(
        revision=case.evidence_revision,
        sources=tuple(case_source_item(source) for source in active_sources),
    )


def case_source_bundle_for_analysis(case: Case, result: CaseAnalysisResult) -> CaseSourceBundle:
    referenced_source_ids: set[str] = set()
    if isinstance(result.trace_json, dict):
        claims = result.trace_json.get("claims")
        if isinstance(claims, list):
            for claim in claims:
                if isinstance(claim, dict):
                    supporting = claim.get("supporting_source_ids")
                    if isinstance(supporting, list):
                        referenced_source_ids.update(str(s) for s in supporting)
                    contradicting = claim.get("contradicting_source_ids")
                    if isinstance(contradicting, list):
                        referenced_source_ids.update(str(s) for s in contradicting)

    if referenced_source_ids:
        analysis_sources = [
            source for source in case.sources
            if str(source.id) in referenced_source_ids
        ]
    else:
        analysis_sources = [
            source for source in case.sources
            if (
                source.created_at <= result.created_at
                and (source.archived_at is None or source.archived_at > result.created_at)
            )
        ]
    analysis_sources.sort(key=lambda source: (source.created_at, str(source.id)))
    return CaseSourceBundle(
        revision=result.evidence_revision,
        sources=tuple(case_source_item(source) for source in analysis_sources),
    )


async def load_case_source_bundle(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    require_sources: bool = True,
) -> CaseSourceBundle:
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.sources).selectinload(CaseSource.document))
        .where(Case.id == case_id)
        .with_for_update()
    )
    case = result.scalar_one_or_none()
    if case is None or (user_id is not None and case.user_id != user_id):
        raise CaseMaterialsError("case_not_found", "Case not found", 404)

    bundle = case_source_bundle_from_case(case)
    for source in bundle.sources:
        if not source.text.strip():
            raise CaseMaterialsError("evidence_text_empty", "Case evidence text is empty")
    if require_sources and not bundle.sources:
        raise CaseMaterialsError("case_evidence_missing", "Add Case material before analysis")
    return bundle


def build_document_source_context(bundle: CaseSourceBundle) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for source in bundle.sources:
        pages = source.provenance.get("pages")
        if not source.document_id or not source.filename or not isinstance(pages, list):
            continue
        document = {
            "document_id": source.document_id,
            "filename": source.filename,
            "page_spans": pages,
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
        context.append({"source_id": source.source_id, "documents": [document]})
    return context


def build_rag_query(bundle: CaseSourceBundle) -> str:
    return "\n\n".join(
        f"[{source_label(source)} · SOURCE {source.source_id}]\n{source.text.strip()}"
        for source in bundle.sources
    )


__all__ = [
    "CaseSourceBundle",
    "CaseSourceItem",
    "build_document_source_context",
    "build_case_reasoning_payload",
    "build_rag_query",
    "case_source_bundle_for_analysis",
    "case_source_bundle_from_case",
    "case_source_item",
    "load_case_source_bundle",
    "provider_source_payload",
    "source_label",
]
