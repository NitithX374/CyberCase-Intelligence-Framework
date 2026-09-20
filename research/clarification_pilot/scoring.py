"""Grading an answer, deterministically where the benchmark allows it.

Three of AskMind's four sources have answers that are a letter, a token, or a
short LaTeX expression, and those are compared as strings. GPQA's answers are
prose and cannot be. Every graded result therefore carries ``scored_by``, so a
table can report the deterministic subset on its own and a reader can see how
much of a number rests on a model's opinion.

Strict string comparison understates every arm's accuracy by the same amount,
which a paired design tolerates. ``judge_fallback`` relaxes it for answers that
miss, and marks each one it touches.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

from .contracts import (
    ArmResult,
    CallRecord,
    HiddenContext,
    JudgeVerdict,
    ScoredResult,
)
from .prompts import COVERAGE_V1, JUDGE_V1, coverage_messages, judge_messages
from .provider import Provider

BOXED = re.compile(r"\\?boxed\s*\{")
ANSWER_IS = re.compile(r"answer\s+is\s*:?\s*\(?\s*([A-Za-z0-9]+)\s*\)?", re.IGNORECASE)
LATEX_NOISE = re.compile(r"\\(?:left|right|!|,|;|:|\s)")


def balanced_brace_content(text: str, open_index: int) -> str | None:
    """What is inside a brace that may hold more braces."""

    depth = 0
    for position in range(open_index, len(text)):
        if text[position] == "{":
            depth += 1
        elif text[position] == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : position]
    return None


def extract_boxed(text: str) -> str | None:
    """The last boxed expression, which is the one a model settles on."""

    last = None
    for match in BOXED.finditer(text):
        content = balanced_brace_content(text, match.end() - 1)
        if content is not None:
            last = content
    return last


def normalise_plain(value: str) -> str:
    cleaned = value.strip().strip("$").strip()
    cleaned = cleaned.rstrip(".").strip()
    cleaned = cleaned.strip("()").strip()
    return " ".join(cleaned.split()).casefold()


def normalise_latex(value: str) -> str:
    cleaned = value.strip().strip("$").strip()
    cleaned = LATEX_NOISE.sub("", cleaned)
    cleaned = cleaned.replace("dfrac", "frac").replace("tfrac", "frac")
    cleaned = cleaned.replace(" ", "").rstrip(".")
    cleaned = cleaned.replace("^{\\circ}", "").replace("^\\circ", "")
    return cleaned.casefold()


def candidate_answer(text: str) -> str:
    """The part of a free-text response that is meant to be the answer.

    Tried in the order the benchmark's own formats suggest: a boxed expression,
    then an "answer is X" sentence, then the last non-empty line.
    """

    boxed = extract_boxed(text)
    if boxed is not None:
        return boxed
    stated = ANSWER_IS.search(text)
    if stated is not None:
        return stated.group(1)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def exact_match(answer: str, gold: str) -> bool:
    """Whether the answer says what the reference says, allowing for formatting."""

    if not answer.strip():
        return False

    gold_boxed = extract_boxed(gold)
    gold_value = gold_boxed if gold_boxed is not None else gold
    gold_stated = ANSWER_IS.search(gold)
    if gold_stated is not None:
        gold_value = gold_stated.group(1)

    extracted = candidate_answer(answer)

    if normalise_plain(extracted) == normalise_plain(gold_value):
        return True
    if normalise_latex(extracted) == normalise_latex(gold_value):
        return True
    # A short reference token that the response ends on, e.g. BBH's "(E)".
    tail = normalise_plain(answer.splitlines()[-1] if answer.splitlines() else "")
    return bool(tail) and tail == normalise_plain(gold_value)


async def judge_answer(
    provider: Provider,
    *,
    question: str,
    gold: str,
    answer: str,
    sink: list[CallRecord],
) -> JudgeVerdict:
    verdict = await provider.structured(
        messages=judge_messages(question, gold, answer),
        schema=JudgeVerdict,
        stage="judge",
        role="judge",
        prompt_version=JUDGE_V1,
        sink=sink,
    )
    return verdict if verdict is not None else JudgeVerdict(correct=False, reason="judge failed")


class CoverageReply(BaseModel):
    """Which rubric points the judge found among the questions asked."""

    model_config = ConfigDict(extra="ignore")

    covered: list[int] = Field(default_factory=list, max_length=64)


async def checkpoint_coverage(
    provider: Provider,
    *,
    hidden: HiddenContext,
    questions: list[str],
    sink: list[CallRecord],
) -> tuple[int, int]:
    """How many rubric points the candidate's questions actually raised.

    Judge-based, because a rubric point and the question that asks for it are
    almost never the same words. Returns (covered, total).
    """

    total = len(hidden.required_points)
    if total == 0 or not questions:
        return 0, total

    reply = await provider.structured(
        messages=coverage_messages(hidden.required_points, questions),
        schema=CoverageReply,
        stage="coverage",
        role="judge",
        prompt_version=COVERAGE_V1,
        sink=sink,
    )
    if reply is None:
        return 0, total
    valid = {index for index in reply.covered if 0 <= index < total}
    return len(valid), total


async def score_result(
    result: ArmResult,
    hidden: HiddenContext,
    provider: Provider,
    *,
    judge_fallback: bool = False,
    measure_coverage: bool = True,
) -> ScoredResult:
    """One arm's run on one sample, graded. Judge calls are billed to the judge."""

    judge_calls: list[CallRecord] = []
    scored_by = hidden.scoring
    reason = None

    if hidden.scoring == "exact_match":
        correct = exact_match(result.final_answer, hidden.gold_answer)
        if not correct and judge_fallback:
            verdict = await judge_answer(
                provider,
                question=hidden.full_input,
                gold=hidden.gold_answer,
                answer=result.final_answer,
                sink=judge_calls,
            )
            correct, reason, scored_by = verdict.correct, verdict.reason, "judge"
    else:
        verdict = await judge_answer(
            provider,
            question=hidden.full_input,
            gold=hidden.gold_answer,
            answer=result.final_answer,
            sink=judge_calls,
        )
        correct, reason = verdict.correct, verdict.reason

    covered = total = 0
    coverage = None
    questions = [turn.question for turn in result.turns if turn.question]
    if measure_coverage:
        covered, total = await checkpoint_coverage(
            provider, hidden=hidden, questions=questions, sink=judge_calls
        )
        coverage = covered / total if total else None

    candidate = [call for call in result.calls if call.role == "candidate"]
    opening = result.turns[0].decision if result.turns else None
    predicted_ask = None if opening is None else opening.status == "NEED_CLARIFICATION"
    return ScoredResult(
        sample_id=result.sample_id,
        arm=result.arm,
        budget=result.budget,
        source_task=hidden.source_task,
        correct=correct,
        scored_by=scored_by,
        judge_reason=reason,
        checkpoint_coverage=coverage,
        checkpoints_total=total,
        checkpoints_covered=covered,
        gold_should_ask=hidden.should_ask,
        predicted_ask=predicted_ask,
        asked=result.asked,
        num_followups=result.num_followups,
        stop_reason=result.stop_reason,
        candidate_calls=len(candidate),
        input_tokens=sum(call.input_tokens for call in candidate),
        output_tokens=sum(call.output_tokens for call in candidate),
        latency_ms=round(sum(call.latency_ms for call in candidate), 2),
        error=result.error,
    )


__all__ = [
    "CoverageReply",
    "balanced_brace_content",
    "candidate_answer",
    "checkpoint_coverage",
    "exact_match",
    "extract_boxed",
    "judge_answer",
    "normalise_latex",
    "normalise_plain",
    "score_result",
]
