from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import torch
import sklearn.metrics as skm
import transformers

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "experiments" / "ladder_joint_model" / "outputs" / "b0"
MAX_LENGTH = 316
SEED = 42
SPLIT_SIZES = {"train": 2214, "dev": 568, "test": 662}
REFERENCE = {"accuracy": 0.8580, "precision": 0.8537, "recall": 0.8640, "f1": 0.8589}
CHECKPOINT_REFERENCE = {
    "model": "AutoModelForSequenceClassification / XLMRobertaForSequenceClassification",
    "base": "xlm-roberta-base",
    "positive_index": 1,
    "max_length_inference": 316,
    "dropout": 0.1,
    "training_source_script": "UNCONFIRMED; not present in repository",
}


class TextClassificationDataset(torch.utils.data.Dataset):
    def __init__(self, rows: list[dict[str, Any]], tokenizer: Any):
        self.encodings = tokenizer(
            [row["text"] for row in rows],
            truncation=True,
            max_length=MAX_LENGTH,
            padding=False,
            add_special_tokens=True,
        )
        self.labels = [row["sentence_label"] for row in rows]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> dict[str, Any]:
        item = {key: values[index] for key, values in self.encodings.items()}
        item["labels"] = self.labels[index]
        return item


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir", type=Path, default=os.environ.get("LADDER_JOINT_DATA_DIR")
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.data_dir is None:
        parser.error("pass --data-dir or set LADDER_JOINT_DATA_DIR")
    args.data_dir = args.data_dir.resolve()
    args.output_dir = args.output_dir.resolve()
    return args


def read_splits(data_dir: Path) -> dict[str, list[dict[str, Any]]]:
    splits: dict[str, list[dict[str, Any]]] = {}
    seen_ids: set[str] = set()
    for split, expected_size in SPLIT_SIZES.items():
        path = data_dir / f"joint_{split}.jsonl"
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(rows) != expected_size:
            raise ValueError(f"{path} has {len(rows)} rows; expected {expected_size}")
        for row_number, row in enumerate(rows, start=1):
            sample_id = row.get("id")
            label = row.get("sentence_label")
            if (
                row.get("split") != split
                or not isinstance(sample_id, str)
                or not sample_id.startswith(f"{split}-cls-")
                or sample_id in seen_ids
                or type(label) is not int
                or label not in (0, 1)
                or not isinstance(row.get("text"), str)
                or not row["text"].strip()
            ):
                raise ValueError(
                    f"Invalid or misplaced frozen row: {path}:{row_number}"
                )
            seen_ids.add(sample_id)
        splits[split] = rows

    audit_path = data_dir / "joint_dataset_statistics.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    for split, rows in splits.items():
        expected = audit["splits"][split]
        actual_counts = {
            "total": len(rows),
            "positive": sum(row["sentence_label"] == 1 for row in rows),
            "negative": sum(row["sentence_label"] == 0 for row in rows),
        }
        audit_counts = {key: expected[key] for key in actual_counts}
        if actual_counts != audit_counts:
            raise ValueError(
                f"{split} labels disagree with {audit_path}: {actual_counts} != {audit_counts}"
            )
    return splits


def token_length_statistics(
    splits: dict[str, list[dict[str, Any]]], tokenizer: Any
) -> dict[str, Any]:
    output = {"model": "xlm-roberta-base", "max_length": MAX_LENGTH, "splits": {}}
    for split, rows in splits.items():
        lengths = [
            len(
                tokenizer(
                    row["text"],
                    add_special_tokens=True,
                    truncation=False,
                    verbose=False,
                )["input_ids"]
            )
            for row in rows
        ]
        values = np.asarray(lengths, dtype=np.int64)
        p50, p90, p95 = np.percentile(values, [50, 90, 95])
        output["splits"][split] = {
            "count": len(lengths),
            "min": int(values.min()),
            "mean": float(values.mean()),
            "median": float(p50),
            "p90": float(p90),
            "p95": float(p95),
            "max": int(values.max()),
            "count_above_316": int((values > MAX_LENGTH).sum()),
        }
    return output


def compute_metrics(labels: np.ndarray, predictions: np.ndarray) -> dict[str, Any]:
    precision, recall, f1, _ = skm.precision_recall_fscore_support(
        labels, predictions, average=None, labels=[0, 1], zero_division=0
    )
    tn, fp, fn, tp = (
        skm.confusion_matrix(labels, predictions, labels=[0, 1]).ravel().tolist()
    )
    return {
        "n": int(len(labels)),
        "accuracy": float(skm.accuracy_score(labels, predictions)),
        "precision": float(precision[1]),
        "recall": float(recall[1]),
        "f1": float(f1[1]),
        "macro_precision": float(precision.mean()),
        "macro_recall": float(recall.mean()),
        "macro_f1": float(f1.mean()),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is required; run this script in a CUDA-enabled Vast AI image"
        )
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {args.output_dir}; choose a new --output-dir"
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    transformers.set_seed(SEED, deterministic=False)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    splits = read_splits(args.data_dir)
    tokenizer = transformers.AutoTokenizer.from_pretrained("xlm-roberta-base")
    token_stats = token_length_statistics(splits, tokenizer)
    write_json(args.output_dir / "token_length_statistics.json", token_stats)

    datasets = {
        name: TextClassificationDataset(rows, tokenizer)
        for name, rows in splits.items()
    }
    model = transformers.AutoModelForSequenceClassification.from_pretrained(
        "xlm-roberta-base", num_labels=2
    )
    trainer_args = transformers.TrainingArguments(
        output_dir=str(args.output_dir / "trainer_checkpoints"),
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=5,
        optim="adamw_torch_fused",
        weight_decay=0.01,
        seed=SEED,
        data_seed=SEED,
        fp16=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=20,
    )
    run_config = {
        "checkpoint_reference": CHECKPOINT_REFERENCE,
        "training_arguments": trainer_args.to_dict(),
        "model": type(model).__name__,
        "label_mapping": {"0": "irrelevant", "1": "relevant"},
        "max_length": MAX_LENGTH,
        "truncation": True,
        "padding": "dynamic per batch",
        "span_fields_used": False,
        "data_dir": str(args.data_dir),
        "split_sizes": {name: len(rows) for name, rows in splits.items()},
        "python": os.sys.version,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "cuda_device": torch.cuda.get_device_name(0),
        "metric_implementation": "scikit-learn; binary positive label 1",
        "unconfirmed_checkpoint_details": "training tokenization, class weighting or custom loss, source script, and data paths",
    }
    write_json(args.output_dir / "config.json", run_config)

    trainer = transformers.Trainer(
        model=model,
        args=trainer_args,
        train_dataset=datasets["train"],
        eval_dataset=datasets["dev"],
        data_collator=transformers.DataCollatorWithPadding(tokenizer=tokenizer),
        processing_class=tokenizer,
        compute_metrics=lambda result: {
            "f1": skm.f1_score(
                result.label_ids,
                np.argmax(result.predictions, axis=-1),
                zero_division=0,
            )
        },
    )
    trainer.train()
    trainer.save_model(str(args.output_dir / "best_model"))
    tokenizer.save_pretrained(args.output_dir / "best_model")
    write_json(args.output_dir / "training_history.json", trainer.state.log_history)

    prediction = trainer.predict(datasets["test"], metric_key_prefix="test")
    logits = (
        prediction.predictions[0]
        if isinstance(prediction.predictions, tuple)
        else prediction.predictions
    )
    shifted = logits - logits.max(axis=1, keepdims=True)
    probabilities = np.exp(shifted) / np.exp(shifted).sum(axis=1, keepdims=True)
    predicted_labels = np.argmax(logits, axis=1)
    gold_labels = prediction.label_ids.astype(int)
    metrics = compute_metrics(gold_labels, predicted_labels)
    metrics["reference"] = REFERENCE
    metrics["delta"] = {key: metrics[key] - value for key, value in REFERENCE.items()}
    metrics["reproduction_status"] = "REVIEW_REQUIRED"
    write_json(args.output_dir / "ladder_test_metrics.json", metrics)

    with (args.output_dir / "ladder_test_predictions.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["text", "gold_label", "predicted_label", "p_relevant", "correct"]
        )
        writer.writerows(
            (
                row["text"],
                int(gold),
                int(predicted),
                float(probability),
                bool(gold == predicted),
            )
            for row, gold, predicted, probability in zip(
                splits["test"],
                gold_labels,
                predicted_labels,
                probabilities[:, 1],
                strict=True,
            )
        )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
