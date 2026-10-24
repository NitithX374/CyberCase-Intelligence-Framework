from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass

from app.config import settings
from app.sources.bundle import CaseSourceItem
from app.sources.markup import source_tables
from app.trace.quotes import MAX_QUOTE_CHARS
from app.trace.sentences import SentenceIndex, segmenter_identity

logger = logging.getLogger(__name__)

EVIDENCE_VERSION = "evidence_units_v4"
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
    tagged = f"{EVIDENCE_VERSION}\0{segmenter_identity()}\0{text}"
    return hashlib.sha256(tagged.encode()).hexdigest()[:16]


def evidence_units(
    source: CaseSourceItem, sentences: SentenceIndex | None = None
) -> tuple[EvidenceUnit, ...]:
    if not source.text:
        return ()
    starts = segmentation_starts(sentences or SentenceIndex(source.text))
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


def segmentation_starts(sentences: SentenceIndex) -> list[int]:
    text = sentences.text
    starts: list[int] = []
    cursor = 0
    for table in source_tables(text):
        starts.extend(start for start, _ in sentences.spans(cursor, table.start))
        starts.extend([table.start, *table.row_starts[1:]])
        cursor = table.end
    starts.extend(start for start, _ in sentences.spans(cursor, len(text)))
    return [0, *starts[1:]]


cutting: set[asyncio.Task] = set()


def cut_ahead(text: str) -> None:
    if not settings.warmup_models or not text:
        return
    source = CaseSourceItem(source_id="cut-ahead", source_kind="narrative", text=text)
    task = asyncio.create_task(asyncio.to_thread(evidence_units, source))
    cutting.add(task)
    task.add_done_callback(cut_finished)


def cut_finished(task: asyncio.Task) -> None:
    cutting.discard(task)
    if not task.cancelled() and task.exception() is not None:
        logger.warning("Cutting a new source ahead of use failed: %r", task.exception())


class EvidenceIndex:
    def __init__(self, sources: Sequence[CaseSourceItem]) -> None:
        self.sources = {source.source_id: source for source in sources}
        if len(self.sources) != len(sources):
            raise ValueError("Evidence source identities must be unique")
        self.revisions = {source.source_id: evidence_revision(source.text) for source in sources}
        self.sentences = {source.source_id: SentenceIndex(source.text) for source in sources}
        self.units: dict[str, dict[str, EvidenceUnit]] = {}

    def units_of(self, source_id: str) -> dict[str, EvidenceUnit]:
        if source_id not in self.units:
            units = evidence_units(self.sources[source_id], self.sentences[source_id])
            self.units[source_id] = {unit.unit_id: unit for unit in units}
        return self.units[source_id]

    def resolve(self, source_id: str, unit_id: str) -> tuple[EvidenceUnit | None, str | None]:
        if source_id not in self.sources:
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
        unit = self.units_of(source_id).get(unit_id)
        if unit is None:
            return None, "unknown_unit"
        if not unit.text.strip():
            return None, "empty_unit"
        return unit, None


__all__ = [
    "EVIDENCE_VERSION",
    "EvidenceIndex",
    "EvidenceUnit",
    "cut_ahead",
    "evidence_revision",
    "evidence_units",
]
