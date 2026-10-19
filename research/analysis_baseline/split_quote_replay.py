"""Split-quote replay: re-bind the saved written traces with the binder that stores a middle-ellipsis quote as one
citation per piece (branch fix/binder-split-ellipsis-quotes). No model is called.

  python split_quote_replay.py --backend F:/cc-split/backend

Every saved written trace of cybercase (main_20260930_020141) and cybercase_nogrammar (main_20260930_193646) is bound
twice: by the pinned binder that wrote the stored bound traces (pinned/1e29bd3/backend, whose trace/bind.py and
trace/quotes.py are byte-identical to origin/main 8750cbc), and by the binder at --backend. Both are the package `app`,
so each binds in its own process. Writes results/split_quote_replay.json and results/split_quote_replay.md.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
PINNED = HERE / "pinned" / "1e29bd3" / "backend"
RUNS = (("main_20260930_020141", "cybercase"), ("main_20260930_193646", "cybercase_nogrammar"))
STORED_M4 = {"main_20260930_020141": 0.872, "main_20260930_193646": 0.928}
WITHOUT_STITCHED_M4 = {"main_20260930_020141": 0.855, "main_20260930_193646": 0.926}
ROLES = ("supporting_citations", "contradicting_citations")
SOURCE_ID = "SRC-1"
CASES = {r["id"]: r for r in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}


def saved_files(run: str, arm: str) -> list[Path]:
    return sorted((HERE / "results" / f"raw_{run}").glob(f"*_{arm}_1.json"))


def bind_all(backend: Path, out: Path) -> None:
    os.environ["MITRE_GATE_MODE"] = "never"
    os.environ["MITRE_GATE_SHADOW"] = "off"
    os.chdir(backend)
    sys.path.insert(0, str(backend))
    from app.sources.bundle import CaseSourceBundle, CaseSourceItem
    from app.trace import bind, quotes
    from app.trace.trace import CaseAnalysisTrace

    result = {}
    for run, arm in RUNS:
        for path in saved_files(run, arm):
            text = CASES[path.name.split("_")[0]]["text"]
            written = CaseAnalysisTrace.model_validate(json.loads(path.read_text(encoding="utf-8"))["written"])
            bundle = CaseSourceBundle(revision=1, sources=(
                CaseSourceItem(source_id=SOURCE_ID, source_kind="narrative", text=text),))
            rebound = bind.resolve_case_trace(written, bundle, mitre_table=[], followup_history=())
            located, first = [], {}
            for position, claim in enumerate(written.claims):
                kept = first.setdefault(claim.claim_id, position) == position
                for role in ROLES:
                    for citation in getattr(claim, role):
                        found = bind.located_quote(text, citation.exact_quote) if citation.source_id == SOURCE_ID else None
                        spans = quotes.find_aligned_quote(text, quotes.without_edge_ellipses(citation.exact_quote))
                        located.append({
                            "kept": kept, "claim": claim.claim_id, "role": role,
                            "source_id": citation.source_id, "quote": citation.exact_quote,
                            "pieces": None if found is None else [found] if isinstance(found, str) else list(found),
                            "spans": spans if isinstance(spans, list) else None,
                        })
            result[f"{run}/{path.name}"] = {"rebound": rebound.model_dump(mode="json"), "located": located}
    out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")


def bound_by(backend: Path, scratch: Path, name: str) -> dict:
    out = scratch / f"{name}.json"
    subprocess.run([sys.executable, str(Path(__file__).resolve()), "--bind", str(backend), "--out", str(out)],
                   check=True)
    return json.loads(out.read_text(encoding="utf-8"))


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def key(citation: dict) -> tuple[str, str]:
    return citation["source_id"], citation["exact_quote"]


def without_citations(trace: dict) -> dict:
    copy = json.loads(json.dumps(trace))
    copy["grounding"] = None
    for claim in copy["claims"]:
        for role in ROLES:
            claim[role] = []
    return copy


def first_claims(trace: dict) -> dict[str, dict]:
    claims: dict[str, dict] = {}
    for claim in trace["claims"]:
        claims.setdefault(claim["claim_id"], claim)
    return claims


def records(run: str, arm: str) -> dict[str, dict]:
    rows = [json.loads(line) for line in (HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines()]
    return {r["case"]: r for r in rows if r["arm"] == arm and r.get("run", 1) == 1
            and r.get("error_kind") not in ("budget", "harness")}


def every_occurrence(text: str, quote: str) -> list[tuple[int, int]]:
    found, start = [], text.find(quote)
    while start >= 0:
        found.append((start, start + len(quote)))
        start = text.find(quote, start + 1)
    return found


def coverage(case: str, spans: list[tuple[int, int]]) -> float:
    lead = [f for f in CASES[case]["gold"] if f["lead"]]
    cited = [f for f in lead if any(a < e and b > s for s, e in f["spans"] for a, b in spans)]
    return len(cited) / len(lead)


def quote_spans(text: str, trace: dict, located_only: dict[str, list[tuple[int, int]]] | None = None) -> list:
    spans = []
    for claim in trace["claims"]:
        for role in ROLES:
            for citation in claim[role]:
                quote = citation["exact_quote"]
                spans += located_only[quote] if located_only and quote in located_only else every_occurrence(text, quote)
    return spans


def compare_file(stored: dict, old: dict, new: dict, text: str) -> dict:
    view = {"old_identical": canonical(old["rebound"]) == canonical(stored),
            "rest_identical": canonical(without_citations(new["rebound"])) == canonical(without_citations(stored)),
            "split": 0, "merged_fallback": 0, "pieces_stored": 0, "piece_texts": [], "ambiguous_pieces": 0,
            "cap_refused": 0,
            "other_citations": 0, "other_identical": True, "order_matches": True, "located_spans": {},
            "other_texts": set()}
    splits: dict[tuple[str, str], dict[tuple[str, str], list[tuple[str, str]]]] = {}
    for before, after in zip(old["located"], new["located"], strict=True):
        if not after["kept"]:
            continue
        if after["pieces"] is None and after["spans"] and len(after["spans"]) > 1:
            view["cap_refused"] += 1
        if after["pieces"] is not None and len(after["pieces"]) == 1 and after["spans"] and len(after["spans"]) > 1:
            view["merged_fallback"] += 1
            assert before["pieces"] == after["pieces"], (before["quote"], before["pieces"], after["pieces"])
        if after["pieces"] is None or len(after["pieces"]) < 2:
            continue
        view["split"] += 1
        merged = text[after["spans"][0][0]:after["spans"][-1][1]]
        assert before["pieces"] == [merged], (before["quote"], before["pieces"])
        pieces = [(after["source_id"], piece) for piece in after["pieces"]]
        splits.setdefault((after["claim"], after["role"]), {})[(after["source_id"], merged)] = pieces
        for (_, piece), span in zip(pieces, after["spans"], strict=True):
            view["located_spans"].setdefault(piece, []).append(tuple(span))
    stored_claims, new_claims = first_claims(stored), first_claims(new["rebound"])
    for claim_id, claim in stored_claims.items():
        for role in ROLES:
            merged_pieces = splits.get((claim_id, role), {})
            piece_keys = {p for pieces in merged_pieces.values() for p in pieces}
            stored_by_key = {key(c): c for c in claim[role]}
            expected, seen = [], set()
            for citation in claim[role]:
                for k in merged_pieces.get(key(citation), [key(citation)]):
                    if k not in seen:
                        expected.append(k)
                        seen.add(k)
            got = new_claims[claim_id][role]
            view["order_matches"] &= [key(c) for c in got] == expected
            for citation in got:
                if key(citation) in stored_by_key:
                    view["other_citations"] += 1
                    view["other_texts"].add(citation["exact_quote"])
                    view["other_identical"] &= canonical(citation) == canonical(stored_by_key[key(citation)])
                elif key(citation) in piece_keys:
                    view["pieces_stored"] += 1
                    view["piece_texts"].append(citation["exact_quote"])
                    view["ambiguous_pieces"] += len(every_occurrence(text, citation["exact_quote"])) > 1
                else:
                    view["other_identical"] = False
            gone = [c for c in claim[role] if key(c) not in {key(g) for g in got}]
            view["other_identical"] &= all(key(c) in merged_pieces for c in gone)
    return view


def grounding_change(stored: dict, new: dict) -> dict[str, int]:
    a, b = stored["grounding"], new["grounding"]
    return {field: b[field] - a[field] for field in a if a[field] != b[field]}


def consistent(grounding: dict) -> bool:
    return (grounding["citations_verified"] <= grounding["citations_claimed"]
            and grounding["citations_duplicated"] >= 0
            and grounding["citations_verified"] + grounding["citations_duplicated"] + grounding["citations_paraphrased"]
            + grounding["citations_unfound"] == grounding["citations_claimed"])


def summarise(run: str, arm: str, old: dict, new: dict) -> dict:
    recs = records(run, arm)
    files = {p.name.split("_")[0]: p for p in saved_files(run, arm)}
    views, changes, m4 = {}, Counter(), {"stored": [], "new": [], "new_located_only": []}
    for case, record in sorted(recs.items()):
        if "error" in record:
            for name in m4:
                m4[name].append(0.0)
            continue
        text = CASES[case]["text"]
        stored = json.loads(files[case].read_text(encoding="utf-8"))["bound"]
        label = f"{run}/{files[case].name}"
        view = compare_file(stored, old[label], new[label], text)
        view["grounding_change"] = grounding_change(stored, new[label]["rebound"])
        view["grounding_consistent"] = consistent(new[label]["rebound"]["grounding"])
        changes.update(view["grounding_change"].keys())
        m4["stored"].append(coverage(case, quote_spans(text, stored)))
        m4["new"].append(coverage(case, quote_spans(text, new[label]["rebound"])))
        located_only = {t: s for t, s in view["located_spans"].items() if t not in view["other_texts"]}
        m4["new_located_only"].append(coverage(case, quote_spans(text, new[label]["rebound"], located_only)))
        views[case] = view
    done = list(views.values())
    return {
        "run": run, "arm": arm, "cases": len(recs), "rebound": len(done),
        "old_binder_reproduces_stored": sum(v["old_identical"] for v in done),
        "rest_of_trace_identical": sum(v["rest_identical"] for v in done),
        "written_citations_split": sum(v["split"] for v in done),
        "cases_with_a_split": sum(v["split"] > 0 for v in done),
        "written_citations_kept_merged": sum(v["merged_fallback"] for v in done),
        "pieces_stored": sum(v["pieces_stored"] for v in done),
        "pieces_found_more_than_once": sum(v["ambiguous_pieces"] for v in done),
        "gapped_quotes_refused_by_the_cap": sum(v["cap_refused"] for v in done),
        "other_citations": sum(v["other_citations"] for v in done),
        "other_citations_identical": all(v["other_identical"] for v in done),
        "citation_order_matches_expansion": all(v["order_matches"] for v in done),
        "grounding_fields_changed": dict(changes),
        "grounding_changes": {c: v["grounding_change"] for c, v in views.items() if v["grounding_change"]},
        "grounding_consistent": all(v["grounding_consistent"] for v in done),
        "M4_stored_recount": mean(m4["stored"]),
        "M4_stored_reported": STORED_M4[run],
        "M4_without_stitched_reported": WITHOUT_STITCHED_M4[run],
        "M4_new": mean(m4["new"]),
        "M4_new_pieces_at_their_located_place": mean(m4["new_located_only"]),
        "split_cases": {c: v["piece_texts"] for c, v in views.items() if v["piece_texts"]},
    }


def report(summaries: list[dict], backend: Path) -> str:
    md = ["# Split-quote replay", "",
          f"Saved written traces re-bound by the pinned binder ({PINNED.relative_to(HERE).as_posix()}) and by the binder "
          f"at `{backend.as_posix()}`. No model was called.", "",
          "| Run (arm) | Re-bound | Pinned binder reproduces stored | Written quotes split | Kept merged (a piece "
          "found more than once) | Pieces stored | Pieces found more than once | Refused by the 2,000-character cap | "
          "Other citations byte-identical | Rest of trace identical | Grounding consistent | M4 stored (recount) | "
          "M4 without stitched (stored) | M4 new |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summaries:
        md.append(f"| {s['run']} ({s['arm']}) | {s['rebound']}/{s['cases']} | {s['old_binder_reproduces_stored']}/"
                  f"{s['rebound']} | {s['written_citations_split']} in {s['cases_with_a_split']} cases | "
                  f"{s['written_citations_kept_merged']} | {s['pieces_stored']} | {s['pieces_found_more_than_once']} | "
                  f"{s['gapped_quotes_refused_by_the_cap']} | {s['other_citations']}, "
                  f"{'yes' if s['other_citations_identical'] and s['citation_order_matches_expansion'] else 'NO'} | "
                  f"{s['rest_of_trace_identical']}/{s['rebound']} | {'yes' if s['grounding_consistent'] else 'NO'} | "
                  f"{s['M4_stored_reported']:.3f} ({s['M4_stored_recount']:.3f}) | "
                  f"{s['M4_without_stitched_reported']:.3f} | {s['M4_new']:.3f} |")
    md.append("")
    for s in summaries:
        changed = ", ".join(f"{field} in {n} traces" for field, n in s["grounding_fields_changed"].items()) or "none"
        md += [f"- {s['arm']}: grounding fields that changed: {changed}. M4 with each piece counted only where it was "
               f"located: {s['M4_new_pieces_at_their_located_place']:.3f}."]
    return "\n".join(md) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=Path)
    parser.add_argument("--bind", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.bind:
        bind_all(args.bind.resolve(), args.out)
        return
    backend = args.backend.resolve()
    with tempfile.TemporaryDirectory() as scratch:
        old = bound_by(PINNED, Path(scratch), "pinned")
        new = bound_by(backend, Path(scratch), "split")
    summaries = [summarise(run, arm, old, new) for run, arm in RUNS]
    (HERE / "results" / "split_quote_replay.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=1),
                                                              encoding="utf-8")
    text = report(summaries, backend)
    (HERE / "results" / "split_quote_replay.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
