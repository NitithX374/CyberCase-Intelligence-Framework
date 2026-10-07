from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, undefer

from app.cases.ownership import owned_case
from app.cases.running import analysis_running
from app.errors import AppError
from app.llm.request import token_count
from app.llm.settings import SOURCE_OVERHEAD_TOKENS, SOURCE_TOKEN_BUDGET
from app.models.case import Case
from app.models.document import CaseDocument
from app.models.source import CaseSource
from app.sources.ingestion.contracts import IngestedDocument
from app.sources.ingestion.provenance import bind_exact_page_spans
from app.sources.ingestion.text import strip_unstorable


class SourceError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class SourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_document(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        ingested: IngestedDocument,
        content: bytes,
    ) -> CaseDocument:
        weight = await asyncio.to_thread(weight_in_payload, ingested.full_text)
        case = await owned_case(self.db, case_id, user_id, lock=True)
        refuse_while_analysing(case.id)
        if not ingested.full_text.strip():
            raise SourceError("extraction_text_empty", "Document extraction text is empty")
        await self.refuse_beyond_budget(case, weight)
        document = CaseDocument(
            case_id=case.id,
            filename=ingested.filename,
            mime_type=ingested.media_type,
            size_bytes=len(content),
            content_bytes=content,
        )
        self.db.add(document)
        await self.db.flush()
        self.db.add(
            CaseSource(
                case_id=case.id,
                source_kind="document",
                document_id=document.id,
                exact_text=ingested.full_text,
                provenance_json=document_provenance(ingested),
                source_metadata_json={"received_via": "document_upload"},
            )
        )
        case.source_revision += 1
        await self.db.flush()
        return document

    async def update_document_extraction(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        document_id: UUID,
        ingested: IngestedDocument,
    ) -> CaseSource:
        case = await owned_case(self.db, case_id, user_id, lock=True)
        refuse_while_analysing(case.id)
        if not ingested.full_text.strip():
            raise SourceError("extraction_text_empty", "Document extraction text is empty")
        weight = await asyncio.to_thread(weight_in_payload, ingested.full_text)
        await self.refuse_beyond_budget(case, weight)
        source = await self.db.scalar(
            select(CaseSource).where(
                CaseSource.case_id == case.id,
                CaseSource.document_id == document_id,
            )
        )
        if source is None:
            raise SourceError("source_not_found", "Case source not found", status.HTTP_404_NOT_FOUND)
        source.exact_text = ingested.full_text
        source.provenance_json = document_provenance(ingested)
        case.source_revision += 1
        await self.db.flush()
        return source

    async def document_content(
        self, case_id: UUID, document_id: UUID, user_id: UUID | None
    ) -> CaseDocument:
        await owned_case(self.db, case_id, user_id)
        document = await self.db.scalar(
            select(CaseDocument)
            .options(undefer(CaseDocument.content_bytes))
            .where(CaseDocument.id == document_id, CaseDocument.case_id == case_id)
        )
        if document is None:
            raise SourceError("document_not_found", "Document not found", status.HTTP_404_NOT_FOUND)
        return document

    async def add_text_source(
        self,
        *,
        case_id: UUID,
        user_id: UUID | None,
        source_kind: str,
        text: str,
        provenance_json: dict[str, object],
        source_metadata_json: dict[str, object] | None = None,
    ) -> CaseSource:
        if source_kind != "narrative":
            raise SourceError("source_kind_invalid", "Unsupported native source kind")
        normalized_text = strip_unstorable(text).strip()
        if not normalized_text:
            raise SourceError("source_text_empty", "The case source text is empty")
        weight = await asyncio.to_thread(weight_in_payload, normalized_text)
        case = await owned_case(self.db, case_id, user_id, lock=True)
        refuse_while_analysing(case.id)
        await self.refuse_beyond_budget(case, weight)
        source = CaseSource(
            case_id=case.id,
            source_kind=source_kind,
            exact_text=normalized_text,
            provenance_json=deepcopy(provenance_json),
            source_metadata_json=source_metadata_json or {},
        )
        self.db.add(source)
        case.source_revision += 1
        await self.db.flush()
        await self.db.refresh(source)
        return source

    async def refuse_beyond_budget(self, case: Case, weight: int) -> None:
        stored = await self.db.scalars(
            select(CaseSource.exact_text).where(CaseSource.case_id == case.id)
        )
        texts = stored.all()
        kept = await asyncio.to_thread(lambda: sum(weight_in_payload(item) for item in texts))
        if weight + kept > SOURCE_TOKEN_BUDGET:
            raise SourceError(
                "source_too_large",
                "The case sources would exceed what the analysis can read",
                status.HTTP_413_CONTENT_TOO_LARGE,
            )

    async def list_sources(self, case_id: UUID, user_id: UUID | None) -> list[CaseSource]:
        await owned_case(self.db, case_id, user_id)
        result = await self.db.execute(
            select(CaseSource)
            .options(selectinload(CaseSource.document))
            .where(CaseSource.case_id == case_id)
            .order_by(CaseSource.created_at, CaseSource.id)
        )
        return list(result.scalars().unique().all())


def weight_in_payload(text: str) -> int:
    return token_count(json.dumps(text, ensure_ascii=False)) + SOURCE_OVERHEAD_TOKENS


def refuse_while_analysing(case_id: UUID) -> None:
    if analysis_running(case_id):
        raise SourceError(
            "analysis_in_progress",
            "The case is being analysed, so a source cannot be added now",
            status.HTTP_409_CONFLICT,
        )


def document_provenance(ingested: IngestedDocument) -> dict[str, object]:
    pages = [page.model_dump(mode="json") for page in ingested.pages]
    return {
        **bind_exact_page_spans({"pages": pages}, ingested.full_text),
        "extraction_method": ingested.extraction_method.value,
        "verification_status": ingested.verification_status,
        "warnings": list(ingested.warnings),
    }


__all__ = [
    "SourceError",
    "SourceService",
]
