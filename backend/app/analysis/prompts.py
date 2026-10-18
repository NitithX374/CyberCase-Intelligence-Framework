from __future__ import annotations

from app.llm.prompt_files import prompt_template
from app.trace.claims import MAX_CLARIFICATION_QUESTION_CHARS

CASE_READING_SYSTEM_PROMPT = "\n" + prompt_template(__file__, "reading") + "\n"

READING_JSON_FORMAT = "\n\n" + prompt_template(__file__, "reading_json_format")

CASE_READING_JSON_PROMPT = CASE_READING_SYSTEM_PROMPT + READING_JSON_FORMAT

CASE_VIEWS_SYSTEM_PROMPT = "\n" + prompt_template(__file__, "views") + "\n"

CASE_CHECKLIST = {
    "who_affected": "who was affected or targeted",
    "who_responsible": "who carried out the incident",
    "what": "what happened, and what was taken, damaged or exposed",
    "when": "when it happened, began or was discovered",
    "where": "where it happened",
    "why": "the motive or purpose",
    "how": "the method, tool or channel used",
    "how_much": "its scale in people, records, money or ransom",
}

CHECKLIST_LINES = "\n".join(f"  {key}: {meaning}" for key, meaning in CASE_CHECKLIST.items())

GAP_IDENTIFICATION_INSTRUCTIONS = prompt_template(__file__, "gaps").format(
    checklist_lines=CHECKLIST_LINES,
    max_question_chars=MAX_CLARIFICATION_QUESTION_CHARS,
)

CASE_JUDGEMENT_SYSTEM_PROMPT = (
    "\n"
    + prompt_template(__file__, "judgement").format(
        gap_instructions=GAP_IDENTIFICATION_INSTRUCTIONS
    )
    + "\n"
)


def case_assessment_prompt() -> str:
    return prompt_template(__file__, "assessment").format(
        gap_instructions=GAP_IDENTIFICATION_INSTRUCTIONS
    )


__all__ = [
    "CASE_CHECKLIST",
    "CASE_JUDGEMENT_SYSTEM_PROMPT",
    "CASE_READING_JSON_PROMPT",
    "CASE_READING_SYSTEM_PROMPT",
    "CASE_VIEWS_SYSTEM_PROMPT",
    "GAP_IDENTIFICATION_INSTRUCTIONS",
    "READING_JSON_FORMAT",
    "case_assessment_prompt",
]
