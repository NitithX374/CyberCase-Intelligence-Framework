"""Error piles: sort every gold fact, written quote and report quote into exactly one pile by fixed rules. No model call.

  python error_piles.py --cases 10049,10246,10081      pilot, every item shown
  python error_piles.py                               all cases, totals only
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import string
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "pinned" / "1e29bd3" / "backend"))

from app.trace.quotes import (  # noqa: E402
    MAX_QUOTE_CHARS,
    expand_unique_ellipsis_quote,
    find_aligned_quote,
    find_folded_quote,
    quote_occurrences,
    without_edge_ellipses,
)

RUN, ARM = "main_20260930_020141", "cybercase"
RQ2 = HERE.parents[1] / "research" / "report_fidelity" / "runs_v2" / "main"
CASES = {r["id"]: r for r in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
COVERAGE = ("cited and stated by the same claim", "cited, stated in another part", "cited, not stated anywhere",
            "stated, not cited", "missed")
BINDER = ("exact", "unicode-normalised", "stitched by a middle ellipsis", "markup or quote style ignored",
          "dropped: every word present in order", "dropped: words changed", "dropped: longer than the limit")
REPORT = ("kept", "cut shorter", "extended", "words changed", "missing from the report")


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def stated(surfaces: list[str], text: str) -> bool:
    haystack = normalize_answer(text)
    return any(n and n in haystack for n in (normalize_answer(s) for s in surfaces))


def own_text(trace: dict) -> str:
    parts = [trace["summary"]]
    parts += [f"{p['name']} {p['role']}" for p in trace["involved_parties"]]
    parts += [f"{t['time']} {t['event']}" for t in trace["timeline"]]
    parts += [f"{c['text']} {c.get('reasoning_summary') or ''}" for c in trace["claims"]]
    parts += [i["description"] for i in trace["impacts"]]
    parts += [f"{g['topic']} {g['description']}" for g in trace["gaps"]]
    return "\n".join(parts)


def positions(text: str, quote: str) -> list[tuple[int, int]]:
    found, start = [], text.find(quote)
    while start >= 0:
        found.append((start, start + len(quote)))
        start = text.find(quote, start + 1)
    return found


def coverage(case_id: str, bound: dict) -> list[dict]:
    case = CASES[case_id]
    text, written = case["text"], own_text(bound)
    out = []
    for fact in (f for f in case["gold"] if f["lead"]):
        surfaces = [text[s:e] for s, e in fact["spans"]]
        citing = [c["claim_id"] for c in bound["claims"]
                  if any(a < fe and b > fs for q in c["supporting_citations"] + c["contradicting_citations"]
                         for a, b in positions(text, q["exact_quote"]) for fs, fe in fact["spans"])]
        same = [cid for cid in citing if stated(surfaces, next(c["text"] for c in bound["claims"] if c["claim_id"] == cid))]
        anywhere = stated(surfaces, written)
        pile = (COVERAGE[0] if same else COVERAGE[1] if citing and anywhere else COVERAGE[2] if citing
                else COVERAGE[3] if anywhere else COVERAGE[4])
        out.append({"role": fact["role"], "fact": surfaces[0], "citing": citing, "same": same, "pile": pile})
    return out


def in_order(source_tokens: list[str], pieces: list[list[str]]) -> bool:
    at = 0
    for piece in pieces:
        hit = next((i for i in range(at, len(source_tokens) - len(piece) + 1)
                    if source_tokens[i:i + len(piece)] == piece), None)
        if hit is None:
            return False
        at = hit + len(piece)
    return True


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower())


def binder_outcome(text: str, quote: str) -> str:
    stripped = without_edge_ellipses(quote)
    if quote_occurrences(text, stripped):
        found, pile = stripped, BINDER[0]
    elif (folded := find_folded_quote(text, stripped)) is not None:
        found, pile = folded, BINDER[1]
    elif (expanded := expand_unique_ellipsis_quote(text, stripped)) is not None:
        found, pile = expanded, BINDER[2]
    elif (relaxed := find_aligned_quote(text, stripped)) is not None:
        found, pile = relaxed, BINDER[3]
    else:
        pieces = [tokens(p) for p in re.split(r"(?:\.{3,}|…+)", stripped)]
        return BINDER[4] if in_order(tokens(text), [p for p in pieces if p]) else BINDER[5]
    return pile if len(found) <= MAX_QUOTE_CHARS else BINDER[6]


def binder(case_id: str, written: dict) -> list[dict]:
    text = CASES[case_id]["text"]
    return [{"claim": c["claim_id"], "chars": len(q["exact_quote"]), "pile": binder_outcome(text, q["exact_quote"])}
            for c in written["claims"] for q in c["supporting_citations"] + c["contradicting_citations"]]


def flat(text: object) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(text or "")).split())


def report(case_id: str) -> list[dict]:
    folder = RQ2 / case_id
    if not (folder / "scores.json").exists():
        return []
    trace = json.loads((folder / "trace.json").read_text(encoding="utf-8"))
    ids = {c["claim_id"] for c in trace["claims"]}
    by_text: dict[str, list[str]] = {}
    for claim in trace["claims"]:
        by_text.setdefault(flat(claim["text"]), []).append(claim["claim_id"])
    out = []
    for run in (1, 2, 3):
        body = json.loads((folder / "arm_a" / f"run_{run}.json").read_text(encoding="utf-8"))
        rows: dict[str, list[dict]] = {}
        for finding in (body.get("findings") or []) if isinstance(body, dict) else []:
            if not isinstance(finding, dict):
                continue
            mapped = ([cid for cid in dict.fromkeys(finding.get("claim_ids") or []) if cid in ids]
                      if "claim_ids" in finding else by_text.get(flat(finding.get("text")), []))
            for cid in mapped:
                rows.setdefault(cid, []).append(finding)
        for claim in trace["claims"]:
            for role, key in (("supporting_citations", "supporting_quotes"), ("contradicting_citations", "contradicting_quotes")):
                shown = [flat(q) for row in rows.get(claim["claim_id"], []) for q in row.get(key) or []]
                for citation in claim[role]:
                    want = flat(citation["exact_quote"])
                    if want in shown:
                        pile = REPORT[0]
                    elif not shown:
                        pile = REPORT[4]
                    else:
                        best = max(shown, key=lambda s: difflib.SequenceMatcher(None, want, s).ratio())
                        pile = REPORT[1] if best in want else REPORT[2] if want in best else REPORT[3]
                    out.append({"run": run, "claim": claim["claim_id"], "chars": len(want), "pile": pile})
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="")
    args = parser.parse_args()
    raw = HERE / "results" / f"raw_{RUN}"
    records = {r["case"]: r for r in map(json.loads, (HERE / "results" / f"{RUN}.jsonl").read_text(encoding="utf-8").splitlines())
               if r["arm"] == ARM and r.get("run", 1) == 1}
    chosen = args.cases.split(",") if args.cases else sorted(records)
    totals = {"coverage": Counter(), "binder": Counter(), "report": Counter()}
    for case_id in chosen:
        record = records[case_id]
        rows_report = report(case_id)
        if "error" in record:
            rows_cov = [{"role": f["role"], "fact": f["text"], "citing": [], "same": [], "pile": "case failed"}
                        for f in CASES[case_id]["gold"] if f["lead"]]
            rows_bind = []
        else:
            data = json.loads((raw / f"{case_id}_{ARM}_1.json").read_text(encoding="utf-8"))
            rows_cov, rows_bind = coverage(case_id, data["bound"]), binder(case_id, data["written"])
        for name, rows in (("coverage", rows_cov), ("binder", rows_bind), ("report", rows_report)):
            totals[name].update(r["pile"] for r in rows)
        if args.cases:
            print(f"\n######## case {case_id}")
            print("-- coverage (each main-event gold fact)")
            for r in rows_cov:
                print(f"   {r['role']:17s} {r['fact'][:45]!r:48s} cited by {','.join(r['citing']) or '-':12s} "
                      f"stated by the same claim {','.join(r['same']) or '-':10s} -> {r['pile']}")
            print("-- binder (each quote the model wrote)")
            for pile, n in Counter(r["pile"] for r in rows_bind).items():
                claims = ",".join(r["claim"] for r in rows_bind if r["pile"] == pile)
                print(f"   {pile:40s} {n:3d}   claims {claims if pile != BINDER[0] else '(all others)'}")
            print("-- report, LLM writer (each trace quote x 3 runs)" + ("" if rows_report else ": not in the RQ2 sample"))
            for pile, n in Counter(r["pile"] for r in rows_report).items():
                where = ", ".join(f"run {r['run']} {r['claim']}" for r in rows_report if r["pile"] == pile)
                print(f"   {pile:40s} {n:3d}   {where if pile != REPORT[0] else ''}")
    print("\n######## totals over", len(chosen), "cases")
    for name, counter in totals.items():
        print(f"{name}: {sum(counter.values())} items -> {dict(counter)}")


if __name__ == "__main__":
    main()
