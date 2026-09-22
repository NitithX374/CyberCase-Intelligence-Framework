from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.experiments.ladder_relevance.gold_oracle_inference import (
    CheckpointResources,
    load_checkpoint,
    predict,
)

from .constants import LADDER_TEST


@dataclass(frozen=True)
class FrozenClassifier:
    resources: CheckpointResources
    threshold: float
    device: str


def load_frozen_classifier(
    checkpoint: Path, threshold: float, device: str
) -> FrozenClassifier:
    resources = load_checkpoint(checkpoint.resolve())
    if device == "auto":
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device not in {"cpu", "cuda"}:
        raise ValueError(f"Unsupported inference device: {device}")
    if device == "cuda":
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable")
    return FrozenClassifier(resources=resources, threshold=threshold, device=device)


def predict_texts(
    classifier: FrozenClassifier, texts: list[str], batch_size: int
) -> tuple[list[float], list[int], list[bool]]:
    return predict(
        classifier.resources,
        texts,
        batch_size=batch_size,
        device_name=classifier.device,
    )


def load_ladder_test() -> list[dict[str, Any]]:
    from backend.experiments.ladder_relevance.data import load_test

    if not LADDER_TEST.is_file():
        raise FileNotFoundError(f"LADDER test split was not found: {LADDER_TEST}")
    frame = load_test()
    return [
        {
            "text": str(row.text),
            "gold_label": int(row.label),
            "document": f"ladder_test_{int(row.sample_id)}",
        }
        for row in frame.itertuples(index=False)
    ]
