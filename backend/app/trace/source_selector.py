from __future__ import annotations

import logging
import threading
from collections.abc import Sequence
from pathlib import Path

from app.config import settings
from app.trace.b1_verifier import ARTIFACT
from app.trace.nli_model import NliUnavailable, file_sha256

logger = logging.getLogger(__name__)
loading = threading.Lock()
inference = threading.Semaphore(1)


class SourceSelector:
    def __init__(self, model) -> None:
        self.model = model

    def similarities(self, claim: str, units: Sequence[str]) -> list[float]:
        import numpy as np

        with inference:
            vectors = self.model.encode(
                [claim, *units],
                batch_size=64,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        return np.dot(vectors[1:], vectors[0]).tolist()


_state: SourceSelector | NliUnavailable | None = None


def build() -> SourceSelector:
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
    global _state
    with loading:
        if _state is None:
            try:
                _state = build()
            except NliUnavailable as error:
                logger.error("Claim Source selector unavailable: %s", error.reason)
                _state = error
    if isinstance(_state, NliUnavailable):
        raise NliUnavailable(_state.reason)
    return _state
