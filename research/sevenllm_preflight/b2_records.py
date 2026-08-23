from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .b2_config import SELECTED_CATEGORIES


CJK_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
SOURCE_ID_FIELDS = ("id", "sample_id", "uid", "example_id")


def load_data_file(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        text = handle.read()
    if path.suffix.lower() == ".json":
        value = json.loads(text)
        if not isinstance(value, list):
            raise ValueError(f"Expected a JSON list in {path}")
        rows = value
    else:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Every record must be an object in {path}")
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def _json_text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def instruction_text(row: dict[str, Any]) -> str:
    instruction = row.get("instruction")
    if isinstance(instruction, str):
        if not instruction.strip():
            raise ValueError("instruction is empty")
        return instruction
    if isinstance(instruction, dict):
        question = instruction.get("question")
        choices = instruction.get("choice", instruction.get("choices"))
        if not isinstance(question, str) or not isinstance(choices, dict):
            raise ValueError("structured instruction is missing question or choices")
        if set(choices) != {"A", "B", "C", "D"}:
            raise ValueError("structured instruction must contain A/B/C/D choices")
        return "\n".join([question, *(f"{label}: {choices[label]}" for label in "ABCD")])
    raise ValueError("instruction must be a string or structured choice object")


def language_for(row: dict[str, Any]) -> str:
    for field in ("language", "lang"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            lowered = value.strip().lower()
            if lowered in {"en", "eng", "english"}:
                return "en"
            if lowered in {"zh", "cn", "chi", "chinese"}:
                return "zh"
            return lowered
    task = row.get("task")
    if isinstance(task, str):
        match = re.search(r"(?:^|[-_])(en|zh|cn)(?:[-_]|$)", task.lower())
        if match:
            return "en" if match.group(1) == "en" else "zh"
    values = [row.get("category", ""), row.get("instruction", ""), row.get("input", ""), row.get("output", "")]
    return "zh" if CJK_PATTERN.search(" ".join(_json_text(value) for value in values)) else "en"


def source_id_for(row: dict[str, Any]) -> str | None:
    for field in SOURCE_ID_FIELDS:
        value = row.get(field)
        if value is not None and str(value).strip():
            return str(value)
    return None


def output_text(row: dict[str, Any]) -> str:
    output = row.get("output")
    if output is None:
        raise ValueError("output is missing")
    text = _json_text(output)
    if not text.strip():
        raise ValueError("output is empty")
    return text


def prompt_fingerprint(row: dict[str, Any]) -> str:
    payload = {
        "category": str(row["category"]),
        "instruction": instruction_text(row),
        "input": str(row["input"]),
    }
    return _fingerprint(payload)


def example_fingerprint(row: dict[str, Any]) -> str:
    payload = {
        "category": str(row["category"]),
        "instruction": instruction_text(row),
        "input": str(row["input"]),
        "output": output_text(row),
    }
    return _fingerprint(payload)


def _fingerprint(payload: dict[str, str]) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_input_text(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"task: {row['category']}",
            f"instruction: {instruction_text(row)}",
            f"context: {row['input']}",
        ]
    )


def build_example(row: dict[str, Any], source_line: int) -> dict[str, Any]:
    if row.get("category") not in SELECTED_CATEGORIES:
        raise ValueError(f"Unsupported category at source line {source_line}")
    if not isinstance(row.get("input"), str) or not row["input"].strip():
        raise ValueError("input is missing or empty")
    instruction = instruction_text(row)
    target = output_text(row)
    return {
        "example_id": f"source-line-{source_line:08d}",
        "source_line": source_line,
        "source_id": source_id_for(row),
        "category": row["category"],
        "language": language_for(row),
        "input_text": build_input_text(row),
        "target_text": target,
        "instruction_text": instruction,
        "prompt_fingerprint": prompt_fingerprint(row),
        "example_fingerprint": example_fingerprint(row),
    }


def filter_english_training_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for source_line, row in enumerate(rows, start=1):
        if row.get("category") not in SELECTED_CATEGORIES or language_for(row) != "en":
            continue
        try:
            selected.append(build_example(row, source_line))
        except (KeyError, TypeError, ValueError) as exc:
            invalid.append({"source_line": source_line, "reason": str(exc)})
    return selected, invalid


def benchmark_id_for(row: dict[str, Any]) -> str:
    value = source_id_for(row)
    if value is None:
        raise ValueError("Benchmark row has no stable id")
    return value
