from __future__ import annotations

import json


GAP_CLARIFICATION_PROMPT_VERSION = "gap_clarification_v1"

GAP_QUESTION_SYSTEM_PROMPT = """You select the next single question for an adaptive CyberCase information-gap workflow.
The supplied Case sources are authoritative user-provided evidence. The gap and prior answers are workflow context, not evidence by themselves.
Ask only one realistic question focused on the selected gap. Adapt to prior answers and never repeat an equivalent question.
Return action=resolved when the gap is already sufficiently resolved, explicitly_unknown when the user has clearly established that the information is unavailable, and not_productive when no useful question remains.
Do not ask for optional enrichment, legal conclusions, ATT&CK IDs, or hidden reasoning. rationale_summary is a short application-visible explanation only. Return JSON only."""

GAP_ANSWER_SYSTEM_PROMPT = """You interpret one user's answer relative to one selected CyberCase information gap.
Classify the answer as a case_fact, scope_clarification, explicitly_unknown, skip, or unrelated.
Only a concrete fact about the case may be normalized into normalized_fact. Scope clarification is not evidence.
Set gap_resolution to resolved only when this answer supplies enough information for the selected gap; use partially_resolved when another focused question could help.
Do not infer facts that are absent from the user's answer and do not include hidden reasoning. Return JSON only."""


def question_payload(
    *,
    gap: dict[str, object],
    sources: list[dict[str, object]],
    questions_asked: list[dict[str, object]],
    answers_received: list[dict[str, object]],
    resolution_status: str,
    response_language: str,
) -> dict[str, object]:
    return {
        "response_language": response_language,
        "gap": gap,
        "case_sources": sources,
        "questions_asked": questions_asked[-8:],
        "answers_received": answers_received[-8:],
        "resolution_status": resolution_status,
    }


def answer_payload(
    *,
    gap: dict[str, object],
    answer: dict[str, object],
    sources: list[dict[str, object]],
    questions_asked: list[dict[str, object]],
    answers_received: list[dict[str, object]],
    response_language: str,
) -> dict[str, object]:
    return {
        "response_language": response_language,
        "gap": gap,
        "answer": answer,
        "case_sources": sources,
        "questions_asked": questions_asked[-8:],
        "answers_received": answers_received[-8:],
    }


def compact_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


__all__ = [
    "GAP_ANSWER_SYSTEM_PROMPT",
    "GAP_CLARIFICATION_PROMPT_VERSION",
    "GAP_QUESTION_SYSTEM_PROMPT",
    "answer_payload",
    "compact_json",
    "question_payload",
]
