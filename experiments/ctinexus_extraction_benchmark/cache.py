from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .schemas import ExtractorPrediction


def load_jsonl_cache(path: Path) -> dict[str, ExtractorPrediction]:
    if not path.exists():
        return {}
    records: dict[str, ExtractorPrediction] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = ExtractorPrediction.model_validate(json.loads(line))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"Invalid cache record at {path}:{line_number}: {exc}") from exc
        records[record.doc_id] = record
    return records


def cache_matches(
    record: ExtractorPrediction,
    *,
    condition: str,
    doc_id: str,
    narrative_sha256: str,
    contract: dict[str, Any],
) -> bool:
    if record.condition != condition or record.doc_id != doc_id:
        return False
    if record.status != "success":
        return False
    if record.narrative_sha256 != narrative_sha256:
        return False
    for key, value in contract.items():
        if record.contract.get(key) != value:
            return False
    return True


def append_jsonl(path: Path, record: ExtractorPrediction) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record.model_dump(mode="json"), ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, path)
