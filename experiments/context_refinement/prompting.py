from __future__ import annotations

from copy import deepcopy

from research.sevenllm_preflight.protocol import build_b0_prompt


def build_condition_prompt(row: dict[str, Any], context: str) -> str:
    prompt_row = deepcopy(row)
    prompt_row["input"] = context
    return build_b0_prompt(prompt_row)


def prompt_template_parts(row: dict[str, Any], raw_context: str, refined_context: str) -> tuple[str, str, str, str]:
    raw_prompt = build_condition_prompt(row, raw_context)
    refined_prompt = build_condition_prompt(row, refined_context)
    raw_marker = f"Context:\n{raw_context}"
    refined_marker = f"Context:\n{refined_context}"
    if raw_marker not in raw_prompt or refined_marker not in refined_prompt:
        raise ValueError(f"Prompt context marker missing for sample {row['id']}")
    raw_prefix, raw_suffix = raw_prompt.split(raw_marker, 1)
    refined_prefix, refined_suffix = refined_prompt.split(refined_marker, 1)
    return raw_prefix, raw_suffix, refined_prefix, refined_suffix


def validate_context_only_prompt_change(row: dict[str, Any], raw_context: str, refined_context: str) -> None:
    raw_prefix, raw_suffix, refined_prefix, refined_suffix = prompt_template_parts(row, raw_context, refined_context)
    if raw_prefix != refined_prefix or raw_suffix != refined_suffix:
        raise ValueError(f"Prompt template changed outside context for sample {row['id']}")
