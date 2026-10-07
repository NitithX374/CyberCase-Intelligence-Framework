import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


LABELS = ["not attributable", "attributable"]
ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def verify(run):
    manifest = json.loads((run / "run_manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    selection = json.loads((run / "selection.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or digest(run / "summary.json") != manifest["summary_sha256"]:
        raise ValueError("Run is incomplete or summary hash changed")
    for filename, expected in manifest["source_sha256"].items():
        if digest(run / manifest["source_snapshot"] / filename) != expected:
            raise ValueError(f"Execution source changed: {filename}")
    scores = {}
    for split in ("dev", "test", "test_ood"):
        data = manifest["dataset"]["files"][split]
        original_path = ROOT / "data" / data["filename"]
        score_path = run / f"scores_{split}.jsonl"
        if digest(original_path) != data["sha256"] or digest(score_path) != summary["score_sha256"][split]:
            raise ValueError(f"Input/score hash changed: {split}")
        original = jsonl(original_path)
        scored = jsonl(score_path)
        if len(scored) != data["rows"] or len(original) != len(scored):
            raise ValueError(f"Missing/extra scored rows: {split}")
        for index, (raw, row) in enumerate(zip(original, scored, strict=True)):
            if row["row_index"] != index or row["split"] != split:
                raise ValueError(f"Score ordering mismatch: {split}:{index}")
            for field in ("id", "claim", "references", "src_dataset"):
                if raw[field] != row[field]:
                    raise ValueError(f"Scored input differs: {split}:{index}:{field}")
            if row["gold"] != raw["attribution_label"]:
                raise ValueError("Gold label changed")
            logits = np.asarray(row["logits"], dtype=np.float64)
            probabilities = np.exp(logits - logits.max())
            probabilities /= probabilities.sum()
            if not np.allclose(probabilities, row["probabilities"], atol=1e-6):
                raise ValueError("Probabilities disagree with raw logits")
            entailment = manifest["model"]["entailment_index"]
            if row["p_entailment"] != row["probabilities"][entailment]:
                raise ValueError("Entailment label mapping changed")
        threshold = selection["threshold"]
        gold = [row["gold"] for row in scored]
        predicted = ["attributable" if row["p_entailment"] >= threshold else "not attributable" for row in scored]
        expected = summary["results"][split]["pooled"]
        if confusion_matrix(gold, predicted, labels=LABELS).tolist() != expected["confusion_matrix"]:
            raise ValueError("Confusion counts disagree")
        if not np.isclose(f1_score(gold, predicted, labels=LABELS, average="macro"), expected["macro_f1"], atol=1e-12):
            raise ValueError("Macro-F1 disagrees")
        if not np.isclose(accuracy_score(gold, predicted), expected["accuracy"], atol=1e-12):
            raise ValueError("Accuracy disagrees")
        independently_scored = classification_report(gold, predicted, labels=LABELS, output_dict=True, zero_division=0)
        for label in LABELS:
            for metric in ("precision", "recall", "f1-score", "support"):
                if not np.isclose(independently_scored[label][metric], expected["per_class"][label][metric], atol=1e-12):
                    raise ValueError("Per-class metrics disagree")
        source_scores = []
        for source, result in summary["results"][split]["source_subsets"].items():
            indices = [i for i, row in enumerate(scored) if row["src_dataset"] == source]
            value = f1_score([gold[i] for i in indices], [predicted[i] for i in indices], labels=LABELS, average="macro")
            if not np.isclose(value, result["macro_f1"], atol=1e-12):
                raise ValueError("Source-subset Macro-F1 disagrees")
            source_scores.append(value)
        if not np.isclose(np.mean(source_scores), summary["results"][split]["mean_source_macro_f1"], atol=1e-12):
            raise ValueError("Paper-style source average disagrees")
        scores[split] = scored
    candidates = []
    sources = sorted({row["src_dataset"] for row in scores["dev"]})
    for value in range(1, 100):
        threshold = value / 100
        per_source = []
        for source in sources:
            rows = [row for row in scores["dev"] if row["src_dataset"] == source]
            predicted = ["attributable" if row["p_entailment"] >= threshold else "not attributable" for row in rows]
            per_source.append(f1_score([row["gold"] for row in rows], predicted, labels=LABELS, average="macro"))
        candidates.append((threshold, float(np.mean(per_source))))
    chosen = min(candidates, key=lambda item: (-item[1], abs(item[0] - 0.5), item[0]))
    if chosen[0] != selection["threshold"] or digest(run / "scores_dev.jsonl") != selection["dev_scores_sha256"]:
        raise ValueError("English-dev threshold selection disagrees")
    receipt = {"status": "passed", "checked_units": {split: len(rows) for split, rows in scores.items()},
               "threshold": chosen[0], "summary_sha256": digest(run / "summary.json"),
        "checks": "Frozen source/input/score hashes; every original row; logits/probability and entailment mapping; independent sklearn confusion/P/R/F1/Accuracy and source averages; EN-dev threshold grid/tie rule"}
    (run / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    verify(parser.parse_args().run)
