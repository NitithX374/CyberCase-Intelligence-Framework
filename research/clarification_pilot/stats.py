"""Paired tests, chosen by what the metric actually is.

Correctness is binary and measured on the same samples under both arms, so the
test for it is McNemar's, computed exactly from the two discordant counts. A
paired t-test or a rank test on 0/1 data answers a question nobody asked.

Turn counts and coverage are not binary, so those get a signed-rank test and a
bootstrap interval instead.

Standard library only: an experiment that needs SciPy installed to report its
own numbers is one more thing that can differ between two machines.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, erfc, sqrt
from random import Random


@dataclass(frozen=True)
class PairedBinary:
    """The four cells of a paired binary comparison."""

    both_right: int
    only_a: int
    only_b: int
    both_wrong: int
    p_value: float

    @property
    def n(self) -> int:
        return self.both_right + self.only_a + self.only_b + self.both_wrong

    @property
    def discordant(self) -> int:
        return self.only_a + self.only_b


def mcnemar(a: list[bool], b: list[bool]) -> PairedBinary:
    """Whether b differs from a, on paired binary outcomes.

    The exact two-sided binomial test over the discordant pairs, which holds at
    the sample sizes an undergraduate budget buys -- the chi-square form needs
    roughly 25 discordant pairs before it is trustworthy.
    """

    if len(a) != len(b):
        raise ValueError("Paired tests need the same samples in the same order")

    both_right = sum(1 for x, y in zip(a, b) if x and y)
    both_wrong = sum(1 for x, y in zip(a, b) if not x and not y)
    only_a = sum(1 for x, y in zip(a, b) if x and not y)
    only_b = sum(1 for x, y in zip(a, b) if y and not x)

    return PairedBinary(
        both_right=both_right,
        only_a=only_a,
        only_b=only_b,
        both_wrong=both_wrong,
        p_value=exact_binomial(only_b, only_a + only_b),
    )


def exact_binomial(successes: int, trials: int) -> float:
    """Two-sided exact p under p=0.5, by summing every outcome at least as extreme."""

    if trials == 0:
        return 1.0
    total = 2**trials
    observed = comb(trials, successes)
    tail = sum(comb(trials, k) for k in range(trials + 1) if comb(trials, k) <= observed)
    return min(1.0, tail / total)


def bootstrap_ci(
    differences: list[float],
    *,
    resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """(mean, low, high) for a paired difference, by percentile bootstrap."""

    if not differences:
        return 0.0, 0.0, 0.0
    mean = sum(differences) / len(differences)
    random = Random(seed)
    size = len(differences)
    means = []
    for _ in range(resamples):
        sample = [differences[random.randrange(size)] for _ in range(size)]
        means.append(sum(sample) / size)
    means.sort()
    lower = (1 - confidence) / 2
    low = means[int(lower * resamples)]
    high = means[min(resamples - 1, int((1 - lower) * resamples))]
    return mean, low, high


def wilcoxon(differences: list[float]) -> float:
    """Signed-rank p for paired non-binary differences, normal approximation.

    Approximate by construction; below roughly 20 non-zero differences read the
    bootstrap interval instead and treat this number as decoration.
    """

    non_zero = [value for value in differences if value != 0]
    if len(non_zero) < 2:
        return 1.0

    ordered = sorted(non_zero, key=abs)
    ranks: list[float] = [0.0] * len(ordered)
    index = 0
    while index < len(ordered):
        stop = index
        while stop + 1 < len(ordered) and abs(ordered[stop + 1]) == abs(ordered[index]):
            stop += 1
        shared = (index + stop) / 2 + 1
        for position in range(index, stop + 1):
            ranks[position] = shared
        index = stop + 1

    positive = sum(rank for value, rank in zip(ordered, ranks) if value > 0)
    count = len(ordered)
    expected = count * (count + 1) / 4
    variance = count * (count + 1) * (2 * count + 1) / 24
    if variance <= 0:
        return 1.0
    z = (positive - expected) / sqrt(variance)
    return erfc(abs(z) / sqrt(2))


__all__ = ["PairedBinary", "bootstrap_ci", "exact_binomial", "mcnemar", "wilcoxon"]
