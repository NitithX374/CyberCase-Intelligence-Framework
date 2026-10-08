from __future__ import annotations

import hashlib
import json
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
MODEL_REVISION = "b5113eb38ab63efdd7f280f8c144ea8b13f978ce"
WEIGHTS_FILE = "model.safetensors"
WEIGHTS_SHA256 = "7c8e29f1115986d032e92b0fbaa0bdef1062a46f658b08705f237c05014a8541"
LABEL_ORDER = ("entailment", "neutral", "contradiction")
MAX_TOKENS = 512
READ_CHUNK = 1 << 20

loading = threading.Lock()
inference = threading.Semaphore(1)


class NliUnavailable(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class Judgement:
    label: str
    entailment: float


@dataclass(frozen=True)
class NliProbabilities:
    entailment: float
    neutral: float
    contradiction: float
    raw_tokens: int
    truncated: bool

    @property
    def vector(self) -> tuple[float, float, float]:
        return self.entailment, self.neutral, self.contradiction

    @property
    def label(self) -> str:
        return LABEL_ORDER[max(range(3), key=self.vector.__getitem__)]


class MdebertaNli:
    name = f"{MODEL_NAME}@{MODEL_REVISION[:12]}"

    def __init__(self, torch: Any, tokenizer: Any, model: Any, order: tuple[str, ...]) -> None:
        self.torch = torch
        self.tokenizer = tokenizer
        self.model = model
        self.order = order

    def encoded(self, premise: str, hypothesis: str) -> Any:
        return self.tokenizer(
            premise, hypothesis, truncation=False, return_tensors="pt", verbose=False
        )

    def fits(self, premise: str, hypothesis: str) -> bool:
        return int(self.encoded(premise, hypothesis)["input_ids"].shape[-1]) <= MAX_TOKENS

    def judge(self, premise: str, hypothesis: str) -> Judgement:
        batch = self.encoded(premise, hypothesis)
        with inference, self.torch.no_grad():
            probabilities = self.torch.softmax(self.model(**batch).logits, dim=-1)[0].tolist()
        scores = dict(zip(self.order, probabilities, strict=True))
        return Judgement(label=max(scores, key=scores.__getitem__), entailment=scores["entailment"])

    def predict(self, premise: str, hypothesis: str) -> NliProbabilities:
        raw_tokens = int(self.encoded(premise, hypothesis)["input_ids"].shape[-1])
        batch = self.tokenizer(
            premise,
            hypothesis,
            truncation=True,
            max_length=MAX_TOKENS,
            return_tensors="pt",
            verbose=False,
        )
        with inference, self.torch.no_grad():
            probabilities = self.torch.softmax(self.model(**batch).logits, dim=-1)[0].tolist()
        scores = dict(zip(self.order, probabilities, strict=True))
        return NliProbabilities(
            scores["entailment"],
            scores["neutral"],
            scores["contradiction"],
            raw_tokens,
            raw_tokens > MAX_TOKENS,
        )


_state: MdebertaNli | NliUnavailable | None = None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(READ_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def label_order(path: Path) -> tuple[str, ...]:
    config = json.loads((path / "config.json").read_text(encoding="utf-8"))
    labels = config.get("id2label") or {}
    order = tuple(str(labels.get(str(index), "")).lower() for index in range(len(labels)))
    if order != LABEL_ORDER:
        raise NliUnavailable("label_mapping_mismatch")
    return order


def build() -> MdebertaNli:
    path = Path(settings.claim_nli_path)
    weights = path / WEIGHTS_FILE
    if not weights.is_file() or not (path / "config.json").is_file():
        raise NliUnavailable("weights_missing")
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as error:
        raise NliUnavailable("libraries_missing") from error
    if file_sha256(weights) != WEIGHTS_SHA256:
        raise NliUnavailable("weights_hash_mismatch")
    order = label_order(path)
    try:
        tokenizer = AutoTokenizer.from_pretrained(path)
        model = AutoModelForSequenceClassification.from_pretrained(path).eval()
    except Exception as error:
        raise NliUnavailable(f"load_failed:{type(error).__name__}") from error
    logger.info("Claim support NLI loaded from %s", path)
    return MdebertaNli(torch, tokenizer, model, order)


def load_nli() -> MdebertaNli:
    global _state
    with loading:
        if _state is None:
            try:
                _state = build()
            except NliUnavailable as error:
                logger.warning("Claim support NLI unavailable: %s", error.reason)
                _state = error
    if isinstance(_state, NliUnavailable):
        raise NliUnavailable(_state.reason)
    return _state


def forget() -> None:
    global _state
    with loading:
        _state = None


__all__ = [
    "Judgement",
    "LABEL_ORDER",
    "MAX_TOKENS",
    "MODEL_NAME",
    "MODEL_REVISION",
    "MdebertaNli",
    "NliUnavailable",
    "WEIGHTS_SHA256",
    "forget",
    "load_nli",
]
