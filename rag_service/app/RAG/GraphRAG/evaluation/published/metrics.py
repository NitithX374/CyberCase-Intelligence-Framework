"""
TechniqueRAG-Compatible Metrics
=================================
Scoring that matches the protocol published with TechniqueRAG
(qcri/TechniqueRAG, evaluate.py) so our numbers land in the same table as
theirs and as the H-TechniqueRAG baselines that reuse it.

Their protocol, restated:

  per sample   precision = |pred INTERSECT gold| / |pred|   (0 when pred empty)
               recall    = |pred INTERSECT gold| / |gold|
  corpus       P = mean(precision), R = mean(recall)      <- macro over samples
               F1 = 2PR / (P + R)                          <- from the MEANS,
                                                              not mean of F1s
  modes        "technique"    : strip .NNN from gold and pred, then dedup
               "subtechnique" : keep full IDs
  validity     predictions not in the ATT&CK knowledge base are dropped before
               scoring; gold is never filtered

Two deliberate deviations, both reported rather than hidden:

1. MRR. Upstream computes reciprocal rank over `preds` AFTER `list(set(preds))`,
   which destroys the model ranking - and because Python randomises str hashing
   per process, upstream MRR is not even reproducible run to run. We keep the
   real ranking and expose `mrr`, plus `mrr_upstream` which reproduces the
   set-mangled variant for anyone who wants the exact upstream number.
   Treat MRR as the one metric that is not strictly comparable.

2. Macro-F1-of-means is a strange estimator, so `f1_micro` is also reported
   (pooled intersection / pooled sizes). Headline comparisons use `f1`, the
   upstream-compatible one.

All functions are pure - no network, no models.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

ATTACK_ID_RE = re.compile(r"T\d{4}(?:\.\d{3})?")

MODES = ("technique", "subtechnique")


def extract_attack_ids(text: str) -> list[str]:
    """Ordered, deduped ATT&CK technique IDs mentioned in free text.

    Order is first-mention order, which is what makes rank-aware scoring
    meaningful on generated answers. Upstream uses `list(set(...))` here and
    loses that ordering.
    """
    seen: list[str] = []
    for match in ATTACK_ID_RE.findall(text or ""):
        if match not in seen:
            seen.append(match)
    return seen


def _normalise(ids: Iterable[str], mode: str) -> list[str]:
    """Apply the mode projection and dedup, preserving first-seen order."""
    out: list[str] = []
    for i in ids:
        v = i.split(".")[0] if mode == "technique" else i
        if v not in out:
            out.append(v)
    return out


@dataclass
class SampleScore:
    precision: float
    recall: float
    reciprocal_rank: float
    n_pred: int
    n_gold: int
    n_hit: int


@dataclass
class CorpusScore:
    """Aggregate scores. `f1` is the upstream-compatible F1-of-means."""

    mode: str
    n_samples: int
    precision: float
    recall: float
    f1: float
    mrr: float
    mrr_upstream: float
    f1_micro: float
    n_empty_predictions: int
    per_sample: list[SampleScore] = field(default_factory=list, repr=False)

    def as_row(self, label: str) -> str:
        return (
            "| " + label
            + " | " + format(self.precision, ".4f")
            + " | " + format(self.recall, ".4f")
            + " | " + format(self.f1, ".4f")
            + " | " + format(self.mrr, ".4f")
            + " | " + format(self.f1_micro, ".4f")
            + " |"
        )


def score_sample(
    predicted: Sequence[str],
    gold: Sequence[str],
    mode: str = "technique",
    valid_ids: Optional[set[str]] = None,
) -> SampleScore:
    """Score one sample. `predicted` must be in model-ranked order."""
    if mode not in MODES:
        raise ValueError("mode must be one of " + str(MODES))

    preds = _normalise(predicted, mode)
    if valid_ids is not None:
        preds = [p for p in preds if p in valid_ids]
    trues = _normalise(gold, mode)
    true_set = set(trues)

    hits = [p for p in preds if p in true_set]
    precision = len(hits) / len(preds) if preds else 0.0
    recall = len(hits) / len(trues) if trues else 0.0

    reciprocal_rank = 0.0
    for rank, p in enumerate(preds, start=1):
        if p in true_set:
            reciprocal_rank = 1.0 / rank
            break

    return SampleScore(
        precision=precision,
        recall=recall,
        reciprocal_rank=reciprocal_rank,
        n_pred=len(preds),
        n_gold=len(trues),
        n_hit=len(hits),
    )


def _upstream_rr(predicted: Sequence[str], gold: Sequence[str], mode: str, valid_ids) -> float:
    """Reproduce upstream MRR, including its order-destroying `list(set(...))`."""
    preds = _normalise(predicted, mode)
    if valid_ids is not None:
        preds = [p for p in preds if p in valid_ids]
    preds = list(set(preds))
    true_set = set(_normalise(gold, mode))
    for rank, p in enumerate(preds, start=1):
        if p in true_set:
            return 1.0 / rank
    return 0.0


def score_corpus(
    samples: Iterable[tuple[Sequence[str], Sequence[str]]],
    mode: str = "technique",
    valid_ids: Optional[set[str]] = None,
) -> CorpusScore:
    """Score (predicted, gold) pairs with the upstream aggregation rules."""
    scores: list[SampleScore] = []
    upstream_rrs: list[float] = []
    pooled_hit = pooled_pred = pooled_gold = 0

    for predicted, gold in samples:
        s = score_sample(predicted, gold, mode=mode, valid_ids=valid_ids)
        scores.append(s)
        upstream_rrs.append(_upstream_rr(predicted, gold, mode, valid_ids))
        pooled_hit += s.n_hit
        pooled_pred += s.n_pred
        pooled_gold += s.n_gold

    n = len(scores)
    if n == 0:
        return CorpusScore(mode, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)

    precision = sum(s.precision for s in scores) / n
    recall = sum(s.recall for s in scores) / n
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    mrr = sum(s.reciprocal_rank for s in scores) / n
    mrr_upstream = sum(upstream_rrs) / n

    micro_p = pooled_hit / pooled_pred if pooled_pred else 0.0
    micro_r = pooled_hit / pooled_gold if pooled_gold else 0.0
    f1_micro = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) else 0.0

    return CorpusScore(
        mode=mode,
        n_samples=n,
        precision=precision,
        recall=recall,
        f1=f1,
        mrr=mrr,
        mrr_upstream=mrr_upstream,
        f1_micro=f1_micro,
        n_empty_predictions=sum(1 for s in scores if s.n_pred == 0),
        per_sample=scores,
    )


def score_at_k(
    samples: Iterable[tuple[Sequence[str], Sequence[str]]],
    k: int,
    mode: str = "technique",
    valid_ids: Optional[set[str]] = None,
) -> CorpusScore:
    """Upstream reports P@k / R@k for k in {1, 3} on ranking methods."""
    truncated = [(list(p)[:k], g) for p, g in samples]
    return score_corpus(truncated, mode=mode, valid_ids=valid_ids)


MARKDOWN_HEADER = (
    "| Run | Precision | Recall | F1 | MRR | F1-micro |\n"
    "|-----|-----------|--------|----|-----|----------|"
)
