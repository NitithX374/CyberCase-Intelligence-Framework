import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, average_precision_score, classification_report, confusion_matrix, f1_score, roc_auc_score
from transformers import AutoTokenizer

from candidate_adapters import prepare_inputs
from candidate_models import MODELS
from data import LABELS, ROOT, cluster_key, sha256


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def close(actual, expected, message, tolerance=1e-12):
    if not np.allclose(actual, expected, atol=tolerance, rtol=0):
        raise ValueError(message)


def check_metrics(rows, predictions, expected):
    gold = [row["gold"] for row in rows]
    matrix = confusion_matrix(gold, predictions, labels=list(LABELS)).tolist()
    if matrix != expected["confusion_matrix"]:
        raise ValueError("Confusion counts disagree")
    close(f1_score(gold, predictions, labels=list(LABELS), average="macro"), expected["macro_f1"], "Macro-F1 disagrees")
    close(accuracy_score(gold, predictions), expected["accuracy"], "Accuracy disagrees")
    report = classification_report(gold, predictions, labels=list(LABELS), output_dict=True, zero_division=0)
    for label in LABELS:
        for metric in ("precision", "recall", "f1-score", "support"):
            close(report[label][metric], expected["per_class"][label][metric], "Per-class metrics disagree")
    close(matrix[0][1] / sum(matrix[0]), expected["false_acceptance"]["rate"], "False acceptance disagrees")
    close(matrix[1][0] / sum(matrix[1]), expected["false_warning"]["rate"], "False warning disagrees")
    scores = [1 - row["p_supported"] for row in rows]
    positive = [label == LABELS[0] for label in gold]
    close(roc_auc_score(positive, scores), expected["auroc_not_attributable"], "AUROC disagrees")
    close(average_precision_score(positive, scores), expected["ap_not_attributable"], "AP disagrees")
    if sum(row["lengths"]["truncated"] for row in rows) != expected["truncated_units"]:
        raise ValueError("Truncation count disagrees")


def verify(run):
    manifest = json.loads((run / "run_manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    selection = json.loads((run / "selection.json").read_text(encoding="utf-8"))
    if manifest["schema_version"] != 2 or manifest["status"] != "complete":
        raise ValueError("Incomplete or incompatible run")
    if sha256(run / "summary.json") != manifest["summary_sha256"]:
        raise ValueError("Summary hash changed")
    for filename, expected in manifest["source_sha256"].items():
        if sha256(run / manifest["source_snapshot"] / filename) != expected:
            raise ValueError(f"Frozen execution source changed: {filename}")
    spec = MODELS[manifest["model"]["key"]]
    if manifest["model"]["revision"] != spec.revision or manifest["model"]["supported_index"] != spec.supported_index:
        raise ValueError("Pinned model/label mapping changed")
    tokenizer = AutoTokenizer.from_pretrained(spec.model, revision=spec.revision, local_files_only=True)
    scored_splits = {}
    for split in ("dev", "test", "test_ood"):
        data = manifest["dataset"]["files"][split]
        original_path = ROOT / "data" / data["filename"]
        score_path = run / f"scores_{split}.jsonl"
        if sha256(original_path) != data["sha256"] or sha256(score_path) != summary["score_sha256"][split]:
            raise ValueError(f"Input/score hash changed: {split}")
        original, scored = read_jsonl(original_path), read_jsonl(score_path)
        if len(scored) != data["rows"] or len(original) != len(scored):
            raise ValueError("Missing/extra rows")
        inputs, lengths = prepare_inputs(tokenizer, spec, original)
        for index, (raw, row) in enumerate(zip(original, scored, strict=True)):
            if row["row_index"] != index or row["split"] != split or row["cluster"] != cluster_key(raw):
                raise ValueError("Row ordering/cluster changed")
            for field in ("id", "claim", "references", "src_dataset"):
                if raw[field] != row[field]:
                    raise ValueError(f"Original input changed: {split}:{index}:{field}")
            if row["gold"] != raw["attribution_label"]:
                raise ValueError("Gold changed")
            if row["input_ids"] != inputs[index]["input_ids"] or row["lengths"] != lengths[index]:
                raise ValueError("Input tokenization/length accounting changed")
            values = np.asarray(row["class_scores"], dtype=np.float64)
            probabilities = np.exp(values - values.max())
            probabilities /= probabilities.sum()
            close(probabilities, row["class_probabilities"], "Class score probabilities disagree", 1e-6)
            close(row["p_supported"], row["class_probabilities"][spec.supported_index], "Support mapping disagrees")
            if row["class_argmax"] != spec.labels[int(values.argmax())]:
                raise ValueError("Class argmax mapping changed")
            if spec.kind == "sequence_label_likelihood":
                tokens = row["score_details"]["label_token_log_probabilities"]
                if [len(items) for items in tokens] != [len(items) for items in manifest["model"]["label_token_ids"]]:
                    raise ValueError("Label sequence lengths disagree")
                close([sum(items) for items in tokens], values, "Sequence log probabilities disagree", 1e-4)
        threshold = selection["threshold"]
        predicted = ["attributable" if row["p_supported"] >= threshold else "not attributable" for row in scored]
        check_metrics(scored, predicted, summary["results"][split]["pooled"])
        source_values = []
        for source, cell in summary["results"][split]["source_subsets"].items():
            indices = [index for index, row in enumerate(scored) if row["src_dataset"] == source]
            selected = [scored[index] for index in indices]
            selected_predictions = [predicted[index] for index in indices]
            check_metrics(selected, selected_predictions, cell)
            source_values.append(f1_score([row["gold"] for row in selected], selected_predictions, labels=list(LABELS), average="macro"))
        close(np.mean(source_values), summary["results"][split]["mean_source_macro_f1"], "Source mean disagrees")
        if split != "dev":
            native = ["attributable" if row["class_argmax"] == spec.labels[spec.supported_index] else "not attributable" for row in scored]
            check_metrics(scored, native, summary["argmax_reference"][split]["pooled"])
        scored_splits[split] = scored
    candidates = []
    dev = scored_splits["dev"]
    for value in range(1, 100):
        threshold = value / 100
        per_source = []
        for source in sorted({row["src_dataset"] for row in dev}):
            selected = [row for row in dev if row["src_dataset"] == source]
            predicted = ["attributable" if row["p_supported"] >= threshold else "not attributable" for row in selected]
            per_source.append(f1_score([row["gold"] for row in selected], predicted, labels=list(LABELS), average="macro"))
        candidates.append((threshold, float(np.mean(per_source))))
    chosen = min(candidates, key=lambda item: (-item[1], abs(item[0] - 0.5), item[0]))
    if chosen[0] != selection["threshold"] or sha256(run / "scores_dev.jsonl") != selection["dev_scores_sha256"]:
        raise ValueError("English-dev threshold selection disagrees")
    close(chosen[1], selection["dev_mean_source_macro_f1"], "Selected dev score disagrees")
    if datetime.fromisoformat(selection["selected_at"]).timestamp() > (run / "scores_test.jsonl").stat().st_mtime:
        raise ValueError("Threshold was not frozen before the test output completed")
    receipt = {
        "status": "passed", "at": datetime.now(timezone.utc).isoformat(), "model": spec.key,
        "checked_units": {split: len(rows) for split, rows in scored_splits.items()}, "threshold": chosen[0],
        "summary_sha256": sha256(run / "summary.json"),
        "checks": "Frozen source/data/score hashes; all original inputs/gold; complete claim/prompt/evidence tokenization; class probabilities/support and sequence-label mapping; independent sklearn confusion/P/R/F1/Accuracy/AUROC/AP/source averages; EN-dev grid/tie rule",
    }
    (run / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt), flush=True)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    verify(parser.parse_args().run)
