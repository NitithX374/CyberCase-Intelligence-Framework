from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class PipelineDependencies:
    session_factory: Callable[..., Any]
    worker_type: type[Any]
    rag_request: Callable[..., Any]
    analysis_request: Callable[..., Any]
    followup_evaluator: Callable[..., Any]
