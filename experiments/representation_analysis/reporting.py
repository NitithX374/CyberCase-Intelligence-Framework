from __future__ import annotations

from collections import defaultdict
from statistics import mean, median
from typing import Any

from .constants import CONDITIONS, PAIRWISE_COMPARISONS


def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    def stats(selected: list[dict[str, Any]], condition: str) -> dict[str, Any]:
        available = [x for x in selected if x[condition]["rouge_l"] is not None]
        return {"count": len(available), "failed": len(selected) - len(available), "rouge_l_mean": round(mean(x[condition]["rouge_l"] for x in available), 6) if available else None, "sbert_mean": round(mean(x[condition]["sbert"] for x in available), 6) if available else None}
    by_task: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_task[record["category"]].append(record)
    pairwise: dict[str, Any] = {}
    for left, right in PAIRWISE_COMPARISONS:
        metrics: dict[str, Any] = {}
        for metric in ("rouge_l", "sbert"):
            deltas = [x[left][metric] - x[right][metric] for x in records if x[left][metric] is not None and x[right][metric] is not None]
            metrics[metric] = {"count": len(deltas), "mean_delta": round(mean(deltas), 6) if deltas else None, "median_delta": round(median(deltas), 6) if deltas else None, "improved": sum(x > 1e-6 for x in deltas), "degraded": sum(x < -1e-6 for x in deltas), "unchanged": sum(abs(x) <= 1e-6 for x in deltas)}
        pairwise[f"{left}-{right}"] = metrics
    return {
        "experiment": "SEvenLLM representation analysis", "sample_count": len(records), "config": config,
        "overall": {condition: stats(records, condition) for condition in CONDITIONS},
        "by_task": {task: {condition: stats(group, condition) for condition in CONDITIONS} for task, group in sorted(by_task.items())},
        "pairwise": pairwise,
        "representation_size": {condition: size_stats(records, condition) for condition in CONDITIONS},
        "failure_examples": failure_examples(records),
    }


def failure_examples(records: list[dict[str, Any]]) -> dict[str, Any]:
    records = [record for record in records if record["B1"]["rouge_l"] is not None and record["B2"]["rouge_l"] is not None]
    def item(record: dict[str, Any], condition: str) -> dict[str, Any]:
        return {"sample_id": record["sample_id"], "category": record["category"], "rouge_delta_vs_b0": round(record[condition]["rouge_l"] - record["B0"]["rouge_l"], 6), "missing_source_strings": record[condition]["diagnostics"]["missing"]}
    return {
        "best_b1": item(max(records, key=lambda x: x["B1"]["rouge_l"] - x["B0"]["rouge_l"]), "B1"),
        "best_b2": item(max(records, key=lambda x: x["B2"]["rouge_l"] - x["B0"]["rouge_l"]), "B2"),
        "worst_b1": item(min(records, key=lambda x: x["B1"]["rouge_l"] - x["B0"]["rouge_l"]), "B1"),
        "most_b2_missing": item(max(records, key=lambda x: x["B2"]["diagnostics"]["missing"]), "B2"),
        "most_b1_possible_unsupported": {"sample_id": max(records, key=lambda x: len(x["B1"]["extraction_diagnostics"]["possible_unsupported_surface_values"] or []))["sample_id"], "values": max(records, key=lambda x: len(x["B1"]["extraction_diagnostics"]["possible_unsupported_surface_values"] or []))["B1"]["extraction_diagnostics"]["possible_unsupported_surface_values"]},
    }


def size_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    available = [record[condition] for record in records if record[condition].get("input_chars") is not None]
    return {"count": len(available), "chars_mean": round(mean(x["input_chars"] for x in available), 3) if available else None, "estimated_tokens_mean": round(mean(x["estimated_input_tokens"] for x in available), 3) if available else None}


def render_markdown(summary: dict[str, Any]) -> str:
    lines = ["# B0/B1/B2 representation comparison", "", f"Frozen English generation cases: **{summary['sample_count']}**", "", "## Comparable results", "", "| Condition | n | ROUGE-L | SBERT | Mean chars | Mean estimated tokens |", "|---|---:|---:|---:|---:|---:|"]
    for condition in CONDITIONS:
        metric, size = summary["overall"][condition], summary["representation_size"][condition]
        lines.append(f"| {condition} | {metric['count']} | {metric['rouge_l_mean']:.6f} | {metric['sbert_mean']:.6f} | {size['chars_mean']:.1f} | {size['estimated_tokens_mean']:.1f} |")
    lines.extend(["", "## Per task", "", "| Task | Condition | n | ROUGE-L | SBERT |", "|---|---|---:|---:|---:|"])
    for task, conditions in summary["by_task"].items():
        for condition in CONDITIONS:
            value = conditions[condition]
            lines.append(f"| {task} | {condition} | {value['count']} | {value['rouge_l_mean']:.6f} | {value['sbert_mean']:.6f} |")
    lines.extend(["", "## Pairwise deltas", "", "| Pair | Metric | Mean delta | Median delta | Better | Worse | Same |", "|---|---|---:|---:|---:|---:|---:|"])
    for pair, metrics in summary["pairwise"].items():
        for metric, value in metrics.items():
            lines.append(f"| {pair} | {metric} | {value['mean_delta']:.6f} | {value['median_delta']:.6f} | {value['improved']} | {value['degraded']} | {value['unchanged']} |")
    lines.extend(["", "The benchmark is evaluation-only. No checkpoint, prompt, or hyperparameter is selected from these scores.", ""])
    return "\n".join(lines)
