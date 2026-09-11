from pathlib import Path

GAP_ANALYSIS_VERSION = "gap_analysis_v1"
GAP_ANALYSIS_PROMPT_VERSION = "gap_analysis_prompt_v7"

GAP_ANALYSIS_SYSTEM = (
    Path(__file__).parent / "prompt_templates" / "gap_analysis_v7.txt"
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
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
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

__all__ = [
    "GAP_ANALYSIS_PROMPT_VERSION",
    "GAP_ANALYSIS_SCHEMA",
    "GAP_ANALYSIS_SYSTEM",
    "GAP_ANALYSIS_VERSION",
]
