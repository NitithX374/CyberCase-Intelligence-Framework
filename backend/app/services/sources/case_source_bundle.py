from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.sources import CaseSource
from app.services.cases.ownership import owned_case
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
    return "CASE NARRATIVE" if source.source_kind == "narrative" else "CASE SOURCE"


def case_source_item(source: CaseSource) -> CaseSourceItem:
    return CaseSourceItem(
        source_id=str(source.id),
        source_kind=source.source_kind,
        text=source.exact_text,
        document_id=str(source.document_id) if source.document_id else None,
        filename=source.filename,
        provenance=source.provenance_json,
        source_metadata=source.source_metadata_json,
    )


def case_source_bundle_from_case(case: Case) -> CaseSourceBundle:
    sources = sorted(case.sources, key=lambda source: (source.created_at, str(source.id)))
    return CaseSourceBundle(
        revision=case.source_revision,
        sources=tuple(case_source_item(source) for source in sources),
    )


class SourcesRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["sources_read_v1"] = "sources_read_v1"
    source_ids: list[str]


def sources_read(bundle: CaseSourceBundle) -> dict[str, object]:
    return SourcesRead(source_ids=[source.source_id for source in bundle.sources]).model_dump(
        mode="json"
    )


def source_ids_of_sources_read(value: object) -> tuple[str, ...]:
    return tuple(SourcesRead.model_validate(value).source_ids)


def case_source_bundle_for_analysis(
    case: Case, result: CaseAnalysisResult, source_ids: Sequence[str]
) -> CaseSourceBundle:
    by_id = {str(source.id): source for source in case.sources}
    missing = [source_id for source_id in source_ids if source_id not in by_id]
    if missing:
        raise ValueError(f"The case no longer has sources the analysis read: {missing}")
    return CaseSourceBundle(
        revision=result.source_revision,
        sources=tuple(case_source_item(by_id[source_id]) for source_id in source_ids),
    )


WITH_SOURCES = (selectinload(Case.sources).selectinload(CaseSource.document),)


async def load_case_source_bundle(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseSourceBundle:
    case = await owned_case(db, case_id, user_id, lock=True, options=WITH_SOURCES)
    return analysable_bundle(case)


def analysable_bundle(case: Case) -> CaseSourceBundle:
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
        context.append({"source_id": source.source_id, "documents": [document]})
    return context


def build_rag_query(bundle: CaseSourceBundle) -> str:
    return "\n\n".join(
        f"[{source_label(source)} · SOURCE {source.source_id}]\n{source.text.strip()}"
        for source in bundle.sources
    )


__all__ = [
    "WITH_SOURCES",
    "CaseSourceBundle",
    "CaseSourceItem",
    "SourcesRead",
    "analysable_bundle",
    "build_document_source_context",
    "build_rag_query",
    "case_source_bundle_for_analysis",
    "case_source_bundle_from_case",
    "case_source_item",
    "load_case_source_bundle",
    "source_ids_of_sources_read",
    "source_label",
    "sources_read",
]
