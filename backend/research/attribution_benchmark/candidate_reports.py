import json


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_report(output, summary):
    model = summary["model"]
    timing = summary["timing"]
    lines = [
        "# AttributionBench candidate evaluation", "",
        f"Model: `{model['model']}` @ `{model['revision']}`.",
        f"Completed {summary['finished_at']}; original English dev/ID/OOD, no fine-tuning or translation.",
        f"Device `{model['device']}`, precision `{model['dtype']}`, batch {model['batch_size']}; parameters {model['parameters']:,}.", "",
        "## Protocol", "",
        "Original-order cited references are concatenated with two newlines. The original claim is kept intact.",
        "Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.",
        f"Adapter: `{model['adapter']}`. Class scores: `{model['class_score_kind']}`.",
        f"Class order: `{model['labels']}`; attributable/support index {model['supported_index']}.",
        f"Primary threshold {summary['selection']['threshold']:.2f}, selected solely on 1,198 English dev rows before test inference.",
        "Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.",
        "Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.", "",
    ]
    if model["adapter"] == "sequence_label_likelihood":
        lines += [
            "AttrScore uses the author's attribution instruction and full claim followed by cited references.",
            "Each of Attributable, Contradictory and Extrapolatory is scored with teacher forcing, including EOS.",
            "Complete label token log probabilities are summed without length normalization, then normalized across the three label sequences.",
            "The resulting supported score is relative among these labels; it is not a calibrated probability or greedy free-text generation.",
            "Prompt tokens consume part of the 512-token budget, and evidence loss is recorded. Binary not attributable combines Contradictory/Extrapolatory.", "",
        ]
    lines += [
        "## Primary results", "",
        "All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.", "",
        "| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for split in ("test", "test_ood"):
        group = summary["results"][split]
        pooled = group["pooled"]
        ci = group["bootstrap"]["mean_source_macro_f1_ci95"]
        lines.append(
            f"| {split} | {pooled['units']} | {100 * group['mean_source_macro_f1']:.2f} | "
            f"[{100 * ci[0]:.2f}, {100 * ci[1]:.2f}] | {100 * pooled['macro_f1']:.2f} | "
            f"{100 * pooled['accuracy']:.2f} | {100 * pooled['false_acceptance']['rate']:.2f} | "
            f"{100 * pooled['false_warning']['rate']:.2f} | {pooled['truncated_units']} |"
        )
    lines += ["", "False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.",
              "", "## Per-source results", "",
              "| Split | Source | Units | Macro-F1 | False acceptance | False warning |", "|---|---|---:|---:|---:|---:|"]
    for split in ("test", "test_ood"):
        for source, cell in summary["results"][split]["source_subsets"].items():
            lines.append(f"| {split} | {source} | {cell['units']} | {100 * cell['macro_f1']:.2f} | "
                         f"{100 * cell['false_acceptance']['rate']:.2f} | {100 * cell['false_warning']['rate']:.2f} |")
    lines += ["", "## Class metrics", "", "| Split | Gold class | Precision | Recall | F1 | Support |",
              "|---|---|---:|---:|---:|---:|"]
    for split in ("test", "test_ood"):
        pooled = summary["results"][split]["pooled"]
        for label, cell in pooled["per_class"].items():
            lines.append(f"| {split} | {label} | {100 * cell['precision']:.2f} | {100 * cell['recall']:.2f} | "
                         f"{100 * cell['f1-score']:.2f} | {int(cell['support'])} |")
        lines += ["", f"{split} confusion [not attributable, attributable]: `{pooled['confusion_matrix']}`.",
                  f"{split} not-attributable AUROC {pooled['auroc_not_attributable']:.4f}; AP {pooled['ap_not_attributable']:.4f}."]
    lines += ["", "## Execution", "",
              f"Valid scored rows {timing['completed_units']}/{timing['attempted_units']}; failures {timing['failures']}.",
              f"Runner wall time {timing['runner_wall_seconds']:.2f}s; model loading {timing['model_load_seconds']:.2f}s.",
              f"Batch p50/p95 seconds `{timing['batch_latency_p50_p95_seconds']}`; batch size {model['batch_size']}.",
              f"CUDA peak allocated/reserved bytes `{summary['resources']}`; excludes other GPU processes and driver overhead.",
              "First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.",
              "Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.",
              "Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.",
              "These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.",
              "", "## Reproduction", "", "```powershell", summary["command"], "```", ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
