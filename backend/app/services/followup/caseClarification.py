from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.caseClarification import CaseClarification
from app.models.caseMaterials import EvidenceSource
from app.models.caseRun import CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.schemas.messageMetadata import serialize_message_metadata
from app.schemas.caseClarifications import CaseClarificationAnswer
from app.services.case_materials import CaseMaterialsService
from app.services.case_materials import CaseMaterialsError
from app.services.followup.contracts import ClarificationExchange
from app.services.workflow.caseRunService import CaseRunError


class CaseClarificationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def create_pending_clarification(
    db: AsyncSession,
    *,
    case_id: UUID,
    result_id: UUID,
    snapshot_id: UUID,
    question: str,
    metadata: dict[str, object],
) -> CaseClarification:
    gap_id = metadata.get("gap_id")
    topic = metadata.get("topic")
    gap_key = metadata.get("gap_key")
    if not all(isinstance(value, str) and value.strip() for value in (gap_id, topic, gap_key)):
        raise CaseClarificationError(
            "clarification_metadata_missing",
            "A clarification requires a stable gap identity and topic",
        )
    if not question.strip():
        raise CaseClarificationError("clarification_question_missing", "Clarification question is empty")
    existing = await db.scalar(
        select(CaseClarification).where(
            CaseClarification.origin_analysis_result_id == result_id,
            CaseClarification.gap_key == gap_key,
        ).with_for_update()
    )
    if existing is not None:
        return existing
    clarification = CaseClarification(
        case_id=case_id,
        origin_analysis_result_id=result_id,
        origin_snapshot_id=snapshot_id,
        gap_key=gap_key,
        gap_id=gap_id,
        topic=topic,
        question=question.strip(),
        metadata_json=deepcopy(metadata),
    )
    db.add(clarification)
    await db.flush()
    return clarification


async def supersede_prior_clarifications(
    db: AsyncSession,
    *,
    case_id: UUID,
    result_id: UUID,
) -> None:
    await db.execute(
        update(CaseClarification)
        .where(
            CaseClarification.case_id == case_id,
            CaseClarification.origin_analysis_result_id != result_id,
            CaseClarification.state == "pending",
        )
        .values(state="superseded", updated_at=datetime.now(timezone.utc))
    )


class CaseClarificationHistoryError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


async def load_case_clarification_exchanges(
    db: AsyncSession,
    case_id: UUID,
) -> tuple[ClarificationExchange, ...]:
    result = await db.execute(
        select(CaseClarification)
        .options(
            selectinload(CaseClarification.answer_evidence_source).selectinload(
                EvidenceSource.revisions
            ),
            selectinload(CaseClarification.origin_snapshot),
        )
        .where(
            CaseClarification.case_id == case_id,
            CaseClarification.state == "answered",
        )
        .order_by(CaseClarification.answered_at, CaseClarification.created_at, CaseClarification.id)
    )
    exchanges: list[ClarificationExchange] = []
    for clarification in result.scalars().all():
        source = clarification.answer_evidence_source
        snapshot = clarification.origin_snapshot
        metadata = clarification.metadata_json
        revision_number = metadata.get("answer_evidence_revision") if isinstance(metadata, dict) else None
        if source is None or type(revision_number) is not int or revision_number < 1:
            raise CaseClarificationHistoryError(
                "clarification_history_invalid",
                "Answered clarification evidence provenance is incomplete",
            )
        revision = next(
            (item for item in source.revisions if item.revision == revision_number),
            None,
        )
        if (
            revision is None
            or not revision.exact_text.strip()
            or source.case_id != case_id
            or snapshot is None
            or snapshot.case_id != case_id
            or hashlib.sha256(revision.exact_text.encode("utf-8")).hexdigest() != revision.text_sha256
            or hashlib.sha256(snapshot.input_text.encode("utf-8")).hexdigest() != snapshot.text_sha256
        ):
            raise CaseClarificationHistoryError(
                "clarification_history_invalid",
                "Answered clarification evidence history is unavailable",
            )
        exchanges.append(
            ClarificationExchange(
                question=clarification.question,
                answer=revision.exact_text,
                gap_id=clarification.gap_id,
                gap_topic=clarification.topic,
                gap_key=clarification.gap_key,
                evidence_sha256=snapshot.text_sha256,
                question_message_id=(
                    str(clarification.question_message_id)
                    if clarification.question_message_id
                    else None
                ),
                answer_message_id=(
                    str(clarification.answer_message_id)
                    if clarification.answer_message_id
                    else None
                ),
            )
        )
    return tuple(exchanges)


async def get_owned_clarifications(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> list[CaseClarification]:
    await _owned_case(db, case_id, user_id)
    result = await db.execute(
        select(CaseClarification)
        .where(CaseClarification.case_id == case_id)
        .order_by(CaseClarification.created_at, CaseClarification.id)
    )
    return list(result.scalars().all())


async def submit_clarification_answer(
    db: AsyncSession,
    *,
    case_id: UUID,
    clarification_id: UUID,
    user_id: UUID | None,
    request: CaseClarificationAnswer,
) -> tuple[CaseClarification, CaseRun]:
    case = await _owned_case(db, case_id, user_id, lock=True)
    thread = await _locked_case_thread(db, case)
    clarification = await db.scalar(
        select(CaseClarification)
        .where(CaseClarification.id == clarification_id, CaseClarification.case_id == case.id)
        .with_for_update()
    )
    if clarification is None:
        raise CaseClarificationError("clarification_not_found", "Clarification not found", status.HTTP_404_NOT_FOUND)
    fingerprint = answer_fingerprint(request)
    if clarification.state == "answered":
        if clarification.answer_fingerprint != fingerprint:
            raise CaseClarificationError("clarification_answer_conflict", "Clarification already has another answer")
        run = await db.scalar(
            select(CaseRun)
            .where(CaseRun.clarification_id == clarification.id)
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
        return clarification, run
    if clarification.state == "superseded":
        raise CaseClarificationError("clarification_superseded", "This clarification belongs to an older analysis")
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
        message_kind="clarification_answer",
        metadata_json=serialize_message_metadata(
            {
                "evidence_kind": "clarification_answer",
                "analysis_kind": "clarification_answer",
                "clarification_id": str(clarification.id),
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
            source_kind="clarification_answer",
            exact_text=request.answer,
            provenance_json={
                "origin": "case_clarification",
                "clarification_id": str(clarification.id),
                "origin_analysis_result_id": str(clarification.origin_analysis_result_id),
                "origin_message_id": str(message.id),
            },
            source_metadata_json={
                "clarification_id": str(clarification.id),
                "origin_message_id": str(message.id),
            },
            origin_message_id=message.id,
        )
        run = await enqueue_case_analysis(
            db,
            case_id=case.id,
            user_id=user_id,
            request=request.model_copy(update={"expected_evidence_revision": case.evidence_revision}),
            clarification_id=clarification.id,
            request_message_id=message.id,
            request_payload_extra={
                "content": request.answer.strip(),
                "action": "clarification_answer",
            },
        )
    except (CaseMaterialsError, CaseRunError) as error:
        raise CaseClarificationError(error.code, error.message, getattr(error, "status_code", 409)) from error
    clarification.state = "answered"
    clarification.answer_evidence_source_id = source.id
    clarification.answer_message_id = message.id
    clarification.answer_fingerprint = fingerprint
    clarification.metadata_json = {
        **clarification.metadata_json,
        "answer_evidence_revision": max(item.revision for item in source.revisions),
    }
    clarification.answered_at = datetime.now(timezone.utc)
    await db.flush()
    message.metadata_json = serialize_message_metadata(
        {
            **message.metadata_json,
            "case_evidence_source_id": str(source.id),
            "case_evidence_revision": max(item.revision for item in source.revisions),
        }
    )
    thread.next_message_ordinal += 1
    thread.status = "processing"
    thread.updated_at = datetime.now(timezone.utc)
    return clarification, run


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
        thread = ChatThread(case_id=case.id, title=case.title, user_id=case.user_id)
        db.add(thread)
        await db.flush()
    return thread


async def find_answered_clarification(
    db: AsyncSession,
    *,
    case_id: UUID,
    request: CaseClarificationAnswer,
) -> CaseClarification | None:
    return await db.scalar(
        select(CaseClarification).where(
            CaseClarification.case_id == case_id,
            CaseClarification.state == "answered",
            CaseClarification.answer_fingerprint == answer_fingerprint(request),
        ).order_by(CaseClarification.answered_at.desc())
    )


def answer_fingerprint(request: CaseClarificationAnswer) -> str:
    payload = {
        "answer": request.answer.strip(),
        "response_language": request.response_language,
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


createPendingClarification = create_pending_clarification
loadCaseClarificationExchanges = load_case_clarification_exchanges
findAnsweredClarification = find_answered_clarification
getOwnedClarifications = get_owned_clarifications
submitClarificationAnswer = submit_clarification_answer
supersedePriorClarifications = supersede_prior_clarifications
answerFingerprint = answer_fingerprint

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
