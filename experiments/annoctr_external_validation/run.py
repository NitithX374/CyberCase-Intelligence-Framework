from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.annoctr_external_validation.analysis import evaluate_dataset
from experiments.annoctr_external_validation.constants import (
    DECISION_THRESHOLD,
    DEFAULT_ANNOCTR_ROOT,
    DEFAULT_CHECKPOINT,
    DEFAULT_OUTPUT_ROOT,
    RANDOM_SEED,
)
from experiments.annoctr_external_validation.conversion import convert_annotations
from experiments.annoctr_external_validation.model import load_frozen_classifier, load_ladder_test
from experiments.annoctr_external_validation.reporting import write_outputs
from experiments.annoctr_external_validation.source import resolve_sources
from experiments.annoctr_external_validation.validation import validate_dataset


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AnnoCTR external validation")
    parser.add_argument("--annoctr-root", type=Path, default=DEFAULT_ANNOCTR_ROOT)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser


def _print_examples(name: str, samples: list[dict]) -> None:
    print(f"\n{name} ({len(samples)})")
    for index, sample in enumerate(samples, 1):
        text = sample["text"].replace("\n", " ")
        preview = text if len(text) <= 500 else text[:500] + "..."
        print(f"{index:02d}. [{sample['document']}] {preview}")


def _print_dataset_statistics(conversion, validation) -> None:
    import random

    def to_dict(sample):
        return {"text": sample.text, "document": sample.document}

    samples = list(conversion.samples)
    randomizer = random.Random(RANDOM_SEED)
    positives = [sample for sample in samples if sample.gold_label == 1]
    negatives = [sample for sample in samples if sample.gold_label == 0]
    shortest = sorted(samples, key=lambda sample: (len(sample.text), sample.document, sample.text))[:20]
    longest = sorted(samples, key=lambda sample: (-len(sample.text), sample.document, sample.text))[:20]
    print(f"total samples: {len(samples)}")
    print(f"positive samples: {len(positives)}")
    print(f"negative samples: {len(negatives)}")
    print(f"positive percentage: {len(positives) / len(samples):.2%}")
    print(f"unique documents: {len({sample.document for sample in samples})}")
    print(f"official test documents: {validation['official_split_document_count']}")
    _print_examples("20 random positive examples", [to_dict(sample) for sample in randomizer.sample(positives, min(20, len(positives)))])
    _print_examples("20 random negative examples", [to_dict(sample) for sample in randomizer.sample(negatives, min(20, len(negatives)))])
    _print_examples("20 shortest examples", [to_dict(sample) for sample in shortest])
    _print_examples("20 longest examples", [to_dict(sample) for sample in longest])


def run(args: argparse.Namespace) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.batch_size <= 0:
        raise ValueError("batch-size must be positive")
    sources = resolve_sources(args.annoctr_root)
    if sources.native_candidates:
        candidates = ", ".join(str(path) for path in sources.native_candidates)
        raise RuntimeError(
            "Native sentence-level candidates were found and require explicit review: "
            + candidates
        )
    conversion = convert_annotations(sources.linking_path)
    validation = validate_dataset(conversion, sources)
    _print_dataset_statistics(conversion, validation)
    classifier = load_frozen_classifier(args.checkpoint, DECISION_THRESHOLD, args.device)
    print(f"\nRELEVANT_LABEL = {classifier.resources.positive_index}")
    print(f"IRRELEVANT_LABEL = {1 - classifier.resources.positive_index}")
    print(f"checkpoint = {classifier.resources.path}")
    print(f"max_length = {classifier.resources.max_length}")
    print(f"evaluation threshold = {classifier.threshold:.2f}")
    anno_rows = [
        {
            "text": sample.text,
            "gold_label": sample.gold_label,
            "document": sample.document,
        }
        for sample in conversion.samples
    ]
    ladder_rows = load_ladder_test()
    annoctr = evaluate_dataset("AnnoCTR", anno_rows, classifier, args.batch_size)
    ladder = evaluate_dataset("LADDER", ladder_rows, classifier, args.batch_size)
    classifier_metadata = {
        "checkpoint": str(classifier.resources.path),
        "base": classifier.resources.card.get("base", "UNSPECIFIED"),
        "tokenizer": getattr(classifier.resources.tokenizer, "name_or_path", "checkpoint tokenizer"),
        "positive_index": classifier.resources.positive_index,
        "relevant_label": 1,
        "irrelevant_label": 0,
        "max_length": classifier.resources.max_length,
        "evaluation_threshold": classifier.threshold,
        "checkpoint_threshold": classifier.resources.threshold,
        "device": classifier.device,
    }
    source_caveat = (
        "The repository had no native sentence-level source; the result uses the "
        "mention-level MITRE-only linking file and its explicit synthetic negative marker."
    )
    write_outputs(
        args.output_root.resolve(),
        conversion,
        validation,
        classifier_metadata,
        ladder,
        annoctr,
        RANDOM_SEED,
        source_caveat,
    )
    print("\nDataset | Accuracy | Precision | Recall | F1 | Macro-F1 | False Skip Rate")
    for result in (ladder, annoctr):
        metrics = result.metrics
        print(
            f"{result.name} | {metrics['accuracy']:.2%} | {metrics['precision']:.2%} | "
            f"{metrics['recall']:.2%} | {metrics['f1']:.2%} | {metrics['macro_f1']:.2%} | "
            f"{metrics['false_skip_rate']:.2%}"
        )
    print(f"\noutputs: {args.output_root.resolve()}")


def main() -> None:
    run(_parser().parse_args())


if __name__ == "__main__":
    main()
