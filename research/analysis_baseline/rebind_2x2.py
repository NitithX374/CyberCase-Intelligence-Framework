from __future__ import annotations

import argparse
import hashlib
import json
import re
import string
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARMS = {"two calls, grammar": ("main_20260930_062138", "cybercase"),
        "two calls, no grammar": ("main_20260930_193646", "cybercase_nogrammar")}
PAIRS = [("two calls, no grammar", "two calls, grammar")]
SEED, RESAMPLES = 2026, 2000


def production(backend: str):
    sys.path.insert(0, backend)
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    sys.path.insert(0, str(HERE))
    from scores_common import lead

    return bind.located_quote, states, lead


def normalize_answer(s: str) -> str:
    s = "".join(ch for ch in s.lower() if ch not in set(string.punctuation))
    return " ".join(re.sub(r"\b(a|an|the)\b", " ", s).split())


def states(text: str, case: dict, fact: dict) -> bool:
    written = normalize_answer(text)
    return any(form and form in written for form in (normalize_answer(case["text"][s:e]) for s, e in fact["spans"]))


def scored(located_quote, states, lead, case: dict, written: dict) -> dict:
    text = case["text"]
    reported = bound = written_quotes = located_quotes = 0
    spans_by_claim: dict[str, list[tuple[int, int]]] = {}
    for claim in written["claims"]:
        quotes = [c.get("exact_quote") for c in claim.get("supporting_citations", []) + claim.get(
            "contradicting_citations", []) if c.get("exact_quote")]
        support = [c.get("exact_quote") for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        positions = []
        for quote in quotes:
            written_quotes += 1
            pieces = located_quote(text, quote)
            if pieces is None:
                continue
            located_quotes += 1
            for piece in pieces:
                start = text.find(piece)
                while start >= 0:
                    positions.append((start, start + len(piece)))
                    start = text.find(piece, start + 1)
        spans_by_claim[claim["claim_id"]] = positions
        if claim.get("epistemic_status") == "reported":
            reported += 1
            bound += any(located_quote(text, q) is not None for q in support)
    facts = lead(case)

    def points(fact: dict, claim_id: str) -> bool:
        return any(a < e and b > s for s, e in fact["spans"] for a, b in spans_by_claim[claim_id])

    texts = {c["claim_id"]: c.get("text", "") for c in written["claims"]}
    m4 = sum(any(points(f, cid) for cid in spans_by_claim) for f in facts) / len(facts)
    m4b = sum(any(points(f, cid) and states(texts[cid], case, f) for cid in spans_by_claim) for f in facts) / len(facts)
    return {"m1": (bound, reported), "m2": (located_quotes, written_quotes), "m3": int(bound == reported),
            "m4": m4, "m4b": m4b}


def arm(located_quote, states, lead, cases: dict, run: str, name: str) -> dict[str, dict | None]:
    out: dict[str, dict | None] = {}
    for line in (HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["arm"] != name or record.get("run", 1) != 1 or record.get("error_kind") in ("budget", "harness"):
            continue
        if "error" in record:
            out[record["case"]] = None
            continue
        saved = json.loads((HERE / "results" / f"raw_{run}" / f"{record['case']}_{name}_1.json").read_text(
            encoding="utf-8"))
        out[record["case"]] = scored(located_quote, states, lead, cases[record["case"]], saved["written"])
    return dict(sorted(out.items()))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    located_quote, states, lead = production(args.backend)
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    views = {label: arm(located_quote, states, lead, cases, *spec) for label, spec in ARMS.items()}
    md = ["# The 2×2 recounted with the production binder", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          "No model call. Failed cases score 0 on M3, M4 and M4b; M1 and M2 pool completed cases.", "",
          "| Arm, cases 151-250 | Cases | Completed | M1 | M2 | M3 | M4 | M4b |", "|---|---|---|---|---|---|---|---|"]
    report: dict = {"arms": {}, "pairs": {}}
    for label, view in views.items():
        done = [v for v in view.values() if v]
        m1 = [sum(v["m1"][0] for v in done), sum(v["m1"][1] for v in done)]
        m2 = [sum(v["m2"][0] for v in done), sum(v["m2"][1] for v in done)]
        m3 = sum(v["m3"] for v in done) / len(view)
        m4 = sum(v["m4"] for v in done) / len(view)
        m4b = sum(v["m4b"] for v in done) / len(view)
        report["arms"][label] = {"cases": len(view), "completed": len(done), "m1": m1, "m2": m2, "m3": m3, "m4": m4,
                                 "m4b": m4b}
        md.append(f"| {label} | {len(view)} | {len(done)} | {m1[0] / m1[1]:.3f} | {m2[0]}/{m2[1]} = {m2[0] / m2[1]:.3f} "
                  f"| {m3:.3f} | {m4:.3f} | {m4b:.3f} |")
    md += ["", "| Pair (failures 0, cases in both lists) | M4 | M4b |", "|---|---|---|"]
    for x, y in PAIRS:
        common = sorted(set(views[x]) & set(views[y]))
        cells = []
        for key in ("m4", "m4b"):
            diff = np.array([(views[x][c][key] if views[x][c] else 0) - (views[y][c][key] if views[y][c] else 0)
                             for c in common])
            picks = np.random.default_rng(SEED).integers(0, len(diff), size=(RESAMPLES, len(diff)))
            means = diff[picks].mean(axis=1)
            cell = [round(float(diff.mean()), 3), round(float(np.percentile(means, 2.5)), 3),
                    round(float(np.percentile(means, 97.5)), 3), len(common)]
            report["pairs"][f"{x} − {y} | {key}"] = cell
            cells.append(f"{cell[0]:+.3f} [{cell[1]:+.3f}, {cell[2]:+.3f}]")
        md.append(f"| {x} − {y} (n {len(common)}) | " + " | ".join(cells) + " |")
    (HERE / "results" / "rebind_2x2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "rebind_2x2.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
