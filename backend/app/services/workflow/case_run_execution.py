from __future__ import annotations

import asyncio
import logging
from builtins import BaseExceptionGroup
from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from uuid import UUID

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure, request_case_analysis
from app.services.chat.case_answer import generate_case_answer, load_case_answer_context
from app.services.case_analysis.contracts import (
    CaseAnalysisOutput as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.followup.case_followup import (
    CaseFollowUpHistoryError,
    load_followup_exchanges,
)
from app.services.followup.decision import evaluate_followup_outcome
from app.services.workflow.case_run_claim import claim_case_run
from app.services.workflow.case_run_completion import (
    CaseRunCompletionError,
    complete_case_run,
)
from app.services.workflow.case_ask_completion import complete_case_ask
from app.services.workflow.case_run_context import (
    CaseRunExecutionError,
    attach_case_augmentation_receipt,
    resolve_case_technical_context,
)
from app.services.workflow.case_run_service import ClaimedCaseRun, fail_case_run

logger = logging.getLogger("app.case_workflow")


async def attach_case_followup(
    output: AnalysisOutput,
    claimed: ClaimedCaseRun,
    followup_exchanges,
) -> AnalysisOutput:
    if not isinstance(output.trace, CaseAnalysisTrace):
        return output
    try:
        resolution = await evaluate_followup_outcome(
            followup_exchanges=followup_exchanges,
            followup_root_ordinal=1,
            source_run_id=claimed.id,
            source_revision=claimed.source_revision,
            canonical_trace=output.trace,
        )
        if resolution.question is None:
            return output
        followup = resolution.metadata_json.get("chat_followup")
        if not isinstance(followup, dict) or not isinstance(followup.get("gap"), dict):
            logger.warning(
                "Case follow-up metadata or gap missing for run %s; skipping follow-up attachment",
                claimed.id,
            )
            return output
        return replace(
            output,
            followup_question=resolution.question,
            followup_metadata=resolution.metadata_json,
        )
    except Exception as exc:
        logger.warning(
            "Failed to evaluate follow-up for run %s: %s; continuing analysis without follow-up",
            claimed.id,
            exc,
        )
        return output


async def execute_case_run(
    run_id: UUID,
    *,
    session_factory: Callable,
    analysis_request=request_case_analysis,
    answer_request=generate_case_answer,
    applicability_gate=None,
    rag_request=None,
) -> None:
    async with session_factory() as db:
        claimed = await claim_case_run(db, run_id)
    if claimed is None:
        return
    try:
        async with asyncio.timeout(settings.case_run_timeout_seconds):
            output = await execute_claimed_work(
                claimed,
                session_factory=session_factory,
                analysis_request=analysis_request,
                answer_request=answer_request,
                applicability_gate=applicability_gate,
                rag_request=rag_request,
            )
        async with session_factory() as db:
            if claimed.operation == "ask":
                await complete_case_ask(db, run_id, claimed.attempt_count, output)
            else:
                await complete_case_run(db, run_id, claimed.attempt_count, output)
    except asyncio.CancelledError:
        await record_cancellation_failure(
            session_factory,
            run_id,
            claimed.attempt_count,
        )
        raise
    except TimeoutError:
        await record_failure(
            session_factory,
            run_id,
            claimed.attempt_count,
            "case_run_timeout",
            "Case processing exceeded its configured execution timeout",
        )
    except CaseRunCompletionError as error:
        await record_failure(session_factory, run_id, claimed.attempt_count, error.code, error.message)
    except CaseAnalysisFailure as error:
        await record_failure(session_factory, run_id, claimed.attempt_count, error.code, error.message)
    except CaseRunExecutionError as error:
        await record_failure(session_factory, run_id, claimed.attempt_count, error.code, error.message)
    except Exception as error:
        unwrapped = unwrap_exception(error)
        if isinstance(unwrapped, (CaseRunCompletionError, CaseAnalysisFailure, CaseRunExecutionError)):
            await record_failure(session_factory, run_id, claimed.attempt_count, unwrapped.code, unwrapped.message)
        else:
            logger.exception("Case processing failed run_id=%s attempt=%s", run_id, claimed.attempt_count)
            await record_failure(
                session_factory,
                run_id,
                claimed.attempt_count,
                "case_processing_error",
                "Failed to process Case analysis",
            )


async def execute_claimed_work(
    claimed: ClaimedCaseRun,
    *,
    session_factory: Callable,
    analysis_request,
    answer_request,
    applicability_gate,
    rag_request,
) -> AnalysisOutput:
    followup_exchanges = ()
    if claimed.operation == "analysis":
        async with session_factory() as db:
            try:
                followup_exchanges = await load_followup_exchanges(
                    db,
                    claimed.case_id,
                )
            except Exception as error:
                logger.warning(
                    "Failed to load follow-up exchanges for case %s: %s; continuing analysis without follow-up history",
                    claimed.case_id,
                    error,
                )
                followup_exchanges = ()
    if claimed.operation == "ask":
        async with session_factory() as db:
            context = await load_case_answer_context(db, claimed.id, claimed.source_bundle)
        output = coerce_analysis_result(
            await answer_request(
                context=context,
                source_bundle=claimed.source_bundle,
                user_message=analysis_request_language(claimed),
            )
        )
    else:
        augmentation = None
        if applicability_gate is not None and rag_request is not None:
            augmentation = await resolve_case_technical_context(
                claimed,
                applicability_gate=applicability_gate,
                rag_request=rag_request,
                session_factory=session_factory,
            )

        technical_context = None
        retrieval_context_id = None
        if (
            augmentation is not None
            and augmentation.status == "retrieved_from_rag"
            and augmentation.context is not None
            and augmentation.mitre_table
        ):
            technical_context = {
                "context": augmentation.context.context,
                "mitre_table": augmentation.mitre_table,
            }
            retrieval_context_id = augmentation.retrieval_context_id

        output = coerce_analysis_result(
            await analysis_request(
                source_bundle=claimed.source_bundle,
                pipeline_config=claimed.pipeline_config,
                question=None,
                user_message=analysis_request_language(claimed),
                mode="case_overview",
                technical_context=technical_context,
                retrieval_context_id=retrieval_context_id,
            )
        )
        if augmentation is not None:
            output = attach_case_augmentation_receipt(output, augmentation)
    if claimed.operation == "analysis" and isinstance(output.trace, CaseAnalysisTrace):
        output = await attach_case_followup(
            output,
            claimed,
            followup_exchanges,
        )
    if output.trace is None:
        raise CaseRunExecutionError(
            "analysis_trace_missing",
            "Case analysis did not produce a validated trace",
        )
    return output


def unwrap_exception(error: BaseException) -> BaseException:
    if isinstance(error, BaseExceptionGroup):
        for sub in error.exceptions:
            sub_unwrapped = unwrap_exception(sub)
            if isinstance(sub_unwrapped, (CaseRunCompletionError, CaseAnalysisFailure, CaseRunExecutionError)):
                return sub_unwrapped
        if error.exceptions:
            return unwrap_exception(error.exceptions[0])
    return error


def analysis_request_language(claimed: ClaimedCaseRun) -> str:
    language = claimed.request_payload.get("response_language")
    return "วิเคราะห์คดีนี้" if language == "thai" else "Analyze this case."


async def record_failure(
    session_factory,
    run_id: UUID,
    claimed_attempt: int,
    code: str,
    message: str,
) -> None:
    async with session_factory() as db:
        await fail_case_run(db, run_id, claimed_attempt, code, message)


async def record_cancellation_failure(
    session_factory,
    run_id: UUID,
    claimed_attempt: int,
) -> None:
    try:
        await asyncio.wait_for(
            record_failure(
                session_factory,
                run_id,
                claimed_attempt,
                "case_run_cancelled",
                "Case processing was cancelled before completion",
            ),
            timeout=settings.case_run_failure_persistence_timeout_seconds,
        )
    except asyncio.CancelledError:
        logger.warning(
            "Case cancellation cleanup was interrupted run_id=%s attempt=%s",
            run_id,
            claimed_attempt,
        )
    except Exception:
        logger.exception(
            "Case cancellation failure could not be persisted run_id=%s attempt=%s",
            run_id,
            claimed_attempt,
        )


def coerce_analysis_result(value: object) -> AnalysisOutput:
    if isinstance(value, AnalysisOutput) and value.answer.strip():
        return value
    if isinstance(value, str) and value.strip():
        return AnalysisOutput(answer=value.strip(), trace=None)
    raise CaseAnalysisFailure(
        "analysis_invalid_response",
        "The Main Case Analysis returned no answer",
    )


async def process_case_run(run_id: UUID) -> None:
    from app.database import async_session
    from app.services.case_analysis.mitre_applicability_gate import evaluate_mitre_applicability
    from app.services.clients.rag_client import request_rag

    await execute_case_run(
        run_id,
        session_factory=async_session,
        applicability_gate=evaluate_mitre_applicability,
        rag_request=request_rag,
    )


__all__ = ["CaseRunExecutionError", "attach_case_followup", "execute_case_run", "process_case_run"]
