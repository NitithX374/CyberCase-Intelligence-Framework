"""What happens to stored identifiers when the segmenter changes (no model calls, no labels).

Units are recomputed from the source text rather than stored, and the revision tag hashes the
segmentation version and the source text only, not the segmenter. This script segments the same
corpora as run.py with SaT, then again with the PyThaiNLP crfcut fall-back that production uses when
SaT cannot be loaded, and resolves every SaT-era identifier against the fall-back units with the
production EvidenceIndex. It counts identifiers that still return their text, identifiers that return
different text without any error, and identifiers that fail with a typed reason.

Run from the repository root with the backend requirements installed:
  python research/traceability_properties/segmenter_switch.py --thai-n 500 --en-n 1000
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run import english_corpus, source, thai_corpus  # noqa: E402

from app.sources.evidence import EVIDENCE_VERSION, EvidenceIndex, evidence_units  # noqa: E402
from app.trace import sentences  # noqa: E402


def switch(name: str, texts: list[str], sat_units: list[tuple]) -> dict:
    same = silent = 0
    reasons: Counter[str] = Counter()
    sources_silent = 0
    fallback_units = 0
    for text, units in zip(texts, sat_units):
        index = EvidenceIndex([source(text)])
        fallback_units += len(evidence_units(source(text)))
        any_silent = False
        for u in units:
            unit, reason = index.resolve("S1", u.unit_id)
            if unit is None:
                reasons[reason or "unresolved"] += 1
            elif unit.text == u.text:
                same += 1
            else:
                silent += 1
                any_silent = True
        sources_silent += any_silent
    old = sum(len(u) for u in sat_units)
    return {
        "corpus": name,
        "sources": len(texts),
        "sat_units": old,
        "fallback_units": fallback_units,
        "old_ids": old,
        "same_text": same,
        "different_text_without_error": silent,
        "typed_failures": dict(reasons),
        "share_different_text_without_error": silent / old,
        "sources_with_a_silent_change": sources_silent,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thai-n", type=int, default=500)
    parser.add_argument("--en-n", type=int, default=1000)
    parser.add_argument("--out", default=str(HERE / "results" / "segmenter_switch.json"))
    args = parser.parse_args()

    if sentences.get_sat_segmenter() is None:
        raise SystemExit("SaT is unavailable; this measurement needs it")
    corpora = [("ThaiSum test (Thai news)", *thai_corpus(args.thai_n)),
               ("AttributionBench references (English)", *english_corpus(args.en_n))]
    sat = [[evidence_units(source(t)) for t in texts] for _, texts, _ in corpora]

    sentences._sat_model = False  # what get_sat_segmenter caches when SaT fails to load
    result = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_version": EVIDENCE_VERSION,
        "before": "SaT sat-3l-sm (threshold %.3f)" % sentences.SAT_THRESHOLD,
        "after": "PyThaiNLP crfcut fall-back (SaT unavailable)",
        "inputs": {name: meta for name, _, meta in corpora},
        "results": [switch(name, texts, units) for (name, texts, _), units in zip(corpora, sat)],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["results"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
