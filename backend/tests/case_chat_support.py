from __future__ import annotations

import uuid
from typing import NamedTuple

from app.models.analysis_result import CaseAnalysisResult
from app.models.case import Case
from app.models.chat_message import ChatMessage
from app.models.source import CaseSource
from app.models.user import User
from app.trace.trace import CaseAnalysisTrace

NARRATIVE = "Files on the shared drive were reported encrypted."
GAP = {
    "gap_id": "G-01",
    "gap_key": "topic:incident-time",
    "topic": "Incident time",
    "status": "NOT_PROVIDED",
    "description": "The incident time is missing.",
    "reason": "Timing fixes the chronology.",
    "priority": "high",
    "askable": True,
    "clarification_question": "When did the incident happen?",
}
TRACE = {
    "version": "case_analysis_trace_v1",
    "analysis_mode": "case_overview",
    "validation_status": "validated",
    "summary": NARRATIVE,
    "claims": [],
    "gaps": [GAP],
    "mitre_associations": [],
}
SETTLED = {**TRACE, "gaps": []}


class SeededCase(NamedTuple):
    case_id: uuid.UUID
    user_id: uuid.UUID
    question_id: uuid.UUID | None


def numbered_gaps(count: int) -> CaseAnalysisTrace:
    return CaseAnalysisTrace.model_validate(
        {
            **TRACE,
            "gaps": [
                {
                    **GAP,
                    "gap_id": f"G-0{n}",
                    "gap_key": f"topic:{n}",
                    "clarification_question": f"Question {n}?",
                }
                for n in range(1, count + 1)
            ],
        }
    )


async def seeded_case(
    session_factory,
    *,
    trace: dict | None = TRACE,
    with_source: bool = True,
    asking: bool = True,
) -> SeededCase:
    async with session_factory() as db, db.begin():
        user = User(email="analyst@example.com", name="Analyst", password_hash="x")
        db.add(user)
        await db.flush()
        case = Case(user_id=user.id, title="Seeded case", source_revision=1)
        db.add(case)
        await db.flush()
        if with_source:
            db.add(CaseSource(case_id=case.id, source_kind="narrative", exact_text=NARRATIVE))
        if trace is None:
            return SeededCase(case.id, user.id, None)
        analysis = CaseAnalysisResult(
            case_id=case.id,
            source_revision=1,
            summary=trace.get("summary", NARRATIVE),
            trace_json=trace,
            pipeline_config={},
            external_context_json={},
        )
        db.add(analysis)
        await db.flush()
        case.latest_analysis_result_id = analysis.id
        if not asking:
            return SeededCase(case.id, user.id, None)
        gap = trace["gaps"][0]
        question = ChatMessage(
            case_id=case.id,
            ordinal=1,
            role="assistant",
            content=gap["clarification_question"],
            message_kind="followup_question",
            gap_key=gap["gap_key"],
            analysis_result_id=analysis.id,
        )
        db.add(question)
        await db.flush()
        return SeededCase(case.id, user.id, question.id)
