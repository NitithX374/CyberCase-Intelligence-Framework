from __future__ import annotations

import json
import re
from typing import Any


SELECTED_CATEGORIES = (
    "Threat Analysis",
    "Protection Strategy Research",
    "Summary Generation",
    "Incident Response Planning",
    "Risk Assessment",
    "Impact Scope",
)


PROMPT_PROTOCOL = {
    "mT5": {
        "generation": "task: <category>\\ninstruction: <instruction>\\ncontext: <input>",
        "choice": "task: <category>\\ninstruction: <question and options exactly as provided>\\ncontext: <input>\\nanswer:",
        "extraction": "task: <category>\\ninstruction: <instruction>\\ncontext: <input>",
    },
    "B0": {
        "user_content": "same task, instruction, and context; append only the fixed format instruction required by the row",
        "rendering": "one OpenRouter user message; no system message, examples, reasoning request, or hidden context",
    },
    "excluded_fields": ["thought", "gold output", "filename", "hidden metadata"],
}


FORMAT_COMPATIBILITY = {
    "choice": {
        "instruction": "question and A/B/C/D option text are copied exactly",
        "expected_output": "normalize generated text to exactly one uppercase A/B/C/D before exact match; retain raw output",
    },
    "extraction": {
        "instruction": "use the supplied extraction instruction unchanged",
        "expected_output": "preserve the requested JSON schema and do not convert freeform outputs",
    },
    "generation": {
        "instruction": "use the supplied instruction unchanged",
        "expected_output": "retain generated freeform text for reference metrics",
    },
}


def language_for(row: dict[str, Any]) -> str:
    return str(row["task"]).split("-")[1]


def format_for(row: dict[str, Any]) -> str:
    suffix = str(row["task"]).split("-")[-1]
    return {
        "gen": "generation",
        "choice": "choice",
        "ex": "extraction",
    }[suffix]


def instruction_text(row: dict[str, Any]) -> str:
    instruction = row["instruction"]
    if isinstance(instruction, str):
        return instruction
    question = str(instruction["question"])
    choices = instruction["choice"]
    option_lines = [f"{label}: {choices[label]}" for label in ("A", "B", "C", "D")]
    return "\n".join([question, *option_lines])


def _build_input(row: dict[str, Any], include_choice_marker: bool) -> str:
    lines = [
        f"task: {row['category']}",
        f"instruction: {instruction_text(row)}",
        f"context: {row['input']}",
    ]
    if include_choice_marker and format_for(row) == "choice":
        lines.append("answer:")
    return "\n".join(lines)


def build_mt5_input(row: dict[str, Any]) -> str:
    return _build_input(row, include_choice_marker=True)


def build_b0_prompt(row: dict[str, Any]) -> str:
    base = "\n\n".join([
        f"Task: {row['category']}",
        f"Instruction:\n{instruction_text(row)}",
        f"Context:\n{row['input']}",
    ])
    output_format = format_for(row)
    if output_format == "choice":
        return f"{base}\n\nReturn only one uppercase letter: A, B, C, or D."
    if output_format == "extraction":
        return f"{base}\n\nReturn only the requested structured output and preserve the requested schema."
    return f"{base}\n\nProvide only the answer to the task. Do not explain your reasoning unless the instruction explicitly requests an explanation."


def normalize_choice_output(raw: str) -> str | None:
    text = raw.strip()
    if len(text) <= 1:
        return text if text in {"A", "B", "C", "D"} else None
    valid_letters = re.findall(r"[ABCD]", text)
    return valid_letters[0] if len(valid_letters) == 1 else None


def gold_output_text(row: dict[str, Any]) -> str:
    output = row["output"]
    if isinstance(output, (dict, list)):
        return json.dumps(output, ensure_ascii=False, separators=(",", ":"))
    return str(output)


def metadata_for(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": str(row["id"]),
        "category": row["category"],
        "language": language_for(row),
        "format": format_for(row),
        "task": row["task"],
    }
