from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationRecord:
    record_id: str
    original_text: str
    normalized_text: str
    sentence_label: int
    split: str
    source_row: int


@dataclass(frozen=True)
class EntityToken:
    text: str
    label: str
    source_line: int


@dataclass(frozen=True)
class EntityRecord:
    record_id: str
    tokens: tuple[EntityToken, ...]
    reconstructed_text: str
    normalized_text: str
    split: str
    block_index: int
    source_line_start: int
    source_line_end: int
    has_attack_token: bool


@dataclass(frozen=True)
class MalformedRecord:
    split: str
    source_path: str
    source_line: int
    kind: str
    message: str
    raw_text: str


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class RowAudit:
    classification: ClassificationRecord
    entity_ids: tuple[str, ...]
    alignment_type: str
    evidence_spans: tuple[Span, ...]
    has_span_annotation: bool
    span_loss_mask: bool
    has_attack_evidence: bool | None
    negative_conflict: bool
    duplicate_alignment: bool
    span_reason: str


@dataclass(frozen=True)
class SourceData:
    classifications: dict[str, tuple[ClassificationRecord, ...]]
    entities: dict[str, tuple[EntityRecord, ...]]
    malformed: tuple[MalformedRecord, ...]


@dataclass(frozen=True)
class DiagnosticCandidate:
    entity_id: str
    text: str
    normalized_text: str
    similarity: float
    category: str


@dataclass(frozen=True)
class AuditBundle:
    source_data: SourceData
    rows: tuple[RowAudit, ...]
    diagnostics: dict[str, DiagnosticCandidate]
    decision: str
    negative_span_supervision_safe: bool
    classification_label_conflict_keys: tuple[str, ...]
    negative_conflict_keys: tuple[str, ...]
