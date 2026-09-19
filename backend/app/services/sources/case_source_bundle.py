from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.sources import CaseSource
from app.services.sources.source_service import SourceError


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
        revision=case.source_revision,
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
            source for source in case.sources if str(source.id) in referenced_source_ids
        ]
    else:
        analysis_sources = [
            source
            for source in case.sources
            if (
                source.created_at <= result.created_at
                and (source.archived_at is None or source.archived_at > result.created_at)
            )
        ]
    analysis_sources.sort(key=lambda source: (source.created_at, str(source.id)))
    return CaseSourceBundle(
        revision=result.source_revision,
        sources=tuple(case_source_item(source) for source in analysis_sources),
    )


async def load_case_source_bundle(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseSourceBundle:
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.sources).selectinload(CaseSource.document))
        .where(Case.id == case_id)
        .with_for_update()
    )
    case = result.scalar_one_or_none()
    if case is None or (user_id is not None and case.user_id != user_id):
        raise SourceError("case_not_found", "Case not found", 404)

    bundle = case_source_bundle_from_case(case)
    for source in bundle.sources:
        if not source.text.strip():
            raise SourceError("source_text_empty", "A case source has no text")
    if not bundle.sources:
        raise SourceError("case_sources_missing", "Add a case source before running an analysis")
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
    "build_rag_query",
    "case_source_bundle_for_analysis",
    "case_source_bundle_from_case",
    "case_source_item",
    "load_case_source_bundle",
    "source_label",
]
