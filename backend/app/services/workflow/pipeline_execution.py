from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID, uuid4

from app.schemas.rag import QueryResponse
from app.services.case_analysis import CaseAnalysisFailure
from app.services.case_state.mutator import (
    MUTATION_METADATA_KEY,
    CaseStateMutationFailure,
)
from app.services.clients.rag_client import RagCallFailure
from app.services.extraction import ExtractionModelAdapter, ExtractionStageFailure
from app.services.followup.schemas import GapAnalyzer, FollowUpPolicy
from app.services.workflow.outcome import AssistantOutcome
from app.services.workflow.pipeline_dependencies import PipelineDependencies
from app.services.workflow.pipeline_failure import record_failure
from app.services.workflow.pipeline_helpers import log_stage
from app.services.workflow.pipeline_initial import run_initial_stage
from app.services.workflow.pipeline_mutation import run_mutation_stage
from app.services.workflow.pipeline_question import run_question_stage
from app.services.workflow.worker import ClaimedChatRun


async def process_chat_run(
    run_id: UUID,
    *,
    policy: FollowUpPolicy | None = None,
    gap_analyzer: GapAnalyzer | None = None,
    rag_call: Callable[[str], Awaitable[QueryResponse]] | None = None,
    ask_call: Callable[..., Awaitable[object]] | None = None,
    extraction_adapter: ExtractionModelAdapter | None = None,
    dependencies: PipelineDependencies,
) -> None:
    worker_id = f"chat-run:{uuid4()}"
    async with dependencies.session_factory() as claim_db:
        claimed_run = await dependencies.worker_type(claim_db).claim_run(
            run_id,
            worker_id,
        )

    if claimed_run is None:
        return

    log_stage(
        "STARTING RUN",
        run_id,
        f"action={claimed_run.post_answer_action or 'initial_query'}",
    )
    followup_metadata_json: dict[str, Any] | None = None
    rag_request = rag_call or dependencies.rag_request
    analysis_request = ask_call or dependencies.analysis_request

    def capture_mutation_metadata(metadata: dict[str, Any]) -> None:
        nonlocal followup_metadata_json
        followup_metadata_json = {MUTATION_METADATA_KEY: metadata}

    try:
        _validate_claimed_run(claimed_run)
        if claimed_run.post_answer_action == "add_case_info":
            outcome, followup_metadata_json = await run_mutation_stage(
                claimed_run,
                policy=policy,
                gap_analyzer=gap_analyzer,
                rag_request=rag_request,
                analysis_request=analysis_request,
                followup_evaluator=dependencies.followup_evaluator,
                extraction_adapter=extraction_adapter,
                dependencies=dependencies,
                capture_metadata=capture_mutation_metadata,
            )
            await _complete_run(
                dependencies,
                run_id,
                worker_id,
                outcome,
                "RUN COMPLETED SUCCESSFULLY",
            )
            return

        if claimed_run.post_answer_action == "ask":
            outcome = await run_question_stage(
                claimed_run,
                analysis_request=analysis_request,
            )
            await _complete_run(
                dependencies,
                run_id,
                worker_id,
                outcome,
                "ASK COMPLETED SUCCESSFULLY",
                stage_name="PERSISTING ASK OUTCOME",
            )
            return

        outcome, followup_metadata_json = await run_initial_stage(
            claimed_run,
            policy=policy,
            gap_analyzer=gap_analyzer,
            rag_request=rag_request,
            analysis_request=analysis_request,
            followup_evaluator=dependencies.followup_evaluator,
            extraction_adapter=extraction_adapter,
            dependencies=dependencies,
        )
        await _complete_run(
            dependencies,
            run_id,
            worker_id,
            outcome,
            "INITIAL RUN COMPLETED SUCCESSFULLY",
        )
    except ExtractionStageFailure as exc:
        print(
            f"\n[CHAT RUN {run_id}] ✖ FAILED AT EXTRACTION STAGE: "
            f"[{exc.code}] {exc.message}\n{'=' * 70}\n",
            flush=True,
        )
        await record_failure(
            dependencies,
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=exc.metadata_json,
        )
    except RagCallFailure as exc:
        print(
            f"\n[CHAT RUN {run_id}] ✖ FAILED AT RAG RETRIEVAL STAGE: "
            f"[{exc.code}] {exc.message}\n{'=' * 70}\n",
            flush=True,
        )
        await record_failure(
            dependencies,
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=followup_metadata_json,
        )
    except CaseStateMutationFailure as exc:
        print(
            f"\n[CHAT RUN {run_id}] ✖ FAILED AT MUTATION STAGE: "
            f"[{exc.code}] {exc.message}\n{'=' * 70}\n",
            flush=True,
        )
        await record_failure(
            dependencies,
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=followup_metadata_json,
        )
    except CaseAnalysisFailure as exc:
        print(
            f"\n[CHAT RUN {run_id}] ✖ FAILED AT ANALYSIS STAGE: "
            f"[{exc.code}] {exc.message}\n{'=' * 70}\n",
            flush=True,
        )
        await record_failure(
            dependencies,
            run_id,
            worker_id,
            exc.code,
            exc.message,
            followup_metadata_json=followup_metadata_json,
        )
    except Exception as exc:
        print(
            f"\n[CHAT RUN {run_id}] ✖ FAILED WITH UNEXPECTED ERROR: {exc}\n"
            f"{'=' * 70}\n",
            flush=True,
        )
        await record_failure(
            dependencies,
            run_id,
            worker_id,
            "rag_processing_error",
            "Failed to process chat message",
            followup_metadata_json=followup_metadata_json,
        )


def _validate_claimed_run(claimed_run: ClaimedChatRun) -> None:
    if not isinstance(claimed_run.content, str):
        raise ValueError("Chat run request content is not a string")
    if not isinstance(claimed_run.rag_query, str):
        raise ValueError("Chat run RAG query is not a string")
    if not isinstance(claimed_run.original_user_content, str):
        raise ValueError("Chat follow-up root content is not a string")
    if claimed_run.operation != "query":
        raise ValueError("Chat run operation is invalid")


async def _complete_run(
    dependencies: PipelineDependencies,
    run_id: UUID,
    worker_id: str,
    outcome: AssistantOutcome,
    success_message: str,
    *,
    stage_name: str = "PERSISTING OUTCOME & COMPLETING RUN",
) -> None:
    log_stage(stage_name, run_id)
    async with dependencies.session_factory() as finalize_db:
        await dependencies.worker_type(finalize_db).complete_run(
            run_id,
            worker_id,
            outcome,
        )
    print(
        f"\n[CHAT RUN {run_id}] ✔ {success_message}\n{'=' * 70}\n",
        flush=True,
    )
