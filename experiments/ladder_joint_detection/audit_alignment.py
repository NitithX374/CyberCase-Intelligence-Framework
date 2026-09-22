from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.ladder_joint_detection.constants import OUTPUT_ROOT, SPLITS
from experiments.ladder_joint_detection.diagnostics import build_diagnostics
from experiments.ladder_joint_detection.matching import build_audit_bundle
from experiments.ladder_joint_detection.parsing import load_sources
from experiments.ladder_joint_detection.reporting import write_audit_outputs
from experiments.ladder_joint_detection.validation import validate_audit_bundle


def run_audit(output_root: Path = OUTPUT_ROOT) -> dict:
    source_data = load_sources()
    bundle = build_audit_bundle(source_data)
    validate_audit_bundle(bundle)
    diagnostics = build_diagnostics(bundle)
    report = write_audit_outputs(bundle, diagnostics, output_root)
    return report


def _print_summary(report: dict) -> None:
    print(f"Decision: {report['decision']}")
    print(f"Negative all-O span supervision safe: {report['negative_span_supervision_safe']}")
    for split in SPLITS:
        stats = report["split_statistics"][split]
        print(
            f"{split}: classification={stats['classification_total']} "
            f"positive={stats['classification_positive']} "
            f"entity={stats['entity_extraction_total']} "
            f"exact={stats['exact_alignment_count']} "
            f"positive_spans={stats['positive_with_span_annotation']} "
            f"positive_masked={stats['positive_without_span_annotation']}"
        )
    print("Matched examples:")
    for row in report["matched_examples"]:
        print(f"  [{row['split']}] {row['text']}")
    print("Unmatched positive examples:")
    for row in report["unmatched_examples"]:
        print(f"  [{row['split']}] {row['text']}")
    print(f"Reports written to {OUTPUT_ROOT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit LADDER relevance/entity alignment")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    report = run_audit(args.output_root.resolve())
    _print_summary(report)


if __name__ == "__main__":
    main()
