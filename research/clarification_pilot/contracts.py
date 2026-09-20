"""What the experiment passes around, and the line nothing crosses.

The one structural idea here is the split between ``CandidateView`` and
``HiddenContext``. A benchmark sample holds both, and the arms are handed only
the first. That is what makes the leakage boundary a property of the types
rather than a rule someone has to remember: an arm cannot read the gold answer
because it was never given the object that holds it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ── The leakage boundary ──────────────────────────────────────────────────────

Scoring = Literal["exact_match", "judge"]


@dataclass(frozen=True)
class CandidateView:
    """Everything the system under test is allowed to see.

    One underspecified prompt. No rubric, no original question, no gold answer,
    and no count of how many things are missing -- knowing there are three would
    itself be a hint worth several turns.
    """

    sample_id: str
    initial_input: str


@dataclass(frozen=True)
class HiddenContext:
    """What only the simulator and the evaluator may see.

    ``should_ask`` is derived, not annotated: AskMind leaves 53 of its 400 items
    undegraded, and for those the fully specified question and the one the
    candidate is shown are the same string. Nothing was removed, so asking is
    unnecessary -- which is a gold label for the ask decision that costs no
    annotation and no judge.
    """

    sample_id: str
    full_input: str
    required_points: tuple[str, ...]
    hidden_summary: str
    gold_answer: str
    should_ask: bool
    scoring: Scoring
    source_task: str


@dataclass(frozen=True)
class ClarificationBenchmarkSample:
    """One benchmark item, already split along the boundary."""

    candidate: CandidateView
    hidden: HiddenContext

    @property
    def sample_id(self) -> str:
        return self.candidate.sample_id


# ── The three decisions, kept apart ───────────────────────────────────────────


class InformationGap(BaseModel):
    """One thing the candidate believes it is missing."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(max_length=64)
    description: str = Field(max_length=2_000)
    priority: float | None = None


class SufficiencyDecision(BaseModel):
    """Decision one: is what I have enough to answer.

    The gaps travel with the decision because the same reading produces both,
    but choosing between them is a separate call -- so an ablation can replace
    the selector without touching the detector.
    """

    model_config = ConfigDict(extra="ignore")

    status: Literal["SUFFICIENT", "NEED_CLARIFICATION"]
    reason: str = Field(default="", max_length=2_000)
    gaps: list[InformationGap] = Field(default_factory=list, max_length=16)


class GapSelection(BaseModel):
    """Decisions two and three: which gap, and how to ask about it."""

    model_config = ConfigDict(extra="ignore")

    selected_gap_id: str = Field(max_length=64)
    question: str = Field(max_length=1_000)


class SimulatorReply(BaseModel):
    """What the simulated user says back.

    ``knew`` is the simulator's own report of whether the hidden context could
    answer what was asked. It drives the ``unknown_information`` stop condition
    and nothing else -- it is never shown to the candidate.
    """

    model_config = ConfigDict(extra="ignore")

    answer: str = Field(max_length=2_000)
    knew: bool = True


class JudgeVerdict(BaseModel):
    """The grader's reading of a free-form answer. Judge-based, and labelled so."""

    model_config = ConfigDict(extra="ignore")

    correct: bool
    reason: str = Field(default="", max_length=1_000)


# ── What a run records ────────────────────────────────────────────────────────

CallRole = Literal["candidate", "simulator", "judge"]

STOP_REASONS = (
    "sufficient",
    "budget_exhausted",
    "repeat_gap",
    "repeat_question",
    "unknown_information",
    "error",
)
StopReason = Literal[
    "sufficient",
    "budget_exhausted",
    "repeat_gap",
    "repeat_question",
    "unknown_information",
    "error",
]


class CallRecord(BaseModel):
    """One model call. ``role`` is what keeps simulator cost out of the candidate's bill."""

    model_config = ConfigDict(extra="forbid")

    stage: str
    role: CallRole
    prompt_version: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    # How many times an infrastructure failure was retried before this
    # call went through. Not a model outcome; kept so a run can be audited.
    retries: int = 0
    error: str | None = None
    # Only filled with --log-prompts. A simulator or judge record may hold
    # hidden context; a candidate record must never.
    prompt: str | None = None
    response: str | None = None


class TurnRecord(BaseModel):
    """One pass around the clarification loop."""

    model_config = ConfigDict(extra="forbid")

    index: int
    decision: SufficiencyDecision | None = None
    selected_gap_id: str | None = None
    question: str | None = None
    simulator_answer: str | None = None
    simulator_knew: bool | None = None


class ArmResult(BaseModel):
    """What one arm did to one sample."""

    model_config = ConfigDict(extra="forbid")

    sample_id: str
    arm: Literal["direct", "multi_stage", "gap_aware", "followup"]
    budget: int
    final_answer: str = ""
    asked: bool = False
    num_followups: int = 0
    stop_reason: StopReason = "sufficient"
    turns: list[TurnRecord] = Field(default_factory=list)
    calls: list[CallRecord] = Field(default_factory=list)
    error: str | None = None

    @property
    def candidate_calls(self) -> int:
        return sum(1 for call in self.calls if call.role == "candidate")


class ScoredResult(BaseModel):
    """One arm on one sample, graded. The unit of the paired analysis."""

    model_config = ConfigDict(extra="forbid")

    sample_id: str
    arm: str
    budget: int
    source_task: str
    correct: bool
    scored_by: Scoring
    judge_reason: str | None = None
    # Of the rubric items, how many the candidate's questions actually raised.
    checkpoint_coverage: float | None = None
    checkpoints_total: int = 0
    checkpoints_covered: int = 0
    gold_should_ask: bool = True
    # What the sufficiency stage decided, for the arms that have one. Separate
    # from ``asked`` because gap-aware decides and is not allowed to act.
    predicted_ask: bool | None = None
    asked: bool = False
    num_followups: int = 0
    stop_reason: str = "sufficient"
    candidate_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    error: str | None = None


class RunManifest(BaseModel):
    """Everything needed to say what produced a results file."""

    model_config = ConfigDict(extra="forbid")

    timestamp: str
    benchmark: str
    dataset_path: str
    dataset_sha256: str
    sample_ids: list[str]
    arms: list[str]
    budgets: list[int]
    candidate_model: str
    simulator_model: str
    judge_model: str
    temperature: float
    max_tokens: int
    seed: int | None
    prompt_versions: dict[str, str]
    dry_run: bool


class RunOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest: RunManifest
    results: list[ArmResult] = Field(default_factory=list)


__all__ = [
    "ArmResult",
    "CallRecord",
    "CallRole",
    "CandidateView",
    "ClarificationBenchmarkSample",
    "GapSelection",
    "HiddenContext",
    "InformationGap",
    "JudgeVerdict",
    "RunManifest",
    "RunOutput",
    "STOP_REASONS",
    "ScoredResult",
    "Scoring",
    "SimulatorReply",
    "StopReason",
    "SufficiencyDecision",
    "TurnRecord",
]
