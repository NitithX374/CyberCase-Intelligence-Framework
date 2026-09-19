"""Fine-tune XLM-R to answer the gate's question, and measure whether it can.

The point of a multilingual encoder here is cross-lingual transfer: the same
weights read a Thai sentence and an English one, so the gate does not need a
Thai model and an English model, or a translation step in front of it. That
also makes it easy to fool yourself. A model trained on English positives and
Thai negatives scores well by detecting the language, so every number below is
reported per language as well as overall, and the language-confound check at
the end is the one that says whether the model learned the task.

The honest test is eval_sentences.jsonl: written by hand, never trained on, and
not produced by the same model that wrote the training material.

    python train.py                  # trains, measures, writes model/
    python train.py --epochs 1       # a short run
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE = "xlm-roberta-base"
MAX_TOKENS = 96


def read(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def split(rows: list[dict], held_out: float, seed: int) -> tuple[list[dict], list[dict]]:
    """Stratified by language and label, so neither side loses a cell."""

    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        groups.setdefault((row["lang"], row["label"]), []).append(row)
    train, validate = [], []
    for key, group in sorted(groups.items()):
        random.Random(seed).shuffle(group)
        cut = max(1, int(len(group) * held_out))
        validate += group[:cut]
        train += group[cut:]
    return train, validate


def batches(rows, tokenizer, size, shuffle):
    def collate(items):
        encoded = tokenizer(
            [item["text"] for item in items],
            padding=True,
            truncation=True,
            max_length=MAX_TOKENS,
            return_tensors="pt",
        )
        encoded["labels"] = torch.tensor([item["label"] for item in items])
        return encoded

    return DataLoader(rows, batch_size=size, shuffle=shuffle, collate_fn=collate)


@torch.no_grad()
def probabilities(model, tokenizer, rows, size=32) -> list[float]:
    model.eval()
    out: list[float] = []
    for batch in batches(rows, tokenizer, size, shuffle=False):
        batch.pop("labels")
        logits = model(**batch).logits
        out += torch.softmax(logits, dim=-1)[:, 1].tolist()
    return out


def counts(rows, scores, threshold):
    true_positive = sum(s >= threshold and r["label"] == 1 for r, s in zip(rows, scores))
    false_positive = sum(s >= threshold and r["label"] == 0 for r, s in zip(rows, scores))
    false_negative = sum(s < threshold and r["label"] == 1 for r, s in zip(rows, scores))
    true_negative = sum(s < threshold and r["label"] == 0 for r, s in zip(rows, scores))
    return true_positive, false_positive, false_negative, true_negative


def report(name, rows, scores, threshold) -> dict:
    tp, fp, fn, tn = counts(rows, scores, threshold)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(rows) if rows else 0.0
    print(
        f"  {name:22} n={len(rows):4}  acc={accuracy:.1%}  P={precision:.1%}  "
        f"R={recall:.1%}  F1={f1:.1%}   tp={tp} fp={fp} fn={fn} tn={tn}"
    )
    return {"n": len(rows), "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def by_language(rows, scores, threshold) -> dict:
    out = {}
    for language in sorted({row["lang"] for row in rows}):
        pairs = [(r, s) for r, s in zip(rows, scores) if r["lang"] == language]
        out[language] = report(f"  {language}", [r for r, _ in pairs], [s for _, s in pairs], threshold)
    return out


def best_threshold(rows, scores) -> float:
    """The threshold with the best F1, preferring precision: the gate guards a
    retrieval, and a false RETRIEVE spends it on a case that has no technique."""

    def score(threshold):
        tp, fp, fn, _ = counts(rows, scores, threshold)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        return (2 * precision * recall / (precision + recall) if precision + recall else 0.0, precision)

    return max((i / 100 for i in range(5, 100, 5)), key=score)


def language_confound(rows, scores, threshold) -> None:
    """Whether the model is reading behaviour or reading the language.

    A model that separates the classes within each language is doing the task.
    One whose scores separate the languages instead has learned that the
    training positives were written in one and the negatives in the other.
    """

    print("\n  language-confound check (mean score)")
    for language in sorted({row["lang"] for row in rows}):
        for label in (1, 0):
            group = [s for r, s in zip(rows, scores) if r["lang"] == language and r["label"] == label]
            if group:
                print(f"    {language} label={label}: {sum(group) / len(group):.3f}  (n={len(group)})")
    gaps = []
    for language in sorted({row["lang"] for row in rows}):
        positive = [s for r, s in zip(rows, scores) if r["lang"] == language and r["label"] == 1]
        negative = [s for r, s in zip(rows, scores) if r["lang"] == language and r["label"] == 0]
        if positive and negative:
            gaps.append(sum(positive) / len(positive) - sum(negative) / len(negative))
    if gaps:
        print(f"    within-language separation: {min(gaps):.3f}..{max(gaps):.3f} (want both high)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="dataset.jsonl")
    parser.add_argument("--eval", default="eval_sentences.jsonl")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--held-out", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=20260919)
    parser.add_argument("--out", default="model")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    rows = read(args.dataset)
    train_rows, validate_rows = split(rows, args.held_out, args.seed)
    print(f"{len(rows)} sentences: {len(train_rows)} train, {len(validate_rows)} validation")
    print(" ", Counter((row["lang"], row["label"]) for row in train_rows))

    tokenizer = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForSequenceClassification.from_pretrained(BASE, num_labels=2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loader = batches(train_rows, tokenizer, args.batch, shuffle=True)
    steps = args.epochs * len(loader)
    schedule = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=args.lr, total_steps=steps, pct_start=0.1)

    step = 0
    for epoch in range(args.epochs):
        model.train()
        running = 0.0
        for batch in loader:
            loss = model(**batch).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            schedule.step()
            optimizer.zero_grad()
            running += loss.item()
            step += 1
            if step % 10 == 0:
                print(f"\r  epoch {epoch + 1}/{args.epochs}  step {step}/{steps}  loss {running / (step - epoch * len(loader)):.4f}", end="")
        print()

    print("\nvalidation (same generator as training)")
    validation_scores = probabilities(model, tokenizer, validate_rows)
    threshold = best_threshold(validate_rows, validation_scores)
    print(f"  threshold chosen on validation: {threshold:.2f}")
    validation = report("overall", validate_rows, validation_scores, threshold)
    validation["by_language"] = by_language(validate_rows, validation_scores, threshold)

    print("\nheld-out hand-written set (the honest test)")
    eval_rows = read(args.eval)
    eval_scores = probabilities(model, tokenizer, eval_rows)
    held = report("overall", eval_rows, eval_scores, threshold)
    held["by_language"] = by_language(eval_rows, eval_scores, threshold)
    language_confound(eval_rows, eval_scores, threshold)

    print("\n  mistakes on the hand-written set")
    for row, score in sorted(zip(eval_rows, eval_scores), key=lambda p: -p[1]):
        if (score >= threshold) != (row["label"] == 1):
            kind = "false RETRIEVE" if row["label"] == 0 else "missed"
            print(f"    {score:.3f}  {kind:15} {row['lang']}  {row['text'][:66]}")

    Path(args.out).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    (Path(args.out) / "gate.json").write_text(
        json.dumps(
            {
                "base": BASE,
                "threshold": threshold,
                "max_tokens": MAX_TOKENS,
                "trained_on": len(train_rows),
                "validation": validation,
                "hand_written": held,
            },
            indent=1,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\nsaved to {args.out}/ with threshold {threshold:.2f}")


if __name__ == "__main__":
    main()
