from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .cache import write_json


def _metric(summary: dict[str, Any], block: str, field: str) -> float:
    return float(summary["overall"][block][field])


def _comparison_rows(e1: dict[str, Any], e2: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    values = [
        ("Entity Precision", "entity", "precision"),
        ("Entity Recall", "entity", "recall"),
        ("Entity F1", "entity", "f1"),
        ("Endpoint Edge Precision", "endpoint_edge", "precision"),
        ("Endpoint Edge Recall", "endpoint_edge", "recall"),
        ("Endpoint Edge F1", "endpoint_edge", "f1"),
        ("Relation Precision", "triplet", "precision"),
        ("Relation Recall", "triplet", "recall"),
        ("Relation F1", "triplet", "f1"),
    ]
    rows = []
    for label, block, field in values:
        left = _metric(e1, block, field)
        right = _metric(e2, block, field)
        rows.append((label, f"{left:.4f}", f"{right:.4f}", f"{right - left:+.4f}"))
    return rows


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _category_table(condition: str, rows: list[dict[str, Any]], key: str) -> str:
    table_rows = []
    for row in rows:
        name = str(row[key])
        table_rows.append([name, str(row["support"]), str(row["tp"]), str(row["fp"]), str(row["fn"]), f"{float(row['precision']):.4f}", f"{float(row['recall']):.4f}", f"{float(row['f1']):.4f}"])
    title = "Entity type" if key == "type" else "Relation type"
    return f"### {condition} by {title.lower()}\n\n" + _markdown_table([title, "Support", "TP", "FP", "FN", "Precision", "Recall", "F1"], table_rows)


def _summary_payload(manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]) -> dict[str, Any]:
    return {
        "experiment_version": config["experiment_version"],
        "dataset": manifest,
        "config": config,
        "conditions": {"E1": e1, "E2": e2},
        "comparison": {"rows": [{"metric": row[0], "production": row[1], "gliner2": row[2], "delta_e2_minus_e1": row[3]} for row in _comparison_rows(e1, e2)]},
        "error_analysis": errors,
        "limitations": [
            "CTINexus test JSON does not include a language field; the fixed project test split is reported as English based on its narratives.",
            "The existing evaluator provides exact normalized surface matching only; no relaxed overlap metric is available in the reused protocol.",
            "Production entity types are open strings, so typed E1 metrics exclude unmappable production types and report the exclusion count.",
            "CTINexus relations are free-text phrases rather than a closed relation ontology; GLiNER2 extracts a generic source-grounded relation span and receives no test-case gold relation values.",
            "The production client exposes token usage but not request cost, so approximate cost is unavailable.",
        ],
    }


def _markdown(manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]) -> str:
    comparison = [[label, left, right, delta] for label, left, right, delta in _comparison_rows(e1, e2)]
    lines = [
        "# CTINexus extraction-only benchmark",
        "",
        "This report compares direct extraction quality only. No downstream analysis LLM, SEvenLLM, ROUGE-L, SBERT, RAG, MITRE mapping, fine-tuning, or manual repair was used.",
        "",
        "## Dataset",
        "",
        f"- Split: `{manifest['split']}`",
        f"- Cases: {manifest['documents']}",
        f"- Language: {manifest['language']} (the source JSON has no language field)",
        f"- Gold entities: {manifest['gold_entities']}",
        f"- Gold explicit relations: {manifest['gold_relations']}",
        f"- Dataset directory: `{manifest['dataset_dir']}`",
        "",
        "The exact case IDs and source hashes are in `dataset_manifest.json`.",
        "",
        "## Primary comparison",
        "",
        _markdown_table(["Metric", "Production LLM", "GLiNER2", "Delta (E2 - E1)"], comparison),
        "",
        "Relation metrics are the existing evaluator's exact normalized full-triplet metrics. Endpoint metrics ignore the relation phrase but preserve direction.",
        "",
        "## Conditions and mapping",
        "",
        f"- E1 model: `{config['production']['model']}`; entrypoint: `{config['production']['entrypoint']}`; prompt: `{config['production']['prompt_version']}`; schema: `{config['production']['schema_version']}`.",
        f"- E2 checkpoint: `{config['gliner']['model']}`; device: `{config['gliner']['device']}`; threshold: `{config['gliner']['threshold']}`.",
        "- E1 mapping: validated production `CaseState.entities` become entity text/type and `CaseState.relationships` become subject/predicate/object; production-only facts, evidence, impacts, and timeline are not scored.",
        "- E2 mapping: GLiNER2 uses the fixed CTINexus entity-type vocabulary plus a generic `subject/relation/object` span schema. Every accepted value must satisfy the exact source-offset check before entering the common projection.",
        "",
        "## Coverage and runtime",
        "",
        _markdown_table(
            ["Condition", "Success", "Failures", "Validation failures", "Empty outputs", "Mean entities/case", "Mean relations/case"],
            [
                [condition, str(summary["coverage"]["successful_extractions"]), str(summary["coverage"]["extraction_failures"]), str(summary["coverage"]["validation_failures"]), str(summary["coverage"]["empty_output_cases"]), str(summary["coverage"]["mean_predicted_entities_per_case"]), str(summary["coverage"]["mean_predicted_relations_per_case"])]
                for condition, summary in (("E1", e1), ("E2", e2))
            ],
        ),
        "",
        f"- E1 latency/tokens/calls: `{json.dumps(e1['latency_and_cost'], ensure_ascii=False)}`",
        f"- E2 latency/load/device/memory: `{json.dumps(e2['latency_and_cost'], ensure_ascii=False)}`",
        f"- E2 confidence: `{json.dumps(e2['coverage'].get('confidence', e2.get('confidence', {})), ensure_ascii=False)}`",
        "",
        "## Per-category metrics",
        "",
        _category_table("E1", e1["entity_type_metrics"], "type"),
        "",
        _category_table("E2", e2["entity_type_metrics"], "type"),
        "",
        _category_table("E1", e1["relation_type_metrics"], "relation"),
        "",
        _category_table("E2", e2["relation_type_metrics"], "relation"),
        "",
        "## Type diagnostics",
        "",
        f"- E1: `{json.dumps(e1['entity_type_diagnostics'], ensure_ascii=False)}`",
        f"- E2: `{json.dumps(e2['entity_type_diagnostics'], ensure_ascii=False)}`",
        "",
        "## Representative errors",
        "",
        "The examples below are selected deterministically from the first cases in sorted case-ID order; they are not a cherry-picked success set.",
        "",
    ]
    for category, examples in errors.items():
        lines.append(f"### {category}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(examples, indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    lines.extend([
        "## Reproduction",
        "",
        "```powershell",
        "$env:SSLKEYLOGFILE = ''",
        f"doppler run -- env_mitre\\Scripts\\python.exe -m experiments.ctinexus_extraction_benchmark --dataset-dir \"{manifest['dataset_dir']}\" --output-dir \"{config['output_dir']}\"",
        "```",
        "",
        "Rerunning the same output directory resumes only exact-condition cache records. Checkpoint files contain canonical per-case predictions and are flushed after each record.",
    ])
    return "\n".join(lines) + "\n"


def write_report(output_dir: Path, manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], errors: dict[str, Any]) -> dict[str, Any]:
    payload = _summary_payload(manifest, config, e1, e2, errors)
    write_json(output_dir / "evaluation_summary.json", payload)
    write_json(output_dir / "dataset_manifest.json", manifest)
    write_json(output_dir / "run_config.json", config)
    (output_dir / "document_evaluations_E1.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in e1_rows) + "\n", encoding="utf-8")
    (output_dir / "document_evaluations_E2.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in e2_rows) + "\n", encoding="utf-8")
    (output_dir / "report.md").write_text(_markdown(manifest, config, e1, e2, errors), encoding="utf-8")
    return payload
