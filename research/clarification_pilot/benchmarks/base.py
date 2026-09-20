"""What a benchmark has to provide, and nothing more.

One adapter per benchmark, each returning the same sample type. The interface
is deliberately one method: anything richer would start encoding one
benchmark's idea of a turn into the harness.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
from random import Random
from typing import Protocol

from ..contracts import ClarificationBenchmarkSample


class BenchmarkAdapter(Protocol):
    name: str
    default_path: Path

    def load(self, path: Path) -> list[ClarificationBenchmarkSample]: ...


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stratified(
    samples: list[ClarificationBenchmarkSample],
    *,
    limit: int | None,
    seed: int = 42,
) -> list[ClarificationBenchmarkSample]:
    """A subset that keeps each source task's share, drawn reproducibly.

    Every arm runs on whatever this returns, so the paired design holds by
    construction -- there is one sample list per run, not one per arm.
    """

    if limit is None or limit >= len(samples):
        return sorted(samples, key=lambda item: item.sample_id)

    groups: dict[str, list[ClarificationBenchmarkSample]] = defaultdict(list)
    for sample in samples:
        groups[sample.hidden.source_task].append(sample)

    chosen: list[ClarificationBenchmarkSample] = []
    for task in sorted(groups):
        members = sorted(groups[task], key=lambda item: item.sample_id)
        share = round(limit * len(members) / len(samples))
        Random(f"{seed}:{task}").shuffle(members)
        chosen.extend(members[:share])

    # Rounding can land a place either side of the limit; settle it in sample
    # id order so the same limit always yields the same set.
    chosen.sort(key=lambda item: item.sample_id)
    if len(chosen) > limit:
        return chosen[:limit]
    if len(chosen) < limit:
        remaining = [s for s in sorted(samples, key=lambda i: i.sample_id) if s not in chosen]
        chosen.extend(remaining[: limit - len(chosen)])
        chosen.sort(key=lambda item: item.sample_id)
    return chosen


__all__ = ["BenchmarkAdapter", "file_sha256", "stratified"]
