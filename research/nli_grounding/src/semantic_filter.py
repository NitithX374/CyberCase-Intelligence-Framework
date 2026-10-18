import json
import logging
from pathlib import Path
from typing import Any
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_MODEL_NAME,
    DEVICE,
    SEMANTIC_CACHE_DIR,
    HF_CACHE_DIRS,
)
from src.datasets.wice import WiCEExample
from src.metrics import compute_evidence_retrieval_metrics

logger = logging.getLogger(__name__)

class SemanticFilter:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME, device: torch.device = DEVICE):
        self.device = device
        self.model = None
        self._load_model(model_name)

    def _load_model(self, model_name: str) -> None:
        loaded = False
        for cache_dir in HF_CACHE_DIRS:
            try:
                self.model = SentenceTransformer(model_name, cache_folder=cache_dir, device=str(self.device))
                loaded = True
                break
            except Exception:
                continue

        if not loaded:
            self.model = SentenceTransformer(model_name, device=str(self.device))
        logger.info(f"SentenceTransformer loaded on {self.device}")

    def compute_similarities(
        self,
        examples: list[WiCEExample],
        batch_size: int = 64,
    ) -> list[list[float]]:
        """
        Computes cosine similarities between Claim and each candidate EvidenceUnit.
        Both embeddings are normalized, so cosine similarity = dot product.
        Optimized to batch-encode all evidence units in a single forward pass.
        """
        if not examples:
            return []

        # Collect claims
        claims = [ex.claim for ex in examples]
        claim_embeddings = self.model.encode(
            claims,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        # Flatten all evidence units
        flat_units: list[str] = []
        slices: list[tuple[int, int]] = []
        curr = 0
        for ex in examples:
            n_u = len(ex.evidence_units)
            slices.append((curr, curr + n_u))
            flat_units.extend(ex.evidence_units)
            curr += n_u

        if flat_units:
            unit_embeddings = self.model.encode(
                flat_units,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        else:
            unit_embeddings = np.empty((0, claim_embeddings.shape[1]), dtype=np.float32)

        all_sims: list[list[float]] = []
        for i, (start, end) in enumerate(slices):
            if end == start:
                all_sims.append([])
            else:
                c_emb = claim_embeddings[i]
                u_embs = unit_embeddings[start:end]
                sims = np.dot(u_embs, c_emb).tolist()
                all_sims.append([float(s) for s in sims])

        return all_sims

    @staticmethod
    def filter_units(
        evidence_units: list[str],
        similarities: list[float],
        threshold: float,
    ) -> tuple[list[str], list[int]]:
        """
        Filters EvidenceUnits using a similarity threshold.
        Deterministic Fallback Rule:
        If no EvidenceUnit passes the threshold, keep the single highest-similarity EvidenceUnit.
        Preserves original document order.
        """
        if not evidence_units:
            return [], []

        selected_indices = [
            idx for idx, sim in enumerate(similarities) if sim >= threshold
        ]

        # Deterministic fallback: keep single highest-similarity unit
        if not selected_indices and similarities:
            best_idx = int(np.argmax(similarities))
            selected_indices = [best_idx]

        filtered_units = [evidence_units[i] for i in selected_indices]
        return filtered_units, selected_indices

def get_cached_semantic_scores(split: str, cache_dir: Path = SEMANTIC_CACHE_DIR) -> list[list[float]] | None:
    cache_file = cache_dir / f"{split}.jsonl"
    if not cache_file.exists():
        return None
    records: list[list[float]] = []
    with open(cache_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                records.append(data["similarities"])
    return records

def save_cached_semantic_scores(
    examples: list[WiCEExample],
    similarities: list[list[float]],
    split: str,
    cache_dir: Path = SEMANTIC_CACHE_DIR,
) -> None:
    cache_file = cache_dir / f"{split}.jsonl"
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        for ex, sims in zip(examples, similarities):
            record = {
                "example_id": ex.example_id,
                "claim_id": ex.claim_id,
                "similarities": sims,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
