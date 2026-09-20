"""Every prompt in the experiment, each with a version in its name.

Three groups, and they are kept apart on purpose:

* **candidate** -- what the system under test is shown. Never contains the
  rubric, the full question or the gold answer.
* **simulator** -- the stand-in for the user. Sees the hidden context, and is
  told to hand over only what was asked for.
* **judge** -- the grader. Sees the gold answer, and never speaks to the
  candidate.

Changing any wording means a new version string, because a results file is only
readable if the prompt that produced it can be named.
"""

from __future__ import annotations

from .contracts import CandidateView, HiddenContext, InformationGap

DIRECT_ANSWER_V1 = "direct_answer_v1"
UNDERSTANDING_V1 = "understanding_v1"
SUFFICIENCY_V1 = "sufficiency_v1"
GAP_SELECTION_V1 = "gap_selection_v1"
QUESTION_GENERATION_V1 = "question_generation_v1"
STATE_UPDATE_V1 = "state_update_v1"
FINAL_ANSWER_V1 = "final_answer_v2"
SIMULATOR_V1 = "simulator_v1"
JUDGE_V1 = "judge_v1"
COVERAGE_V1 = "coverage_v1"

PROMPT_VERSIONS = {
    "direct_answer": DIRECT_ANSWER_V1,
    "understanding": UNDERSTANDING_V1,
    "sufficiency": SUFFICIENCY_V1,
    "gap_selection": GAP_SELECTION_V1,
    "question_generation": QUESTION_GENERATION_V1,
    "state_update": STATE_UPDATE_V1,
    "final_answer": FINAL_ANSWER_V1,
    "simulator": SIMULATOR_V1,
    "judge": JUDGE_V1,
    "coverage": COVERAGE_V1,
}

FORMAT_RULE = (
    "If the task states an answer format, follow it exactly. "
    "End with the final answer and nothing after it."
)

# -- Candidate ---------------------------------------------------------------

DIRECT_ANSWER_SYSTEM = f"""
You are answering a task. Give the answer.

{FORMAT_RULE}
""".strip()

UNDERSTANDING_SYSTEM = """
Read the task and write down what it actually specifies, as plain prose notes.

Cover what is being asked, the quantities, entities and conditions that are
stated, and anything the task refers to without pinning down. Write only what
the task says. Do not answer it, do not guess at values it leaves open, and do
not invent detail to fill a hole.
""".strip()

SUFFICIENCY_SYSTEM = """
Decide whether the task as stated contains enough information to answer it
correctly, and return JSON only.

{
  "status": "SUFFICIENT" or "NEED_CLARIFICATION",
  "reason": "one sentence",
  "gaps": [{"id": "gap_1", "description": "what is missing", "priority": 0.9}]
}

Rules:
- SUFFICIENT means you could answer now and be right. Return an empty gaps list.
- NEED_CLARIFICATION means some fact you need is absent, vague, or ambiguous,
  and not knowing it could change the answer.
- A task can be hard and still be sufficient. Difficulty is not a gap.
- Do not invent a gap to appear careful. An unnecessary question costs the user.
- Each gap must name one missing fact, not a topic.
- priority is a number from 0 to 1: how much the answer depends on that fact.
- Return at most 6 gaps, highest priority first.
""".strip()

GAP_SELECTION_SYSTEM = """
You may ask the user exactly one question now. Choose which gap to close and
write the question. Return JSON only.

{"selected_gap_id": "gap_1", "question": "..."}

Rules:
- Choose the gap whose answer would most change your final answer.
- Do not choose a gap that an earlier question already covered.
- One question, one fact, answerable in a sentence.
- Ask the user for the missing information. Do not ask them to solve the task.
""".strip()

QUESTION_GENERATION_SYSTEM = """
Write the single question that would close the supplied gap. Return JSON only.

{"question": "..."}

One question, one fact, answerable in a sentence. Ask for the missing
information, not for the solution.
""".strip()

STATE_UPDATE_SYSTEM = """
Update the notes with what the user just told you. Return the updated notes as
plain prose.

Fold the answer into what was already written. Keep everything still true, drop
nothing that is still relevant, and record the new fact where it belongs. If the
user did not know, record that the fact is unavailable rather than guessing it.
Do not answer the task.
""".strip()

FINAL_ANSWER_SYSTEM = f"""
Answer the task, using your notes and anything the user told you.

If something you needed was never supplied, make the most reasonable assumption
and answer anyway. An answer is required.

Anything listed as still missing was established to be missing and could not be
obtained. Let it decide which assumption you make. It is not a reason to
withhold an answer.

{FORMAT_RULE}
""".strip()


def direct_answer_messages(view: CandidateView) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": DIRECT_ANSWER_SYSTEM},
        {"role": "user", "content": view.initial_input},
    ]


def understanding_messages(view: CandidateView) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": UNDERSTANDING_SYSTEM},
        {"role": "user", "content": f"TASK\n----\n{view.initial_input}"},
    ]


def sufficiency_messages(view: CandidateView, state: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SUFFICIENCY_SYSTEM},
        {
            "role": "user",
            "content": f"TASK\n----\n{view.initial_input}\n\nNOTES\n-----\n{state}",
        },
    ]


def gap_selection_messages(
    view: CandidateView,
    state: str,
    gaps: list[InformationGap],
    asked_before: list[str],
) -> list[dict[str, str]]:
    listing = "\n".join(
        f"- {gap.id} (priority {gap.priority if gap.priority is not None else 'unset'}): "
        f"{gap.description}"
        for gap in gaps
    )
    already = ""
    if asked_before:
        asked = "\n".join(f"- {question}" for question in asked_before)
        already = f"\n\nQUESTIONS ALREADY ASKED\n-----------------------\n{asked}"
    return [
        {"role": "system", "content": GAP_SELECTION_SYSTEM},
        {
            "role": "user",
            "content": (
                f"TASK\n----\n{view.initial_input}\n\nNOTES\n-----\n{state}\n\n"
                f"GAPS\n----\n{listing}{already}"
            ),
        },
    ]


def question_generation_messages(
    view: CandidateView, state: str, gap: InformationGap
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": QUESTION_GENERATION_SYSTEM},
        {
            "role": "user",
            "content": (
                f"TASK\n----\n{view.initial_input}\n\nNOTES\n-----\n{state}\n\n"
                f"GAP\n---\n{gap.id}: {gap.description}"
            ),
        },
    ]


def state_update_messages(state: str, question: str, answer: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": STATE_UPDATE_SYSTEM},
        {
            "role": "user",
            "content": (
                f"NOTES\n-----\n{state}\n\nYOU ASKED\n---------\n{question}\n\n"
                f"THE USER REPLIED\n----------------\n{answer}"
            ),
        },
    ]


def final_answer_messages(
    view: CandidateView,
    state: str,
    exchanges: list[tuple[str, str]],
    outstanding: list[InformationGap] | None = None,
) -> list[dict[str, str]]:
    """The answering call, and everything the run established before it.

    ``outstanding`` is what the sufficiency stage still called missing when the
    loop stopped. Without it the gap-aware arm is character for character the
    multi-stage arm: it would reason about what it lacks and then answer from a
    prompt that never mentions it, so the arm could only measure sampling noise.
    """

    transcript = ""
    if exchanges:
        lines = "\n".join(f"Q: {question}\nA: {answer}" for question, answer in exchanges)
        transcript = (
            "\n\nWHAT YOU ASKED AND WHAT YOU WERE TOLD\n"
            "-------------------------------------\n" + lines
        )
    missing = ""
    if outstanding:
        listing = "\n".join(f"- {gap.description}" for gap in outstanding)
        missing = "\n\nWHAT IS STILL MISSING\n---------------------\n" + listing
    return [
        {"role": "system", "content": FINAL_ANSWER_SYSTEM},
        {
            "role": "user",
            "content": (
                f"TASK\n----\n{view.initial_input}\n\n"
                f"NOTES\n-----\n{state}{transcript}{missing}"
            ),
        },
    ]


# -- Simulator: the only place hidden context may reach the candidate, and
#    then only through what it chooses to say -------------------------------

SIMULATOR_SYSTEM = """
You are the user who asked the question. An assistant is asking you for
clarification. Answer from the reference material below and from nothing else.
Return JSON only.

{"answer": "what you tell the assistant", "knew": true}

Rules:
- Answer only what was asked. Do not volunteer anything else, however helpful
  it would be, and never hand over the whole reference.
- Copy values from the reference exactly. Do not round, rephrase or infer them.
- If the reference does not settle what was asked, set knew to false and say you
  do not know. Never invent a fact to be helpful.
- Do not solve the task, and do not reveal the answer to it.
- Two or three sentences at most, in the voice of the person who asked.
""".strip()


def simulator_messages(hidden: HiddenContext, question: str) -> list[dict[str, str]]:
    points = "\n".join(f"- {point}" for point in hidden.required_points)
    return [
        {"role": "system", "content": SIMULATOR_SYSTEM},
        {
            "role": "user",
            "content": (
                "REFERENCE: THE FULLY SPECIFIED TASK\n"
                "-----------------------------------\n"
                f"{hidden.full_input}\n\n"
                "WHAT WAS LEFT OUT OF THE VERSION THE ASSISTANT SAW\n"
                "--------------------------------------------------\n"
                f"{hidden.hidden_summary}\n\n"
                "POINTS THE ASSISTANT MAY NEED\n"
                "-----------------------------\n"
                f"{points}\n\n"
                "THE ASSISTANT ASKS\n"
                "------------------\n"
                f"{question}"
            ),
        },
    ]


# -- Judge: grading only, never in the candidate's context --------------------

JUDGE_SYSTEM = """
Decide whether a candidate's final answer matches the reference answer. Return
JSON only.

{"correct": true, "reason": "one sentence"}

Judge the substance, not the wording. Equivalent formulations, equivalent
algebra and equivalent units are correct. A different value, a different
conclusion, or an answer that hedges without committing is not.
""".strip()


def judge_messages(question: str, gold: str, answer: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": JUDGE_SYSTEM},
        {
            "role": "user",
            "content": (
                f"QUESTION\n--------\n{question}\n\n"
                f"REFERENCE ANSWER\n----------------\n{gold}\n\n"
                f"CANDIDATE ANSWER\n----------------\n{answer}"
            ),
        },
    ]


COVERAGE_SYSTEM = """
Decide which of the listed points the assistant's questions actually asked
about. Return JSON only.

{"covered": [0, 2]}

Use the index of each point, starting at 0. A point counts as covered only if
one of the questions asks for that specific fact. Asking around the subject does
not count. Return an empty list if none were covered.
""".strip()


def coverage_messages(points: tuple[str, ...], questions: list[str]) -> list[dict[str, str]]:
    listing = "\n".join(f"{index}. {point}" for index, point in enumerate(points))
    asked = "\n".join(f"- {question}" for question in questions)
    if not asked:
        asked = "(the assistant asked nothing)"
    return [
        {"role": "system", "content": COVERAGE_SYSTEM},
        {
            "role": "user",
            "content": f"POINTS\n------\n{listing}\n\nQUESTIONS ASKED\n---------------\n{asked}",
        },
    ]


__all__ = [
    "COVERAGE_SYSTEM",
    "COVERAGE_V1",
    "DIRECT_ANSWER_SYSTEM",
    "DIRECT_ANSWER_V1",
    "FINAL_ANSWER_SYSTEM",
    "FINAL_ANSWER_V1",
    "GAP_SELECTION_SYSTEM",
    "GAP_SELECTION_V1",
    "JUDGE_SYSTEM",
    "JUDGE_V1",
    "PROMPT_VERSIONS",
    "QUESTION_GENERATION_SYSTEM",
    "QUESTION_GENERATION_V1",
    "SIMULATOR_SYSTEM",
    "SIMULATOR_V1",
    "STATE_UPDATE_SYSTEM",
    "STATE_UPDATE_V1",
    "SUFFICIENCY_SYSTEM",
    "SUFFICIENCY_V1",
    "UNDERSTANDING_SYSTEM",
    "UNDERSTANDING_V1",
    "coverage_messages",
    "direct_answer_messages",
    "final_answer_messages",
    "gap_selection_messages",
    "judge_messages",
    "question_generation_messages",
    "simulator_messages",
    "state_update_messages",
    "sufficiency_messages",
    "understanding_messages",
]
