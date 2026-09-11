from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from uuid import UUID, uuid4

from app.config import settings
from app.services.case_analysis import CaseAnalysisFailure, request_case_analysis
from app.services.chat.caseAnswer import generateCaseAnswer, loadCaseAnswerContext
from app.services.case_analysis.contracts import (
    CaseAnalysisResult as AnalysisOutput,
    NativeCaseAnalysisTrace,
    build_native_source_registry,
)
from app.services.case_analysis.pipelineConfig import read_pipeline
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import (
    CaseRunCompletionError,
    complete_case_run,
)
from app.services.workflow.caseAskCompletion import completeCaseAsk
from app.services.workflow.caseRunService import ClaimedCaseRun, fail_case_run
from app.services.workflow.caseMitreAugmentation import (
    merge_case_mitre_trace,
    run_case_mitre_augmentation,
)
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.caseClarification import (
    CaseClarificationHistoryError,
    load_case_clarification_exchanges,
)

logger = logging.getLogger("app.case_workflow")


class CaseRunExecutionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


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
    worker_id = f"case-run:{uuid4()}"
    async with session_factory() as db:
        claimed = await claimCaseRun(db, run_id, worker_id)
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
            context = await loadCaseAnswerContext(db, claimed.id, _analysis_context(claimed))
        output = coerce_analysis_result(
            await answer_request(
                context=context,
                analysis_context=_analysis_context(claimed),
                user_message=_analysis_request_language(claimed),
            )
        )
    else:
        output = coerce_analysis_result(
            await analysis_request(
                raw_evidence=claimed.input_text,
                analysis_context=_analysis_context(claimed),
                question=None,
                user_message=_analysis_request_language(claimed),
                mode="case_overview",
            )
        )
    if (
        claimed.operation == "analysis"
        and isinstance(output.trace, NativeCaseAnalysisTrace)
        and applicability_gate is not None
        and rag_request is not None
    ):
        output = await _attach_case_augmentation(
            output,
            claimed,
            applicability_gate,
            rag_request,
            mapping_request,
        )
    if claimed.operation == "analysis" and isinstance(output.trace, NativeCaseAnalysisTrace):
        output = await _attach_case_followup(
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


def _analysis_context(claimed: ClaimedCaseRun) -> dict[str, object]:
    document_context = []
    for entry in claimed.manifest:
        provenance = entry.get("provenance")
        if not isinstance(provenance, dict):
            continue
        document_id = entry.get("document_id")
        filename = entry.get("filename")
        pages = provenance.get("pages")
        if not isinstance(document_id, str) or not isinstance(filename, str) or not isinstance(pages, list):
            continue
        document_entry = {
            "document_id": document_id,
            "filename": filename,
            "page_spans": pages,
        }
        for quality_key in (
            "extraction_method",
            "provider",
            "verification_status",
            "confidence_status",
            "minimum_confidence",
            "warnings",
        ):
            if quality_key in provenance:
                document_entry[quality_key] = provenance[quality_key]
        document_context.append(
            {
                "source_id": str(entry["source_id"]),
                "documents": [document_entry],
            }
        )
    return {
        "source_ids": list(claimed.source_ids),
        "source_revisions": {
            str(entry["source_id"]): int(entry["revision"])
            for entry in claimed.manifest
        },
        "source_reference_type": "case_evidence_source",
        "_source_text_by_source_id": dict(claimed.source_text_by_id),
        "document_source_context": document_context,
        "_evidence_sha256": claimed.text_sha256,
        "_analysis_pipeline": dict(claimed.pipeline_config),
    }


async def _attach_case_augmentation(
    output,
    claimed: ClaimedCaseRun,
    applicability_gate,
    rag_request,
    mapping_request,
):
    context = _analysis_context(claimed)
    config = read_pipeline(claimed.pipeline_config)
    calls = output.execution_receipt.get("calls", []) if isinstance(output.execution_receipt, dict) else []
    if not isinstance(calls, list):
        raise CaseRunExecutionError("analysis_receipt_invalid", "Case analysis receipt calls are invalid")
    augmentation = await run_case_mitre_augmentation(
        run_id=claimed.id,
        input_text=claimed.input_text,
        manifest=claimed.manifest,
        base_trace=output.trace,
        document_context=context.get("document_source_context", []),
        config=config,
        applicability_gate=applicability_gate,
        rag_request=rag_request,
        mapping_request=mapping_request,
        calls=calls,
    )
    sources = build_native_source_registry(context)
    merged_trace = merge_case_mitre_trace(
        output.trace,
        augmentation,
        sources,
        context.get("document_source_context", []),
    )
    receipt = deepcopy(output.execution_receipt or {})
    receipt["technical_augmentation"] = augmentation.to_metadata(claimed.input_text)
    return replace(
        output,
        trace=merged_trace,
        execution_receipt=receipt,
    )


def _analysis_request_language(claimed: ClaimedCaseRun) -> str:
    language = claimed.request_payload.get("response_language")
    return "วิเคราะห์คดีนี้" if language == "thai" else "Analyze this case."


async def _attach_case_followup(
    output,
    claimed: ClaimedCaseRun,
    clarification_exchanges,
):
    claims = [claim.model_dump(mode="json") for claim in output.trace.claims]
    resolution = await evaluate_followup_outcome(
        original_user_content=claimed.input_text,
        clarification_exchanges=clarification_exchanges,
        followup_root_ordinal=1,
        source_run_id=claimed.id,
        raw_evidence=claimed.input_text,
        analysis_answer=output.answer,
        analysis_context=_analysis_context(claimed),
        analysis_claims=claims,
        canonical_trace=output.trace,
        canonical_state_required=True,
        evidence_sha256=claimed.text_sha256,
    )
    if resolution.question is None:
        return output
    metadata = deepcopy(resolution.metadata_json)
    followup = metadata.get("chat_followup")
    if not isinstance(followup, dict):
        raise CaseRunExecutionError(
            "clarification_metadata_missing",
            "Case clarification metadata is missing",
        )
    detail = followup.get("selected_gap_detail")
    detail = detail if isinstance(detail, dict) else {}
    context = followup.get("followup_context")
    context = context if isinstance(context, dict) else {}
    topic = detail.get("topic") or followup.get("selected_gap")
    gap_key = context.get("gap_key")
    gap_id = detail.get("gap_id") or context.get("gap_id") or gap_key
    if not all(isinstance(value, str) and value.strip() for value in (gap_id, topic, gap_key)):
        raise CaseRunExecutionError(
            "clarification_metadata_missing",
            "Case clarification has no stable gap identity",
        )
    metadata.update(
        {
            "gap_id": gap_id,
            "topic": topic,
            "gap_key": gap_key,
        }
    )
    return replace(
        output,
        followup_question=resolution.question,
        followup_metadata=metadata,
    )


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
