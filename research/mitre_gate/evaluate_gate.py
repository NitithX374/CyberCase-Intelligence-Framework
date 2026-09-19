"""Measure a trained sentence classifier against the gate's question.

The LADDER model was trained on English CTI prose to answer "does this sentence
describe an attack pattern". The gate asks the same question of Thai and
English police reports, which is neither the language nor the register it was
trained on -- so what it scores here is the whole question.

Every number is reported per language. A multilingual model trained on English
can separate the classes in English and rank Thai by nothing at all, and an
overall accuracy hides exactly that.

    python evaluate_gate.py --model ../../backend/xlmr_ladder_best/xlmr_ladder_best
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def read(path: str) -> list[dict]:
    """Our JSONL, or LADDER's own splits, which are tab-separated .csv files."""

    if path.endswith(".csv"):
        with open(path, encoding="utf-8") as handle:
            return [
                {"text": row["text"], "label": int(row["label"]), "lang": "en"}
                for row in csv.DictReader(handle, delimiter="\t")
                if row.get("text") and row.get("label")
            ]
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


@torch.no_grad()
def probabilities(model, tokenizer, texts, index, max_tokens, batch=16):
    out = []
    for start in range(0, len(texts), batch):
        encoded = tokenizer(
            texts[start : start + batch],
            padding=True,
            truncation=True,
            max_length=max_tokens,
            return_tensors="pt",
        )
        out += torch.softmax(model(**encoded).logits, dim=-1)[:, index].tolist()
    return out


def counts(rows, scores, threshold):
    tp = sum(s >= threshold and r["label"] == 1 for r, s in zip(rows, scores))
    fp = sum(s >= threshold and r["label"] == 0 for r, s in zip(rows, scores))
    fn = sum(s < threshold and r["label"] == 1 for r, s in zip(rows, scores))
    tn = sum(s < threshold and r["label"] == 0 for r, s in zip(rows, scores))
    return tp, fp, fn, tn


def measure(rows, scores, threshold):
    tp, fp, fn, tn = counts(rows, scores, threshold)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n": len(rows),
        "accuracy": (tp + tn) / len(rows) if rows else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def show(name, result):
    print(
        f"  {name:14} n={result['n']:3}  acc={result['accuracy']:6.1%}  "
        f"P={result['precision']:6.1%}  R={result['recall']:6.1%}  F1={result['f1']:6.1%}   "
        f"tp={result['tp']} fp={result['fp']} fn={result['fn']} tn={result['tn']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="../../backend/xlmr_ladder_best/xlmr_ladder_best")
    parser.add_argument("--eval", default="eval_sentences.jsonl")
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--save", default=None, help="write gate.json with the chosen threshold")
    args = parser.parse_args()

    rows = read(args.eval)
    texts = [row["text"] for row in rows]
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model).eval()

    # Nothing in the checkpoint says which output means "attack pattern", so
    # take the one that agrees with the labels and say which it was.
    candidates = {
        index: probabilities(model, tokenizer, texts, index, args.max_tokens)
        for index in (0, 1)
    }
    agreement = {
        index: max(measure(rows, scores, t / 100)["accuracy"] for t in range(5, 100, 5))
        for index, scores in candidates.items()
    }
    index = max(agreement, key=agreement.get)
    scores = candidates[index]
    print(f"positive output index = {index}  (index 0 agrees {agreement[0]:.0%}, index 1 agrees {agreement[1]:.0%})\n")

    print("at the model's own decision boundary (0.50)")
    show("overall", measure(rows, scores, 0.5))

    threshold = max(
        (t / 100 for t in range(5, 100, 5)),
        key=lambda t: (measure(rows, scores, t)["f1"], measure(rows, scores, t)["precision"]),
    )
    print(f"\nbest threshold on this set: {threshold:.2f}  (an upper bound -- chosen here)")
    show("overall", measure(rows, scores, threshold))
    for language in sorted({row["lang"] for row in rows}):
        pairs = [(r, s) for r, s in zip(rows, scores) if r["lang"] == language]
        show(language, measure([r for r, _ in pairs], [s for _, s in pairs], threshold))

    print("\n  mean score by cell (does it separate within each language?)")
    for language in sorted({row["lang"] for row in rows}):
        for label in (1, 0):
            cell = [s for r, s in zip(rows, scores) if r["lang"] == language and r["label"] == label]
            print(f"    {language} label={label}: {sum(cell) / len(cell):.3f}  (n={len(cell)})")

    if len(rows) > 120:
        return

    print("\n  every sentence, ranked")
    for row, score in sorted(zip(rows, scores), key=lambda pair: -pair[1]):
        wrong = "  <-- wrong" if (score >= threshold) != (row["label"] == 1) else ""
        print(f"    {score:.3f}  y={row['label']}  {row['lang']}  {row['text'][:58]:60}{wrong}")

    if args.save:
        Path(args.save).write_text(
            json.dumps(
                {
                    "base": "xlm-roberta-base (LADDER attack-pattern sentence classifier)",
                    "positive_index": index,
                    "threshold": threshold,
                    "max_tokens": args.max_tokens,
                    "hand_written": measure(rows, scores, threshold),
                },
                indent=1,
            ),
            encoding="utf-8",
        )
        print(f"\nwrote {args.save}")


if __name__ == "__main__":
    main()
