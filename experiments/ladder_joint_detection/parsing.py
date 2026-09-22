from __future__ import annotations

import csv
from pathlib import Path

from .constants import CLASSIFICATION_ROOT, ENTITY_LABELS, ENTITY_ROOT, SPLITS
from .models import (
    ClassificationRecord,
    EntityRecord,
    EntityToken,
    MalformedRecord,
    SourceData,
)
from .normalization import normalize_text


def _classification_records(path: Path, split: str) -> tuple[list[ClassificationRecord], list[MalformedRecord]]:
    records: list[ClassificationRecord] = []
    malformed: list[MalformedRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or {"text", "label"}.difference(reader.fieldnames):
            raise ValueError(f"Classification file has an invalid header: {path}")
        for row_number, row in enumerate(reader, 2):
            text = row.get("text") or ""
            raw_label = row.get("label") or ""
            try:
                label = int(raw_label)
            except ValueError:
                malformed.append(
                    MalformedRecord(split, str(path), row_number, "classification_row", "Invalid label", raw_label)
                )
                continue
            if label not in {0, 1} or not text.strip():
                malformed.append(
                    MalformedRecord(split, str(path), row_number, "classification_row", "Invalid label or empty text", text)
                )
                continue
            record_id = f"{split}-cls-{row_number - 1:06d}"
            records.append(
                ClassificationRecord(record_id, text, normalize_text(text), label, split, row_number)
            )
    return records, malformed


def _entity_records(path: Path, split: str) -> tuple[list[EntityRecord], list[MalformedRecord]]:
    records: list[EntityRecord] = []
    malformed: list[MalformedRecord] = []
    current: list[EntityToken] = []
    block_start = 0
    block_invalid = False
    block_index = 0

    def flush(end_line: int) -> None:
        nonlocal current, block_start, block_invalid, block_index
        if not current and not block_invalid:
            block_start = 0
            return
        block_index += 1
        if not block_invalid:
            reconstructed = " ".join(token.text for token in current)
            records.append(
                EntityRecord(
                    f"{split}-ent-{block_index:06d}",
                    tuple(current),
                    reconstructed,
                    normalize_text(reconstructed),
                    split,
                    block_index,
                    block_start,
                    end_line,
                    any(token.label == "ATK" for token in current),
                )
            )
        current = []
        block_start = 0
        block_invalid = False

    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line:
            flush(line_number - 1)
            continue
        if block_start == 0:
            block_start = line_number
        parts = line.rsplit(None, 1)
        if len(parts) != 2 or parts[1] not in ENTITY_LABELS or not parts[0]:
            block_invalid = True
            malformed.append(
                MalformedRecord(split, str(path), line_number, "entity_line", "Expected token and ATK/O label", raw_line)
            )
            continue
        current.append(EntityToken(parts[0], parts[1], line_number))
    flush(len(lines))
    return records, malformed


def load_sources() -> SourceData:
    classifications: dict[str, tuple[ClassificationRecord, ...]] = {}
    entities: dict[str, tuple[EntityRecord, ...]] = {}
    malformed: list[MalformedRecord] = []
    for split in SPLITS:
        classification, classification_errors = _classification_records(
            CLASSIFICATION_ROOT / f"{split}.csv", split
        )
        entity, entity_errors = _entity_records(ENTITY_ROOT / f"{split}.txt", split)
        classifications[split] = tuple(classification)
        entities[split] = tuple(entity)
        malformed.extend(classification_errors)
        malformed.extend(entity_errors)
    return SourceData(classifications, entities, tuple(malformed))
