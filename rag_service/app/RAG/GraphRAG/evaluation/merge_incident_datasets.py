"""
Merge Incident Draft Datasets
==============================
Combines several `incident_draft*.json` files into one evaluation dataset the
benchmark harness can consume, with validation so a bad sample never reaches
a paid run:

  - schema check   : Thai query + query_en + 3-7 gold ids + well-formed steps
  - id collision   : ids must be unique across files (use distinct --id-prefix)
  - duplicate check: same technique set in two files → reported, first kept
  - summary        : per-source counts, cue-type mix, gold-size distribution

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.merge_incident_datasets \
        --inputs incident_draft.json,incident_draft_campaign.json \
        --out incident_eval_set.json
    # add --strict to fail (exit 1) instead of dropping invalid samples
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ is None or __package__ == "evaluation":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    __package__ = "GraphRAG.evaluation"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT_DIR = Path(__file__).resolve().parent / "data"


def validate(sample: dict) -> list[str]:
    """Return a list of problems; empty list means the sample is usable."""
    problems: list[str] = []
    if not (sample.get("query") or "").strip():
        problems.append("empty query")
    if not (sample.get("query_en") or "").strip():
        problems.append("missing query_en")
    gold = sample.get("gold_attack_ids") or []
    if not 3 <= len(gold) <= 7:
        problems.append(f"gold_attack_ids={len(gold)} (want 3-7)")
    steps = sample.get("attack_steps") or []
    if not steps:
        problems.append("no attack_steps")
    for i, st in enumerate(steps):
        if st.get("cue_type") not in ("named", "described"):
            problems.append(f"step{i}: bad cue_type {st.get('cue_type')!r}")
        if not (st.get("cue") or "").strip():
            problems.append(f"step{i}: empty cue")
        if not st.get("gold_attack_ids"):
            problems.append(f"step{i}: no gold ids")
        # a cue must be traceable back into the narrative verbatim
        elif st.get("cue") and st["cue"] not in (sample.get("query") or ""):
            problems.append(f"step{i}: cue not verbatim in query")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge incident draft datasets")
    parser.add_argument("--inputs", required=True,
                        help="Comma-separated filenames under data/")
    parser.add_argument("--out", default="incident_eval_set.json",
                        help="Merged output filename under data/")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any sample is invalid "
                             "(default: drop invalid, keep going)")
    args = parser.parse_args()

    files = [f.strip() for f in args.inputs.split(",") if f.strip()]
    merged: list[dict] = []
    seen_ids: set[str] = set()
    seen_tech: dict[tuple, str] = {}
    dropped: list[tuple[str, str]] = []
    per_file: Counter = Counter()

    for name in files:
        path = OUT_DIR / name
        with open(path, "r", encoding="utf-8") as f:
            samples = json.load(f)
        for s in samples:
            sid = s.get("id", "<no-id>")

            problems = validate(s)
            if problems:
                dropped.append((sid, "; ".join(problems)))
                continue

            if sid in seen_ids:
                dropped.append((sid, "duplicate id across files"))
                continue

            tech = tuple(s["gold_attack_ids"])
            if tech in seen_tech:
                dropped.append((sid, f"duplicate technique set of {seen_tech[tech]}"))
                continue

            seen_ids.add(sid)
            seen_tech[tech] = sid
            merged.append(s)
            per_file[name] += 1

    # ── Summary ────────────────────────────────────────────────────────────
    cue = Counter(st["cue_type"] for s in merged for st in s["attack_steps"])
    gold_sizes = Counter(len(s["gold_attack_ids"]) for s in merged)
    steps_total = sum(len(s["attack_steps"]) for s in merged)

    print(f"\n[MERGE] {len(merged)} samples from {len(files)} file(s)")
    for name in files:
        print(f"  {name}: {per_file[name]} kept")
    print(f"[MERGE] attack steps: {steps_total} "
          f"(named {cue['named']} / described {cue['described']})")
    print(f"[MERGE] gold per sample: "
          + ", ".join(f"{k}→{v}" for k, v in sorted(gold_sizes.items())))
    print(f"[MERGE] avg gold/sample: "
          f"{sum(len(s['gold_attack_ids']) for s in merged) / len(merged):.1f}"
          if merged else "[MERGE] no samples")

    if dropped:
        print(f"\n[MERGE] dropped {len(dropped)}:")
        for sid, why in dropped[:15]:
            print(f"  {sid}: {why}")
        if len(dropped) > 15:
            print(f"  … and {len(dropped) - 15} more")

    out_path = OUT_DIR / args.out
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"\n[MERGE] Saved: {out_path}")

    if dropped and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
