from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import UUID

from app.database import async_session
from app.schemas.rag import QueryResponse
from app.services.case_analysis import request_case_analysis
from app.services.clients.rag_client import request_rag
from app.services.followup import evaluate_followup_outcome
from app.services.followup.schemas import FollowUpPolicy, GapAnalyzer
from app.services.workflow.pipeline_dependencies import PipelineDependencies
from app.services.workflow.pipeline_execution import process_chat_run as execute_chat_run
from app.services.workflow.worker import ChatRunWorker


def build_dependencies() -> PipelineDependencies:
    return PipelineDependencies(
        session_factory=async_session,
        worker_type=ChatRunWorker,
        rag_request=request_rag,
        analysis_request=request_case_analysis,
        followup_evaluator=evaluate_followup_outcome,
    )


async def process_chat_run(
    run_id: UUID,
    *,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    rag_call: Callable[[str], Awaitable[QueryResponse]] | None = None,
    ask_call: Callable[..., Awaitable[object]] | None = None,
) -> None:
    await execute_chat_run(
        run_id,
        policy=policy,
        gap_analyzer=gap_analyzer,
        rag_call=rag_call,
        ask_call=ask_call,
        dependencies=build_dependencies(),
    )


__all__ = ["build_dependencies", "process_chat_run"]
