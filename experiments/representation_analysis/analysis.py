from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import DOWNSTREAM_GENERATION_CONFIG, DOWNSTREAM_MODEL
from .prompting import build_condition_prompt, validate_context_only_prompt_change
from .serializers import estimate_tokens
from .storage import read_jsonl


def analysis_record(row: dict[str, Any], condition: str, context: str, response: dict[str, Any], reused_from: str | None = None) -> dict[str, Any]:
    return {
        **response, "sample_id": str(row["id"]), "category": row["category"], "task": row["task"],
        "language": "en", "format": "generation", "condition": condition,
        "input_context": context, "input_chars": len(context), "estimated_input_tokens": estimate_tokens(context),
        "prompt": build_condition_prompt(row, context), "reused_from": reused_from,
    }


def validated_b0_cache(path: Path, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    expected = {str(row["id"]): row for row in rows}
    valid: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(path):
        sample_id = str(record.get("sample_id", ""))
        row = expected.get(sample_id)
        if not row or record.get("condition") != "B0":
            continue
        if record.get("error") or record.get("requested_model") != DOWNSTREAM_MODEL or record.get("generation_config") != DOWNSTREAM_GENERATION_CONFIG:
            continue
        if record.get("prompt") != build_condition_prompt(row, str(row["input"])):
            continue
        if sample_id in valid:
            raise ValueError(f"Duplicate valid B0 cache record for {sample_id}")
        valid[sample_id] = record
    return valid


def validate_shared_prompt(row: dict[str, Any], context: str) -> None:
    validate_context_only_prompt_change(row, str(row["input"]), context)
