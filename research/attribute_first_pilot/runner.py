"""CLI Runner for the Attribute-First Reasoning Research Pilot.

Executes the three conditions (B0 direct, A1 predicted attribute-first, A2 oracle attribute-first)
over the benchmark dataset using meta-llama/llama-3.1-8b-instruct at temperature=0.0.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .contracts import (
    BenchmarkItem,
    BenchmarkSuite,
    ItemRunResult,
    PilotRunOutput,
)
from .prompts import (
    build_attribute_first_messages,
    build_attribute_prediction_messages,
    build_direct_baseline_messages,
)
from .provider import DEFAULT_MODEL, PilotLlmProvider

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_PATH = SCRIPT_DIR / "benchmark.json"
DEFAULT_RESULTS_DIR = SCRIPT_DIR / "results"
DEFAULT_MANUAL_SCORING_CSV = SCRIPT_DIR / "manual_scoring.csv"


def load_benchmark(path: Path) -> BenchmarkSuite:
    """Load and validate benchmark suite."""
    if not path.exists():
        raise FileNotFoundError(f"Benchmark file not found at {path}")
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    return BenchmarkSuite.model_validate(raw_data)


def export_manual_scoring_template(
    run_output: PilotRunOutput,
    csv_path: Path,
) -> None:
    """Export blank manual scoring CSV template with blind/comparative answer rows."""
    headers = [
        "benchmark_id",
        "condition",
        "question",
        "b0_direct_answer",
        "b0_correctness_0_2",
        "b0_grounding_0_2",
        "b0_uncertainty_0_2",
        "a1_predicted_attributes_json",
        "a1_attribute_first_answer",
        "a1_correctness_0_2",
        "a1_grounding_0_2",
        "a1_uncertainty_0_2",
        "a2_oracle_attributes_json",
        "a2_oracle_answer",
        "a2_correctness_0_2",
        "a2_grounding_0_2",
        "a2_uncertainty_0_2",
        "evaluator_notes",
    ]

    rows = []
    for item in run_output.results:
        a1_attr_json = (
            json.dumps(item.predicted_attributes.attributes.model_dump())
            if item.predicted_attributes.attributes
            else (item.predicted_attributes.error or "")
        )
        a2_attr_json = json.dumps(item.gold_attributes.model_dump())
        rows.append({
            "benchmark_id": item.benchmark_id,
            "condition": item.condition,
            "question": item.question,
            "b0_direct_answer": item.direct.answer.replace("\n", " "),
            "b0_correctness_0_2": "",
            "b0_grounding_0_2": "",
            "b0_uncertainty_0_2": "",
            "a1_predicted_attributes_json": a1_attr_json,
            "a1_attribute_first_answer": item.attribute_first.answer.replace("\n", " "),
            "a1_correctness_0_2": "",
            "a1_grounding_0_2": "",
            "a1_uncertainty_0_2": "",
            "a2_oracle_attributes_json": a2_attr_json,
            "a2_oracle_answer": item.oracle_attribute.answer.replace("\n", " "),
            "a2_correctness_0_2": "",
            "a2_grounding_0_2": "",
            "a2_uncertainty_0_2": "",
            "evaluator_notes": "",
        })

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


async def run_single_item(
    item: BenchmarkItem,
    provider: PilotLlmProvider,
) -> ItemRunResult:
    """Run B0, A1 (step 1 & 2), and A2 for a single benchmark item."""
    context_str = item.formatted_context()
    question_str = item.question

    # 1. B0: Direct Zero-Shot
    b0_messages = build_direct_baseline_messages(context_str, question_str)
    direct_res = await provider.generate_answer(b0_messages)

    # 2. A1 Step 1: Attribute Prediction
    a1_pred_messages = build_attribute_prediction_messages(context_str, question_str)
    pred_attr_res = await provider.predict_attributes(a1_pred_messages)

    # 3. A1 Step 2: Attribute-First Generation with Predicted Attributes
    if pred_attr_res.attributes:
        a1_gen_messages = build_attribute_first_messages(
            context_str, question_str, pred_attr_res.attributes
        )
        a1_gen_res = await provider.generate_answer(a1_gen_messages)
    else:
        # If attribute prediction failed, record failure without silent substitution
        a1_gen_res = direct_res.model_copy(
            update={
                "answer": "",
                "latency_ms": 0.0,
                "error": f"Skipped generation: attribute prediction failed ({pred_attr_res.error})",
            }
        )

    # 4. A2: Oracle Attribute-First Generation with Gold Attributes
    a2_gen_messages = build_attribute_first_messages(
        context_str, question_str, item.gold_attributes
    )
    a2_gen_res = await provider.generate_answer(a2_gen_messages)

    return ItemRunResult(
        benchmark_id=item.id,
        base_case_id=item.base_case_id,
        condition=item.condition.value,
        question=item.question,
        gold_attributes=item.gold_attributes,
        direct=direct_res,
        predicted_attributes=pred_attr_res,
        attribute_first=a1_gen_res,
        oracle_attribute=a2_gen_res,
    )


async def run_pilot(
    benchmark_path: Path = DEFAULT_BENCHMARK_PATH,
    results_dir: Path = DEFAULT_RESULTS_DIR,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    limit: int | None = None,
    dry_run: bool = False,
) -> Path:
    """Execute the full pilot pipeline and write results."""
    results_dir.mkdir(parents=True, exist_ok=True)
    suite = load_benchmark(benchmark_path)
    items = suite.items[:limit] if limit else suite.items

    print(f"=== CyberCase Attribute-First Pilot Runner ===")
    print(f"Model: {model}")
    print(f"Temperature: {temperature}")
    print(f"Total benchmark items: {len(items)} (of {len(suite.items)})")
    print(f"Mode: {'DRY RUN (mock calls)' if dry_run else 'LIVE API CALLS'}")
    print(f"Calls per item: 4 (B0 direct + A1 predict + A1 generate + A2 oracle)")
    print(f"Total expected LLM calls: {len(items) * 4}")
    print("=" * 48)

    provider = PilotLlmProvider(
        model=model,
        temperature=temperature,
        dry_run=dry_run,
    )

    results: list[ItemRunResult] = []
    t_start = datetime.now(timezone.utc)

    for idx, item in enumerate(items, start=1):
        print(f"[{idx}/{len(items)}] Running {item.id} (Condition: {item.condition.value})...", flush=True)
        res = await run_single_item(item, provider)
        results.append(res)
        status_b0 = "OK" if not res.direct.error else f"ERR: {res.direct.error}"
        status_a1_pred = "OK" if not res.predicted_attributes.error else f"ERR: {res.predicted_attributes.error}"
        status_a1 = "OK" if not res.attribute_first.error else f"ERR: {res.attribute_first.error}"
        status_a2 = "OK" if not res.oracle_attribute.error else f"ERR: {res.oracle_attribute.error}"
        print(f"    B0: {status_b0} | A1-Pred: {status_a1_pred} | A1-Gen: {status_a1} | A2-Oracle: {status_a2}")

    timestamp_str = t_start.strftime("%Y%m%d_%H%M%S")
    output_filename = f"run_{timestamp_str}.json"
    output_path = results_dir / output_filename

    run_output = PilotRunOutput(
        timestamp=t_start.isoformat(),
        model=model,
        temperature=temperature,
        total_items=len(results),
        results=results,
    )

    output_path.write_text(run_output.model_dump_json(indent=2), encoding="utf-8")
    print(f"\n[OK] Results saved to: {output_path}")

    # Generate manual scoring template
    csv_path = results_dir / f"manual_scoring_{timestamp_str}.csv"
    export_manual_scoring_template(run_output, csv_path)
    # Also update default manual_scoring.csv
    export_manual_scoring_template(run_output, DEFAULT_MANUAL_SCORING_CSV)
    print(f"[OK] Manual scoring template saved to: {csv_path}")

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CyberCase Attribute-First Reasoning Pilot")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK_PATH, help="Path to benchmark.json")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR, help="Results output directory")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="OpenRouter model ID")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items to run")
    parser.add_argument("--dry-run", action="store_true", help="Perform mock run without live API calls")

    args = parser.parse_args()
    asyncio.run(
        run_pilot(
            benchmark_path=args.benchmark,
            results_dir=args.results_dir,
            model=args.model,
            temperature=args.temperature,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
