"""Evaluation and metrics module for the Attribute-First Reasoning Research Pilot.

Computes:
1. Automatic Attribute Metrics (Accuracy, Macro-F1, Evidence P/R/F1).
2. Deterministic Context-Behavior Metrics (Abstention rate, Contradiction handling, Distractor robustness, Reorder consistency).
3. Efficiency Metrics (latency by condition, token counts).
4. Manual Scoring Metrics (Correctness, Grounding, Uncertainty handling if scored CSV provided).
5. Comprehensive Markdown Summary Report.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import (
    AnswerabilityEnum,
    EpistemicStateEnum,
    ItemRunResult,
    PilotRunOutput,
    QuestionTypeEnum,
)


def calculate_macro_f1(gold: list[str], pred: list[str], labels: list[str]) -> float:
    """Calculate macro-averaged F1 score over discrete categories."""
    if not gold:
        return 0.0

    f1_scores: list[float] = []
    for label in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == label and p == label)
        fp = sum(1 for g, p in zip(gold, pred) if g != label and p == label)
        fn = sum(1 for g, p in zip(gold, pred) if g == label and p != label)

        if tp + fp == 0:
            precision = 0.0
        else:
            precision = tp / (tp + fp)

        if tp + fn == 0:
            recall = 0.0
        else:
            recall = tp / (tp + fn)

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        f1_scores.append(f1)

    return sum(f1_scores) / len(f1_scores) if f1_scores else 0.0


def calculate_evidence_metrics(
    gold_sets: list[set[str]], pred_sets: list[set[str]]
) -> tuple[float, float, float]:
    """Calculate mean precision, recall, and F1 for relevant evidence sentence selection."""
    if not gold_sets:
        return 0.0, 0.0, 0.0

    precisions = []
    recalls = []
    f1s = []

    for g_set, p_set in zip(gold_sets, pred_sets):
        if not p_set and not g_set:
            precisions.append(1.0)
            recalls.append(1.0)
            f1s.append(1.0)
            continue
        if not p_set:
            precisions.append(0.0)
            recalls.append(0.0)
            f1s.append(0.0)
            continue
        if not g_set:
            precisions.append(0.0)
            recalls.append(1.0)
            f1s.append(0.0)
            continue

        tp = len(g_set.intersection(p_set))
        p = tp / len(p_set)
        r = tp / len(g_set)
        f = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

        precisions.append(p)
        recalls.append(r)
        f1s.append(f)

    mean_p = sum(precisions) / len(precisions)
    mean_r = sum(recalls) / len(recalls)
    mean_f = sum(f1s) / len(f1s)
    return mean_p, mean_r, mean_f


@dataclass
class AttributeEvaluationReport:
    total_items: int
    parsed_items: int
    parse_success_rate: float
    answerability_acc: float
    answerability_macro_f1: float
    epistemic_acc: float
    epistemic_macro_f1: float
    question_type_acc: float
    question_type_macro_f1: float
    evidence_precision: float
    evidence_recall: float
    evidence_f1: float
    abstention_rate: float
    contradiction_handling_acc: float
    distractor_robustness: float
    reorder_consistency: float


def evaluate_attributes(run_output: PilotRunOutput) -> AttributeEvaluationReport:
    """Evaluate predicted attributes against gold attributes."""
    items = run_output.results
    total = len(items)
    if total == 0:
        return AttributeEvaluationReport(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    gold_ans: list[str] = []
    pred_ans: list[str] = []

    gold_epi: list[str] = []
    pred_epi: list[str] = []

    gold_qtype: list[str] = []
    pred_qtype: list[str] = []

    gold_evidence: list[set[str]] = []
    pred_evidence: list[set[str]] = []

    parsed_count = 0

    # Index by (base_case_id, condition) for behavioral metrics
    case_condition_map: dict[tuple[str, str], ItemRunResult] = {}

    for item in items:
        case_condition_map[(item.base_case_id, item.condition)] = item

        g_attr = item.gold_attributes
        gold_ans.append(g_attr.answerability.value)
        gold_epi.append(g_attr.epistemic_state.value)
        gold_qtype.append(g_attr.question_type.value)
        gold_evidence.append(set(g_attr.relevant_evidence_ids))

        p_res = item.predicted_attributes
        if p_res.attributes:
            parsed_count += 1
            pred_ans.append(p_res.attributes.answerability.value)
            pred_epi.append(p_res.attributes.epistemic_state.value)
            pred_qtype.append(p_res.attributes.question_type.value)
            pred_evidence.append(set(p_res.attributes.relevant_evidence_ids))
        else:
            # Failed parse treated as incorrect/unpredicted
            pred_ans.append("FAILED")
            pred_epi.append("FAILED")
            pred_qtype.append("FAILED")
            pred_evidence.append(set())

    # Accuracies
    ans_acc = sum(1 for g, p in zip(gold_ans, pred_ans) if g == p) / total
    epi_acc = sum(1 for g, p in zip(gold_epi, pred_epi) if g == p) / total
    qtype_acc = sum(1 for g, p in zip(gold_qtype, pred_qtype) if g == p) / total

    # Macro-F1s
    ans_labels = [e.value for e in AnswerabilityEnum]
    epi_labels = [e.value for e in EpistemicStateEnum]
    qtype_labels = [e.value for e in QuestionTypeEnum]

    ans_f1 = calculate_macro_f1(gold_ans, pred_ans, ans_labels)
    epi_f1 = calculate_macro_f1(gold_epi, pred_epi, epi_labels)
    qtype_f1 = calculate_macro_f1(gold_qtype, pred_qtype, qtype_labels)

    # Evidence selection
    ev_p, ev_r, ev_f1 = calculate_evidence_metrics(gold_evidence, pred_evidence)

    # Behavioral metrics:
    # 1. Correct Abstention Rate: When gold is INSUFFICIENT or UNESTABLISHED
    insufficient_items = [
        item for item in items
        if item.gold_attributes.answerability == AnswerabilityEnum.INSUFFICIENT
        or item.gold_attributes.epistemic_state == EpistemicStateEnum.UNESTABLISHED
    ]
    if insufficient_items:
        correct_abstentions = sum(
            1 for it in insufficient_items
            if it.predicted_attributes.attributes
            and (
                it.predicted_attributes.attributes.answerability in (AnswerabilityEnum.INSUFFICIENT, AnswerabilityEnum.CONFLICTING)
                or it.predicted_attributes.attributes.epistemic_state == EpistemicStateEnum.UNESTABLISHED
            )
        )
        abstention_rate = correct_abstentions / len(insufficient_items)
    else:
        abstention_rate = 1.0

    # 2. Contradiction Handling: When gold condition is CONTRADICTION or epistemic state is CONTRADICTED
    contradiction_items = [
        item for item in items
        if item.condition == "CONTRADICTION"
        or item.gold_attributes.epistemic_state == EpistemicStateEnum.CONTRADICTED
    ]
    if contradiction_items:
        correct_contradictions = sum(
            1 for it in contradiction_items
            if it.predicted_attributes.attributes
            and it.predicted_attributes.attributes.epistemic_state == EpistemicStateEnum.CONTRADICTED
        )
        contradiction_handling_acc = correct_contradictions / len(contradiction_items)
    else:
        contradiction_handling_acc = 1.0

    # 3. Distractor Robustness: C3 predicted attributes match C0 predicted attributes
    distractor_matches = 0
    distractor_total = 0
    for (base_id, cond), item in case_condition_map.items():
        if cond == "DISTRACTOR":
            c0_item = case_condition_map.get((base_id, "ORIGINAL"))
            if c0_item and item.predicted_attributes.attributes and c0_item.predicted_attributes.attributes:
                distractor_total += 1
                if (
                    item.predicted_attributes.attributes.epistemic_state
                    == c0_item.predicted_attributes.attributes.epistemic_state
                    and item.predicted_attributes.attributes.answerability
                    == c0_item.predicted_attributes.attributes.answerability
                ):
                    distractor_matches += 1
    distractor_robustness = (distractor_matches / distractor_total) if distractor_total > 0 else 1.0

    # 4. Reorder Consistency: C4 predicted attributes match C0 predicted attributes
    reorder_matches = 0
    reorder_total = 0
    for (base_id, cond), item in case_condition_map.items():
        if cond == "REORDER":
            c0_item = case_condition_map.get((base_id, "ORIGINAL"))
            if c0_item and item.predicted_attributes.attributes and c0_item.predicted_attributes.attributes:
                reorder_total += 1
                if (
                    item.predicted_attributes.attributes.epistemic_state
                    == c0_item.predicted_attributes.attributes.epistemic_state
                    and item.predicted_attributes.attributes.answerability
                    == c0_item.predicted_attributes.attributes.answerability
                ):
                    reorder_matches += 1
    reorder_consistency = (reorder_matches / reorder_total) if reorder_total > 0 else 1.0

    return AttributeEvaluationReport(
        total_items=total,
        parsed_items=parsed_count,
        parse_success_rate=parsed_count / total,
        answerability_acc=ans_acc,
        answerability_macro_f1=ans_f1,
        epistemic_acc=epi_acc,
        epistemic_macro_f1=epi_f1,
        question_type_acc=qtype_acc,
        question_type_macro_f1=qtype_f1,
        evidence_precision=ev_p,
        evidence_recall=ev_r,
        evidence_f1=ev_f1,
        abstention_rate=abstention_rate,
        contradiction_handling_acc=contradiction_handling_acc,
        distractor_robustness=distractor_robustness,
        reorder_consistency=reorder_consistency,
    )


@dataclass
class EfficiencyReport:
    total_calls: int
    b0_latency_mean: float
    a1_pred_latency_mean: float
    a1_gen_latency_mean: float
    a2_oracle_latency_mean: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


def evaluate_efficiency(run_output: PilotRunOutput) -> EfficiencyReport:
    """Evaluate latency and token usage across conditions."""
    items = run_output.results
    n = len(items)
    if n == 0:
        return EfficiencyReport(0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0)

    b0_lats = [it.direct.latency_ms for it in items]
    a1_pred_lats = [it.predicted_attributes.latency_ms for it in items]
    a1_gen_lats = [it.attribute_first.latency_ms for it in items]
    a2_lats = [it.oracle_attribute.latency_ms for it in items]

    total_prompt = sum(
        it.direct.usage.prompt_tokens
        + it.predicted_attributes.usage.prompt_tokens
        + it.attribute_first.usage.prompt_tokens
        + it.oracle_attribute.usage.prompt_tokens
        for it in items
    )
    total_comp = sum(
        it.direct.usage.completion_tokens
        + it.predicted_attributes.usage.completion_tokens
        + it.attribute_first.usage.completion_tokens
        + it.oracle_attribute.usage.completion_tokens
        for it in items
    )

    return EfficiencyReport(
        total_calls=n * 4,
        b0_latency_mean=sum(b0_lats) / n,
        a1_pred_latency_mean=sum(a1_pred_lats) / n,
        a1_gen_latency_mean=sum(a1_gen_lats) / n,
        a2_oracle_latency_mean=sum(a2_lats) / n,
        total_tokens=total_prompt + total_comp,
        prompt_tokens=total_prompt,
        completion_tokens=total_comp,
    )


def load_manual_scores(csv_path: Path) -> dict[str, dict[str, float]]:
    """Parse manual scores from CSV file if filled."""
    if not csv_path.exists():
        return {}

    scores: dict[str, list[float]] = defaultdict(list)
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in [
                "b0_correctness_0_2",
                "b0_grounding_0_2",
                "b0_uncertainty_0_2",
                "a1_correctness_0_2",
                "a1_grounding_0_2",
                "a1_uncertainty_0_2",
                "a2_correctness_0_2",
                "a2_grounding_0_2",
                "a2_uncertainty_0_2",
            ]:
                val = row.get(field, "").strip()
                if val:
                    try:
                        scores[field].append(float(val))
                    except ValueError:
                        pass

    summary: dict[str, dict[str, float]] = {}
    for cond in ["b0", "a1", "a2"]:
        c_scores = scores.get(f"{cond}_correctness_0_2", [])
        g_scores = scores.get(f"{cond}_grounding_0_2", [])
        u_scores = scores.get(f"{cond}_uncertainty_0_2", [])
        if c_scores or g_scores or u_scores:
            summary[cond] = {
                "correctness_mean": sum(c_scores) / len(c_scores) if c_scores else 0.0,
                "grounding_mean": sum(g_scores) / len(g_scores) if g_scores else 0.0,
                "uncertainty_mean": sum(u_scores) / len(u_scores) if u_scores else 0.0,
                "count": len(c_scores),
            }

    return summary


def generate_markdown_report(
    run_output: PilotRunOutput,
    attr_report: AttributeEvaluationReport,
    eff_report: EfficiencyReport,
    manual_scores: dict[str, dict[str, float]] | None = None,
) -> str:
    """Generate Markdown evaluation summary."""
    lines: list[str] = [
        "# CyberCase Attribute-First Reasoning Pilot - Evaluation Report",
        "",
        f"- **Model**: `{run_output.model}`",
        f"- **Temperature**: `{run_output.temperature}`",
        f"- **Timestamp**: `{run_output.timestamp}`",
        f"- **Total Evaluated Benchmark Items**: `{run_output.total_items}`",
        "",
        "---",
        "",
        "## 1. Automatic Attribute Prediction Metrics (A1 Step 1)",
        "",
        "Evaluates the capability of the zero-shot base model to predict the intermediate attribute contract accurately.",
        "",
        "| Metric Dimension | Value | Description |",
        "| :--- | :--- | :--- |",
        f"| **Strict JSON Parse Success Rate** | `{attr_report.parse_success_rate * 100:.1f}%` ({attr_report.parsed_items}/{attr_report.total_items}) | Valid JSON adhering to AttributeContract |",
        f"| **Answerability Accuracy** | `{attr_report.answerability_acc * 100:.1f}%` | SUFFICIENT / INSUFFICIENT / CONFLICTING |",
        f"| **Answerability Macro-F1** | `{attr_report.answerability_macro_f1:.3f}` | Unweighted macro F1 across classes |",
        f"| **Epistemic State Accuracy** | `{attr_report.epistemic_acc * 100:.1f}%` | SUPPORTED / UNESTABLISHED / CONTRADICTED |",
        f"| **Epistemic State Macro-F1** | `{attr_report.epistemic_macro_f1:.3f}` | Macro F1 preserving uncertainty & contradiction |",
        f"| **Question Type Accuracy** | `{attr_report.question_type_acc * 100:.1f}%` | MEANS / PROGRESSION / CORRELATION / IMPACT / OBJECTIVE |",
        f"| **Question Type Macro-F1** | `{attr_report.question_type_macro_f1:.3f}` | Macro F1 across question types |",
        f"| **Evidence Selection Precision** | `{attr_report.evidence_precision:.3f}` | Relevant sentence precision |",
        f"| **Evidence Selection Recall** | `{attr_report.evidence_recall:.3f}` | Relevant sentence recall |",
        f"| **Evidence Selection F1** | `{attr_report.evidence_f1:.3f}` | Evidence sentence overlap F1 |",
        "",
        "---",
        "",
        "## 2. Deterministic Context-Behavior Metrics",
        "",
        "| Behavioral Dimension | Value | Interpretation |",
        "| :--- | :--- | :--- |",
        f"| **Correct Abstention Rate** | `{attr_report.abstention_rate * 100:.1f}%` | Rate of correctly flagging INSUFFICIENT / UNESTABLISHED items |",
        f"| **Contradiction Handling Accuracy** | `{attr_report.contradiction_handling_acc * 100:.1f}%` | Rate of recognizing CONTRADICTED or CONFLICTING evidence |",
        f"| **Distractor Robustness (C3 vs C0)** | `{attr_report.distractor_robustness * 100:.1f}%` | Consistency of predicted state when distractors are introduced |",
        f"| **Reorder Consistency (C4 vs C0)** | `{attr_report.reorder_consistency * 100:.1f}%` | Invariance of predicted state under sentence permutation |",
        "",
        "---",
        "",
        "## 3. Downstream Generation & Efficiency Comparison",
        "",
        "| Condition | Mean Latency (ms) | Notes |",
        "| :--- | :--- | :--- |",
        f"| **B0 - Direct Zero-Shot** | `{eff_report.b0_latency_mean:.1f} ms` | 1 LLM call per item |",
        f"| **A1 - Predicted Attribute-First** | `{eff_report.a1_pred_latency_mean + eff_report.a1_gen_latency_mean:.1f} ms` | 2 LLM calls (Pred: `{eff_report.a1_pred_latency_mean:.1f} ms` + Gen: `{eff_report.a1_gen_latency_mean:.1f} ms`) |",
        f"| **A2 - Oracle Attribute-First** | `{eff_report.a2_oracle_latency_mean:.1f} ms` | 1 LLM call with gold attributes |",
        "",
        f"- **Total Model Calls**: `{eff_report.total_calls}`",
        f"- **Total Token Usage**: `{eff_report.total_tokens:,}` (Prompt: `{eff_report.prompt_tokens:,}`, Completion: `{eff_report.completion_tokens:,}`)",
        "",
        "---",
        "",
        "## 4. Manual Human Scoring",
        "",
    ]

    if manual_scores and any(v.get("count", 0) > 0 for v in manual_scores.values()):
        lines.extend([
            "| Condition | Evaluated Items | Mean Correctness (0-2) | Mean Grounding (0-2) | Mean Uncertainty Handling (0-2) |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])
        for cond, name in [
            ("b0", "B0 Direct"),
            ("a1", "A1 Predicted Attribute-First"),
            ("a2", "A2 Oracle Attribute-First"),
        ]:
            if cond in manual_scores:
                sc = manual_scores[cond]
                lines.append(
                    f"| **{name}** | `{sc['count']}` | `{sc['correctness_mean']:.2f}` | `{sc['grounding_mean']:.2f}` | `{sc['uncertainty_mean']:.2f}` |"
                )
    else:
        lines.extend([
            "> [!NOTE]",
            "> Manual answer scoring is pending. Open `manual_scoring.csv` to blind-score generated answers for Correctness, Context Grounding, and Uncertainty Handling.",
            "",
            "- `correctness`: 0 = incorrect / unsupported conclusion, 1 = partially correct, 2 = correct analytical conclusion.",
            "- `context_grounding`: 0 = materially introduces unsupported information, 1 = mostly grounded, 2 = fully grounded.",
            "- `uncertainty_handling`: 0 = materially strengthens/ignores uncertainty, 1 = partially appropriate, 2 = correctly preserves evidentiary state.",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## 5. Statistical & Hypothesis Exploration Guidelines",
        "",
        "- All metrics in this pilot are exploratory given the small sample size ($N = 33$).",
        "- Key interpretation axes:",
        "  - If **$B0 \\approx A1 \\approx A2$**: Explicit attribute-first representation provides little downstream benefit.",
        "  - If **$A2 \\gg B0$ and $A1 \\approx B0$**: Attribute representation is valuable, but zero-shot attribute prediction is the bottleneck.",
        "  - If **$A1 > B0$ and $A2 \\ge A1$**: Strong evidence that attribute-first reasoning improves zero-shot cybersecurity QA.",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CyberCase Attribute-First Pilot Results")
    parser.add_argument("--results", type=Path, required=True, help="Path to run_<timestamp>.json")
    parser.add_argument("--manual-csv", type=Path, default=None, help="Optional path to filled manual_scoring.csv")
    parser.add_argument("--output-report", type=Path, default=None, help="Optional output path for Markdown report")

    args = parser.parse_args()

    if not args.results.exists():
        raise FileNotFoundError(f"Results file not found at {args.results}")

    raw_json = json.loads(args.results.read_text(encoding="utf-8"))
    run_output = PilotRunOutput.model_validate(raw_json)

    attr_report = evaluate_attributes(run_output)
    eff_report = evaluate_efficiency(run_output)

    manual_csv = args.manual_csv or (args.results.parent / "manual_scoring.csv")
    manual_scores = load_manual_scores(manual_csv) if manual_csv and manual_csv.exists() else {}

    report_md = generate_markdown_report(run_output, attr_report, eff_report, manual_scores)

    if args.output_report:
        args.output_report.write_text(report_md, encoding="utf-8")
        print(f"[OK] Evaluation report written to: {args.output_report}")
    else:
        # Save alongside results
        default_out = args.results.parent / f"report_{args.results.stem}.md"
        default_out.write_text(report_md, encoding="utf-8")
        print(f"[OK] Evaluation report written to: {default_out}")

    print("\n" + report_md)


if __name__ == "__main__":
    main()
