"""Benchmark adapters. One per benchmark, registered by name."""

from __future__ import annotations

from .askbench import AskMindAdapter
from .base import BenchmarkAdapter, file_sha256, stratified
from .cybercase import CyberCaseAdapter

ADAPTERS: dict[str, type] = {
    AskMindAdapter.name: AskMindAdapter,
    CyberCaseAdapter.name: CyberCaseAdapter,
}


def adapter_for(name: str):
    if name not in ADAPTERS:
        raise KeyError(f"Unknown benchmark {name!r}. Available: {sorted(ADAPTERS)}")
    return ADAPTERS[name]()


__all__ = [
    "ADAPTERS",
    "AskMindAdapter",
    "BenchmarkAdapter",
    "CyberCaseAdapter",
    "adapter_for",
    "file_sha256",
    "stratified",
]
