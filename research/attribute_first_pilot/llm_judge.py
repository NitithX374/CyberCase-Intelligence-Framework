"""LLM Judge for scoring B0, A1, and A2 downstream answers.

Evaluates each answer independently against the benchmark evaluation notes:
- correctness (0, 1, 2)
- context_grounding (0, 1, 2)
- uncertainty_handling (0, 1, 2)
- rationales
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import time
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .contracts import (
    BenchmarkSuite,
    ItemRunResult,
    PilotRunOutput,
)
from .provider import clean_json_text, get_api_key

DEFAULT_JUDGE_MODEL = "openai/gpt-4o-mini"
SCRIPT_DIR = Path(__file__).resolve().parent


class JudgeScore(BaseModel):
    correctness: int = Field(..., ge=0, le=2, description="0=incorrect, 1=partially correct, 2=correct")
    context_grounding: int = Field(..., ge=0, le=2, description="0=materially ungrounded, 1=minor issue, 2=fully grounded")
    uncertainty_handling: int = Field(..., ge=0, le=2, description="0=ignores uncertainty/conflict, 1=partial, 2=correctly preserves state")
    rationale: str = Field(..., description="Brief explanation of scoring")


JUDGE_SYSTEM_PROMPT = """You are an expert cybersecurity benchmark judge evaluating analytical question-answering.

You will be given:
1. Case Context (numbered sentences [S1], [S2]...)
2. Analytical Question
3. Ground Truth Evaluation Criteria:
   - Expected Behavior
   - Required Key Points
   - Forbidden Points / Hallucinations
4. Candidate Answer to Evaluate

Score the candidate answer strictly and impartially along 3 dimensions:

1. correctness:
   0 = Incorrect conclusion, unsupported claim, or fails to address core analytical question.
   1 = Partially correct, incomplete, or ambiguous conclusion.
   2 = Completely correct analytical conclusion aligned with expected behavior.

2. context_grounding:
   0 = Materially introduces external facts, unobserved attack phases, or hallucinated details not in context.
   1 = Mostly grounded with minor extrapolations or speculative wording.
   2 = Fully grounded strictly in supplied context facts without introducing uncontained claims.

3. uncertainty_handling:
   0 = Materially overstates confidence, ignores missing evidence, or picks one side in a material conflict.
   1 = Partially acknowledges limitations but with slight overconfidence or weak nuance.
   2 = Correctly preserves evidentiary state (explicitly abstaining on unestablished claims, preserving conflicts, or confirming supported claims).

Return JSON only in this exact format:
{
  "correctness": 0 | 1 | 2,
  "context_grounding": 0 | 1 | 2,
  "uncertainty_handling": 0 | 1 | 2,
  "rationale": "short explanation"
}"""


JUDGE_USER_TEMPLATE = """Case Context:
{context}

Analytical Question:
{question}

Evaluation Criteria:
- Expected Behavior: {expected_behavior}
- Required Points: {required_points}
- Forbidden Points: {forbidden_points}

Candidate Answer:
{candidate_answer}"""


async def judge_single_answer(
    client: httpx.AsyncClient,
    model: str,
    api_key: str,
    context: str,
    question: str,
    expected_behavior: str,
    required_points: list[str],
    forbidden_points: list[str],
    candidate_answer: str,
    base_url: str = "https://openrouter.ai/api/v1",
) -> JudgeScore:
    """Judge a single candidate answer."""
    if not candidate_answer or candidate_answer.strip().startswith("[DRY RUN]"):
        return JudgeScore(correctness=1, context_grounding=1, uncertainty_handling=1, rationale="Mock/empty answer")

    user_content = JUDGE_USER_TEMPLATE.format(
        context=context,
        question=question,
        expected_behavior=expected_behavior,
        required_points=json.dumps(required_points),
        forbidden_points=json.dumps(forbidden_points),
        candidate_answer=candidate_answer,
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/CyberCase-Intelligence-Framework",
        "X-Title": "CyberCase Attribute First LLM Judge",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=45.0)
        if resp.status_code != 200:
            return JudgeScore(correctness=0, context_grounding=0, uncertainty_handling=0, rationale=f"Judge API error: {resp.status_code}")
        
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        cleaned = clean_json_text(content)
        parsed = json.loads(cleaned)
        return JudgeScore.model_validate(parsed)
    except Exception as e:
        return JudgeScore(correctness=0, context_grounding=0, uncertainty_handling=0, rationale=f"Judge parse error: {str(e)}")


async def run_judge_pipeline(
    results_path: Path,
    benchmark_path: Path,
    output_csv_path: Path,
    judge_model: str = DEFAULT_JUDGE_MODEL,
) -> None:
    """Run LLM judge across all items for B0, A1, and A2."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("OpenRouter API key missing for judge.")

    raw_results = json.loads(results_path.read_text(encoding="utf-8"))
    run_output = PilotRunOutput.model_validate(raw_results)

    raw_bench = json.loads(benchmark_path.read_text(encoding="utf-8"))
    bench_suite = BenchmarkSuite.model_validate(raw_bench)
    bench_map = {item.id: item for item in bench_suite.items}

    print(f"=== Running LLM Judge ({judge_model}) ===")
    print(f"Total items to judge: {len(run_output.results)}")
    print(f"Total conditions per item: 3 (B0, A1, A2)")
    print(f"Total judge evaluations: {len(run_output.results) * 3}")
    print("=" * 48)

    judged_rows: list[dict[str, Any]] = []

    async with httpx.AsyncClient() as client:
        for idx, item in enumerate(run_output.results, start=1):
            bench_item = bench_map.get(item.benchmark_id)
            if not bench_item:
                continue

            context_str = bench_item.formatted_context()
            notes = bench_item.evaluation_notes

            print(f"[{idx}/{len(run_output.results)}] Judging {item.benchmark_id}...", flush=True)

            # Judge B0
            b0_score = await judge_single_answer(
                client, judge_model, api_key,
                context_str, item.question,
                notes.expected_behavior, notes.required_points, notes.forbidden_points,
                item.direct.answer,
            )

            # Judge A1
            a1_score = await judge_single_answer(
                client, judge_model, api_key,
                context_str, item.question,
                notes.expected_behavior, notes.required_points, notes.forbidden_points,
                item.attribute_first.answer,
            )

            # Judge A2
            a2_score = await judge_single_answer(
                client, judge_model, api_key,
                context_str, item.question,
                notes.expected_behavior, notes.required_points, notes.forbidden_points,
                item.oracle_attribute.answer,
            )

            print(f"    B0: C={b0_score.correctness}, G={b0_score.context_grounding}, U={b0_score.uncertainty_handling}")
            print(f"    A1: C={a1_score.correctness}, G={a1_score.context_grounding}, U={a1_score.uncertainty_handling}")
            print(f"    A2: C={a2_score.correctness}, G={a2_score.context_grounding}, U={a2_score.uncertainty_handling}")

            a1_attr_json = (
                json.dumps(item.predicted_attributes.attributes.model_dump())
                if item.predicted_attributes.attributes
                else (item.predicted_attributes.error or "")
            )
            a2_attr_json = json.dumps(item.gold_attributes.model_dump())

            notes_summary = f"B0: {b0_score.rationale} | A1: {a1_score.rationale} | A2: {a2_score.rationale}"

            judged_rows.append({
                "benchmark_id": item.benchmark_id,
                "condition": item.condition,
                "question": item.question,
                "b0_direct_answer": item.direct.answer.replace("\n", " "),
                "b0_correctness_0_2": b0_score.correctness,
                "b0_grounding_0_2": b0_score.context_grounding,
                "b0_uncertainty_0_2": b0_score.uncertainty_handling,
                "a1_predicted_attributes_json": a1_attr_json,
                "a1_attribute_first_answer": item.attribute_first.answer.replace("\n", " "),
                "a1_correctness_0_2": a1_score.correctness,
                "a1_grounding_0_2": a1_score.context_grounding,
                "a1_uncertainty_0_2": a1_score.uncertainty_handling,
                "a2_oracle_attributes_json": a2_attr_json,
                "a2_oracle_answer": item.oracle_attribute.answer.replace("\n", " "),
                "a2_correctness_0_2": a2_score.correctness,
                "a2_grounding_0_2": a2_score.context_grounding,
                "a2_uncertainty_0_2": a2_score.uncertainty_handling,
                "evaluator_notes": notes_summary,
            })

    headers = list(judged_rows[0].keys())
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(judged_rows)

    print(f"\n[OK] Judged scores exported to: {output_csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM Judge for scoring pilot answers")
    parser.add_argument("--results", type=Path, required=True, help="Path to run_<timestamp>.json")
    parser.add_argument("--benchmark", type=Path, default=SCRIPT_DIR / "benchmark.json", help="Path to benchmark.json")
    parser.add_argument("--output-csv", type=Path, default=SCRIPT_DIR / "manual_scoring.csv", help="Path to output scored CSV")
    parser.add_argument("--judge-model", type=str, default=DEFAULT_JUDGE_MODEL, help="OpenRouter judge model ID")

    args = parser.parse_args()
    asyncio.run(
        run_judge_pipeline(
            results_path=args.results,
            benchmark_path=args.benchmark,
            output_csv_path=args.output_csv,
            judge_model=args.judge_model,
        )
    )


if __name__ == "__main__":
    main()
