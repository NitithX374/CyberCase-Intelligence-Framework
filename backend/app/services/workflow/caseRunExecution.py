from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from uuid import UUID

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure, request_case_analysis
from app.services.chat.caseAnswer import generateCaseAnswer, loadCaseAnswerContext
from app.services.case_analysis.contracts import (
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import (
    CaseRunCompletionError,
    complete_case_run,
)
from app.services.workflow.caseAskCompletion import completeCaseAsk
from app.services.workflow.caseRunContext import attachCaseAugmentation, buildAnalysisContext
from app.services.workflow.caseRunErrors import CaseRunExecutionError
from app.services.workflow.caseRunFollowup import attachCaseFollowup
from app.services.workflow.caseRunService import ClaimedCaseRun, fail_case_run
from app.services.followup.caseClarification import (
    CaseClarificationHistoryError,
    load_case_clarification_exchanges,
)

logger = logging.getLogger("app.case_workflow")


async def executeCaseRun(
    run_id: UUID,
    *,
    session_factory: Callable,
    analysis_request=request_case_analysis,
    answer_request=generateCaseAnswer,
    applicability_gate=None,
    rag_request=None,
    mapping_request=None,
) -> None:
    async with session_factory() as db:
        claimed = await claimCaseRun(db, run_id)
    if claimed is None:
        return
    try:
        async with asyncio.timeout(settings.case_run_timeout_seconds):
            output = await _execute_claimed_work(
                claimed,
                session_factory=session_factory,
                analysis_request=analysis_request,
                answer_request=answer_request,
                applicability_gate=applicability_gate,
                rag_request=rag_request,
                mapping_request=mapping_request,
            )
        async with session_factory() as db:
            if claimed.operation == "ask":
                await completeCaseAsk(db, run_id, claimed.attempt_count, output)
            else:
                await complete_case_run(db, run_id, claimed.attempt_count, output)
    except asyncio.CancelledError:
        await _record_cancellation_failure(
            session_factory,
            run_id,
            claimed.attempt_count,
        )
        raise
    except TimeoutError:
        await _record_failure(
            session_factory,
            run_id,
            claimed.attempt_count,
            "case_run_timeout",
            "Case processing exceeded its configured execution timeout",
        )
    except CaseRunCompletionError as error:
        await _record_failure(session_factory, run_id, claimed.attempt_count, error.code, error.message)
    except CaseAnalysisFailure as error:
        await _record_failure(session_factory, run_id, claimed.attempt_count, error.code, error.message)
    except CaseRunExecutionError as error:
        await _record_failure(session_factory, run_id, claimed.attempt_count, error.code, error.message)
    except Exception as error:
        unwrapped = _unwrap_exception(error)
        if isinstance(unwrapped, (CaseRunCompletionError, CaseAnalysisFailure, CaseRunExecutionError)):
            await _record_failure(session_factory, run_id, claimed.attempt_count, unwrapped.code, unwrapped.message)
        else:
            logger.exception("Case processing failed run_id=%s attempt=%s", run_id, claimed.attempt_count)
            await _record_failure(
                session_factory,
                run_id,
                claimed.attempt_count,
                "case_processing_error",
                "Failed to process Case analysis",
            )


async def _execute_claimed_work(
    claimed: ClaimedCaseRun,
    *,
    session_factory: Callable,
    analysis_request,
    answer_request,
    applicability_gate,
    rag_request,
    mapping_request,
) -> AnalysisOutput:
    clarification_exchanges = ()
    if claimed.operation == "analysis":
        async with session_factory() as db:
            try:
                clarification_exchanges = await load_case_clarification_exchanges(
                    db,
                    claimed.case_id,
                )
            except CaseClarificationHistoryError as error:
                raise CaseRunExecutionError(error.code, error.message) from error
    if claimed.operation == "ask":
        async with session_factory() as db:
            context = await loadCaseAnswerContext(db, claimed.id, buildAnalysisContext(claimed))
        output = coerce_analysis_result(
            await answer_request(
                context=context,
                analysis_context=buildAnalysisContext(claimed),
                user_message=_analysis_request_language(claimed),
            )
        )
    else:
        output = coerce_analysis_result(
            await analysis_request(
                raw_evidence=claimed.input_text,
                analysis_context=buildAnalysisContext(claimed),
                question=None,
                user_message=_analysis_request_language(claimed),
                mode="case_overview",
            )
        )
    if (
        claimed.operation == "analysis"
        and isinstance(output.trace, CaseAnalysisTrace)
        and applicability_gate is not None
        and rag_request is not None
    ):
        output = await attachCaseAugmentation(
            output,
            claimed,
            applicability_gate,
            rag_request,
            mapping_request,
            session_factory=session_factory,
    )
    if claimed.operation == "analysis" and isinstance(output.trace, CaseAnalysisTrace):
        output = await attachCaseFollowup(
            output,
            claimed,
            clarification_exchanges,
        )
    if output.trace is None:
        raise CaseRunExecutionError(
            "analysis_trace_missing",
            "Case analysis did not produce a validated trace",
        )
    return output


def _unwrap_exception(error: BaseException) -> BaseException:
    if isinstance(error, BaseExceptionGroup):
        for sub in error.exceptions:
            sub_unwrapped = _unwrap_exception(sub)
            if isinstance(sub_unwrapped, (CaseRunCompletionError, CaseAnalysisFailure, CaseRunExecutionError)):
                return sub_unwrapped
        if error.exceptions:
            return _unwrap_exception(error.exceptions[0])
    return error


def _analysis_request_language(claimed: ClaimedCaseRun) -> str:
    language = claimed.request_payload.get("response_language")
    return "วิเคราะห์คดีนี้" if language == "thai" else "Analyze this case."


async def _record_failure(
    session_factory,
    run_id: UUID,
    claimed_attempt: int,
    code: str,
    message: str,
) -> None:
    async with session_factory() as db:
        await fail_case_run(db, run_id, claimed_attempt, code, message)


async def _record_cancellation_failure(
    session_factory,
    run_id: UUID,
    claimed_attempt: int,
) -> None:
    try:
        await asyncio.wait_for(
            _record_failure(
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
    from app.services.case_analysis.mitreApplicabilityGate import evaluate_mitre_applicability
    from app.services.clients.ragClient import request_rag
    from app.services.workflow.caseMitreAugmentation import request_case_mitre_mapping

    await executeCaseRun(
        run_id,
        session_factory=async_session,
        applicability_gate=evaluate_mitre_applicability,
        rag_request=request_rag,
        mapping_request=request_case_mitre_mapping,
    )


processCaseRun = process_case_run

__all__ = ["CaseRunExecutionError", "executeCaseRun", "processCaseRun", "process_case_run"]
