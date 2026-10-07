import json
import logging
from pathlib import Path
from typing import Any
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import (
    NLI_MODEL_NAME,
    DEVICE,
    NLI_MAX_LENGTH,
    FORWARD_NLI_CACHE_DIR,
    REVERSE_NLI_CACHE_DIR,
    HF_CACHE_DIRS,
)

logger = logging.getLogger(__name__)

class NLIRunner:
    def __init__(self, model_name: str = NLI_MODEL_NAME, device: torch.device = DEVICE):
        self.device = device
        self.tokenizer = None
        self.model = None
        self.id2label = None
        self.entail_idx = None
        self.neutral_idx = None
        self.contra_idx = None
        self._load_model(model_name)

    def _load_model(self, model_name: str) -> None:
        # Check cache directories
        loaded = False
        for cache_dir in HF_CACHE_DIRS:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
                loaded = True
                break
            except Exception:
                continue

        if not loaded:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

        self.model.to(self.device)
        self.model.eval()

        self.id2label = self.model.config.id2label
        # Map label names to class indices
        label2id = {v.lower(): k for k, v in self.id2label.items()}
        self.entail_idx = label2id["entailment"]
        self.neutral_idx = label2id["neutral"]
        self.contra_idx = label2id["contradiction"]
        logger.info(
            f"NLI Model loaded on {self.device}. Label mapping: entail={self.entail_idx}, "
            f"neutral={self.neutral_idx}, contra={self.contra_idx}"
        )

    def predict_probs(
        self,
        premises: list[str],
        hypotheses: list[str],
        batch_size: int = 8,
    ) -> tuple[np.ndarray, list[dict[str, Any]]]:
        """
        Runs NLI inference on premise-hypothesis pairs.
        Returns:
            probs: np.ndarray of shape (N, 3) where columns are [P(entail), P(neutral), P(contra)]
            meta: list of dicts with token counts and truncation info.
        """
        all_probs: list[np.ndarray] = []
        meta_list: list[dict[str, Any]] = []

        for i in range(0, len(premises), batch_size):
            batch_p = premises[i : i + batch_size]
            batch_h = hypotheses[i : i + batch_size]

            # Tokenize without truncation first to check true token count
            raw_encoded = self.tokenizer(
                batch_p,
                batch_h,
                padding=False,
                truncation=False,
                return_attention_mask=False,
            )

            # Tokenize with truncation to max_length
            inputs = self.tokenizer(
                batch_p,
                batch_h,
                padding=True,
                truncation=True,
                max_length=NLI_MAX_LENGTH,
                return_tensors="pt",
            ).to(self.device)

            with torch.inference_mode():
                outputs = self.model(**inputs)
                logits = outputs.logits
                batch_softmax = torch.softmax(logits, dim=-1).cpu().numpy()

            for idx, raw_ids in enumerate(raw_encoded["input_ids"]):
                num_tokens = len(raw_ids)
                is_truncated = num_tokens > NLI_MAX_LENGTH
                meta_list.append(
                    {
                        "num_tokens": num_tokens,
                        "truncated": is_truncated,
                    }
                )

                row = batch_softmax[idx]
                ordered_probs = np.array(
                    [row[self.entail_idx], row[self.neutral_idx], row[self.contra_idx]],
                    dtype=np.float32,
                )
                all_probs.append(ordered_probs)

        return np.vstack(all_probs), meta_list


def get_cached_nli(
    cache_dir: Path,
    cache_key: str,
) -> list[dict[str, Any]] | None:
    cache_file = cache_dir / f"{cache_key}.jsonl"
    if not cache_file.exists():
        return None
    records: list[dict[str, Any]] = []
    with open(cache_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def save_cached_nli(
    cache_dir: Path,
    cache_key: str,
    records: list[dict[str, Any]],
) -> None:
    cache_file = cache_dir / f"{cache_key}.jsonl"
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
