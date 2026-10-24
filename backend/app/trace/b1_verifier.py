from __future__ import annotations

import hashlib
import json
import logging
import math
import threading
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from app.config import settings
from app.trace.nli_model import MdebertaNli, NliProbabilities, NliUnavailable, file_sha256, load_nli

logger = logging.getLogger(__name__)
selector_loading = threading.Lock()
selector_inference = threading.Semaphore(1)

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


class SourceSelector:
    def __init__(self, model) -> None:
        self.model = model

    def similarities(self, claim: str, units: Sequence[str]) -> list[float]:
        import numpy as np

        with selector_inference:
            vectors = self.model.encode(
                [claim, *units],
                batch_size=64,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        return np.dot(vectors[1:], vectors[0]).tolist()


_selector: SourceSelector | NliUnavailable | None = None


def build_selector() -> SourceSelector:
    path = Path(settings.claim_selector_path)
    for filename, expected in ARTIFACT["selector_hashes"].items():
        asset = path / filename
        if not asset.is_file():
            raise NliUnavailable(f"selector_asset_missing:{filename}")
        if file_sha256(asset) != expected:
            raise NliUnavailable(f"selector_hash_mismatch:{filename}")
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise NliUnavailable("selector_libraries_missing") from error
    try:
        model = SentenceTransformer(str(path), device="cpu", local_files_only=True)
    except Exception as error:
        raise NliUnavailable(f"selector_load_failed:{type(error).__name__}") from error
    if model.max_seq_length != ARTIFACT["selector_max_tokens"]:
        raise NliUnavailable("selector_token_limit_mismatch")
    logger.info("Claim Source selector loaded from %s", path)
    return SourceSelector(model)


def load_selector() -> SourceSelector:
    global _selector
    with selector_loading:
        if _selector is None:
            try:
                _selector = build_selector()
            except NliUnavailable as error:
                logger.error("Claim Source selector unavailable: %s", error.reason)
                _selector = error
    if isinstance(_selector, NliUnavailable):
        raise NliUnavailable(_selector.reason)
    return _selector


def load_verifier() -> B1Verifier:
    return B1Verifier(load_selector(), load_nli())
