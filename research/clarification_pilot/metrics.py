"""Turning per-sample records into the table the thesis reports.

Three things are kept visibly apart, because conflating them is how a
clarification result gets overstated:

* **what the answer scored** -- and how much of that rests on a judge,
* **whether asking was the right call** -- scored against the 53 AskMind items
  that were never degraded, so "asked unnecessarily" has a gold meaning,
* **what asking cost** -- candidate calls and tokens only. The simulator and
  the judge are apparatus; billing them to the system would flatter the
  baselines and inflate the treatment.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from statistics import median

from .contracts import ArmResult, ScoredResult
from .stats import PairedBinary, bootstrap_ci, mcnemar, wilcoxon

ARM_LABELS = {
    "direct": "Direct",
    "multi_stage": "Multi-stage",
    "gap_aware": "Gap-aware",
    "followup": "Bounded Follow-up",
}

FAILURE_KEYS = (
    "failed_to_ask",
    "asked_unnecessarily",
    "asked_irrelevant",
    "repeated_gap_or_question",
    "informed_but_still_wrong",
    "no_gain_over_baseline",
)


def key(scored: ScoredResult) -> tuple[str, int]:
    return scored.arm, scored.budget


@dataclass
class AskDecision:
    n: int = 0
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None


@dataclass
class ArmSummary:
    arm: str
    budget: int
    n: int
    accuracy: float
    deterministic_n: int
    deterministic_accuracy: float | None
    judged_n: int
    ask: AskDecision
    coverage_mean: float | None
    turns_mean: float
    turns_median: float
    turns_max: int
    questions_per_solved: float | None
    unnecessary_question_rate: float | None
    calls_mean: float
    input_tokens_mean: float
    output_tokens_mean: float
    latency_ms_mean: float
    stop_reasons: dict[str, int] = field(default_factory=dict)
    failures: dict[str, int] = field(default_factory=dict)
    errors: int = 0


def ask_decision(rows: list[ScoredResult]) -> AskDecision:
    """How well the sufficiency stage judged when clarification was needed.

    Only over rows where the arm actually made that decision, so Direct and
    Multi-stage come back empty rather than silently scoring as "never asks".
    """

    decided = [row for row in rows if row.predicted_ask is not None]
    if not decided:
        return AskDecision()

    tp = sum(1 for row in decided if row.predicted_ask and row.gold_should_ask)
    fp = sum(1 for row in decided if row.predicted_ask and not row.gold_should_ask)
    fn = sum(1 for row in decided if not row.predicted_ask and row.gold_should_ask)
    tn = sum(1 for row in decided if not row.predicted_ask and not row.gold_should_ask)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return AskDecision(
        n=len(decided),
        accuracy=(tp + tn) / len(decided),
        precision=precision,
        recall=recall,
        f1=f1,
    )


def failure_counts(
    rows: list[ScoredResult],
    runs: dict[str, ArmResult],
    baseline: dict[str, ScoredResult] | None,
) -> dict[str, int]:
    """The named ways a run went wrong, counted from records rather than judged."""

    counts = dict.fromkeys(FAILURE_KEYS, 0)
    for row in rows:
        run = runs.get(row.sample_id)
        # Only an arm that was allowed to ask can have failed to. Gap-aware
        # never asks by construction; its ask decision is scored in its own
        # table, not counted as a failure here.
        if row.budget > 0 and row.gold_should_ask and not row.asked:
            counts["failed_to_ask"] += 1
        if not row.gold_should_ask and row.asked:
            counts["asked_unnecessarily"] += 1
        if row.asked and row.checkpoints_total and row.checkpoints_covered == 0:
            counts["asked_irrelevant"] += 1
        if row.stop_reason in ("repeat_gap", "repeat_question"):
            counts["repeated_gap_or_question"] += 1
        if run is not None:
            informed = any(turn.simulator_knew for turn in run.turns)
            if row.asked and informed and not row.correct:
                counts["informed_but_still_wrong"] += 1
        if baseline is not None and row.asked:
            other = baseline.get(row.sample_id)
            if other is not None and other.correct == row.correct:
                counts["no_gain_over_baseline"] += 1
    return counts


def summarise(
    scored: list[ScoredResult],
    results: list[ArmResult],
    *,
    baseline_arm: str = "multi_stage",
) -> list[ArmSummary]:
    """One row per (arm, budget), over whatever samples the run covered."""

    by_arm: dict[tuple[str, int], list[ScoredResult]] = {}
    for row in scored:
        by_arm.setdefault(key(row), []).append(row)

    runs_by_arm: dict[tuple[str, int], dict[str, ArmResult]] = {}
    for run in results:
        runs_by_arm.setdefault((run.arm, run.budget), {})[run.sample_id] = run

    baselines = {row.sample_id: row for row in scored if row.arm == baseline_arm}

    def in_reading_order(item: tuple[tuple[str, int], list[ScoredResult]]) -> tuple[int, int]:
        (arm, budget), _ = item
        order = list(ARM_LABELS)
        return (order.index(arm) if arm in order else len(order), budget)

    summaries: list[ArmSummary] = []
    for (arm, budget), rows in sorted(by_arm.items(), key=in_reading_order):
        deterministic = [row for row in rows if row.scored_by == "exact_match"]
        judged = [row for row in rows if row.scored_by == "judge"]
        turns = [row.num_followups for row in rows]
        solved = [row for row in rows if row.correct]
        covered = [row.checkpoint_coverage for row in rows if row.checkpoint_coverage is not None]
        never_needed = [row for row in rows if not row.gold_should_ask]

        summaries.append(
            ArmSummary(
                arm=arm,
                budget=budget,
                n=len(rows),
                accuracy=sum(row.correct for row in rows) / len(rows),
                deterministic_n=len(deterministic),
                deterministic_accuracy=(
                    sum(row.correct for row in deterministic) / len(deterministic)
                    if deterministic
                    else None
                ),
                judged_n=len(judged),
                ask=ask_decision(rows),
                coverage_mean=sum(covered) / len(covered) if covered else None,
                turns_mean=sum(turns) / len(turns),
                turns_median=median(turns),
                turns_max=max(turns),
                questions_per_solved=(sum(turns) / len(solved)) if solved else None,
                unnecessary_question_rate=(
                    sum(1 for row in never_needed if row.asked) / len(never_needed)
                    if never_needed
                    else None
                ),
                calls_mean=sum(row.candidate_calls for row in rows) / len(rows),
                input_tokens_mean=sum(row.input_tokens for row in rows) / len(rows),
                output_tokens_mean=sum(row.output_tokens for row in rows) / len(rows),
                latency_ms_mean=sum(row.latency_ms for row in rows) / len(rows),
                stop_reasons=dict(Counter(row.stop_reason for row in rows)),
                failures=failure_counts(
                    rows,
                    runs_by_arm.get((arm, budget), {}),
                    baselines if arm != baseline_arm else None,
                ),
                errors=sum(1 for row in rows if row.error),
            )
        )
    return summaries


@dataclass
class Comparison:
    """One arm against another, on the samples both ran."""

    treatment: str
    baseline: str
    budget: int
    n: int
    treatment_accuracy: float
    baseline_accuracy: float
    recovery_gain: float
    ci_low: float
    ci_high: float
    mcnemar: PairedBinary
    turns_p: float


def compare(
    scored: list[ScoredResult],
    *,
    treatment: str,
    baseline: str,
    budget: int,
) -> Comparison | None:
    """Recovery gain, paired on sample id. The headline the experiment exists for."""

    treated = {
        row.sample_id: row for row in scored if row.arm == treatment and row.budget == budget
    }
    control = {row.sample_id: row for row in scored if row.arm == baseline}
    shared = sorted(set(treated) & set(control))
    if not shared:
        return None

    a = [control[sample].correct for sample in shared]
    b = [treated[sample].correct for sample in shared]
    differences = [float(y) - float(x) for x, y in zip(a, b)]
    mean, low, high = bootstrap_ci(differences)
    turn_differences = [
        float(treated[sample].num_followups - control[sample].num_followups) for sample in shared
    ]

    return Comparison(
        treatment=treatment,
        baseline=baseline,
        budget=budget,
        n=len(shared),
        treatment_accuracy=sum(b) / len(b),
        baseline_accuracy=sum(a) / len(a),
        recovery_gain=mean,
        ci_low=low,
        ci_high=high,
        mcnemar=mcnemar(a, b),
        turns_p=wilcoxon(turn_differences),
    )


# -- rendering ----------------------------------------------------------------


def percent(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def number(value: float | None, places: int = 2) -> str:
    return "—" if value is None else f"{value:.{places}f}"


def render_markdown(
    summaries: list[ArmSummary],
    comparisons: list[Comparison],
    *,
    title: str = "Clarification pilot",
) -> str:
    lines = [f"# {title}", ""]

    lines += [
        "## Final task performance",
        "",
        "| Method | Budget | n | Accuracy | Acc (deterministic) | Ask-F1 | CheckpointCov | Turns | Calls |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        lines.append(
            f"| {ARM_LABELS.get(item.arm, item.arm)} | {item.budget} | {item.n} | "
            f"{percent(item.accuracy)} | "
            f"{percent(item.deterministic_accuracy)} ({item.deterministic_n}) | "
            f"{percent(item.ask.f1)} | {percent(item.coverage_mean)} | "
            f"{number(item.turns_mean)} | {number(item.calls_mean)} |"
        )

    lines += [
        "",
        "## Ask decision, against the 53 items that were never degraded",
        "",
        "| Method | Budget | n decided | Accuracy | Precision | Recall | F1 | Unnecessary-ask rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        if not item.ask.n:
            continue
        lines.append(
            f"| {ARM_LABELS.get(item.arm, item.arm)} | {item.budget} | {item.ask.n} | "
            f"{percent(item.ask.accuracy)} | {percent(item.ask.precision)} | "
            f"{percent(item.ask.recall)} | {percent(item.ask.f1)} | "
            f"{percent(item.unnecessary_question_rate)} |"
        )

    lines += [
        "",
        "## Cost",
        "",
        "| Method | Budget | Candidate calls | Input tokens | Output tokens | Latency (ms) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        lines.append(
            f"| {ARM_LABELS.get(item.arm, item.arm)} | {item.budget} | "
            f"{number(item.calls_mean)} | {number(item.input_tokens_mean, 0)} | "
            f"{number(item.output_tokens_mean, 0)} | {number(item.latency_ms_mean, 0)} |"
        )

    lines += [
        "",
        "## Interaction",
        "",
        "| Method | Budget | Turns mean | median | max | Questions per solved | Stop reasons |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in summaries:
        stops = ", ".join(f"{name} {count}" for name, count in sorted(item.stop_reasons.items()))
        lines.append(
            f"| {ARM_LABELS.get(item.arm, item.arm)} | {item.budget} | "
            f"{number(item.turns_mean)} | {number(item.turns_median)} | {item.turns_max} | "
            f"{number(item.questions_per_solved)} | {stops} |"
        )

    lines += [
        "",
        "## Failure categories",
        "",
        "| Method | Budget | " + " | ".join(FAILURE_KEYS) + " |",
        "|---|---:|" + "---:|" * len(FAILURE_KEYS),
    ]
    for item in summaries:
        cells = " | ".join(str(item.failures.get(name, 0)) for name in FAILURE_KEYS)
        lines.append(f"| {ARM_LABELS.get(item.arm, item.arm)} | {item.budget} | {cells} |")

    if comparisons:
        lines += [
            "",
            "## Recovery gain, paired on sample id",
            "",
            "| Treatment | Baseline | Budget | n | Treatment | Baseline | Gain | 95% CI | McNemar p | discordant |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|---:|",
        ]
        for item in comparisons:
            lines.append(
                f"| {ARM_LABELS.get(item.treatment, item.treatment)} | "
                f"{ARM_LABELS.get(item.baseline, item.baseline)} | {item.budget} | {item.n} | "
                f"{percent(item.treatment_accuracy)} | {percent(item.baseline_accuracy)} | "
                f"{item.recovery_gain:+.1%} | "
                f"[{item.ci_low:+.1%}, {item.ci_high:+.1%}] | "
                f"{item.mcnemar.p_value:.4f} | {item.mcnemar.discordant} |"
            )

    lines += [
        "",
        "## Reading these numbers",
        "",
        "- Accuracy mixes string comparison with a judge. The deterministic column is the",
        "  one that rests on nothing but the benchmark's own answers.",
        "- Checkpoint coverage is judge-scored throughout.",
        "- Calls and tokens count the candidate only; the simulator and the judge are apparatus.",
        "- Direct and Multi-stage have no loop, so their stop reason is recorded as",
        '  `sufficient` by default. It means "never entered the loop", not "judged sufficient".',
        "- A gain that the McNemar column does not support is a difference between two",
        "  samples, not between two systems.",
        "",
    ]
    return "\n".join(lines)


__all__ = [
    "ARM_LABELS",
    "AskDecision",
    "ArmSummary",
    "Comparison",
    "FAILURE_KEYS",
    "ask_decision",
    "compare",
    "failure_counts",
    "render_markdown",
    "summarise",
]
