import json
from pathlib import Path
from typing import Any
import numpy as np

from config import (
    FORWARD_NLI_CACHE_DIR,
    REVERSE_NLI_CACHE_DIR,
)
from src.datasets.wice import WiCEExample
from src.nli import NLIRunner

def load_or_compute_nli(
    runner: NLIRunner,
    premises: list[str],
    hypotheses: list[str],
    examples: list[WiCEExample],
    cache_dir: Path,
    cache_key: str,
    batch_size: int = 8,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    cache_file = cache_dir / f"{cache_key}.jsonl"
    if cache_file.exists():
        records: list[dict[str, Any]] = []
        with open(cache_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        if len(records) == len(examples):
            probs = np.array(
                [[r["p_entailment"], r["p_neutral"], r["p_contradiction"]] for r in records],
                dtype=np.float32,
            )
            meta = [{"num_tokens": r["num_tokens"], "truncated": r["truncated"]} for r in records]
            return probs, meta

    # Compute
    probs, meta = runner.predict_probs(premises, hypotheses, batch_size=batch_size)

    # Save cache
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        for idx, ex in enumerate(examples):
            rec = {
                "example_id": ex.example_id,
                "claim_id": ex.claim_id,
                "gold_label_3class": ex.gold_label_3class,
                "gold_label_binary": ex.gold_label_binary,
                "p_entailment": float(probs[idx, 0]),
                "p_neutral": float(probs[idx, 1]),
                "p_contradiction": float(probs[idx, 2]),
                "num_tokens": meta[idx]["num_tokens"],
                "truncated": meta[idx]["truncated"],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return probs, meta

def get_forward_nli_all(
    runner: NLIRunner,
    examples: list[WiCEExample],
    split: str,
    batch_size: int = 8,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    premises = ["\n".join(ex.evidence_units) for ex in examples]
    hypotheses = [ex.claim for ex in examples]
    return load_or_compute_nli(
        runner,
        premises,
        hypotheses,
        examples,
        FORWARD_NLI_CACHE_DIR,
        f"{split}_forward_all",
        batch_size=batch_size,
    )

def get_reverse_nli_all(
    runner: NLIRunner,
    examples: list[WiCEExample],
    split: str,
    batch_size: int = 8,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    premises = [ex.claim for ex in examples]
    hypotheses = ["\n".join(ex.evidence_units) for ex in examples]
    return load_or_compute_nli(
        runner,
        premises,
        hypotheses,
        examples,
        REVERSE_NLI_CACHE_DIR,
        f"{split}_reverse_all",
        batch_size=batch_size,
    )

def get_forward_nli_filtered(
    runner: NLIRunner,
    examples: list[WiCEExample],
    filtered_evidence_list: list[list[str]],
    split: str,
    threshold_str: str,
    batch_size: int = 8,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    premises = ["\n".join(units) for units in filtered_evidence_list]
    hypotheses = [ex.claim for ex in examples]
    return load_or_compute_nli(
        runner,
        premises,
        hypotheses,
        examples,
        FORWARD_NLI_CACHE_DIR,
        f"{split}_forward_filt_{threshold_str}",
        batch_size=batch_size,
    )

def get_reverse_nli_filtered(
    runner: NLIRunner,
    examples: list[WiCEExample],
    filtered_evidence_list: list[list[str]],
    split: str,
    threshold_str: str,
    batch_size: int = 8,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    premises = [ex.claim for ex in examples]
    hypotheses = ["\n".join(units) for units in filtered_evidence_list]
    return load_or_compute_nli(
        runner,
        premises,
        hypotheses,
        examples,
        REVERSE_NLI_CACHE_DIR,
        f"{split}_reverse_filt_{threshold_str}",
        batch_size=batch_size,
    )
