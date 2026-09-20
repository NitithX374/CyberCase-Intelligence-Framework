"""The four systems under comparison, each one step apart from the last.

    direct       task -> answer
    multi_stage  task -> notes -> answer
    gap_aware    task -> notes -> sufficiency -> answer          (may not ask)
    followup     task -> notes -> sufficiency -> ask -> ... -> answer

The last two run the same function. Gap-aware is bounded follow-up with a
budget of zero and a simulator that refuses to be asked, so the difference
between them is one number rather than a second implementation that can drift.
That is what makes "does explicit gap reasoning alone help" a question the data
can answer.

Every arm ends in an answer, including the ones that stopped early. An arm that
declined to answer would score zero for a reason that has nothing to do with
clarification.
"""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    ArmResult,
    CallRecord,
    CandidateView,
    GapSelection,
    InformationGap,
    StopReason,
    SufficiencyDecision,
    TurnRecord,
)
from .prompts import (
    DIRECT_ANSWER_V1,
    FINAL_ANSWER_V1,
    GAP_SELECTION_V1,
    QUESTION_GENERATION_V1,
    STATE_UPDATE_V1,
    SUFFICIENCY_V1,
    UNDERSTANDING_V1,
    direct_answer_messages,
    final_answer_messages,
    gap_selection_messages,
    question_generation_messages,
    state_update_messages,
    sufficiency_messages,
    understanding_messages,
)
from .provider import Provider


@dataclass(frozen=True)
class ArmConfig:
    """What bounds a run. Nothing here is decided by a model."""

    budget: int = 3
    # How many times running the simulator may say it does not know before the
    # loop gives up. One unknown is ordinary; two in a row means the remaining
    # gaps are not answerable and further turns only cost.
    unknown_tolerance: int = 2
    # Split gap selection from question writing into two calls, for the ablation
    # that isolates question generation.
    separate_question_call: bool = False


def normalised(question: str) -> str:
    return " ".join(question.lower().split())


async def run_direct(
    view: CandidateView, provider: Provider, simulator, config: ArmConfig
) -> ArmResult:
    """Answer the task as stated. No state, no gaps, no questions."""

    calls: list[CallRecord] = []
    answer = await provider.call(
        messages=direct_answer_messages(view),
        stage="direct_answer",
        role="candidate",
        prompt_version=DIRECT_ANSWER_V1,
        sink=calls,
    )
    return ArmResult(
        sample_id=view.sample_id,
        arm="direct",
        budget=0,
        final_answer=answer.strip(),
        stop_reason="sufficient",
        calls=calls,
        error=first_error(calls),
    )


async def run_multi_stage(
    view: CandidateView, provider: Provider, simulator, config: ArmConfig
) -> ArmResult:
    """Write the task down as structured notes, then answer from them.

    The control that separates "a second call helped" from "reasoning about
    what is missing helped". Without it, every gain in the later arms could be
    the extra pass.
    """

    calls: list[CallRecord] = []
    state = await understanding(view, provider, calls)
    answer = await final_answer(view, provider, state, [], calls)
    return ArmResult(
        sample_id=view.sample_id,
        arm="multi_stage",
        budget=0,
        final_answer=answer,
        stop_reason="sufficient",
        calls=calls,
        error=first_error(calls),
    )


async def run_clarifying(
    view: CandidateView,
    provider: Provider,
    simulator,
    config: ArmConfig,
    *,
    arm: str,
) -> ArmResult:
    """Notes, then a bounded loop of sufficiency and one question at a time.

    With ``config.budget == 0`` the loop judges sufficiency once, asks nothing,
    and answers -- which is the gap-aware arm.
    """

    calls: list[CallRecord] = []
    turns: list[TurnRecord] = []
    exchanges: list[tuple[str, str]] = []
    asked_gap_ids: list[str] = []
    asked_questions: list[str] = []
    consecutive_unknown = 0
    stop: StopReason = "budget_exhausted"

    state = await understanding(view, provider, calls)

    for index in range(config.budget + 1):
        decision = await provider.structured(
            messages=sufficiency_messages(view, state),
            schema=SufficiencyDecision,
            stage="sufficiency",
            role="candidate",
            prompt_version=SUFFICIENCY_V1,
            sink=calls,
        )
        if decision is None:
            turns.append(TurnRecord(index=index))
            stop = "error"
            break

        turn = TurnRecord(index=index, decision=decision)
        turns.append(turn)

        if decision.status == "SUFFICIENT" or not decision.gaps:
            stop = "sufficient"
            break
        if index >= config.budget:
            stop = "budget_exhausted"
            break

        selection = await select_gap(
            view, provider, state, decision.gaps, asked_questions, config, calls
        )
        if selection is None:
            stop = "error"
            break

        if selection.selected_gap_id in asked_gap_ids:
            stop = "repeat_gap"
            break
        if normalised(selection.question) in asked_questions:
            stop = "repeat_question"
            break

        turn.selected_gap_id = selection.selected_gap_id
        turn.question = selection.question
        asked_gap_ids.append(selection.selected_gap_id)
        asked_questions.append(normalised(selection.question))

        reply = await simulator.answer(selection.question, calls)
        turn.simulator_answer = reply.answer
        turn.simulator_knew = reply.knew
        exchanges.append((selection.question, reply.answer))

        consecutive_unknown = 0 if reply.knew else consecutive_unknown + 1

        state = (
            await provider.call(
                messages=state_update_messages(state, selection.question, reply.answer),
                stage="state_update",
                role="candidate",
                prompt_version=STATE_UPDATE_V1,
                sink=calls,
            )
            or state
        )

        if consecutive_unknown >= config.unknown_tolerance:
            stop = "unknown_information"
            break

    answer = await final_answer(view, provider, state, exchanges, calls, unresolved(turns))
    return ArmResult(
        sample_id=view.sample_id,
        arm=arm,
        budget=config.budget,
        final_answer=answer,
        asked=bool(exchanges),
        num_followups=len(exchanges),
        stop_reason=stop,
        turns=turns,
        calls=calls,
        error=first_error(calls),
    )


async def run_gap_aware(
    view: CandidateView, provider: Provider, simulator, config: ArmConfig
) -> ArmResult:
    """Sufficiency reasoning with nothing to do about it: budget zero."""

    return await run_clarifying(
        view,
        provider,
        simulator,
        ArmConfig(budget=0, unknown_tolerance=config.unknown_tolerance),
        arm="gap_aware",
    )


async def run_followup(
    view: CandidateView, provider: Provider, simulator, config: ArmConfig
) -> ArmResult:
    return await run_clarifying(view, provider, simulator, config, arm="followup")


# -- the pieces the arms share -----------------------------------------------


def unresolved(turns: list[TurnRecord]) -> list[InformationGap]:
    """What the last sufficiency decision still called missing.

    This is what separates the gap-aware arm from the multi-stage one. Both
    write notes and then answer from them; only this arm is told what its own
    sufficiency stage concluded was absent. Without it that stage spends a call
    whose output never reaches the answer, and the arm cannot differ from
    multi-stage by anything but sampling noise.

    Empty when the decision was SUFFICIENT: a stage that judged nothing
    material to be missing has no limitation to report.
    """

    decision = next(
        (turn.decision for turn in reversed(turns) if turn.decision is not None), None
    )
    if decision is None or decision.status == "SUFFICIENT":
        return []
    return list(decision.gaps)


async def understanding(view: CandidateView, provider: Provider, calls: list[CallRecord]) -> str:
    text = await provider.call(
        messages=understanding_messages(view),
        stage="understanding",
        role="candidate",
        prompt_version=UNDERSTANDING_V1,
        sink=calls,
    )
    return text.strip()


async def select_gap(
    view: CandidateView,
    provider: Provider,
    state: str,
    gaps: list[InformationGap],
    asked_questions: list[str],
    config: ArmConfig,
    calls: list[CallRecord],
) -> GapSelection | None:
    """Decision two, and decision three either with it or after it."""

    if not config.separate_question_call:
        return await provider.structured(
            messages=gap_selection_messages(view, state, gaps, asked_questions),
            schema=GapSelection,
            stage="gap_selection",
            role="candidate",
            prompt_version=GAP_SELECTION_V1,
            sink=calls,
        )

    chosen = await provider.structured(
        messages=gap_selection_messages(view, state, gaps, asked_questions),
        schema=GapSelection,
        stage="gap_selection",
        role="candidate",
        prompt_version=GAP_SELECTION_V1,
        sink=calls,
    )
    if chosen is None:
        return None
    gap = next((item for item in gaps if item.id == chosen.selected_gap_id), gaps[0])
    written = await provider.structured(
        messages=question_generation_messages(view, state, gap),
        schema=GapSelection,
        stage="question_generation",
        role="candidate",
        prompt_version=QUESTION_GENERATION_V1,
        sink=calls,
    )
    if written is None:
        return None
    return GapSelection(selected_gap_id=gap.id, question=written.question)


async def final_answer(
    view: CandidateView,
    provider: Provider,
    state: str,
    exchanges: list[tuple[str, str]],
    calls: list[CallRecord],
    outstanding: list[InformationGap] | None = None,
) -> str:
    text = await provider.call(
        messages=final_answer_messages(view, state, exchanges, outstanding),
        stage="final_answer",
        role="candidate",
        prompt_version=FINAL_ANSWER_V1,
        sink=calls,
    )
    return text.strip()


def first_error(calls: list[CallRecord]) -> str | None:
    return next((call.error for call in calls if call.error), None)


ARMS = {
    "direct": run_direct,
    "multi_stage": run_multi_stage,
    "gap_aware": run_gap_aware,
    "followup": run_followup,
}

INTERACTIVE_ARMS = {"followup"}


__all__ = [
    "ARMS",
    "INTERACTIVE_ARMS",
    "ArmConfig",
    "final_answer",
    "first_error",
    "normalised",
    "run_clarifying",
    "run_direct",
    "run_followup",
    "run_gap_aware",
    "run_multi_stage",
    "select_gap",
    "understanding",
    "unresolved",
]
