from __future__ import annotations

import hashlib
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np

MODEL_ID = "BAAI/bge-m3"
REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
MAX_LENGTH = 8192
ASSETS = (
    "pytorch_model.bin",
    "config.json",
    "modules.json",
    "sentence_bert_config.json",
    "config_sentence_transformers.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "sentencepiece.bpe.model",
    "special_tokens_map.json",
    "1_Pooling/config.json",
)


def file_hash(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def cosine_pairs(embeddings: np.ndarray) -> np.ndarray:
    vectors = np.asarray(embeddings, dtype=np.float32)
    if vectors.ndim != 2 or len(vectors) % 2 or not np.isfinite(vectors).all():
        raise ValueError("Expected finite alternating EN/TH embedding pairs")
    norms = np.linalg.norm(vectors, axis=1)
    if np.any(norms == 0):
        raise ValueError("Zero embedding cannot define cosine similarity")
    vectors = vectors / norms[:, None]
    scores = np.einsum("ij,ij->i", vectors[::2], vectors[1::2])
    if np.any(np.abs(scores) > 1.00001):
        raise ValueError("Invalid cosine range")
    return np.clip(scores, -1, 1)


def load_model(path: Path, device: str, precision: str):
    import torch
    from sentence_transformers import SentenceTransformer

    if path.name != REVISION:
        raise ValueError("Use the declared pinned local BGE-M3 snapshot")
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Explicit CUDA runtime is unavailable")
    hashes = {name: file_hash(path / name) for name in ASSETS}
    model = SentenceTransformer(
        str(path),
        device=device,
        local_files_only=True,
        model_kwargs={
            "dtype": getattr(torch, precision),
            "attn_implementation": "sdpa",
        },
    )
    if (
        model.get_sentence_embedding_dimension() != 1024
        or model.max_seq_length != MAX_LENGTH
    ):
        raise ValueError("Unexpected pinned BGE-M3 embedding contract")
    runtime = {
        "model": MODEL_ID,
        "revision": REVISION,
        "asset_sha256": hashes,
        "device": device,
        "precision": str(next(model.parameters()).dtype),
        "pooling": "CLS",
        "dimension": 1024,
        "maximum_tokens": MAX_LENGTH,
        "attention": "sdpa",
        "similarity": "cosine; float32 L2 normalization and dot product",
        "python": platform.python_version(),
        "libraries": {
            name: version(name)
            for name in ("torch", "transformers", "sentence-transformers")
        },
        "cuda_device": torch.cuda.get_device_name() if device == "cuda" else None,
    }
    return model, runtime


def token_lengths(tokenizer, pairs: dict[str, dict]) -> dict[str, tuple[int, int]]:
    keys = list(pairs)
    lengths = {}
    for offset in range(0, len(keys), 256):
        batch = keys[offset : offset + 256]
        encodings = tokenizer(
            [
                pairs[key][language]
                for key in batch
                for language in ("source", "translation")
            ],
            truncation=False,
            padding=False,
        )["input_ids"]
        for index, key in enumerate(batch):
            lengths[key] = (len(encodings[2 * index]), len(encodings[2 * index + 1]))
    return lengths


def pair_batches(keys, lengths, maximum_pairs: int, token_budget: int):
    if maximum_pairs < 1 or token_budget < 2:
        raise ValueError("Batch settings must be positive")
    batch = []
    maximum = 0
    for key in sorted(keys, key=lambda key: (max(lengths[key]), key)):
        length = min(max(lengths[key]), MAX_LENGTH)
        next_maximum = max(maximum, length)
        if batch and (
            len(batch) == maximum_pairs
            or 2 * (len(batch) + 1) * next_maximum > token_budget
        ):
            yield batch
            batch, maximum = [], 0
        batch.append(key)
        maximum = max(maximum, length)
    if batch:
        yield batch
