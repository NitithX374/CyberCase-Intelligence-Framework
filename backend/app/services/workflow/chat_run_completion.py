from __future__ import annotations

from collections.abc import Awaitable, Callable
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_state import CaseStateVersion
from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.services.case_state.mutator import (
    MUTATION_METADATA_KEY, CaseStateDelta, CaseStateMutationFailure, apply_case_state_delta,
)
from app.services.case_state.update_projection import build_case_update_projection, empty_case_state_delta
from app.services.case_analysis.contracts import AnalysisTrace
from app.services.workflow.chat_run_contracts import is_no_change_case_update
from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread
from app.services.workflow.outcome import AssistantOutcome

async def complete_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
    outcome: AssistantOutcome,
    *,
    lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None = None,
    lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None = None,
) -> bool:
    """Persist an assistant message only while this invocation owns the lease."""

    now = datetime.now(timezone.utc)
    async with db.begin():
        thread = await (
            lock_run_thread_fn(run_id)
            if lock_run_thread_fn is not None
            else lock_run_thread(db, run_id)
        )
        if thread is None:
            return False

        run = await (
            lock_owned_running_run_fn(run_id, worker_id)
            if lock_owned_running_run_fn is not None
            else lock_owned_running_run(db, run_id, worker_id)
        )
        if run is None or run.thread_id != thread.id:
            return False

        has_case_state = outcome.validated_case_state_json is not None
        has_rag_context = outcome.rag_context_payload is not None
        if has_case_state != has_rag_context:
            raise ValueError(
                "A successful initial analysis must persist Case State and "
                "durable RAG context together"
            )

        has_mutation = (
            outcome.case_state_delta_json is not None
            or outcome.expected_parent_case_state_version_id is not None
        )
        if has_mutation and (
            not has_case_state
            or not has_rag_context
            or outcome.case_state_delta_json is None
            or outcome.expected_parent_case_state_version_id is None
        ):
            raise ValueError(
                "A Case State mutation must include its merged snapshot, "
                "delta, and fresh RAG context"
            )

        case_state_version: CaseStateVersion | None = None
        parent_version: CaseStateVersion | None = None
        if has_mutation:
            expected_parent_id = outcome.expected_parent_case_state_version_id
            if thread.current_case_state_version_id != expected_parent_id:
                raise CaseStateMutationFailure(
                    "case_state_stale_parent",
                    "The Case State changed before this mutation completed",
                )
            parent_result = await db.execute(
                select(CaseStateVersion)
                .where(
                    CaseStateVersion.id == expected_parent_id,
                    CaseStateVersion.thread_id == thread.id,
                )
                .with_for_update()
            )
            parent_version = parent_result.scalar_one_or_none()
            if parent_version is None:
                raise CaseStateMutationFailure(
                    "case_state_parent_missing",
                    "The mutation parent Case State could not be loaded",
                )
            try:
                delta = CaseStateDelta.model_validate(
                    outcome.case_state_delta_json
                )
                chat_action = outcome.metadata_json.get("chat_action")
                allow_empty_delta = (
                    isinstance(chat_action, dict)
                    and chat_action.get("action") == "clarification_answer"
                )
                if not delta.changes and not allow_empty_delta:
                    raise ValueError("an empty delta cannot create a child version")
                merged_state = apply_case_state_delta(
                    parent_version.state_json,
                    delta,
                    source_message_id=run.request_message_id,
                )
            except Exception as exc:
                if isinstance(exc, CaseStateMutationFailure):
                    raise
                raise CaseStateMutationFailure(
                    "case_state_delta_invalid",
                    "The persisted mutation delta failed deterministic validation",
                ) from exc
            if merged_state != outcome.validated_case_state_json:
                raise CaseStateMutationFailure(
                    "case_state_delta_invalid",
                    "The merged Case State does not match its delta",
                )
            case_state_version = CaseStateVersion(
                id=uuid4(),
                thread_id=thread.id,
                version=parent_version.version + 1,
                parent_version_id=parent_version.id,
                trigger_message_id=run.request_message_id,
                delta_json=delta.model_dump(mode="json"),
                state_json=deepcopy(outcome.validated_case_state_json),
            )
            db.add(case_state_version)
            await db.flush()
        elif (
            outcome.validated_case_state_json is not None
            and thread.current_case_state_version_id is None
        ):
            case_state_version = CaseStateVersion(
                id=uuid4(),
                thread_id=thread.id,
                version=1,
                parent_version_id=None,
                trigger_message_id=run.request_message_id,
                delta_json={},
                state_json=outcome.validated_case_state_json,
            )
            db.add(case_state_version)
            await db.flush()
            thread.current_case_state_version_id = case_state_version.id

        if outcome.rag_context_payload is not None:
            if case_state_version is None:
                raise ValueError(
                    "A durable RAG context requires a new case-state version"
                )
            payload = outcome.rag_context_payload
            db.add(
                RagContext(
                    retrieval_context_id=payload.retrieval_context_id,
                    thread_id=thread.id,
                    case_state_version_id=case_state_version.id,
                    context=payload.context,
                    mitre_table=deepcopy(list(payload.mitre_table)),
                )
            )

        if has_mutation and case_state_version is not None:
            thread.current_case_state_version_id = case_state_version.id

        assistant_metadata = deepcopy(outcome.metadata_json)
        if has_mutation and case_state_version is not None and parent_version is not None:
            assistant_metadata["case_update"] = build_case_update_projection(
                parent_id=parent_version.id,
                parent_version=parent_version.version,
                child_id=case_state_version.id,
                child_version=case_state_version.version,
                delta_json=case_state_version.delta_json,
            )
        elif is_no_change_case_update(assistant_metadata):
            current_version_result = await db.execute(
                select(CaseStateVersion).where(
                    CaseStateVersion.id == thread.current_case_state_version_id,
                    CaseStateVersion.thread_id == thread.id,
                )
            )
            current_version = current_version_result.scalar_one_or_none()
            if current_version is not None:
                assistant_metadata["case_update"] = build_case_update_projection(
                    parent_id=current_version.id,
                    parent_version=current_version.version,
                    child_id=None,
                    child_version=None,
                    delta_json=empty_case_state_delta(),
                )

        if outcome.analysis_trace_draft is not None:
            bound_case_state_version_id = (
                case_state_version.id
                if case_state_version is not None
                else thread.current_case_state_version_id
            )
            expected_analysis_version_id = (
                outcome.expected_analysis_case_state_version_id
            )
            if case_state_version is None and expected_analysis_version_id is None:
                raise ValueError(
                    "A reused Analysis Trace requires its loaded Case State version"
                )
            if (
                expected_analysis_version_id is not None
                and bound_case_state_version_id != expected_analysis_version_id
            ):
                raise CaseStateMutationFailure(
                    "analysis_trace_stale_case_state",
                    "The Case State changed before the analysis trace was committed",
                )
            if bound_case_state_version_id is None or not outcome.retrieval_context_id:
                raise ValueError(
                    "A validated Analysis Trace requires Case State and retrieval bindings"
                )
            if (
                outcome.rag_context_payload is not None
                and outcome.rag_context_payload.retrieval_context_id
                != outcome.retrieval_context_id
            ):
                raise ValueError(
                    "Analysis Trace retrieval binding does not match durable context"
                )
            chat_action = assistant_metadata.get("chat_action")
            expected_analysis_mode = (
                chat_action.get("analysis_mode")
                if isinstance(chat_action, dict)
                else None
            )
            if expected_analysis_mode != outcome.analysis_trace_draft.analysis_mode:
                raise ValueError(
                    "Analysis Trace mode does not match the persisted chat action"
                )
            assistant_metadata["analysis_trace"] = AnalysisTrace(
                **outcome.analysis_trace_draft.model_dump(mode="python"),
                case_state_version_id=str(bound_case_state_version_id),
                retrieval_context_id=outcome.retrieval_context_id,
            ).model_dump(mode="json")
        elif outcome.analysis_trace_failure is not None:
            assistant_metadata["analysis_trace_failure"] = (
                outcome.analysis_trace_failure.model_dump(mode="json")
            )

        assistant_message = ChatMessage(
            thread_id=thread.id,
            ordinal=thread.next_message_ordinal,
            role="assistant",
            content=outcome.content,
            retrieval_context_id=outcome.retrieval_context_id,
            metadata_json=assistant_metadata,
        )
        db.add(assistant_message)

        thread.next_message_ordinal += 1
        thread.status = outcome.thread_status
        thread.active_rag_session_id = outcome.active_rag_session_id

        run.status = "completed"
        run.error_code = None
        run.error_message = None
        run.finished_at = now
        run.lease_owner = None
        run.lease_expires_at = None
        await db.flush()

    return True
