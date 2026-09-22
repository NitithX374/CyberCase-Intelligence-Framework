from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .analysis import EvaluationResult, error_rows
from .constants import ERROR_COLUMNS, PREDICTION_COLUMNS
from .conversion import BinarySample, ConversionResult


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _sample_payload(sample: BinarySample) -> dict[str, Any]:
    return {
        "text": sample.text,
        "gold_label": sample.gold_label,
        "document": sample.document,
        "has_attack_technique": sample.has_attack_technique,
        "source_split": sample.source_split,
    }


def _annotation_quality_caveats(samples: list[BinarySample]) -> dict[str, int]:
    return {
        "shorter_than_or_equal_to_10_characters": sum(
            len(sample.text) <= 10 for sample in samples
        ),
        "no_ascii_alphanumeric_character": sum(
            not re.search(r"[A-Za-z0-9]", sample.text) for sample in samples
        ),
        "markdown_or_table_like": sum(
            bool(re.match(r"^(?:#{1,6}\s|\*{1,3}\s|\|)", sample.text))
            for sample in samples
        ),
        "image_markdown_like": sum(sample.text.startswith("![") for sample in samples),
    }


def dataset_statistics(
    conversion: ConversionResult,
    validation: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    import random

    samples = list(conversion.samples)
    randomizer = random.Random(seed)
    positives = [sample for sample in samples if sample.gold_label == 1]
    negatives = [sample for sample in samples if sample.gold_label == 0]
    shortest = sorted(samples, key=lambda sample: (len(sample.text), sample.document, sample.text))[:20]
    longest = sorted(samples, key=lambda sample: (-len(sample.text), sample.document, sample.text))[:20]
    quality = _annotation_quality_caveats(samples)
    return {
        **conversion.statistics,
        "validation": validation,
        "annotation_level_quality_caveats": quality,
        "random_seed": seed,
        "random_positive_examples": [
            _sample_payload(sample) for sample in randomizer.sample(positives, min(20, len(positives)))
        ],
        "random_negative_examples": [
            _sample_payload(sample) for sample in randomizer.sample(negatives, min(20, len(negatives)))
        ],
        "shortest_examples": [_sample_payload(sample) for sample in shortest],
        "longest_examples": [_sample_payload(sample) for sample in longest],
    }


def _metric_row(name: str, result: EvaluationResult) -> dict[str, Any]:
    metrics = result.metrics
    return {
        "dataset": name,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "macro_f1": metrics["macro_f1"],
        "false_skip_rate": metrics["false_skip_rate"],
    }


def _format_percent(value: float) -> str:
    return f"{value:.2%}"


def _top_error_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "None"
    return "\n".join(
        f"- `{row['p_relevant']:.6f}` `{row['document']}` — {row['text']}" for row in rows[:20]
    )


def write_readme(
    path: Path,
    classifier: dict[str, Any],
    conversion: ConversionResult,
    validation: dict[str, Any],
    ladder: EvaluationResult,
    annoctr: EvaluationResult,
    source_caveat: str,
) -> None:
    ladder_metrics = ladder.metrics
    anno_metrics = annoctr.metrics
    ladder_tokens = ladder.token_statistics
    anno_tokens = annoctr.token_statistics
    fn = error_rows(annoctr, 1, 0)
    fp = error_rows(annoctr, 0, 1)
    quality = _annotation_quality_caveats(list(conversion.samples))
    lines = [
        "# AnnoCTR External Validation",
        "",
        "## Research question",
        "",
        "Does an ATT&CK relevance classifier trained on LADDER generalize to an independently annotated CTI corpus?",
        "",
        "## Configuration",
        "",
        f"- Checkpoint: `{classifier['checkpoint']}`",
        f"- Checkpoint base: `{classifier['base']}`",
        f"- Tokenizer: `{classifier['tokenizer']}`",
        f"- Relevant output index: `{classifier['positive_index']}`",
        f"- Relevant label: `{classifier['relevant_label']}`",
        f"- Irrelevant label: `{classifier['irrelevant_label']}`",
        f"- max_length: `{classifier['max_length']}`",
        f"- Evaluation threshold: `{classifier['evaluation_threshold']}`",
        f"- Checkpoint operational threshold, recorded only: `{classifier['checkpoint_threshold']}`",
        "- Adaptation: none; the checkpoint was not retrained or tuned on AnnoCTR.",
        "",
        "## AnnoCTR conversion",
        "",
        f"- Dataset root: `{conversion.statistics['source_file']}`",
        "- Official source split: `test`",
        "- Native sentence-level source: none was found in the checkout.",
        "- Fallback source: `AnnoCTR/linking_mitre_only/test_w_neg.jsonl`",
        "- Sentence identity: `(document, normalized(_context_left + mention + _context_right))`; synthetic No Annotation rows use their complete mention.",
        "- Positive rule: at least one valid `attack.mitre.org/techniques/` link in the aggregated sentence group.",
        "- Negative rule: no such link, including explicit `label_link=No Annotation` rows.",
        f"- Samples: `{conversion.statistics['unique_sentence_samples']}` ({conversion.statistics['positive_samples']} positive, {conversion.statistics['negative_samples']} negative)",
        f"- Documents represented: `{conversion.statistics['unique_documents']}` of `{validation['official_split_document_count']}` official test documents",
        "",
        "## Results",
        "",
        "| Dataset | Accuracy | Precision | Recall | F1 | Macro-F1 | False Skip Rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| LADDER | {_format_percent(ladder_metrics['accuracy'])} | {_format_percent(ladder_metrics['precision'])} | {_format_percent(ladder_metrics['recall'])} | {_format_percent(ladder_metrics['f1'])} | {_format_percent(ladder_metrics['macro_f1'])} | {_format_percent(ladder_metrics['false_skip_rate'])} |",
        f"| AnnoCTR | {_format_percent(anno_metrics['accuracy'])} | {_format_percent(anno_metrics['precision'])} | {_format_percent(anno_metrics['recall'])} | {_format_percent(anno_metrics['f1'])} | {_format_percent(anno_metrics['macro_f1'])} | {_format_percent(anno_metrics['false_skip_rate'])} |",
        "",
        f"AnnoCTR ATT&CK Relevant Recall: **{_format_percent(anno_metrics['attack_relevant_recall'])}**",
        f"AnnoCTR False Invocation Rate: **{_format_percent(anno_metrics['false_invocation_rate'])}**",
        "",
        "## Top false negatives",
        "",
        _top_error_lines(fn),
        "",
        "## Top false positives",
        "",
        _top_error_lines(fp),
        "",
        "## Token-length comparison",
        "",
        f"- LADDER: min `{ladder_tokens['min']}`, mean `{ladder_tokens['mean']}`, median `{ladder_tokens['median']}`, p90 `{ladder_tokens['p90']}`, p95 `{ladder_tokens['p95']}`, max `{ladder_tokens['max']}`, over limit `{ladder_tokens['exceeding_configured_max_length_count']}` ({_format_percent(ladder_tokens['exceeding_configured_max_length_percentage'])})",
        f"- AnnoCTR: min `{anno_tokens['min']}`, mean `{anno_tokens['mean']}`, median `{anno_tokens['median']}`, p90 `{anno_tokens['p90']}`, p95 `{anno_tokens['p95']}`, max `{anno_tokens['max']}`, over limit `{anno_tokens['exceeding_configured_max_length_count']}` ({_format_percent(anno_tokens['exceeding_configured_max_length_percentage'])})",
        "- The configured max length was not changed after inspecting AnnoCTR.",
        "",
        "## Caveats",
        "",
        f"- {source_caveat}",
        "- AnnoCTR is a mention-level/linking corpus rather than a native sentence-classification benchmark.",
        "- The fallback contains explicit synthetic negative rows whose `entity_type` can be `TECHNIQUE` while `label_link` is `No Annotation`; the conversion uses that explicit marker and validates unexpected variants instead of treating entity type alone as ground truth.",
        "- Error-pattern fields are deterministic diagnostics, not LLM judgments.",
        f"- Annotation-level quality audit: `{quality['shorter_than_or_equal_to_10_characters']}` samples are at most 10 characters, `{quality['no_ascii_alphanumeric_character']}` have no ASCII alphanumeric character, `{quality['markdown_or_table_like']}` are markdown/table-like, and `{quality['image_markdown_like']}` are image-markdown-like.",
        "- Conclusion: this is defensible as a sentence-level presence-of-AnnoCTR-technique-link benchmark, but it is not equivalent to a native explicit/implicit/no-technique behavioral sentence-label task. The result must be reported with that narrower interpretation.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    output_root: Path,
    conversion: ConversionResult,
    validation: dict[str, Any],
    classifier: dict[str, Any],
    ladder: EvaluationResult,
    annoctr: EvaluationResult,
    seed: int,
    source_caveat: str,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    anno_predictions = [
        {column: record[column] for column in PREDICTION_COLUMNS}
        for record in annoctr.records
    ]
    false_negatives = error_rows(annoctr, 1, 0)
    false_positives = error_rows(annoctr, 0, 1)
    _write_csv(output_root / "annoctr_test_binary.csv", (
        {
            "text": sample.text,
            "gold_label": sample.gold_label,
            "document": sample.document,
            "has_attack_technique": sample.has_attack_technique,
            "source_split": sample.source_split,
        }
        for sample in conversion.samples
    ), ["text", "gold_label", "document", "has_attack_technique", "source_split"])
    _write_csv(output_root / "annoctr_test_predictions.csv", anno_predictions, PREDICTION_COLUMNS)
    _write_csv(output_root / "annoctr_false_negatives.csv", false_negatives, ERROR_COLUMNS)
    _write_csv(output_root / "annoctr_false_positives.csv", false_positives, ERROR_COLUMNS)
    stats = dataset_statistics(conversion, validation, seed)
    _write_json(
        output_root / "dataset_statistics.json",
        stats,
    )
    _write_json(
        output_root / "token_length_statistics.json",
        {"LADDER": ladder.token_statistics, "AnnoCTR": annoctr.token_statistics},
    )
    _write_json(
        output_root / "metrics.json",
        {
            "classifier": classifier,
            "datasets": {
                "LADDER": ladder.metrics,
                "AnnoCTR": annoctr.metrics,
            },
            "comparison": [_metric_row("LADDER", ladder), _metric_row("AnnoCTR", annoctr)],
            "annoctr_false_negative_count": len(false_negatives),
            "annoctr_false_positive_count": len(false_positives),
            "top_20_false_negatives": false_negatives[:20],
            "top_20_false_positives": false_positives[:20],
        },
    )
    write_readme(
        output_root / "README.md",
        classifier,
        conversion,
        validation,
        ladder,
        annoctr,
        source_caveat,
    )
