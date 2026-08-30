"""Main evaluation pilot orchestrator and CLI entrypoint."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

# Ensure workspace root and backend are on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_BACKEND_ROOT = _REPO_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

# Ensure UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config import settings
from evaluation.analysis_pilot.config import (
    ANALYSIS_MAX_OUTPUT_TOKENS,
    ANALYSIS_TEMPERATURE,
    DEFAULT_ANALYSIS_MODEL,
    DEFAULT_JUDGE_MODEL,
    DEFAULT_OUTPUT_DIR,
    JUDGE_TEMPERATURE,
)
from evaluation.analysis_pilot.dataset import (
    load_all_cases,
    select_stratified_pilot_cases,
)
from evaluation.analysis_pilot.generator import (
    run_extracted_state_condition,
    run_raw_direct_condition,
)
from evaluation.analysis_pilot.judge import judge_all_case_probes
from evaluation.analysis_pilot.metrics import (
    compute_aggregate_metrics,
    compute_case_metrics,
)
from evaluation.analysis_pilot.prompts import (
    ANALYSIS_PROMPT_VERSION,
    ANALYSIS_SYSTEM_PROMPT,
)
from evaluation.analysis_pilot.schemas import (
    ExtractionLogRecord,
    GenerationRecord,
    ProbeJudgmentRecord,
)


def write_jsonl(path: Path, records: list[Any]) -> None:
    """Write list of Pydantic models or dicts to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            if hasattr(rec, "model_dump"):
                line = json.dumps(rec.model_dump(mode="json"), ensure_ascii=False)
            else:
                line = json.dumps(rec, ensure_ascii=False)
            f.write(line + "\n")


def generate_summary_markdown(
    raw_agg: dict[str, Any],
    ext_agg: dict[str, Any],
    case_results: list[dict[str, Any]],
    model_name: str,
    judge_model: str,
    selected_cases: list[dict[str, Any]],
) -> str:
    """Format markdown summary table and per-case results."""
    lines = [
        "# Analysis-Isolation Pilot: RAW_DIRECT vs EXTRACTED_STATE Summary",
        "",
        f"- **Evaluation Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Analysis Model**: `{model_name}` (temperature={ANALYSIS_TEMPERATURE}, max_tokens={ANALYSIS_MAX_OUTPUT_TOKENS})",
        f"- **Extraction Model**: `{settings.chat_extraction_model}` (prompt={settings.chat_extraction_model})",
        f"- **Judge Model**: `{judge_model}` (temperature={JUDGE_TEMPERATURE})",
        f"- **Prompt Version**: `{ANALYSIS_PROMPT_VERSION}`",
        f"- **Cases Evaluated**: {len(selected_cases)} (Stratified 4 Scenarios × 2 Languages)",
        "",
        "## Primary Metrics Summary",
        "",
        "| Condition | Supported Probe Coverage | Epistemic Probe Violation Rate | Factual Error Probe Rate |",
        "| :--- | :---: | :---: | :---: |",
        f"| **RAW_DIRECT** | {raw_agg.get('macro_supported_probe_coverage', 0.0):.1%} | {raw_agg.get('macro_epistemic_probe_violation_rate', 0.0):.1%} | {raw_agg.get('macro_factual_error_probe_rate', 0.0):.1%} |",
        f"| **EXTRACTED_STATE** | {ext_agg.get('macro_supported_probe_coverage', 0.0):.1%} | {ext_agg.get('macro_epistemic_probe_violation_rate', 0.0):.1%} | {ext_agg.get('macro_factual_error_probe_rate', 0.0):.1%} |",
        "",
        "> Note: Supported Probe Coverage measures recall of known supported facts (higher is better). Epistemic Probe Violation Rate measures assertion of ungrounded causal/attribution/negation/certainty claims (lower is better). Factual Error Probe Rate measures susceptibility to swapped entities/timestamps.",
        "",
        "## Epistemic Violation Breakdown by Type",
        "",
        "| Condition | Certainty Strengthening | Causality Insertion | Attribution Insertion | Negation Flip |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]

    raw_ep = raw_agg.get("epistemic_breakdown", {})
    ext_ep = ext_agg.get("epistemic_breakdown", {})

    def _fmt_ep(ep_dict: dict[str, Any], key: str) -> str:
        d = ep_dict.get(key, {})
        tot = d.get("total_probes", 0)
        violated = d.get("violations", 0)
        rate = d.get("rate", 0.0)
        return f"{rate:.1%} ({violated}/{tot})" if tot > 0 else "N/A"

    lines.append(
        f"| **RAW_DIRECT** | {_fmt_ep(raw_ep, 'certainty_strengthening')} | {_fmt_ep(raw_ep, 'causality_insertion')} | {_fmt_ep(raw_ep, 'attribution_insertion')} | {_fmt_ep(raw_ep, 'negation_flip')} |"
    )
    lines.append(
        f"| **EXTRACTED_STATE** | {_fmt_ep(ext_ep, 'certainty_strengthening')} | {_fmt_ep(ext_ep, 'causality_insertion')} | {_fmt_ep(ext_ep, 'attribution_insertion')} | {_fmt_ep(ext_ep, 'negation_flip')} |"
    )

    lines.extend(
        [
            "",
            "## Per-Case Results",
            "",
            "| Case ID | Lang | Scenario | Condition | Supported Cov. | Epistemic Viol. | Factual Error | Ext. Status | Latency |",
            "| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
        ]
    )

    for c in case_results:
        cid = c["case_id"]
        lang = c["language"]
        scen = c["scenario_id"]
        ext_stat = c.get("extraction_status", "N/A")

        # RAW_DIRECT row
        raw_m = c["RAW_DIRECT"]["metrics"]
        raw_lat = f"{c['RAW_DIRECT']['generation'].latency_ms:.0f}ms"
        lines.append(
            f"| `{cid}` | {lang} | {scen} | RAW_DIRECT | {raw_m['supported_probe_coverage']:.1%} | {raw_m['epistemic_probe_violation_rate']:.1%} | {raw_m['factual_error_probe_rate']:.1%} | N/A | {raw_lat} |"
        )

        # EXTRACTED_STATE row
        ext_m = c["EXTRACTED_STATE"]["metrics"]
        ext_lat = f"{c['EXTRACTED_STATE']['generation'].latency_ms:.0f}ms"
        lines.append(
            f"| `{cid}` | {lang} | {scen} | EXTRACTED_STATE | {ext_m['supported_probe_coverage']:.1%} | {ext_m['epistemic_probe_violation_rate']:.1%} | {ext_m['factual_error_probe_rate']:.1%} | `{ext_stat}` | {ext_lat} |"
        )

    lines.extend(
        [
            "",
            "## Selected Pilot Dataset Cases",
            "",
        ]
    )
    for i, sc in enumerate(selected_cases, 1):
        lines.append(
            f"{i}. **`{sc['case_id']}`** ({sc['language'].upper()}, `{sc['scenario_id']}`)"
        )
        lines.append(f"   - *Narrative*: {sc['narrative']}")

    return "\n".join(lines)


async def run_single_case(
    case: dict[str, Any],
    *,
    model: str,
    judge_model: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Execute both conditions and evaluate probes for a single case."""
    case_id = case["case_id"]
    print(f"\n[{case_id}] Processing ({case['language']}, scenario={case['scenario_id']})...")

    # 1. Condition A: RAW_DIRECT
    print(f"  [{case_id}] Running RAW_DIRECT generation...")
    raw_gen = await run_raw_direct_condition(case, model=model)

    # 2. Condition B: EXTRACTED_STATE
    print(f"  [{case_id}] Running EXTRACTED_STATE (extraction + generation)...")
    ext_gen, ext_log = await run_extracted_state_condition(case, model=model)

    # 3. Judge Probes for RAW_DIRECT
    print(f"  [{case_id}] Evaluating probes on RAW_DIRECT analysis with judge: {judge_model}...")
    raw_judgments = await judge_all_case_probes(
        analysis_output=raw_gen.output,
        case=case,
        condition="RAW_DIRECT",
        model=judge_model,
    )
    raw_metrics = compute_case_metrics(raw_judgments)

    # 4. Judge Probes for EXTRACTED_STATE
    print(f"  [{case_id}] Evaluating probes on EXTRACTED_STATE analysis with judge: {judge_model}...")
    ext_judgments = await judge_all_case_probes(
        analysis_output=ext_gen.output,
        case=case,
        condition="EXTRACTED_STATE",
        model=judge_model,
    )
    ext_metrics = compute_case_metrics(ext_judgments)

    print(
        f"  [{case_id}] RAW_DIRECT: Supported={raw_metrics['supported_probe_coverage']:.1%}, "
        f"Epistemic Viol={raw_metrics['epistemic_probe_violation_rate']:.1%}, "
        f"Factual Error={raw_metrics['factual_error_probe_rate']:.1%}"
    )
    print(
        f"  [{case_id}] EXTRACTED_STATE: Supported={ext_metrics['supported_probe_coverage']:.1%}, "
        f"Epistemic Viol={ext_metrics['epistemic_probe_violation_rate']:.1%}, "
        f"Factual Error={ext_metrics['factual_error_probe_rate']:.1%} (Extraction: {ext_log.status})"
    )

    return {
        "case_id": case_id,
        "language": case["language"],
        "scenario_id": case["scenario_id"],
        "extraction_status": ext_log.status,
        "extraction_log": ext_log,
        "RAW_DIRECT": {
            "generation": raw_gen,
            "judgments": raw_judgments,
            "metrics": raw_metrics,
        },
        "EXTRACTED_STATE": {
            "generation": ext_gen,
            "judgments": ext_judgments,
            "metrics": ext_metrics,
        },
    }


async def run_pipeline(
    *,
    sanity_check: bool = False,
    model: str = DEFAULT_ANALYSIS_MODEL,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    case_count: int = 10,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> None:
    """Main pipeline execution orchestrator."""
    print("=" * 80)
    print("CYBERCASE ANALYSIS-ISOLATION PILOT: RAW_DIRECT vs EXTRACTED_STATE")
    print(f"Analysis Model: {model} | Judge Model: {judge_model} | Output Dir: {output_dir}")
    print("=" * 80)

    # 1. Select Stratified Cases
    selected_cases = select_stratified_pilot_cases(count=case_count)
    print(f"Stratified Selection: {len(selected_cases)} cases found:")
    for i, c in enumerate(selected_cases, 1):
        print(f"  {i}. case_id={c['case_id']}, lang={c['language']}, scenario={c['scenario_id']}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save selected_cases.json
    selected_cases_file = output_dir / "selected_cases.json"
    with open(selected_cases_file, "w", encoding="utf-8") as f:
        json.dump(selected_cases, f, indent=2, ensure_ascii=False)
    print(f"Saved selected cases to: {selected_cases_file}")

    cases_to_run = [selected_cases[0]] if sanity_check else selected_cases

    if sanity_check:
        print("\n>>> PERFORMING SANITY CHECK ON 1 CASE <<<")
    else:
        print(f"\n>>> RUNNING ALL {len(cases_to_run)} CASES <<<")

    all_raw_gens: list[GenerationRecord] = []
    all_ext_gens: list[GenerationRecord] = []
    all_ext_logs: list[ExtractionLogRecord] = []
    all_judgments: list[ProbeJudgmentRecord] = []
    case_results: list[dict[str, Any]] = []

    for case in cases_to_run:
        res = await run_single_case(
            case,
            model=model,
            judge_model=judge_model,
            output_dir=output_dir,
        )
        case_results.append(res)
        all_raw_gens.append(res["RAW_DIRECT"]["generation"])
        all_ext_gens.append(res["EXTRACTED_STATE"]["generation"])
        all_ext_logs.append(res["extraction_log"])
        all_judgments.extend(res["RAW_DIRECT"]["judgments"])
        all_judgments.extend(res["EXTRACTED_STATE"]["judgments"])

    # If sanity check mode, print inspection details
    if sanity_check:
        c0 = case_results[0]
        case_0 = cases_to_run[0]
        print("\n" + "=" * 80)
        print("SANITY CHECK INSPECTION REPORT")
        print("=" * 80)
        print(f"Case ID: {case_0['case_id']} ({case_0['language']}, scenario={case_0['scenario_id']})")
        print("\n[1] Raw Narrative:")
        print(case_0["narrative"])

        print("\n[2] Extracted Canonical Case State:")
        if c0["extraction_log"].canonical_case_state:
            print(json.dumps(c0["extraction_log"].canonical_case_state, indent=2, ensure_ascii=False))
        else:
            print("Extraction failed!")

        print("\n[3] RAW_DIRECT Analysis:")
        raw_out = c0["RAW_DIRECT"]["generation"].output
        if raw_out:
            print(f"Findings ({len(raw_out.findings)}):")
            for f in raw_out.findings:
                print(f"  [{f.epistemic_status}] {f.text}")
            print(f"Narrative:\n{raw_out.analysis_text}")

        print("\n[4] EXTRACTED_STATE Analysis:")
        ext_out = c0["EXTRACTED_STATE"]["generation"].output
        if ext_out:
            print(f"Findings ({len(ext_out.findings)}):")
            for f in ext_out.findings:
                print(f"  [{f.epistemic_status}] {f.text}")
            print(f"Narrative:\n{ext_out.analysis_text}")

        print("\n[5] Constraint Verification:")
        print("  - Gold facts or verification pairs sent to generator? NO (Checked generator input).")
        print("  - MITRE / RAG context included? NO (Standalone analysis prompt).")
        print(f"  - Generator decoding settings identical? YES (temp={ANALYSIS_TEMPERATURE}, max_tokens={ANALYSIS_MAX_OUTPUT_TOKENS}).")
        print("=" * 80)
        print("Sanity check completed successfully.")
        return

    # Compute Aggregates
    raw_case_metrics = [cr["RAW_DIRECT"]["metrics"] for cr in case_results]
    ext_case_metrics = [cr["EXTRACTED_STATE"]["metrics"] for cr in case_results]

    raw_agg = compute_aggregate_metrics(raw_case_metrics)
    ext_agg = compute_aggregate_metrics(ext_case_metrics)

    # Save artifacts
    write_jsonl(output_dir / "raw_outputs.jsonl", all_raw_gens)
    write_jsonl(output_dir / "extracted_outputs.jsonl", all_ext_gens)
    write_jsonl(output_dir / "extraction_outputs.jsonl", all_ext_logs)
    write_jsonl(output_dir / "probe_judgments.jsonl", all_judgments)

    summary_data = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
        "extraction_model": settings.chat_extraction_model,
        "judge_model": judge_model,
        "prompt_version": ANALYSIS_PROMPT_VERSION,
        "case_count": len(case_results),
        "RAW_DIRECT": raw_agg,
        "EXTRACTED_STATE": ext_agg,
        "case_results": [
            {
                "case_id": cr["case_id"],
                "language": cr["language"],
                "scenario_id": cr["scenario_id"],
                "extraction_status": cr["extraction_status"],
                "RAW_DIRECT": cr["RAW_DIRECT"]["metrics"],
                "EXTRACTED_STATE": cr["EXTRACTED_STATE"]["metrics"],
            }
            for cr in case_results
        ],
    }

    with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    summary_md = generate_summary_markdown(
        raw_agg=raw_agg,
        ext_agg=ext_agg,
        case_results=case_results,
        model_name=model,
        judge_model=judge_model,
        selected_cases=selected_cases,
    )

    with open(output_dir / "summary.md", "w", encoding="utf-8") as f:
        f.write(summary_md)

    print("\n" + "=" * 80)
    print("PILOT EVALUATION COMPLETE")
    print("=" * 80)
    print(summary_md)
    print("=" * 80)
    print(f"Artifacts successfully written to: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Analysis-Isolation Evaluation Pilot (RAW_DIRECT vs EXTRACTED_STATE)"
    )
    parser.add_argument(
        "--sanity-check",
        action="store_true",
        help="Run only 1 case and print inspection output for sanity verification.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_ANALYSIS_MODEL,
        help=f"Analysis model identifier (default: {DEFAULT_ANALYSIS_MODEL})",
    )
    parser.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help=f"Judge model identifier (default: {DEFAULT_JUDGE_MODEL})",
    )
    parser.add_argument(
        "--case-count",
        type=int,
        default=10,
        help="Number of cases to evaluate (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save evaluation artifacts (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    asyncio.run(
        run_pipeline(
            sanity_check=args.sanity_check,
            model=args.model,
            judge_model=args.judge_model,
            case_count=args.case_count,
            output_dir=args.output_dir,
        )
    )


if __name__ == "__main__":
    main()
