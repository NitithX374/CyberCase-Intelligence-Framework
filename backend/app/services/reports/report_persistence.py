from __future__ import annotations;

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.case_state import CaseStateVersion
from app.models.chat import ChatThread
from app.models.rag_context import RagContext
from app.models.report import ChatReport
from app.schemas.reports import ChatReportCreate, ChatReportRead, StructuredReport
from app.services.reports.report_contracts import ReportInputSnapshot
from app.services.reports.report_errors import ReportGenerationConflict, ReportNotFound
from app.services.reports.report_generation import (
    run_report_generation,
    source_snapshot_hash,
    validate_structured_report,
)
from app.services.reports.report_pdf import render_chat_report_pdf
from app.services.reports.report_serialization import serialize_chat_report
from app.services.reports.report_snapshot import build_current_report_snapshot

class ChatReportService:
    """Persist immutable report attempts scoped to one chat thread."""

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def generate_report(
        self,
        thread_id: UUID,
        request: ChatReportCreate,
    ) -> ChatReportRead:
        if not settings.chat_report_enabled:
            raise ReportGenerationConflict(
                "report_generation_disabled",
                "Report generation is disabled by the backend configuration.",
            )

        async with self.db.begin():
            thread_result = await self.db.execute(
                select(ChatThread)
                .options(selectinload(ChatThread.messages))
                .where(ChatThread.id == thread_id)
                .with_for_update()
            )
            thread = thread_result.scalar_one_or_none()
            if thread is None:
                raise ReportNotFound("chat_thread_not_found", "Chat thread not found")

            current_case_state: CaseStateVersion | None = None
            current_rag_context: RagContext | None = None
            if thread.current_case_state_version_id is not None:
                state_result = await self.db.execute(
                    select(CaseStateVersion).where(
                        CaseStateVersion.id == thread.current_case_state_version_id,
                        CaseStateVersion.thread_id == thread.id,
                    )
                )
                current_case_state = state_result.scalar_one_or_none()
                context_result = await self.db.execute(
                    select(RagContext).where(
                        RagContext.thread_id == thread.id,
                        RagContext.case_state_version_id
                        == thread.current_case_state_version_id,
                    )
                )
                current_rag_context = context_result.scalar_one_or_none()
                if current_case_state is None or current_rag_context is None:
                    raise ReportGenerationConflict(
                        "report_case_state_context_missing",
                        "The latest Case State and retrieval context are not available for reporting.",
                    )
                snapshot = build_current_report_snapshot(
                    thread,
                    current_case_state_json=current_case_state.state_json,
                    rag_context=current_rag_context,
                    case_state_version_id=current_case_state.id,
                )
            else:
                # Keep direct legacy fixtures/read-only callers compatible; all
                # production chat runs now persist the pointer and context.
                snapshot = build_current_report_snapshot(thread)
            snapshot_hash = source_snapshot_hash(snapshot)
            idempotency_key = request.idempotency_key or snapshot_hash

            existing_result = await self.db.execute(
                select(ChatReport)
                .where(
                    ChatReport.thread_id == thread_id,
                    ChatReport.idempotency_key == idempotency_key,
                )
                .with_for_update()
            )
            existing = existing_result.scalar_one_or_none()
            if existing is not None:
                if existing.source_snapshot_hash != snapshot_hash:
                    raise ReportGenerationConflict(
                        "report_idempotency_conflict",
                        "The idempotency key is already associated with another report snapshot.",
                    )
                return serialize_chat_report(existing)

            version_result = await self.db.execute(
                select(func.max(ChatReport.version_number)).where(
                    ChatReport.thread_id == thread_id
                )
            )
            latest_version = version_result.scalar_one() or 0
            run_result = await run_report_generation(
                snapshot,
            )
            now = datetime.now(timezone.utc)
            report = ChatReport(
                thread_id=thread_id,
                version_number=latest_version + 1,
                idempotency_key=idempotency_key,
                source_snapshot_json=snapshot.model_dump(mode="json"),
                source_snapshot_hash=snapshot_hash,
                extraction_message_id=snapshot.extraction_id,
                extraction_version=snapshot.extraction_version,
                prompt_version=run_result.prompt_version,
                provider=run_result.provider,
                model=run_result.model,
                decoding_settings={},
                status=run_result.status,
                validation_status=(
                    "validated" if run_result.status == "completed" else "failed"
                ),
                validation_errors_json=list(run_result.validation_errors),
                structured_report=(
                    run_result.report.model_dump(mode="json")
                    if run_result.report is not None
                    else None
                ),
                failure_code=run_result.failure_code,
                failure_message=run_result.failure_message,
                finished_at=now,
                latency_ms=run_result.latency_ms,
                input_tokens=run_result.input_tokens,
                output_tokens=run_result.output_tokens,
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
            .order_by(ChatReport.version_number.desc(), ChatReport.created_at.desc())
        )
        return [serialize_chat_report(report) for report in result.scalars().all()]

    async def get_report(
        self,
        thread_id: UUID,
        report_id: UUID,
    ) -> ChatReportRead:
        result = await self.db.execute(
            select(ChatReport).where(
                ChatReport.thread_id == thread_id,
                ChatReport.id == report_id,
            )
        )
        report = result.scalar_one_or_none()
        if report is None:
            raise ReportNotFound("chat_report_not_found", "Chat report not found")
        return serialize_chat_report(report)

    async def get_report_pdf(
        self,
        thread_id: UUID,
        report_id: UUID,
    ) -> tuple[bytes, str]:
        result = await self.db.execute(
            select(ChatReport)
            .options(selectinload(ChatReport.thread))
            .where(
                ChatReport.thread_id == thread_id,
                ChatReport.id == report_id,
            )
        )
        report = result.scalar_one_or_none()
        if report is None:
            raise ReportNotFound("chat_report_not_found", "Chat report not found")
        if (
            report.status != "completed"
            or report.validation_status != "validated"
            or not isinstance(report.structured_report, dict)
        ):
            raise ReportGenerationConflict(
                "report_pdf_requires_validated_report",
                "Only a completed and validated report can be exported as a PDF.",
            )

        try:
            snapshot = ReportInputSnapshot.model_validate(report.source_snapshot_json)
            structured_report = StructuredReport.model_validate(report.structured_report)
            evidence_ids = {item.evidence_id for item in snapshot.extraction.evidence}
            timeline_ids = {item.event_id for item in snapshot.extraction.timeline}
            validate_structured_report(
                structured_report,
                incident_ids=evidence_ids | timeline_ids,
                mitre_ids={row.technique_id for row in snapshot.mitre_rows},
                evidence_ids=evidence_ids,
                timeline_ids=timeline_ids,
            )
        except Exception as exc:
            raise ReportGenerationConflict(
                "report_pdf_requires_validated_report",
                "The persisted report failed validation and cannot be exported as a PDF.",
            ) from exc

        serialized = serialize_chat_report(report)
        if serialized.report is None:
            raise ReportGenerationConflict(
                "report_pdf_requires_validated_report",
                "Only a completed and validated report can be exported as a PDF.",
            )
        thread_title = getattr(report.thread, "title", None) or "New chat"
        content = await asyncio.to_thread(
            render_chat_report_pdf,
            serialized,
            thread_title=thread_title,
        )
        filename = f"cybercase-report-v{report.version_number}-{report.id}.pdf"
        return content, filename

    async def _ensure_thread(self, thread_id: UUID) -> None:
        result = await self.db.execute(
            select(ChatThread.id).where(ChatThread.id == thread_id)
        )
        if result.scalar_one_or_none() is None:
            raise ReportNotFound("chat_thread_not_found", "Chat thread not found")
