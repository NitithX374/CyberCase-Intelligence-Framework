"""
Multi-label retrieval metrics
=============================
Metrics for the case where one incident falls under several sections at once.

Ordinary retrieval metrics assume one right answer. Legal work does not: a
ransomware case is พ.ร.บ.คอม ม.๙ *and* ม.๑๒ *and* ป.อาญา ม.๓๓๗, and a system
that finds two of the three has not half-answered the question — it has given a
prosecutor an incomplete charge sheet. Hit-rate at k counts that as a success,
which is why it is the wrong headline number here.

The formulations follow NitiBench (arXiv:2502.10868), which proposes
multi-label variants for exactly this reason in Thai legal QA. The paper's
prose descriptions are implemented as read; they have not been checked against
the authors' own code, so a difference in tie-breaking or in how an unreachable
gold item is scored is possible. Treat these as "our reading of NitiBench's
metrics", not as a reproduction of their numbers, and do not compare absolute
values against the paper.

    Recall@k         proportion of the gold sections that appear in the top k.
                     Partial credit; the gentlest of the three.
    MultiHitRate@k   1 only when *every* gold section appears in the top k.
                     All-or-nothing, and the number that matches what a charge
                     sheet actually needs.
    MultiMRR@k       reciprocal of the rank at which the last gold section
                     arrives — how deep a reader must go to have them all.
                     Zero when they are not all there.

Precision and F1 are included because recall alone rewards returning
everything, and a suggestion list that names fifteen sections is not usable by
someone who has to justify each one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean


@dataclass
class CaseScore:
    """Scores for one incident at one cut-off."""

    case_id: str
    k: int
    gold: list[str] = field(default_factory=list)
    retrieved: list[str] = field(default_factory=list)
    recall: float = 0.0
    precision: float = 0.0
    f1: float = 0.0
    multi_hit: float = 0.0
    multi_mrr: float = 0.0
    # Gold sections the retriever never returned, at any depth. Reported
    # separately because "ranked badly" and "absent from the index" need
    # different fixes.
    missed: list[str] = field(default_factory=list)


def score_case(
    case_id: str,
    gold: list[str],
    ranked: list[str],
    k: int,
) -> CaseScore:
    """Score one ranked list against one set of gold sections.

    `ranked` is the full ordered result list; `k` is where the caller would cut
    it. Passing the full list rather than a pre-truncated one lets `missed`
    distinguish a section ranked 30th from one that was never retrieved.
    """
    gold_set = list(dict.fromkeys(gold))
    top = ranked[:k]
    top_set = set(top)
    found = [g for g in gold_set if g in top_set]

    recall = len(found) / len(gold_set) if gold_set else 0.0
    precision = len(found) / len(top) if top else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    complete = len(found) == len(gold_set) and bool(gold_set)
    multi_hit = 1.0 if complete else 0.0
    # The rank that covers everything is the deepest gold item, not the first.
    multi_mrr = 1.0 / (max(top.index(g) for g in gold_set) + 1) if complete else 0.0

    return CaseScore(
        case_id=case_id,
        k=k,
        gold=gold_set,
        retrieved=top,
        recall=recall,
        precision=precision,
        f1=f1,
        multi_hit=multi_hit,
        multi_mrr=multi_mrr,
        missed=[g for g in gold_set if g not in ranked],
    )


@dataclass
class Summary:
    k: int
    cases: int
    recall: float
    precision: float
    f1: float
    multi_hit_rate: float
    multi_mrr: float
    never_retrieved: int

    def as_row(self) -> str:
        return (
            f"{self.k:>3}{self.recall:>10.3f}{self.precision:>11.3f}"
            f"{self.f1:>8.3f}{self.multi_hit_rate:>13.3f}"
            f"{self.multi_mrr:>10.3f}{self.never_retrieved:>10}"
        )


def summarise(scores: list[CaseScore], k: int) -> Summary:
    if not scores:
        return Summary(k, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
    return Summary(
        k=k,
        cases=len(scores),
        recall=mean(s.recall for s in scores),
        precision=mean(s.precision for s in scores),
        f1=mean(s.f1 for s in scores),
        multi_hit_rate=mean(s.multi_hit for s in scores),
        multi_mrr=mean(s.multi_mrr for s in scores),
        never_retrieved=sum(len(s.missed) for s in scores),
    )


HEADER = (
    f"{'k':>3}{'Recall':>10}{'Precision':>11}{'F1':>8}"
    f"{'MultiHit':>13}{'MultiMRR':>10}{'ขาดหาย':>10}"
)
