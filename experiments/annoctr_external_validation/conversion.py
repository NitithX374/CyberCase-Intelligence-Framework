from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .constants import SOURCE_SPLIT


class ConversionError(ValueError):
    pass


@dataclass(frozen=True)
class BinarySample:
    text: str
    gold_label: int
    document: str
    has_attack_technique: bool
    source_split: str


@dataclass(frozen=True)
class SentenceGroup:
    sample: BinarySample
    row_count: int
    technique_rows: int
    explicit_negative_rows: int
    entity_types: tuple[str, ...]
    source_lines: tuple[int, ...]


@dataclass(frozen=True)
class ConversionResult:
    samples: tuple[BinarySample, ...]
    groups: tuple[SentenceGroup, ...]
    statistics: dict[str, int | float | str]


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def _string(row: dict, key: str) -> str:
    value = row.get(key, "")
    return "" if value is None else str(value)


def _technique_link(value: str) -> bool:
    parsed = urlsplit(value.strip())
    return (
        parsed.scheme in {"http", "https"}
        and parsed.netloc.casefold() == "attack.mitre.org"
        and parsed.path.casefold().startswith("/techniques/")
        and bool(parsed.path.removeprefix("/techniques/").strip("/"))
    )


def _explicit_negative(row: dict) -> bool:
    return (
        _string(row, "label_link").strip().casefold() == "no annotation"
        and _string(row, "label_title").strip().casefold() == "no annotation"
    )


def reconstruct_sentence(row: dict) -> str:
    mention = _string(row, "mention")
    left = _string(row, "_context_left")
    right = _string(row, "_context_right")
    text = mention if not left and not right else left + mention + right
    normalized = normalize_whitespace(text)
    if not normalized:
        raise ConversionError("An annotation reconstructed to empty text")
    return normalized


def _row_class(row: dict) -> tuple[bool, bool]:
    entity_type = _string(row, "entity_type").strip().upper()
    technique_link = _technique_link(_string(row, "label_link"))
    explicit_negative = _explicit_negative(row)
    if entity_type == "TECHNIQUE" and not technique_link and not explicit_negative:
        raise ConversionError(
            "TECHNIQUE row has neither a valid ATT&CK technique link nor "
            "the explicit No Annotation marker"
        )
    return technique_link, explicit_negative


def _read_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ConversionError(f"Invalid JSON at {path}:{line_number}") from error
        if not isinstance(row, dict):
            raise ConversionError(f"Expected an object at {path}:{line_number}")
        required = {"mention", "_context_left", "_context_right", "document"}
        missing = sorted(key for key in required if key not in row)
        if missing:
            raise ConversionError(f"Missing fields at {path}:{line_number}: {missing}")
        row["_line_number"] = line_number
        rows.append(row)
    if not rows:
        raise ConversionError(f"No annotations found in {path}")
    return rows


def convert_annotations(path: Path) -> ConversionResult:
    grouped: dict[tuple[str, str], dict] = {}
    raw_rows = _read_rows(path)
    technique_row_count = 0
    explicit_negative_row_count = 0
    for row in raw_rows:
        document = _string(row, "document").strip()
        if not document:
            raise ConversionError(f"Annotation at line {row['_line_number']} has no document")
        text = reconstruct_sentence(row)
        is_technique, is_explicit_negative = _row_class(row)
        technique_row_count += int(is_technique)
        explicit_negative_row_count += int(is_explicit_negative)
        key = (document, text)
        group = grouped.setdefault(
            key,
            {
                "technique_rows": 0,
                "explicit_negative_rows": 0,
                "entity_types": set(),
                "source_lines": [],
            },
        )
        group["technique_rows"] += int(is_technique)
        group["explicit_negative_rows"] += int(is_explicit_negative)
        group["entity_types"].add(_string(row, "entity_type").strip().upper())
        group["source_lines"].append(int(row["_line_number"]))

    groups: list[SentenceGroup] = []
    for (document, text), evidence in sorted(grouped.items()):
        has_technique = evidence["technique_rows"] > 0
        sample = BinarySample(
            text=text,
            gold_label=int(has_technique),
            document=document,
            has_attack_technique=has_technique,
            source_split=SOURCE_SPLIT,
        )
        groups.append(
            SentenceGroup(
                sample=sample,
                row_count=len(evidence["source_lines"]),
                technique_rows=evidence["technique_rows"],
                explicit_negative_rows=evidence["explicit_negative_rows"],
                entity_types=tuple(sorted(evidence["entity_types"])),
                source_lines=tuple(evidence["source_lines"]),
            )
        )

    samples = tuple(group.sample for group in groups)
    positive_count = sum(sample.gold_label == 1 for sample in samples)
    statistics: dict[str, int | float | str] = {
        "source_file": str(path.resolve()),
        "source_split": SOURCE_SPLIT,
        "raw_annotation_rows": len(raw_rows),
        "technique_link_rows": technique_row_count,
        "explicit_negative_rows": explicit_negative_row_count,
        "unique_sentence_samples": len(samples),
        "positive_samples": positive_count,
        "negative_samples": len(samples) - positive_count,
        "positive_percentage": positive_count / len(samples) if samples else 0.0,
        "unique_documents": len({sample.document for sample in samples}),
        "multi_annotation_sentence_groups": sum(group.row_count > 1 for group in groups),
    }
    return ConversionResult(tuple(samples), tuple(groups), statistics)
