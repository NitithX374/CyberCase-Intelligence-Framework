from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from app.trace.nli_model import MdebertaNli, NliProbabilities, load_nli

ARTIFACT_PATH = Path(__file__).with_name("b1_lr.json")
ARTIFACT = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
METHOD = ARTIFACT["method"]
THRESHOLD = ARTIFACT["threshold"]
ARTIFACT_SHA256 = hashlib.sha256(ARTIFACT_PATH.read_bytes()).hexdigest()


def supported_probability(probabilities: Sequence[float]) -> float:
    if len(probabilities) != 3 or any(
        not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities
    ):
        raise ValueError("B1-LR requires three finite NLI probabilities in E/N/C order")
    if not math.isclose(sum(probabilities), 1, abs_tol=0.002):
        raise ValueError("NLI probabilities must sum to one")
    logit = ARTIFACT["intercept"] + sum(
        weight * probability
        for weight, probability in zip(ARTIFACT["weights"], probabilities, strict=True)
    )
    return 1 / (1 + math.exp(-logit))


def selected_indices(similarities: Sequence[float]) -> tuple[int, ...]:
    if any(not math.isfinite(value) for value in similarities):
        raise ValueError("Source similarities must be finite")
    indices = tuple(
        i for i, value in enumerate(similarities) if value >= ARTIFACT["selector_threshold"]
    )
    if not indices and similarities:
        indices = (max(range(len(similarities)), key=similarities.__getitem__),)
    return indices


@dataclass(frozen=True)
class ClaimVerification:
    nli: NliProbabilities
    p_supported: float
    indices: tuple[int, ...]
    similarities: tuple[float, ...]
    selection_ms: float


class B1Verifier:
    name = f"{METHOD}:{MdebertaNli.name}"

    def __init__(self, selector, nli: MdebertaNli) -> None:
        self.selector = selector
        self.nli = nli

    def verify(self, claim: str, units: Sequence[str]) -> ClaimVerification:
        if not units:
            raise ValueError("B1-LR requires resolved Source units")
        started = perf_counter()
        similarities = tuple(self.selector.similarities(claim, units))
        if len(similarities) != len(units):
            raise ValueError("Selector scores must address every Source unit")
        indices = selected_indices(similarities)
        selection_ms = (perf_counter() - started) * 1_000
        premise = ARTIFACT["premise_separator"].join(units[index] for index in indices)
        result = self.nli.predict(premise, claim)
        return ClaimVerification(
            result, supported_probability(result.vector), indices, similarities, selection_ms
        )


def load_verifier() -> B1Verifier:
    from app.trace.source_selector import load_selector

    return B1Verifier(load_selector(), load_nli())
