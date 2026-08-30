from __future__ import annotations

import json
from collections import defaultdict
from statistics import mean
from typing import Any


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * fraction, 6)


def _metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    rouge = [float(record[condition]["rouge_l"]) for record in records]
    sbert = [float(record[condition]["sbert"]) for record in records]
    return {
        "count": len(records),
        "rouge_l_mean": round(mean(rouge), 6) if rouge else 0.0,
        "sbert_mean": round(mean(sbert), 6) if sbert else 0.0,
    }


def _group_metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["category"])].append(record)
    return {category: _metric_stats(grouped[category], condition) for category in sorted(grouped)}


def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    raw_chars = [float(record["raw_context_chars"]) for record in records]
    refined_chars = [float(record["refined_context_chars"]) for record in records]
    retention = [float(record["char_retention_ratio"]) for record in records]
    compression = [float(record["char_compression_ratio"]) for record in records]
    spans = [record["protected_span_diagnostics"] for record in records]
    deltas = [
        {
            "sample_id": record["sample_id"],
            "category": record["category"],
            "rouge_l_delta": round(record["B1"]["rouge_l"] - record["B0"]["rouge_l"], 6),
            "sbert_delta": round(record["B1"]["sbert"] - record["B0"]["sbert"], 6),
        }
        for record in records
    ]
    return {
        "experiment": "SEvenLLM context refinement paired ablation",
        "config": config,
        "sample_count": len(records),
        "conditions": {
            "B0_raw": _metric_stats(records, "B0"),
            "B1_refined": _metric_stats(records, "B1"),
            "B0_by_category": _group_metric_stats(records, "B0"),
            "B1_by_category": _group_metric_stats(records, "B1"),
        },
        "compression": {
            "raw_chars": {"p50": _percentile(raw_chars, 0.50), "p95": _percentile(raw_chars, 0.95), "max": max(raw_chars, default=0)},
            "refined_chars": {"p50": _percentile(refined_chars, 0.50), "p95": _percentile(refined_chars, 0.95), "max": max(refined_chars, default=0)},
            "char_retention_ratio": {"mean": round(mean(retention), 6) if retention else 0.0, "p50": _percentile(retention, 0.50), "p95": _percentile(retention, 0.95)},
            "char_compression_ratio": {"mean": round(mean(compression), 6) if compression else 0.0, "p50": _percentile(compression, 0.50), "p95": _percentile(compression, 0.95)},
        },
        "protected_spans": {
            "total": sum(int(item["total"]) for item in spans),
            "preserved": sum(int(item["preserved"]) for item in spans),
            "missing": sum(int(item["missing"]) for item in spans),
            "by_type": _sum_span_types(spans, "by_type"),
            "missing_by_type": _sum_span_types(spans, "missing_by_type"),
        },
        "paired_deltas": {
            "rouge_l_mean": round(mean(item["rouge_l_delta"] for item in deltas), 6) if deltas else 0.0,
            "sbert_mean": round(mean(item["sbert_delta"] for item in deltas), 6) if deltas else 0.0,
            "improved": _ranked_examples(deltas, "improved"),
            "unchanged": _ranked_examples(deltas, "unchanged"),
            "degraded": _ranked_examples(deltas, "degraded"),
        },
    }


def _sum_span_types(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    totals: defaultdict[str, int] = defaultdict(int)
    for record in records:
        for name, count in record[field].items():
            totals[name] += int(count)
    return dict(sorted(totals.items()))


def _ranked_examples(deltas: list[dict[str, Any]], group: str) -> list[dict[str, Any]]:
    if group == "improved":
        selected = [item for item in deltas if item["rouge_l_delta"] > 0]
        return sorted(selected, key=lambda item: item["rouge_l_delta"], reverse=True)[:5]
    if group == "degraded":
        selected = [item for item in deltas if item["rouge_l_delta"] < 0]
        return sorted(selected, key=lambda item: item["rouge_l_delta"])[:5]
    selected = [item for item in deltas if item["rouge_l_delta"] == 0]
    return sorted(selected, key=lambda item: item["sample_id"])[:5]


def render_markdown(summary: dict[str, Any]) -> str:
    config = json.dumps(summary["config"], ensure_ascii=False, indent=2, sort_keys=True)
    conditions = summary["conditions"]
    lines = [
        "# SEvenLLM Context Refinement Experiment",
        "",
        f"Paired English generation cases: **{summary['sample_count']}**",
        "",
        "## Conditions and metrics",
        "",
        "| Condition | n | ROUGE-L mean | SBERT mean |",
        "|---|---:|---:|---:|",
        f"| B0 raw | {conditions['B0_raw']['count']} | {conditions['B0_raw']['rouge_l_mean']:.6f} | {conditions['B0_raw']['sbert_mean']:.6f} |",
        f"| B1 refined | {conditions['B1_refined']['count']} | {conditions['B1_refined']['rouge_l_mean']:.6f} | {conditions['B1_refined']['sbert_mean']:.6f} |",
        "",
        "## Per-task metrics",
        "",
        "| Category | B0 ROUGE-L | B1 ROUGE-L | B0 SBERT | B1 SBERT |",
        "|---|---:|---:|---:|---:|",
    ]
    for category in conditions["B0_by_category"]:
        raw = conditions["B0_by_category"][category]
        refined = conditions["B1_by_category"][category]
        lines.append(f"| {category} | {raw['rouge_l_mean']:.6f} | {refined['rouge_l_mean']:.6f} | {raw['sbert_mean']:.6f} | {refined['sbert_mean']:.6f} |")
    compression = summary["compression"]
    lines.extend([
        "",
        "## Compression statistics",
        "",
        f"- Raw context chars p50/p95/max: {compression['raw_chars']['p50']:.1f} / {compression['raw_chars']['p95']:.1f} / {compression['raw_chars']['max']:.0f}",
        f"- Refined context chars p50/p95/max: {compression['refined_chars']['p50']:.1f} / {compression['refined_chars']['p95']:.1f} / {compression['refined_chars']['max']:.0f}",
        f"- Character retention mean/p50/p95: {compression['char_retention_ratio']['mean']:.6f} / {compression['char_retention_ratio']['p50']:.6f} / {compression['char_retention_ratio']['p95']:.6f}",
        f"- Character compression ratio mean/p50/p95: {compression['char_compression_ratio']['mean']:.6f} / {compression['char_compression_ratio']['p50']:.6f} / {compression['char_compression_ratio']['p95']:.6f}",
        "",
        "## Protected cyber spans",
        "",
        f"- Total/preserved/missing: {summary['protected_spans']['total']} / {summary['protected_spans']['preserved']} / {summary['protected_spans']['missing']}",
        f"- Missing by type: `{json.dumps(summary['protected_spans']['missing_by_type'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "## Paired examples",
        "",
        f"- Improved by ROUGE-L: `{json.dumps(summary['paired_deltas']['improved'], ensure_ascii=False)}`",
        f"- Unchanged by ROUGE-L: `{json.dumps(summary['paired_deltas']['unchanged'], ensure_ascii=False)}`",
        f"- Degraded by ROUGE-L: `{json.dumps(summary['paired_deltas']['degraded'], ensure_ascii=False)}`",
        "",
        "## Exact run configuration",
        "",
        "```json",
        config,
        "```",
        "",
        "This report is descriptive. It does not select a checkpoint, tune a prompt, or tune a hyperparameter.",
        "",
    ])
    return "\n".join(lines)

