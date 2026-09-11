"""Prompt and schema for phrasing one backend-selected clarification gap."""

from __future__ import annotations

from pathlib import Path

from app.services.followup.context import build_bounded_context


FOLLOWUP_POLICY_VERSION = "deterministic_gap_selection_v1"
FOLLOWUP_PROMPT_VERSION = "followup_question_realization_v1"
FOLLOWUP_POLICY_PROVIDER = "core_llm"


FOLLOWUP_POLICY_SYSTEM = (
    Path(__file__).parent / "prompt_templates" / "followup_policy_v4.txt"
).read_text(encoding="utf-8")


FOLLOWUP_POLICY_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["ask_followup", "proceed"],
        },
        "selected_gap": {"type": ["string", "null"]},
        "question": {"type": "string"},
    },
    "required": ["decision", "selected_gap", "question"],
    "additionalProperties": False,
}


__all__ = [
    "FOLLOWUP_POLICY_PROVIDER",
    "FOLLOWUP_POLICY_SCHEMA",
    "FOLLOWUP_POLICY_SYSTEM",
    "FOLLOWUP_POLICY_VERSION",
    "FOLLOWUP_PROMPT_VERSION",
    "build_bounded_context",
]
