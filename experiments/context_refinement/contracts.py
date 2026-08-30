from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class RefinedContext:
    raw_context: str
    refined_context: str
    origin_tokens: int | None
    refined_tokens: int | None


class ContextRefiner(Protocol):
    name: str
    config: dict[str, Any]

    def refine(self, context: str) -> RefinedContext:
        ...

