from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.chat import ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.models.report import ChatReport
from app.schemas.reports import ChatReportCreate, ChatReportRead, StructuredReport
from app.services.reports.report_contracts import (
    ReportGenerationConflict,
    ReportInputSnapshot,
    ReportNotFound,
)
from app.services.reports.report_generation import run_report_generation
from app.services.reports.report_pdf import render_chat_report_pdf
from app.services.reports.report_snapshot import build_current_report_snapshot
from app.services.reports.report_validation import (
    source_snapshot_hash,
    validate_structured_report,
)


def serialize_chat_report(report: ChatReport) -> ChatReportRead:
    structured_report: StructuredReport | None = None
    if isinstance(report.structured_report, dict):
        structured_report = StructuredReport.model_validate(report.structured_report)
    validation_errors = report.validation_errors_json
    if not isinstance(validation_errors, list):
        validation_errors = []
    return ChatReportRead(
        report_id=report.id,
        thread_id=report.thread_id,
        version_number=report.version_number,
        idempotency_key=report.idempotency_key,
        source_snapshot_hash=report.source_snapshot_hash,
        analysis_message_id=report.analysis_message_id,
        retrieval_context_id=report.retrieval_context_id,
        prompt_version=report.prompt_version,
        provider=report.provider,
        model=report.model,
        decoding_settings=dict(report.decoding_settings or {}),
        persistence_status=report.status,
        validation_status=report.validation_status,
        report=structured_report,
        validation_errors=[str(error) for error in validation_errors],
        failure_code=report.failure_code,
        failure_message=report.failure_message,
        created_at=report.created_at,
        finished_at=report.finished_at,
        latency_ms=report.latency_ms,
        input_tokens=report.input_tokens,
        output_tokens=report.output_tokens,
        source_snapshot=report.source_snapshot_json if isinstance(report.source_snapshot_json, dict) else None,
    )


class ChatReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_report(
        self,
        thread_id: UUID,
        request: ChatReportCreate,
    ) -> ChatReportRead:
        if not settings.chat_report_enabled:
            raise ReportGenerationConflict(
                "report_generation_disabled",
                "Report generation is disabled by backend configuration.",
            )
        async with self.db.begin():
            thread = await self._thread_with_messages(thread_id, lock=True)
            rag_context = await self._latest_rag_context(thread_id)
            snapshot = build_current_report_snapshot(thread, rag_context=rag_context)
            snapshot_hash = source_snapshot_hash(snapshot)
            idempotency_key = request.idempotency_key or snapshot_hash
            existing = await self._existing_report(thread_id, idempotency_key)
            if existing is not None:
                if existing.source_snapshot_hash != snapshot_hash:
                    raise ReportGenerationConflict(
                        "report_idempotency_conflict",
                        "The idempotency key belongs to another report snapshot.",
                    )
                return serialize_chat_report(existing)
            version = await self._next_version(thread_id)
            result = await run_report_generation(snapshot)
            report = ChatReport(
                thread_id=thread_id,
                version_number=version,
                idempotency_key=idempotency_key,
                source_snapshot_json=snapshot.model_dump(mode="json"),
                source_snapshot_hash=snapshot_hash,
                analysis_message_id=snapshot.analysis_message_id,
                retrieval_context_id=snapshot.retrieval_context_id,
                prompt_version=result.prompt_version,
                provider=result.provider,
                model=result.model,
                decoding_settings={},
                status=result.status,
                validation_status="validated" if result.status == "completed" else "failed",
                validation_errors_json=list(result.validation_errors),
                structured_report=(
                    result.report.model_dump(mode="json") if result.report is not None else None
                ),
                failure_code=result.failure_code,
                failure_message=result.failure_message,
                finished_at=datetime.now(timezone.utc),
                latency_ms=result.latency_ms,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
            )
            self.db.add(report)
            await self.db.flush()
            await self.db.refresh(report)
            return serialize_chat_report(report)

    async def list_reports(self, thread_id: UUID) -> list[ChatReportRead]:
        await self._ensure_thread(thread_id)
        result = await self.db.execute(
            select(ChatReport)
            .where(ChatReport.thread_id == thread_id)
            .order_by(ChatReport.version_number.desc())
        )
        return [serialize_chat_report(report) for report in result.scalars().all()]

    async def get_report(self, thread_id: UUID, report_id: UUID) -> ChatReportRead:
        report = await self._report(thread_id, report_id)
        return serialize_chat_report(report)

    async def get_report_pdf(
        self,
        thread_id: UUID,
        report_id: UUID,
    ) -> tuple[bytes, str]:
        report = await self._report(thread_id, report_id, load_thread=True)
        if report.status != "completed" or not isinstance(report.structured_report, dict):
            raise ReportGenerationConflict(
                "report_pdf_requires_validated_report",
                "Only a completed validated report can be exported.",
            )
        snapshot = ReportInputSnapshot.model_validate(report.source_snapshot_json)
        structured = StructuredReport.model_validate(report.structured_report)
        validate_structured_report(
            structured,
            source_message_ids={str(item.message_id) for item in snapshot.source_messages},
            mitre_ids={row.technique_id for row in snapshot.mitre_rows},
        )
        serialized = serialize_chat_report(report)
        content = await asyncio.to_thread(
            render_chat_report_pdf,
            serialized,
            thread_title=report.thread.title,
        )
        return content, f"cybercase-report-v{report.version_number}-{report.id}.pdf"

    async def _thread_with_messages(self, thread_id: UUID, *, lock: bool) -> ChatThread:
        statement = select(ChatThread).options(selectinload(ChatThread.messages)).where(
            ChatThread.id == thread_id
        )
        if lock:
            statement = statement.with_for_update()
        result = await self.db.execute(statement)
        thread = result.scalar_one_or_none()
        if thread is None:
            raise ReportNotFound("chat_thread_not_found", "Chat thread not found")
        return thread

    async def _latest_rag_context(self, thread_id: UUID) -> RagContext:
        result = await self.db.execute(
            select(RagContext)
            .join(ChatRun, ChatRun.id == RagContext.run_id)
            .where(RagContext.thread_id == thread_id, ChatRun.status == "completed")
            .order_by(ChatRun.created_at.desc())
            .limit(1)
        )
        context = result.scalar_one_or_none()
        if context is None:
            raise ReportGenerationConflict(
                "report_context_missing",
                "A completed retrieval context is required before generating a report.",
            )
        return context

    async def _existing_report(self, thread_id: UUID, key: str) -> ChatReport | None:
        result = await self.db.execute(
            select(ChatReport).where(
                ChatReport.thread_id == thread_id,
                ChatReport.idempotency_key == key,
            )
        )
        return result.scalar_one_or_none()

    async def _next_version(self, thread_id: UUID) -> int:
        result = await self.db.execute(
            select(func.max(ChatReport.version_number)).where(ChatReport.thread_id == thread_id)
        )
        return (result.scalar_one() or 0) + 1

    async def _ensure_thread(self, thread_id: UUID) -> None:
        await self._thread_with_messages(thread_id, lock=False)

    async def _report(
        self,
        thread_id: UUID,
        report_id: UUID,
        *,
        load_thread: bool = False,
    ) -> ChatReport:
        statement = select(ChatReport).where(
            ChatReport.thread_id == thread_id,
            ChatReport.id == report_id,
        )
        if load_thread:
            statement = statement.options(selectinload(ChatReport.thread))
        result = await self.db.execute(statement)
        report = result.scalar_one_or_none()
        if report is None:
            raise ReportNotFound("chat_report_not_found", "Chat report not found")
        return report


__all__ = ["ChatReportService", "serialize_chat_report"]
