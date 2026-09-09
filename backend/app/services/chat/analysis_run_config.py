from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun
from app.services.case_analysis.pipeline_config import (
    AnalysisPipelineConfig,
    configured_pipeline,
    read_pipeline,
)


async def pipeline_for_new_run(
    db: AsyncSession,
    *,
    thread_id: UUID,
    root_ordinal: int,
    action: str,
    clarification_answer: bool,
) -> dict[str, object]:
    if action == "ask":
        return AnalysisPipelineConfig().model_dump(mode="json")
    if not clarification_answer:
        return configured_pipeline().model_dump(mode="json")
    result = await db.execute(
        select(ChatRun)
        .join(ChatMessage, ChatMessage.id == ChatRun.request_message_id)
        .where(ChatRun.thread_id == thread_id, ChatMessage.ordinal == root_ordinal)
    )
    root = result.scalar_one_or_none()
    if root is None:
        raise ValueError("Clarification root run is missing")
    return read_pipeline(root.request_payload.get("analysis_pipeline")).model_dump(
        mode="json"
    )
