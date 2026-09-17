from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.services.case_analysis.analysis_trace_contracts import CaseAnalysisTrace


@dataclass(frozen=True)
class CaseChatContext:
    current_evidence_revision: int
    analysis_evidence_revision: int | None
    analysis_context: dict[str, object] | None
    active_clarification: dict[str, object] | None
    technical_context: dict[str, object] | None
    conversation_history: list[dict[str, str]]


async def load_case_chat_context(
    db: AsyncSession,
    *,
    case: Case,
    current_message_ordinal: int,
) -> CaseChatContext:
    analysis = await _load_latest_analysis(db, case)
    messages = await _load_chat_messages(
        db,
        case=case,
        current_message_ordinal=current_message_ordinal,
    )
    active_clarification = _active_clarification(messages, case, analysis)
    history = _conversation_history(messages)
    analysis_context = _analysis_context(case, analysis)
    technical_context = _technical_context(analysis)
    return CaseChatContext(
        current_evidence_revision=case.evidence_revision,
        analysis_evidence_revision=analysis.evidence_revision if analysis else None,
        analysis_context=analysis_context,
        active_clarification=active_clarification,
        technical_context=technical_context,
        conversation_history=history,
    )


async def _load_latest_analysis(
    db: AsyncSession,
    case: Case,
) -> CaseAnalysisResult | None:
    if case.latest_analysis_result_id is None:
        return None
    return await db.scalar(
        select(CaseAnalysisResult)
        .options(selectinload(CaseAnalysisResult.run).selectinload(CaseRun.rag_context))
        .where(
            CaseAnalysisResult.id == case.latest_analysis_result_id,
            CaseAnalysisResult.case_id == case.id,
        )
    )


async def _load_chat_messages(
    db: AsyncSession,
    *,
    case: Case,
    current_message_ordinal: int,
) -> list[ChatMessage]:
    return list(
        (
            await db.scalars(
                select(ChatMessage)
                .where(
                    ChatMessage.case_id == case.id,
                    ChatMessage.ordinal < current_message_ordinal,
                )
                .order_by(ChatMessage.ordinal.desc())
                .limit(64)
            )
        ).all()
    )


def _active_clarification(
    messages: list[ChatMessage],
    case: Case,
    latest_analysis: CaseAnalysisResult | None,
) -> dict[str, object] | None:
    questions = [
        message for message in messages if message.message_kind == "followup_question"
    ]
    if not questions:
        return None
    answered_ids = {
        message.in_reply_to_message_id
        for message in messages
        if message.message_kind == "followup_answer"
    }
    question = next((item for item in questions if item.id not in answered_ids), None)
    if question is None:
        return None
    followup = _followup_metadata(question)
    gap = followup.get("gap")
    gap_data = dict(gap) if isinstance(gap, dict) else {}
    source_analysis_id = _optional_text(followup.get("source_analysis_id"))
    source_revision = followup.get("source_revision")
    current = bool(
        latest_analysis
        and source_analysis_id == str(latest_analysis.id)
        and source_revision == case.evidence_revision
    )
    return {
        "status": "current" if current else "stale",
        "question_message_id": str(question.id),
        "question": _clip(question.content, 4_000),
        "gap_id": _optional_text(gap_data.get("gap_id")),
        "gap_key": _optional_text(gap_data.get("gap_key")),
        "topic": _clip_optional(gap_data.get("topic"), 500),
        "target_information": _clip_optional(followup.get("target_information"), 1_000),
        "rationale_summary": _clip_optional(
            followup.get("rationale_summary") or gap_data.get("reason"),
            1_000,
        ),
        "source_analysis_id": source_analysis_id,
        "source_evidence_revision": source_revision,
        "clarification_session_id": _optional_text(followup.get("clarification_session_id")),
    }


def _conversation_history(messages: list[ChatMessage]) -> list[dict[str, str]]:
    return [
        {"role": message.role, "content": message.content}
        for message in reversed(messages[:12])
        if message.content
    ]


def _analysis_context(
    case: Case,
    analysis: CaseAnalysisResult | None,
) -> dict[str, object] | None:
    if analysis is None:
        return None
    freshness = "current" if analysis.evidence_revision == case.evidence_revision else "stale"
    context: dict[str, object] = {
        "analysis_id": str(analysis.id),
        "run_id": str(analysis.run_id),
        "analysis_evidence_revision": analysis.evidence_revision,
        "current_evidence_revision": case.evidence_revision,
        "freshness": freshness,
        "status": analysis.status,
        "answer": _clip(analysis.answer, 12_000),
        "summary": _clip(analysis.summary, 12_000),
    }
    if not isinstance(analysis.trace_json, dict):
        context["trace_status"] = "unavailable"
        return context
    try:
        trace = CaseAnalysisTrace.model_validate(analysis.trace_json)
    except ValidationError:
        context["trace_status"] = "invalid"
        return context
    context.update(
        {
            "trace_status": "validated",
            "claims": [_claim_context(claim) for claim in trace.claims[:16]],
            "timeline": [_timeline_context(item) for item in trace.timeline[:16]],
            "impacts": [_impact_context(item) for item in trace.impacts[:16]],
            "gaps": [_gap_context(item) for item in trace.gaps[:16]],
            "mitre_associations": [
                _mitre_context(item) for item in trace.mitre_associations[:16]
            ],
        }
    )
    return context


def _technical_context(analysis: CaseAnalysisResult | None) -> dict[str, object] | None:
    rag = analysis.run.rag_context if analysis and analysis.run else None
    if rag is None:
        return None
    return {
        "retrieval_context_id": rag.retrieval_context_id,
        "case_run_id": str(rag.case_run_id),
        "context": _clip(rag.context_text, 12_000),
        "mitre_table": list(rag.mitre_table[:32]),
    }


def _claim_context(claim) -> dict[str, object]:
    return {
        "claim_id": claim.claim_id,
        "claim_type": claim.claim_type,
        "text": _clip(claim.text, 2_000),
        "epistemic_status": claim.epistemic_status,
        "supporting_source_ids": list(claim.supporting_source_ids),
        "contradicting_source_ids": list(claim.contradicting_source_ids),
    }


def _timeline_context(item) -> dict[str, object]:
    return {
        "time": _clip(item.time, 500),
        "event": _clip(item.event, 1_000),
        "claim_ids": list(item.claim_ids),
    }


def _impact_context(item) -> dict[str, object]:
    return {
        "description": _clip(item.description, 1_000),
        "claim_ids": list(item.claim_ids),
    }


def _gap_context(gap) -> dict[str, object]:
    return {
        "gap_id": gap.gap_id,
        "gap_key": gap.gap_key,
        "topic": _clip(gap.topic, 500),
        "status": gap.status,
        "description": _clip(gap.description, 2_000),
        "priority": gap.priority,
        "askable": gap.askable,
        "affected_claim_ids": list(gap.affected_claim_ids),
        "clarification_question": _clip_optional(gap.clarification_question, 300),
    }


def _mitre_context(item) -> dict[str, object]:
    return {
        "association_id": item.association_id,
        "technique_id": item.technique_id,
        "claim_ids": list(item.claim_ids),
        "reason": _clip(item.reason, 1_000),
        "status": item.status,
        "support_role": item.support_role,
    }


def _followup_metadata(message: ChatMessage) -> dict[str, object]:
    metadata = message.metadata_json if isinstance(message.metadata_json, dict) else {}
    followup = metadata.get("chat_followup")
    return dict(followup) if isinstance(followup, dict) else {}


def _optional_text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _clip_optional(value: object, limit: int) -> str | None:
    return _clip(value, limit) if isinstance(value, str) else None


def _clip(value: object, limit: int) -> str:
    text = str(value)
    return text if len(text) <= limit else text[:limit].rstrip()


__all__ = ["CaseChatContext", "load_case_chat_context"]
