from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot, EvidenceSource
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.schemas.caseClarifications import (
    CaseClarificationAnswer,
    CaseClarificationRead,
    ClarificationState,
)
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_materials import CaseMaterialsError, CaseMaterialsService
from app.services.followup.contracts import ClarificationExchange
from app.services.workflow.caseRunService import CaseRunError


class CaseClarificationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class CaseClarificationHistoryError(CaseClarificationError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message)


def answer_fingerprint(request: CaseClarificationAnswer) -> str:
    payload = {
        "answer": request.answer.strip(),
        "response_language": request.response_language,
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


async def _owned_case(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
    *,
    lock: bool = False,
) -> Case:
    statement = select(Case).where(Case.id == case_id)
    if lock:
        statement = statement.with_for_update()
    case = await db.scalar(statement)
    if case is None or case.user_id != user_id:
        raise CaseClarificationError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


async def _locked_case_thread(db: AsyncSession, case: Case) -> ChatThread:
    thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case.id).with_for_update())
    if thread is None:
        thread = ChatThread(case_id=case.id)
        db.add(thread)
        await db.flush()
    return thread


async def load_case_clarification_exchanges(
    db: AsyncSession,
    case_id: UUID,
) -> tuple[ClarificationExchange, ...]:
    thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
    if thread is None:
        return ()

    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == thread.id,
            ChatMessage.role == "user",
            ChatMessage.message_kind.in_(("followup_answer", "clarification_answer")),
        )
        .order_by(ChatMessage.ordinal)
    )
    answer_messages = list(result.scalars().all())
    if not answer_messages:
        return ()

    exchanges: list[ClarificationExchange] = []
    for ans_msg in answer_messages:
        question_msg = None
        if ans_msg.in_reply_to_message_id:
            question_msg = await db.get(ChatMessage, ans_msg.in_reply_to_message_id)
        if question_msg is None:
            question_msg = await db.scalar(
                select(ChatMessage)
                .where(
                    ChatMessage.thread_id == thread.id,
                    ChatMessage.ordinal < ans_msg.ordinal,
                    ChatMessage.role == "assistant",
                    ChatMessage.message_kind == "followup_question",
                )
                .order_by(ChatMessage.ordinal.desc())
            )
        if question_msg is None:
            continue

        q_meta = question_msg.metadata_json if isinstance(question_msg.metadata_json, dict) else {}
        gap_id = str(q_meta.get("gap_id") or "G-001")
        topic = str(q_meta.get("topic") or q_meta.get("clarification_topic") or "")
        gap_key = str(q_meta.get("gap_key") or f"{gap_id}:{topic.lower()}")

        snapshot_id_str = q_meta.get("evidence_snapshot_id")
        snapshot_sha = ""
        if snapshot_id_str:
            try:
                snap = await db.get(CaseEvidenceSnapshot, UUID(str(snapshot_id_str)))
                if snap:
                    snapshot_sha = snap.text_sha256
            except Exception:
                pass

        exchanges.append(
            ClarificationExchange(
                question=question_msg.content,
                answer=ans_msg.content,
                gap_id=gap_id,
                gap_topic=topic,
                gap_key=gap_key,
                evidence_sha256=snapshot_sha,
                question_message_id=str(question_msg.id),
                answer_message_id=str(ans_msg.id),
            )
        )
    return tuple(exchanges)


async def get_owned_clarifications(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None = None,
) -> list[CaseClarificationRead]:
    case = await _owned_case(db, case_id, user_id)
    thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case.id))
    if thread is None:
        if case.latest_analysis_result_id is not None:
            analysis = await db.get(CaseAnalysisResult, case.latest_analysis_result_id)
            if analysis is not None and isinstance(analysis.provider_metadata_json, dict):
                fq = analysis.provider_metadata_json.get("followup_question")
                if fq and isinstance(fq, str) and fq.strip():
                    trace_json = analysis.trace_json if isinstance(analysis.trace_json, dict) else {}
                    gaps = trace_json.get("gaps", [])
                    gap_id = "G-001"
                    topic = ""
                    if gaps and isinstance(gaps, list) and isinstance(gaps[0], dict):
                        gap_id = str(gaps[0].get("gap_id") or "G-001")
                        topic = str(gaps[0].get("description") or "")
                    return [
                        CaseClarificationRead(
                            id=analysis.id,
                            case_id=case.id,
                            origin_analysis_result_id=analysis.id,
                            origin_snapshot_id=analysis.snapshot_id,
                            gap_key=f"{gap_id}:{topic.lower()}",
                            gap_id=gap_id,
                            topic=topic,
                            question=fq.strip(),
                            metadata_json={},
                            state="pending",
                            answer_evidence_source_id=None,
                            question_message_id=None,
                            answer_message_id=None,
                            answer_fingerprint=None,
                            answered_at=None,
                            created_at=analysis.created_at,
                            updated_at=analysis.created_at,
                        )
                    ]
        return []

    q_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == thread.id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
        .order_by(ChatMessage.created_at, ChatMessage.ordinal)
    )
    question_messages = list(q_result.scalars().all())
    if not question_messages:
        return []

    a_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == thread.id,
            ChatMessage.role == "user",
            ChatMessage.message_kind.in_(("followup_answer", "clarification_answer")),
        )
        .order_by(ChatMessage.ordinal)
    )
    answer_messages = list(a_result.scalars().all())

    answers_by_question: dict[UUID, ChatMessage] = {}
    for ans in answer_messages:
        if ans.in_reply_to_message_id:
            answers_by_question[ans.in_reply_to_message_id] = ans

    clarifications: list[CaseClarificationRead] = []
    for q_msg in question_messages:
        q_meta = q_msg.metadata_json if isinstance(q_msg.metadata_json, dict) else {}
        ans_msg = answers_by_question.get(q_msg.id)
        if ans_msg is None:
            for ans in answer_messages:
                if ans.ordinal > q_msg.ordinal and (ans.in_reply_to_message_id is None or ans.in_reply_to_message_id == q_msg.id):
                    ans_msg = ans
                    break

        origin_result_id = q_msg.analysis_result_id
        if origin_result_id is None:
            raise CaseClarificationHistoryError(
                "clarification_context_invalid",
                "Clarification question has no pinned analysis result",
            )
        origin_result = await db.get(CaseAnalysisResult, origin_result_id)
        if origin_result is None or origin_result.case_id != case.id:
            raise CaseClarificationHistoryError(
                "clarification_context_invalid",
                "Clarification question has an invalid analysis result",
            )
        origin_snapshot_id = origin_result.snapshot_id
        gap_id = str(q_meta.get("gap_id") or "G-001")
        topic = str(q_meta.get("topic") or q_meta.get("clarification_topic") or "")
        gap_key = str(q_meta.get("gap_key") or f"{gap_id}:{topic.lower()}")

        if ans_msg is not None:
            state: ClarificationState = "answered"
            ans_meta = ans_msg.metadata_json if isinstance(ans_msg.metadata_json, dict) else {}
            src_id_str = ans_meta.get("case_evidence_source_id")
            answer_source_id = UUID(str(src_id_str)) if src_id_str else None
            answer_msg_id = ans_msg.id
            answered_at = ans_msg.created_at
            fingerprint = answer_fingerprint(CaseClarificationAnswer(answer=ans_msg.content, idempotency_key="read"))
        else:
            if case.latest_analysis_result_id and case.latest_analysis_result_id != origin_result_id:
                state = "superseded"
            else:
                state = "pending"
            answer_source_id = None
            answer_msg_id = None
            answered_at = None
            fingerprint = None

        clarification_id = UUID(str(q_meta.get("clarification_id"))) if q_meta.get("clarification_id") else q_msg.id

        clarifications.append(
            CaseClarificationRead(
                id=clarification_id,
                case_id=case.id,
                origin_analysis_result_id=origin_result_id,
                origin_snapshot_id=origin_snapshot_id,
                gap_key=gap_key,
                gap_id=gap_id,
                topic=topic,
                question=q_msg.content,
                metadata_json=q_meta,
                state=state,
                answer_evidence_source_id=answer_source_id,
                question_message_id=q_msg.id,
                answer_message_id=answer_msg_id,
                answer_fingerprint=fingerprint,
                answered_at=answered_at,
                created_at=q_msg.created_at,
                updated_at=answered_at or q_msg.created_at,
            )
        )
    return clarifications


async def submit_clarification_answer(
    db: AsyncSession,
    *,
    case_id: UUID,
    clarification_id: UUID,
    user_id: UUID | None,
    request: CaseClarificationAnswer,
) -> tuple[CaseClarificationRead, CaseRun]:
    case = await _owned_case(db, case_id, user_id, lock=True)
    thread = await _locked_case_thread(db, case)

    q_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == thread.id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
        .order_by(ChatMessage.ordinal.desc())
    )
    questions = list(q_result.scalars().all())
    question = None
    for q in questions:
        q_meta = q.metadata_json if isinstance(q.metadata_json, dict) else {}
        if q.id == clarification_id or q_meta.get("clarification_id") == str(clarification_id):
            question = q
            break

    if question is None and case.latest_analysis_result_id is not None:
        analysis = await db.get(CaseAnalysisResult, case.latest_analysis_result_id)
        if analysis is not None and (analysis.id == clarification_id or str(analysis.id) == str(clarification_id)):
            fq = (analysis.provider_metadata_json or {}).get("followup_question")
            if fq and isinstance(fq, str) and fq.strip():
                trace_json = analysis.trace_json if isinstance(analysis.trace_json, dict) else {}
                gaps = trace_json.get("gaps", [])
                gap_id = "G-001"
                topic = ""
                if gaps and isinstance(gaps, list) and isinstance(gaps[0], dict):
                    gap_id = str(gaps[0].get("gap_id") or "G-001")
                    topic = str(gaps[0].get("description") or "")
                gap_key = f"{gap_id}:{topic.lower()}"
                question = ChatMessage(
                    id=uuid4(),
                    thread_id=thread.id,
                    ordinal=thread.next_message_ordinal,
                    role="assistant",
                    content=fq.strip(),
                    message_kind="followup_question",
                    analysis_result_id=analysis.id,
                    metadata_json=serialize_message_metadata(
                        {
                            "clarification_id": str(clarification_id),
                            "gap_id": gap_id,
                            "topic": topic,
                            "gap_key": gap_key,
                        }
                    ),
                )
                db.add(question)
                thread.next_message_ordinal += 1
                await db.flush()

    if question is None:
        raise CaseClarificationError("clarification_not_found", "Clarification not found", status.HTTP_404_NOT_FOUND)

    existing_answer = await db.scalar(
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == thread.id,
            ChatMessage.role == "user",
            ChatMessage.message_kind.in_(("followup_answer", "clarification_answer")),
            ChatMessage.in_reply_to_message_id == question.id,
        )
    )
    fingerprint = answer_fingerprint(request)
    if existing_answer is not None:
        existing_fp = answer_fingerprint(CaseClarificationAnswer(answer=existing_answer.content, idempotency_key="check"))
        if existing_fp != fingerprint:
            raise CaseClarificationError("clarification_answer_conflict", "Clarification already has another answer")
        run = await db.scalar(
            select(CaseRun)
            .where(CaseRun.case_id == case.id, CaseRun.request_message_id == existing_answer.id)
            .order_by(CaseRun.created_at.desc())
            .with_for_update()
        )
        if run is None:
            run = await db.scalar(
                select(CaseRun)
                .where(CaseRun.case_id == case.id)
                .order_by(CaseRun.created_at.desc())
                .with_for_update()
            )
        if run is None:
            raise CaseClarificationError("clarification_run_missing", "Clarification answer run is missing")
        if run.status == "failed":
            from app.services.workflow.caseRunService import requeue_failed_case_run

            try:
                await requeue_failed_case_run(db, case, run)
            except CaseRunError as error:
                raise CaseClarificationError(error.code, error.message, error.status_code) from error

        read_items = await get_owned_clarifications(db, case_id=case.id, user_id=user_id)
        clarification_read = next((item for item in read_items if item.id == clarification_id or item.question_message_id == question.id), None)
        if clarification_read is None:
            raise CaseClarificationError("clarification_not_found", "Clarification not found", status.HTTP_404_NOT_FOUND)
        return clarification_read, run

    if case.latest_analysis_result_id and question.analysis_result_id and case.latest_analysis_result_id != question.analysis_result_id:
        raise CaseClarificationError("clarification_superseded", "This clarification belongs to an older analysis")
    if question.analysis_result_id is None:
        raise CaseClarificationError("clarification_context_invalid", "This clarification has no pinned analysis result")
    question_result = await db.get(CaseAnalysisResult, question.analysis_result_id)
    if question_result is None or question_result.case_id != case.id:
        raise CaseClarificationError("clarification_context_invalid", "This clarification has an invalid analysis result")

    active = await db.scalar(
        select(CaseRun.id).where(CaseRun.case_id == case.id, CaseRun.status.in_(("queued", "running")))
    )
    if active is not None:
        raise CaseClarificationError("case_run_active", "Case already has an active analysis run")

    message = ChatMessage(
        thread_id=thread.id,
        ordinal=thread.next_message_ordinal,
        role="user",
        content=request.answer.strip(),
        message_kind="followup_answer",
        analysis_result_id=question.analysis_result_id,
        in_reply_to_message_id=question.id,
        metadata_json=serialize_message_metadata(
            {
                "evidence_kind": "clarification_answer",
                "analysis_kind": "clarification_answer",
                "clarification_id": str(clarification_id),
                "in_reply_to_message_id": str(question.id),
            }
        ),
    )
    db.add(message)
    await db.flush()

    try:
        from app.services.workflow.caseRunService import enqueue_case_analysis

        source = await CaseMaterialsService(db).admitText(
            case_id=case.id,
            user_id=user_id,
            source_kind="followup_answer",
            exact_text=request.answer,
            provenance_json={
                "origin": "case_clarification",
                "clarification_id": str(clarification_id),
                "origin_message_id": str(message.id),
            },
            source_metadata_json={
                "clarification_id": str(clarification_id),
                "origin_message_id": str(message.id),
            },
            origin_message_id=message.id,
        )
        run = await enqueue_case_analysis(
            db,
            case_id=case.id,
            user_id=user_id,
            request=request.model_copy(update={"expected_evidence_revision": case.evidence_revision}),
            request_message_id=message.id,
            request_payload_extra={
                "content": request.answer.strip(),
                "action": "clarification_answer",
            },
        )
    except (CaseMaterialsError, CaseRunError) as error:
        raise CaseClarificationError(error.code, error.message, getattr(error, "status_code", 409)) from error

    message.metadata_json = serialize_message_metadata(
        {
            **message.metadata_json,
            "case_evidence_source_id": str(source.id),
            "case_evidence_revision": max(item.revision for item in source.revisions),
        }
    )
    thread.next_message_ordinal += 1
    thread.updated_at = datetime.now(timezone.utc)
    await db.flush()

    read_items = await get_owned_clarifications(db, case_id=case.id, user_id=user_id)
    clarification_read = next((item for item in read_items if item.id == clarification_id or item.question_message_id == question.id), None)
    if clarification_read is None:
        raise CaseClarificationError("clarification_not_found", "Clarification read serialization failed")
    return clarification_read, run


async def find_answered_clarification(
    db: AsyncSession,
    *,
    case_id: UUID,
    request: CaseClarificationAnswer,
) -> CaseClarificationRead | None:
    clarifications = await get_owned_clarifications(db, case_id=case_id, user_id=None)
    fp = answer_fingerprint(request)
    for c in reversed(clarifications):
        if c.state == "answered" and c.answer_fingerprint == fp:
            return c
    return None


async def create_pending_clarification(*args, **kwargs):
    return None


async def supersede_prior_clarifications(*args, **kwargs):
    return None


answerFingerprint = answer_fingerprint
createPendingClarification = create_pending_clarification
findAnsweredClarification = find_answered_clarification
getOwnedClarifications = get_owned_clarifications
loadCaseClarificationExchanges = load_case_clarification_exchanges
submitClarificationAnswer = submit_clarification_answer
supersedePriorClarifications = supersede_prior_clarifications

__all__ = [
    "CaseClarificationError",
    "CaseClarificationHistoryError",
    "answerFingerprint",
    "answer_fingerprint",
    "createPendingClarification",
    "create_pending_clarification",
    "findAnsweredClarification",
    "find_answered_clarification",
    "getOwnedClarifications",
    "get_owned_clarifications",
    "loadCaseClarificationExchanges",
    "load_case_clarification_exchanges",
    "submitClarificationAnswer",
    "submit_clarification_answer",
    "supersedePriorClarifications",
    "supersede_prior_clarifications",
]
