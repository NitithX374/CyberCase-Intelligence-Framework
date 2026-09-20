"""AskMind, the intent-deficient half of AskBench.

Fields are the ones the published file actually carries, read from
`jialeuuz/askbench_bench` (MIT) and checked against all 400 rows rather than
taken from the paper:

    id  ori_question  degraded_question  degraded_info  required_points
    expected_answer  source_task        [solution] [category] [err_info]

Three of those are optional and appear in different combinations, so every
field but the five the harness needs is read defensively.

Two readings of the data that the harness depends on:

* **The ask label is free.** 53 of the 400 rows were never degraded -- the
  question shown to the candidate is character for character the full one, and
  ``degraded_info`` says as much. Nothing is missing, so asking is unnecessary.
  ``required_points`` is populated on those rows anyway, which is why the label
  is drawn from the two questions rather than from the rubric.

* **Only GPQA needs a judge.** MedQA answers are always "The answer is X.",
  BBH answers are single tokens, and Math500 answers are short LaTeX. GPQA
  answers are prose. Three quarters of the set therefore scores by string
  comparison, and the quarter that cannot is marked so it can be reported apart.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..contracts import CandidateView, ClarificationBenchmarkSample, HiddenContext

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_PATH = DATA_DIR / "ask_mind.jsonl"

# The one subset whose answers are prose rather than a token or a formula.
JUDGE_TASKS = {"ask_mind_gpqade"}

REQUIRED_FIELDS = ("id", "ori_question", "degraded_question", "expected_answer", "source_task")


class AskMindAdapter:
    name = "askmind"
    default_path = DEFAULT_PATH

    def load(self, path: Path | None = None) -> list[ClarificationBenchmarkSample]:
        source = Path(path) if path is not None else self.default_path
        if not source.exists():
            raise FileNotFoundError(
                f"AskMind data not found at {source}. Download ask_bench_data/ask_mind.jsonl "
                "from https://huggingface.co/datasets/jialeuuz/askbench_bench"
            )
        rows = [
            json.loads(line)
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return [sample_from_row(row) for row in rows]


def sample_from_row(row: dict) -> ClarificationBenchmarkSample:
    missing = [name for name in REQUIRED_FIELDS if not row.get(name)]
    if missing:
        raise ValueError(f"AskMind row is missing {missing}; schema changed")

    degraded = str(row["degraded_question"])
    original = str(row["ori_question"])
    source_task = str(row["source_task"])
    points = row.get("required_points") or []

    return ClarificationBenchmarkSample(
        candidate=CandidateView(
            sample_id=str(row["id"]),
            initial_input=degraded,
        ),
        hidden=HiddenContext(
            sample_id=str(row["id"]),
            full_input=original,
            required_points=tuple(str(point) for point in points),
            hidden_summary=str(row.get("degraded_info") or ""),
            gold_answer=str(row["expected_answer"]),
            # Nothing was removed, so there is nothing worth asking about.
            should_ask=degraded.strip() != original.strip(),
            scoring="judge" if source_task in JUDGE_TASKS else "exact_match",
            source_task=source_task,
        ),
    )


__all__ = ["AskMindAdapter", "DEFAULT_PATH", "JUDGE_TASKS", "sample_from_row"]
