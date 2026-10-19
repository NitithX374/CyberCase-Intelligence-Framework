"""Re-scores identifier precision with each trace's own reference IDs removed from its text first. Added after the main
run: the frozen scorer read a claim reference such as "(A-01, A-02)" as the numbers 01 and 02, which no article holds.
Only the IDs the trace itself defines are removed (claims, gaps, ATT&CK associations and cited sources); the prose arm
has none. Uses the saved outputs and makes no model call. Writes <results>_ids_rescored.jsonl beside the input.

  python rescore_identifiers.py results/main_20260928_081639.jsonl
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import run

from app.trace.trace import CaseAnalysisTrace  # noqa: E402

HERE = Path(__file__).resolve().parent
results = HERE / sys.argv[1]
raw = results.parent / f"raw_{results.stem}"
records = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
cases = {row["id"]: row for row in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}


def reference_ids(trace: CaseAnalysisTrace) -> set[str]:
    ids = {c.claim_id for c in trace.claims} | {g.gap_id for g in trace.gaps}
    ids |= {a.association_id for a in trace.mitre_associations}
    ids |= {cite.source_id for c in trace.claims for cite in [*c.supporting_citations, *c.contradicting_citations]}
    return {i for i in ids if i}


removed = Counter()
out = results.with_name(f"{results.stem}_ids_rescored.jsonl")
with out.open("w", encoding="utf-8") as handle:
    for r in records:
        if "error" not in r and r["arm"] != "prose":
            saved = json.loads((raw / f"{r['case']}_{r['arm']}_{r['run']}.json").read_text(encoding="utf-8"))
            trace = CaseAnalysisTrace.model_validate(saved["bound"])
            text = run.own_text(trace)
            for ref in sorted(reference_ids(trace), key=len, reverse=True):
                text, count = re.subn(rf"(?<![\w-]){re.escape(ref)}(?![\w-])", " ", text)
                removed[r["arm"]] += count
            r = {**r, "identifiers_frozen_scorer": r["identifiers"],
                 "identifiers": run.identifier_check(text, cases[r["case"]]["text"])}
        handle.write(json.dumps(r, ensure_ascii=False) + "\n")
print("reference ids removed:", dict(removed))
for arm in ("prose", "cybercase", "single"):
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    done = [r for r in rows if r["arm"] == arm and "error" not in r]
    written = sum(r["identifiers"]["written"] for r in done)
    supported = sum(r["identifiers"]["supported"] for r in done)
    print(f"{arm:9s} identifier precision {supported}/{written} = {supported / written:.3f}")
