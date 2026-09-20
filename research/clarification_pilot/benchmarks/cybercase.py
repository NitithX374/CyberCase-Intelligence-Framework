"""The domain case study: the same four arms over CyberCase incident material.

Not a second statistically powered benchmark. Thirty-three items over seven base
scenarios is a demonstration that the architecture runs on cyber-case input and
a place to read failures that AskMind's maths and medicine cannot show -- not a
basis for a significance claim, and the report says so.

It reuses ``research/attribute_first_pilot/benchmark.json``, which already
exists in this repository and already carries what the harness needs:

* ``gold_attributes.answerability`` is the ask label. SUFFICIENT means answer
  now; INSUFFICIENT means something was removed. CONFLICTING is mapped to
  should-ask as well, because a conflict between two sources is a gap the
  production pipeline is built to raise -- a judgement call, recorded here
  rather than buried.
* ``gold_attributes.missing_information`` is the checkpoint list.
* The perturbed conditions are paired with an ORIGINAL by ``base_case_id``, so
  the unperturbed case is what the simulator answers from. Nothing had to be
  written to give the simulator a reference.

Expectations in this set are prose ("abstain from confirming exfiltration"), so
every item is judge-scored. There is no deterministic subset here, which is the
main reason it stays a case study.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..contracts import CandidateView, ClarificationBenchmarkSample, HiddenContext

RESEARCH_DIR = Path(__file__).resolve().parents[2]
DEFAULT_PATH = RESEARCH_DIR / "attribute_first_pilot" / "benchmark.json"

# Which answerability values mean the system should have asked.
SHOULD_ASK = {"INSUFFICIENT", "CONFLICTING"}


def formatted(item: dict) -> str:
    sentences = "\n".join(f"[{entry['id']}] {entry['text']}" for entry in item["context_sentences"])
    return f"CASE SOURCES\n------------\n{sentences}\n\nQUESTION\n--------\n{item['question']}"


class CyberCaseAdapter:
    name = "cybercase"
    default_path = DEFAULT_PATH

    def load(self, path: Path | None = None) -> list[ClarificationBenchmarkSample]:
        source = Path(path) if path is not None else self.default_path
        if not source.exists():
            raise FileNotFoundError(f"CyberCase pilot benchmark not found at {source}")
        items = json.loads(source.read_text(encoding="utf-8"))["items"]

        originals = {
            item["base_case_id"]: item for item in items if item["condition"] == "ORIGINAL"
        }
        return [sample_from_item(item, originals.get(item["base_case_id"])) for item in items]


def sample_from_item(item: dict, original: dict | None) -> ClarificationBenchmarkSample:
    attributes = item["gold_attributes"]
    notes = item["evaluation_notes"]
    missing = tuple(attributes.get("missing_information") or ())

    # The unperturbed case is the simulator's reference. An ORIGINAL item is its
    # own reference, which is right: there is nothing missing from it to reveal.
    reference = formatted(original) if original is not None else formatted(item)

    return ClarificationBenchmarkSample(
        candidate=CandidateView(
            sample_id=item["id"],
            initial_input=formatted(item),
        ),
        hidden=HiddenContext(
            sample_id=item["id"],
            full_input=reference,
            required_points=missing,
            hidden_summary=(
                f"Condition {item['condition']}. "
                f"Answerability {attributes['answerability']}. "
                + (f"Missing: {'; '.join(missing)}." if missing else "Nothing was removed.")
            ),
            gold_answer=notes["expected_behavior"],
            should_ask=attributes["answerability"] in SHOULD_ASK,
            # Expectations are written as behaviour, not as a value to match.
            scoring="judge",
            source_task=f"cybercase_{item['condition'].lower()}",
        ),
    )


__all__ = ["CyberCaseAdapter", "DEFAULT_PATH", "SHOULD_ASK", "formatted", "sample_from_item"]
