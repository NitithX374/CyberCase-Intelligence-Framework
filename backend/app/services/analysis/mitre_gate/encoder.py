from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import settings
from app.services.analysis.mitre_gate.llm import (
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.services.analysis.mitre_gate.sentences import split_sources
from app.services.sources.case_source_bundle import CaseSourceItem

logger = logging.getLogger(__name__)

MAX_TRIGGERS = 16
MAX_TRIGGER_CHARS = 500
BATCH = 32


@dataclass(frozen=True)
class Loaded:
    torch: Any
    tokenizer: Any
    model: Any
    positive_index: int
    threshold: float
    max_tokens: int


@lru_cache(maxsize=1)
def loaded_gate() -> Loaded:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    path = Path(settings.mitre_gate_model_path)
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path).eval()
    card = json.loads((path / "gate.json").read_text(encoding="utf-8"))
    logger.info("MITRE encoder gate loaded from %s threshold=%.2f", path, card["threshold"])
    return Loaded(
        torch=torch,
        tokenizer=tokenizer,
        model=model,
        positive_index=int(card["positive_index"]),
        threshold=float(card["threshold"]),
        max_tokens=int(card["max_tokens"]),
    )


def scores(texts: Sequence[str]) -> list[float]:
    gate = loaded_gate()
    out: list[float] = []
    for start in range(0, len(texts), BATCH):
        encoded = gate.tokenizer(
            list(texts[start : start + BATCH]),
            padding=True,
            truncation=True,
            max_length=gate.max_tokens,
            return_tensors="pt",
        )
        with gate.torch.no_grad():
            logits = gate.model(**encoded).logits
        out += gate.torch.softmax(logits, dim=-1)[:, gate.positive_index].tolist()
    return out


async def evaluate_mitre_applicability_encoder(
    *,
    case_sources: Sequence[CaseSourceItem],
) -> MitreApplicabilityRecord:
    sentences = split_sources(case_sources)
    if not sentences:
        return skipped_mitre_applicability()

    threshold = loaded_gate().threshold
    measured = await asyncio.to_thread(scores, [item.text for item in sentences])

    triggered = sorted(
        (
            (score, sentence)
            for score, sentence in zip(measured, sentences, strict=True)
            if score >= threshold
        ),
        key=lambda pair: -pair[0],
    )

    trigger_text: list[str] = []
    source_message_ids: list[str] = []
    for _, sentence in triggered:
        text = sentence.text[:MAX_TRIGGER_CHARS]
        if text in trigger_text:
            continue
        trigger_text.append(text)
        if sentence.source_id not in source_message_ids:
            source_message_ids.append(sentence.source_id)
        if len(trigger_text) == MAX_TRIGGERS:
            break

    if not trigger_text:
        return skipped_mitre_applicability()
    return MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=source_message_ids,
        trigger_text=trigger_text,
    )


__all__ = ["MAX_TRIGGERS", "evaluate_mitre_applicability_encoder", "scores"]
