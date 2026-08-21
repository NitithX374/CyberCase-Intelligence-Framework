"""Claim, lease-lock, and finalize persistent chat background runs."""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_state import CaseStateVersion
from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.services.case_state.mutator import (
    MUTATION_METADATA_KEY,
    CaseStateDelta,
    CaseStateMutationFailure,
    apply_case_state_delta,
)
from app.services.case_state.raw_evidence import resolve_raw_case_evidence_history
from app.services.case_state.update_projection import (
    build_case_update_projection,
    empty_case_state_delta,
)
from app.services.case_analysis.contracts import AnalysisTrace
from app.services.chat.chat_message import reconstruct_clarification_chain
from app.services.extraction.llm_extraction import (
    EXTRACTION_METADATA_KEY,
    ExtractionInput,
    ExtractionSourceMessage,
    build_extraction_input,
)
from app.services.followup.schemas import ClarificationExchange
from app.services.workflow.outcome import AssistantOutcome


logger = logging.getLogger("app.chat")
RUN_LEASE_DURATION = timedelta(minutes=6)


def _is_no_change_case_update(metadata: dict[str, Any]) -> bool:
    action = metadata.get("chat_action")
    return (
        isinstance(action, dict)
        and action.get("action") == "add_case_info"
        and action.get("status") == "no_change"
        and action.get("state_mutated") is False
    )


@dataclass(frozen=True)
class ClaimedChatRun:
    """Detached input needed after the claim transaction has closed."""

    id: UUID
    operation: str
    input_rag_session_id: str | None
    content: object
    rag_query: object
    original_user_content: object
    clarification_exchanges: tuple[ClarificationExchange, ...]
    followup_root_ordinal: int
    pending_question: str | None = None
    extraction_input: ExtractionInput | None = None
    post_answer_action: str | None = None
    clarification_answer: bool = False
    request_message_id: UUID | None = None
    case_state_version_id: UUID | None = None
    case_state_json: dict[str, object] | None = None
    analysis_context: dict[str, object] | None = None
    raw_case_narrative: str | None = None


class ChatRunWorker:
    """Perform short, lease-guarded database transitions for one chat run."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def claim_run(
        self,
        run_id: UUID,
        worker_id: str,
    ) -> ClaimedChatRun | None:
        now = datetime.now(timezone.utc)

        async with self.db.begin():
            statement = (
                select(ChatRun)
                .where(
                    ChatRun.id == run_id,
                    ChatRun.status == "queued",
                )
                .with_for_update(skip_locked=True)
            )
            result = await self.db.execute(statement)
            run = result.scalar_one_or_none()
            if run is None:
                return None

            run.status = "running"
            run.attempt_count += 1
            run.lease_owner = worker_id
            run.lease_expires_at = now + RUN_LEASE_DURATION
            run.started_at = now

            request_payload = run.request_payload
            content = (
                request_payload.get("content")
                if isinstance(request_payload, dict)
                else None
            )
            rag_query = (
                request_payload.get("rag_query", content)
                if isinstance(request_payload, dict)
                else None
            )
            requested_root_ordinal = (
                request_payload.get("followup_root_ordinal")
                if isinstance(request_payload, dict)
                else None
            )
            if (
                not isinstance(requested_root_ordinal, int)
                or isinstance(requested_root_ordinal, bool)
                or requested_root_ordinal < 1
            ):
                requested_root_ordinal = None
            requested_round = (
                request_payload.get("followup_round")
                if isinstance(request_payload, dict)
                else None
            )
            if (
                not isinstance(requested_round, int)
                or isinstance(requested_round, bool)
                or requested_round < 0
            ):
                requested_round = None
            legacy_followup = (
                request_payload.get("skip_followup_policy") is True
                if isinstance(request_payload, dict)
                else False
            )
            post_answer_action = (
                request_payload.get("action")
                if isinstance(request_payload, dict)
                else None
            )
            if post_answer_action not in (None, "ask", "add_case_info"):
                post_answer_action = None
            clarification_answer = (
                isinstance(request_payload, dict)
                and request_payload.get("clarification_answer") is True
            )

            case_state_json: dict[str, object] | None = None
            analysis_context: dict[str, object] | None = None
            case_state_version_id: UUID | None = None
            requested_parent_version_id: UUID | None = None
            if isinstance(request_payload, dict):
                raw_parent_version_id = request_payload.get("case_state_version_id")
                if raw_parent_version_id is not None:
                    try:
                        requested_parent_version_id = UUID(str(raw_parent_version_id))
                    except (TypeError, ValueError, AttributeError):
                        requested_parent_version_id = None
            if post_answer_action in ("ask", "add_case_info"):
                pointer_result = await self.db.execute(
                    select(ChatThread.current_case_state_version_id).where(
                        ChatThread.id == run.thread_id,
                    )
                )
                current_state_version_id = pointer_result.scalar_one_or_none()
                state_lookup_id = (
                    requested_parent_version_id
                    if post_answer_action == "add_case_info"
                    and requested_parent_version_id is not None
                    else current_state_version_id
                )
                if state_lookup_id is not None:
                    case_state_version_id = state_lookup_id
                    state_result = await self.db.execute(
                        select(CaseStateVersion).where(
                            CaseStateVersion.id == state_lookup_id,
                            CaseStateVersion.thread_id == run.thread_id,
                        )
                    )
                    case_state = state_result.scalar_one_or_none()
                    if case_state is not None and isinstance(
                        case_state.state_json,
                        dict,
                    ):
                        case_state_json = deepcopy(case_state.state_json)
                        if post_answer_action == "ask":
                            rag_context_result = await self.db.execute(
                                select(RagContext).where(
                                    RagContext.thread_id == run.thread_id,
                                    RagContext.case_state_version_id
                                    == state_lookup_id,
                                )
                            )
                            rag_context = rag_context_result.scalar_one_or_none()
                            if rag_context is not None:
                                mitre_table = rag_context.mitre_table
                                analysis_context = {
                                    "retrieved_context": (
                                        rag_context.context
                                        if isinstance(rag_context.context, str)
                                        else ""
                                    ),
                                    "retrieval_context_id": rag_context.retrieval_context_id,
                                    "mitre_table": (
                                        deepcopy(mitre_table)
                                        if isinstance(mitre_table, list)
                                        else []
                                    ),
                                    "previous_analysis": None,
                                }

            original_user_content: object = content
            clarification_exchanges: tuple[ClarificationExchange, ...] = ()
            pending_question: str | None = None
            followup_root_ordinal = requested_root_ordinal
            history: list[ChatMessage] | None = None
            if requested_root_ordinal is not None and requested_round == 0:
                pass
            elif requested_root_ordinal is None and not legacy_followup:
                request_message_result = await self.db.execute(
                    select(ChatMessage).where(
                        ChatMessage.id == run.request_message_id
                    )
                )
                request_message = request_message_result.scalar_one_or_none()
                if request_message is not None:
                    original_user_content = request_message.content
                    followup_root_ordinal = request_message.ordinal
            else:
                history_result = await self.db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.thread_id == run.thread_id)
                    .order_by(ChatMessage.ordinal)
                )
                history = history_result.scalars().all()
                request_index = next(
                    (
                        index
                        for index, message in enumerate(history)
                        if message.id == run.request_message_id
                    ),
                    None,
                )
                if request_index is None:
                    thread_result = await self.db.execute(
                        select(ChatThread)
                        .where(ChatThread.id == run.thread_id)
                        .with_for_update()
                    )
                    thread = thread_result.scalar_one_or_none()
                    if thread is not None:
                        thread.status = (
                            "awaiting_followup"
                            if isinstance(requested_round, int)
                            and not isinstance(requested_round, bool)
                            and requested_round > 0
                            else "failed"
                        )
                        thread.active_rag_session_id = None
                    run.status = "failed"
                    run.error_code = "chat_followup_request_missing"
                    run.error_message = (
                        "The persisted chat request could not be reconstructed."
                    )
                    run.finished_at = now
                    run.lease_owner = None
                    run.lease_expires_at = None
                    await self.db.flush()
                    return None
                history = history[: request_index + 1]
                chain = reconstruct_clarification_chain(
                    history,
                    root_ordinal=requested_root_ordinal,
                )
                if chain is not None:
                    original_user_content = chain.original_user_content
                    clarification_exchanges = chain.exchanges
                    pending_question = chain.pending_question
                    followup_root_ordinal = chain.root_ordinal
                if followup_root_ordinal is None:
                    request_message = next(
                        (
                            message
                            for message in history
                            if message.id == run.request_message_id
                        ),
                        None,
                    )
                    if request_message is not None:
                        original_user_content = request_message.content
                        followup_root_ordinal = request_message.ordinal
            if followup_root_ordinal is None:
                followup_root_ordinal = 1

            extraction_input: ExtractionInput | None = None
            if post_answer_action in (None, "add_case_info"):
                try:
                    if history is not None:
                        extraction_input = build_extraction_input(
                            thread_id=run.thread_id,
                            messages=history,
                            root_ordinal=followup_root_ordinal,
                        )
                    elif isinstance(content, str):
                        extraction_input = ExtractionInput(
                            thread_id=run.thread_id,
                            messages=[
                                ExtractionSourceMessage(
                                    message_id=run.request_message_id,
                                    ordinal=followup_root_ordinal,
                                    source_type="user_case_statement",
                                    content=content,
                                )
                            ],
                        )
                except (TypeError, ValueError):
                    logger.warning(
                        "Chat extraction source packet could not be built "
                        "run_id=%s",
                        run.id,
                    )

            if requested_round == 0 and post_answer_action is None and isinstance(content, str) and content.strip():
                raw_case_narrative = content.strip()
            else:
                raw_case_narrative = await resolve_raw_case_evidence_history(
                    self.db,
                    thread_id=run.thread_id,
                    current_request_message_id=run.request_message_id,
                    current_request_payload=(
                        request_payload if isinstance(request_payload, dict) else {}
                    ),
                    current_content=content if isinstance(content, str) else None,
                    history=history,
                )

            claimed_run = ClaimedChatRun(
                id=run.id,
                operation=run.operation,
                input_rag_session_id=run.input_rag_session_id,
                content=content,
                rag_query=rag_query,
                original_user_content=original_user_content,
                clarification_exchanges=clarification_exchanges,
                pending_question=pending_question,
                followup_root_ordinal=followup_root_ordinal,
                extraction_input=extraction_input,
                post_answer_action=post_answer_action,
                clarification_answer=clarification_answer,
                request_message_id=run.request_message_id,
                case_state_version_id=case_state_version_id,
                case_state_json=case_state_json,
                analysis_context=analysis_context,
                raw_case_narrative=raw_case_narrative,
            )
            await self.db.flush()

        return claimed_run

    async def complete_run(
        self,
        run_id: UUID,
        worker_id: str,
        outcome: AssistantOutcome,
    ) -> bool:
        """Persist an assistant message only while this invocation owns the lease."""

        now = datetime.now(timezone.utc)
        async with self.db.begin():
            thread = await self._lock_run_thread(run_id)
            if thread is None:
                return False

            run = await self._lock_owned_running_run(run_id, worker_id)
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
                parent_result = await self.db.execute(
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
                self.db.add(case_state_version)
                await self.db.flush()
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
                self.db.add(case_state_version)
                await self.db.flush()
                thread.current_case_state_version_id = case_state_version.id

            if outcome.rag_context_payload is not None:
                if case_state_version is None:
                    raise ValueError(
                        "A durable RAG context requires a new case-state version"
                    )
                payload = outcome.rag_context_payload
                self.db.add(
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
            elif _is_no_change_case_update(assistant_metadata):
                current_version_result = await self.db.execute(
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
            self.db.add(assistant_message)

            thread.next_message_ordinal += 1
            thread.status = outcome.thread_status
            thread.active_rag_session_id = outcome.active_rag_session_id

            run.status = "completed"
            run.error_code = None
            run.error_message = None
            run.finished_at = now
            run.lease_owner = None
            run.lease_expires_at = None
            await self.db.flush()

        return True

    async def fail_run(
        self,
        run_id: UUID,
        worker_id: str,
        error_code: str,
        error_message: str,
        followup_metadata_json: dict[str, Any] | None = None,
    ) -> bool:
        """Persist a safe failure without exposing upstream response content."""

        now = datetime.now(timezone.utc)
        async with self.db.begin():
            thread = await self._lock_run_thread(run_id)
            if thread is None:
                return False

            run = await self._lock_owned_running_run(run_id, worker_id)
            if run is None or run.thread_id != thread.id:
                return False

            request_payload = run.request_payload
            if followup_metadata_json:
                updated_payload = dict(request_payload or {})
                for audit_key in (
                    "chat_followup",
                    EXTRACTION_METADATA_KEY,
                    MUTATION_METADATA_KEY,
                ):
                    audit_value = followup_metadata_json.get(audit_key)
                    if isinstance(audit_value, dict):
                        updated_payload[audit_key] = audit_value
                if updated_payload != dict(request_payload or {}):
                    run.request_payload = updated_payload
            followup_round = (
                request_payload.get("followup_round")
                if isinstance(request_payload, dict)
                else None
            )
            thread.status = (
                "awaiting_followup"
                if isinstance(followup_round, int)
                and not isinstance(followup_round, bool)
                and followup_round > 0
                else "failed"
            )
            thread.active_rag_session_id = None

            run.status = "failed"
            run.error_code = error_code
            run.error_message = error_message
            run.finished_at = now
            run.lease_owner = None
            run.lease_expires_at = None
            await self.db.flush()

        return True

    async def _lock_run_thread(self, run_id: UUID) -> ChatThread | None:
        """Lock the parent thread before the run to match message creation order."""

        thread_id_result = await self.db.execute(
            select(ChatRun.thread_id).where(ChatRun.id == run_id)
        )
        thread_id = thread_id_result.scalar_one_or_none()
        if thread_id is None:
            return None

        thread_result = await self.db.execute(
            select(ChatThread)
            .where(ChatThread.id == thread_id)
            .with_for_update()
        )
        return thread_result.scalar_one_or_none()

    async def _lock_owned_running_run(
        self,
        run_id: UUID,
        worker_id: str,
    ) -> ChatRun | None:
        result = await self.db.execute(
            select(ChatRun).where(ChatRun.id == run_id).with_for_update()
        )
        run = result.scalar_one_or_none()
        if (
            run is None
            or run.status != "running"
            or run.lease_owner != worker_id
        ):
            return None
        return run


__all__ = [
    "ChatRunWorker",
    "ClaimedChatRun",
    "RUN_LEASE_DURATION",
]
