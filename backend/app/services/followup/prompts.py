"""Prompts and bounded provider payloads for the two follow-up stages."""

from __future__ import annotations

from pathlib import Path

from app.services.followup.context import build_bounded_context


GAP_ANALYSIS_VERSION = "gap_analysis_v1"
GAP_ANALYSIS_PROMPT_VERSION = "gap_analysis_prompt_v7"

FOLLOWUP_POLICY_VERSION = "stateful_adaptive_followup_v5"
FOLLOWUP_PROMPT_VERSION = "followup_policy_prompt_v4"
FOLLOWUP_POLICY_PROVIDER = "core_llm"


GAP_ANALYSIS_SYSTEM = (
    Path(__file__).parent / "prompt_templates" / "gap_analysis_v7.txt"
).read_text(encoding="utf-8")


FOLLOWUP_POLICY_SYSTEM = (
    Path(__file__).parent / "prompt_templates" / "followup_policy_v4.txt"
).read_text(encoding="utf-8")


GAP_ANALYSIS_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "gaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "NOT_PROVIDED",
                            "EXPLICITLY_UNKNOWN",
                            "AMBIGUOUS",
                            "CONFLICTING",
                        ],
                    },
                    "description": {"type": "string"},
                    "affects": {"type": "string"},
                    "reason": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "askable": {"type": "boolean"},
                },
                "required": [
                    "topic",
                    "status",
                    "description",
                    "affects",
                    "reason",
                    "priority",
                    "askable",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["gaps"],
    "additionalProperties": False,
}

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
    "GAP_ANALYSIS_PROMPT_VERSION",
    "GAP_ANALYSIS_SCHEMA",
    "GAP_ANALYSIS_SYSTEM",
    "GAP_ANALYSIS_VERSION",
    "build_bounded_context",
]
