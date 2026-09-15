from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RawEvidenceSource:
    message_id: UUID
    content: str
    document_sources: tuple[dict[str, object], ...] = ()


__all__ = ["RawEvidenceSource"]
