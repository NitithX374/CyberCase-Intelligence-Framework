from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass

from app.sources.bundle import CaseSourceItem
from app.sources.markup import source_tables
from app.trace.quotes import MAX_QUOTE_CHARS
from app.trace.sentences import sentence_spans

EVIDENCE_VERSION = "evidence_units_v2"
UNIT_PATTERN = re.compile(
    r"(?P<source>[^:]{1,160}):U(?P<number>[0-9]{3,})-(?P<revision>[a-f0-9]{16})"
)


@dataclass(frozen=True)
class EvidenceUnit:
    unit_id: str
    source_id: str
    start: int
    end: int
    text: str


def evidence_revision(text: str) -> str:
    return hashlib.sha256(f"{EVIDENCE_VERSION}\0{text}".encode()).hexdigest()[:16]


def evidence_units(source: CaseSourceItem) -> tuple[EvidenceUnit, ...]:
    if not source.text:
        return ()
    starts = segmentation_starts(source.text)
    ends = [*starts[1:], len(source.text)]
    revision = evidence_revision(source.text)
    spans = [
        (offset, min(offset + MAX_QUOTE_CHARS, end))
        for start, end in zip(starts, ends, strict=True)
        for offset in range(start, end, MAX_QUOTE_CHARS)
    ]
    return tuple(
        EvidenceUnit(
            unit_id=f"{source.source_id}:U{index:03d}-{revision}",
            source_id=source.source_id,
            start=start,
            end=end,
            text=source.text[start:end],
        )
        for index, (start, end) in enumerate(spans, 1)
    )


def segmentation_starts(text: str) -> list[int]:
    starts: list[int] = []
    cursor = 0
    for table in source_tables(text):
        starts.extend(cursor + start for start, _ in sentence_spans(text[cursor : table.start]))
        starts.extend([table.start, *table.row_starts[1:]])
        cursor = table.end
    starts.extend(cursor + start for start, _ in sentence_spans(text[cursor:]))
    return [0, *starts[1:]]


def evidence_payload(source: CaseSourceItem) -> dict[str, object]:
    return {
        "evidence_version": EVIDENCE_VERSION,
        "evidence_units": [
            {key: value for key, value in asdict(unit).items() if key != "source_id"}
            for unit in evidence_units(source)
        ],
    }


class EvidenceIndex:
    def __init__(self, sources: Sequence[CaseSourceItem]) -> None:
        self.sources = {source.source_id: source for source in sources}
        if len(self.sources) != len(sources):
            raise ValueError("Evidence source identities must be unique")
        self.revisions = {source.source_id: evidence_revision(source.text) for source in sources}
        self.units: dict[str, dict[str, EvidenceUnit]] = {}

    def resolve(self, source_id: str, unit_id: str) -> tuple[EvidenceUnit | None, str | None]:
        source = self.sources.get(source_id)
        if source is None:
            return None, "unknown_source"
        match = UNIT_PATTERN.fullmatch(unit_id)
        if (
            match is None
            or int(match["number"]) < 1
            or match["number"] != f"{int(match['number']):03d}"
        ):
            return None, "malformed_id"
        if match["source"] != source_id:
            return None, "cross_source"
        if match["revision"] != self.revisions[source_id]:
            return None, "stale_id"
        if source_id not in self.units:
            self.units[source_id] = {unit.unit_id: unit for unit in evidence_units(source)}
        unit = self.units[source_id].get(unit_id)
        if unit is None:
            return None, "unknown_unit"
        if not unit.text.strip():
            return None, "empty_unit"
        return unit, None

    def units_for(self, source_id: str) -> list[EvidenceUnit]:
        source = self.sources.get(source_id)
        if source is None:
            return []
        if source_id not in self.units:
            self.units[source_id] = {unit.unit_id: unit for unit in evidence_units(source)}
        return list(self.units[source_id].values())


__all__ = [
    "EVIDENCE_VERSION",
    "EvidenceIndex",
    "EvidenceUnit",
    "evidence_payload",
    "evidence_revision",
    "evidence_units",
]
