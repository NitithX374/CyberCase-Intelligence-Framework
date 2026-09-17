from __future__ import annotations

import re

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from sqlalchemy import select

from app.config import settings
from app.models.chat import ChatMessage
from app.services.followup.contracts import answer_indicates_unavailable
from app.services.gap_clarification.context import load_gap_context
from app.services.gap_clarification.contracts import (
    ClarificationResumeAnswer,
    GapAnswerInterpretation,
    GapClarificationState,
    GapNextStep,
)
from app.services.gap_clarification.model import invoke_gap_stage
from app.services.gap_clarification.persistence import commit_answer, persist_question
from app.services.gap_clarification.prompts import (
    GAP_ANSWER_SYSTEM_PROMPT,
    GAP_QUESTION_SYSTEM_PROMPT,
    answer_payload,
    question_payload,
)
from app.services.gap_clarification.runtime import (
    GapClarificationError,
    current_session_factory,
    parse_uuid,
    session_id_from_config,
)


async def select_question(
    state: GapClarificationState,
    config: RunnableConfig,
) -> dict[str, object]:
    if state.get("attempt_count", 0) >= settings.gap_clarification_max_attempts:
        return {
            "resolution_status": "not_productive",
            "pending_question_message_id": None,
        }

    session_id = session_id_from_config(config)
    async with current_session_factory()() as db:
        context = await load_gap_context(
            db,
            state,
            session_id=session_id,
            include_history=True,
        )
    decision = await invoke_gap_stage(
        config_value=context.pipeline_config,
        stage="select_question",
        system=GAP_QUESTION_SYSTEM_PROMPT,
        content=question_payload(
            gap=context.gap.model_dump(mode="json"),
            sources=context.sources,
            questions_asked=context.questions_asked,
            answers_received=context.answers_received,
            resolution_status=state.get("resolution_status", "unresolved"),
            response_language=state["response_language"],
        ),
        schema=GapNextStep,
    )
    if not isinstance(decision, GapNextStep):
        raise GapClarificationError(
            "gap_question_invalid",
            "Question selection returned an invalid decision",
        )
    if decision.action != "ask":
        return {
            "resolution_status": decision.action,
            "pending_question_message_id": None,
        }

    question_text = (decision.question or "").strip()
    normalized = normalize_question(question_text)
    if not normalized or any(
        normalized == normalize_question(str(item.get("question", "")))
        for item in context.questions_asked
    ):
        return {
            "resolution_status": "not_productive",
            "pending_question_message_id": None,
        }

    next_attempt = int(state.get("attempt_count", 0)) + 1
    question_message_id = await persist_question(
        state,
        config,
        question=question_text,
        target_information=decision.target_information,
        rationale_summary=decision.rationale_summary,
        attempt=next_attempt,
    )
    return {
        "attempt_count": next_attempt,
        "pending_question_message_id": question_message_id,
        "resolution_status": "unresolved",
    }


async def ask_user(
    state: GapClarificationState,
    config: RunnableConfig,
) -> dict[str, object]:
    question_id = parse_uuid(
        state["pending_question_message_id"], "pending_question_message_id"
    )
    session_id = session_id_from_config(config)
    async with current_session_factory()() as db:
        question = await db.scalar(
            select(ChatMessage).where(
                ChatMessage.id == question_id,
                ChatMessage.case_id == parse_uuid(state["case_id"], "case_id"),
                ChatMessage.message_kind == "followup_question",
                ChatMessage.role == "assistant",
            )
        )
    if question is None:
        raise GapClarificationError(
            "clarification_question_missing",
            "Clarification question is missing",
        )
    metadata = question.metadata_json if isinstance(question.metadata_json, dict) else {}
    followup = metadata.get("chat_followup")
    target_information = (
        followup.get("target_information")
        if isinstance(followup, dict)
        else None
    )
    answer = interrupt(
        {
            "type": "gap_clarification",
            "case_id": state["case_id"],
            "clarification_session_id": session_id,
            "question_message_id": str(question.id),
            "question": question.content,
            "target_information": target_information,
            "attempt": state["attempt_count"],
        }
    )
    if not isinstance(answer, dict):
        answer = {"content": str(answer), "disposition": "answered"}
    return {"latest_answer": dict(answer)}


async def interpret_answer(
    state: GapClarificationState,
    config: RunnableConfig,
) -> dict[str, object]:
    raw = ClarificationResumeAnswer.model_validate(
        {
            **(state.get("latest_answer") or {}),
            "question_message_id": state["pending_question_message_id"],
        }
    )
    if raw.disposition == "unavailable" or answer_indicates_unavailable(raw.content):
        interpretation = GapAnswerInterpretation(
            response_type="explicitly_unknown",
            gap_resolution="unresolved",
        )
    elif raw.disposition == "skipped":
        interpretation = GapAnswerInterpretation(
            response_type="skip",
            gap_resolution="unresolved",
        )
    else:
        session_id = session_id_from_config(config)
        async with current_session_factory()() as db:
            context = await load_gap_context(
                db,
                state,
                session_id=session_id,
                include_history=True,
            )
        interpretation = await invoke_gap_stage(
            config_value=context.pipeline_config,
            stage="interpret_answer",
            system=GAP_ANSWER_SYSTEM_PROMPT,
            content=answer_payload(
                gap=context.gap.model_dump(mode="json"),
                answer={"content": raw.content, "disposition": raw.disposition},
                sources=context.sources,
                questions_asked=context.questions_asked,
                answers_received=context.answers_received,
                response_language=state["response_language"],
            ),
            schema=GapAnswerInterpretation,
        )
    if not isinstance(interpretation, GapAnswerInterpretation):
        raise GapClarificationError(
            "gap_answer_invalid",
            "Answer interpretation returned an invalid result",
        )
    return {"latest_interpretation": interpretation.model_dump(mode="json")}


def evaluate_gap(state: GapClarificationState) -> dict[str, object]:
    interpretation = GapAnswerInterpretation.model_validate(state["latest_interpretation"])
    if interpretation.response_type == "explicitly_unknown":
        status = "explicitly_unknown"
    elif interpretation.response_type == "skip":
        status = "skipped"
    elif interpretation.response_type == "unrelated":
        status = "not_productive"
    elif interpretation.gap_resolution == "resolved":
        status = "resolved"
    elif state.get("attempt_count", 0) >= settings.gap_clarification_max_attempts:
        status = "not_productive"
    else:
        status = "unresolved"
    return {
        "resolution_status": status,
        "pending_question_message_id": None,
        "latest_answer": None,
        "latest_interpretation": None,
    }


def normalize_question(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


__all__ = [
    "GapClarificationError",
    "ask_user",
    "commit_answer",
    "evaluate_gap",
    "interpret_answer",
    "select_question",
]
