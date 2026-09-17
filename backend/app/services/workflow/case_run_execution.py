from __future__ import annotations

import asyncio
import logging
from builtins import BaseExceptionGroup
from collections.abc import Callable
from copy import deepcopy
from uuid import UUID

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure, request_case_analysis
from app.services.case_analysis.contracts import (
    CaseAnalysisOutput as AnalysisOutput,
)
from app.services.gap_clarification import (
    GapClarificationError,
    start_gap_clarification_for_run,
)
from app.services.workflow.case_run_claim import claim_case_run
from app.services.workflow.case_run_completion import (
    CaseRunCompletionError,
    complete_case_run,
)
from app.services.workflow.case_run_context import (
    CaseRunExecutionError,
    attach_case_augmentation_receipt,
    resolve_case_technical_context,
)
from app.services.workflow.case_run_service import ClaimedCaseRun, fail_case_run

logger = logging.getLogger("app.case_workflow")


async def execute_case_run(
    run_id: UUID,
    *,
    session_factory: Callable,
    analysis_request=request_case_analysis,
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
                applicability_gate=applicability_gate,
                rag_request=rag_request,
            )
        async with session_factory() as db:
            completed = await complete_case_run(db, run_id, claimed.attempt_count, output)
        if completed:
            try:
                await start_gap_clarification_for_run(
                    run_id=run_id,
                    session_factory=session_factory,
                )
            except GapClarificationError as error:
                logger.warning(
                    "Adaptive clarification did not start for run %s: %s (%s)",
                    run_id,
                    error.message,
                    error.code,
                )
            except Exception:
                logger.exception(
                    "Adaptive clarification failed after completed analysis run %s",
                    run_id,
                )
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
    applicability_gate=None,
    rag_request=None,
    **_kwargs,
) -> AnalysisOutput:
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


__all__ = ["CaseRunExecutionError", "execute_case_run", "process_case_run"]
