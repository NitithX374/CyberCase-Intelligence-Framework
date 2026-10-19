"""Error piles: every gold fact, written quote and report quote in exactly one pile, by fixed rules. No model call.

  python error_piles.py                                  the final system (main_20260930_193646), all cases
  python error_piles.py --run main_20260930_020141 --arm cybercase
  python error_piles.py --run main_20260930_020141 --arm cybercase --cases 10049,10246,10081    the pilot, every item

The rules are book_scores.py's, imported, so the piles add up to the book's numbers by construction; the checks at the
end of the output say whether they do. The report piles read the RQ2 v2 runs and do not depend on --run. A full run
writes results/error_piles.md and .json, and for the final system results/error_piles_samples.md. The 3-case pilot
that fixed these piles is kept unchanged as error_piles_pilot.py.
"""
from __future__ import annotations

import argparse
import difflib
import json
from collections import Counter

import numpy as np

import book_scores as bs

COVERAGE = ("cited and stated by the same claim", "cited, stated in another part", "cited, not stated anywhere",
            "stated, not cited", "missed", "case failed")
BINDER = ("exact", "unicode-normalised", "stitched by a middle ellipsis", "markup or quote style ignored",
          "dropped: every word kept, in order", "dropped: words changed", "dropped: longer than the limit")
REPORT = ("kept", "cut shorter", "extended", "words changed", "missing from the report")
FINAL_M4, FINAL_M4B = "0.928", "0.775"
VERDICT = "wording only / really not stated / gold problem"


def coverage_pile(case: dict, trace: dict, fact: dict) -> str:
    """Where a main-event fact stands: cited and stated by one claim, cited only, stated only, or neither."""
    if bs.stating(case, trace["claims"], fact):
        return COVERAGE[0]
    anywhere = bs.states(bs.own_text(trace), case, fact)
    if bs.citing(case, trace["claims"], fact):
        return COVERAGE[1] if anywhere else COVERAGE[2]
    return COVERAGE[3] if anywhere else COVERAGE[4]


def binder_pile(text: str, quote: str) -> str:
    """The first step of the pinned binder's chain that finds a written quote, or why the binder dropped it."""
    why = bs.dropped_because(text, quote)
    if why is not None:
        return f"dropped: {why}"
    stripped = bs.without_edge_ellipses(quote)
    if bs.quote_occurrences(text, stripped):
        return BINDER[0]
    if bs.find_folded_quote(text, stripped) is not None:
        return BINDER[1]
    if bs.expand_unique_ellipsis_quote(text, stripped) is not None:
        return BINDER[2]
    return BINDER[3]


def report_pile(want: str, shown: list[str]) -> str:
    """A trace quote against the claim's own report quotes of the same role, all normalised."""
    if want in shown:
        return REPORT[0]
    if not shown:
        return REPORT[4]
    best = max(shown, key=lambda s: difflib.SequenceMatcher(None, want, s).ratio())
    return REPORT[1] if best in want else REPORT[2] if want in best else REPORT[3]


def report_piles(trace: dict, report: object) -> list[dict]:
    """One pile per trace quote for one report; a malformed report keeps nothing."""
    rows = bs.rows_by_claim(trace, report) if isinstance(report, dict) else {}
    out = []
    for claim in trace["claims"]:
        mine = rows.get(claim["claim_id"], [])
        for role, field in (("supporting_citations", "supporting_quotes"),
                            ("contradicting_citations", "contradicting_quotes")):
            shown = [bs.normalise(q) for row in mine for q in row.get(field) or []]
            for citation in claim[role]:
                want = bs.normalise(citation["exact_quote"])
                out.append({"claim": claim["claim_id"], "chars": len(want), "pile": report_pile(want, shown)})
    return out


def sentence_at(text: str, start: int, end: int) -> str:
    """The article text from the sentence end before the span to the sentence end after it."""
    marks = (". ", "! ", "? ", "\n")
    left = max((text.rfind(m, 0, start) + len(m) for m in marks if text.rfind(m, 0, start) >= 0), default=0)
    right = min((text.find(m, end) + 1 for m in marks if text.find(m, end) >= 0), default=len(text))
    return " ".join(text[left:right].split())


def views_of(run: str, arm: str) -> dict[str, dict]:
    """book_scores' loader, for any run and arm: the scored records by case, failed cases marked."""
    bs.ARMS = {**bs.ARMS, "piles": (run, arm)}
    return bs.arm("piles")


def analysis_piles(views: dict[str, dict]) -> dict[str, dict]:
    out = {}
    for case_id, view in views.items():
        case = view["case"]
        if not view["done"]:
            out[case_id] = {"coverage": [{"role": f["role"], "fact": f["text"], "pile": COVERAGE[5]} for f in bs.lead(case)],
                            "binder": []}
            continue
        trace, text = view["trace"], case["text"]
        out[case_id] = {
            "coverage": [{"role": f["role"], "fact": f["text"], "citing": bs.citing(case, trace["claims"], f),
                          "stating": bs.stating(case, trace["claims"], f), "pile": coverage_pile(case, trace, f)}
                         for f in bs.lead(case)],
            "binder": [{"claim": c["claim_id"], "chars": len(q), "pile": binder_pile(text, q)}
                       for c in view["written"]["claims"] for q in bs.quotes_of(c)],
        }
    return out


def all_report_piles() -> dict[str, dict[str, list[dict]]]:
    out = {}
    for folder in sorted(p for p in bs.RQ2.iterdir() if (p / "trace.json").exists()):
        trace = json.loads((folder / "trace.json").read_text(encoding="utf-8"))
        out[folder.name] = {arm: [dict(item, run=k) for k in (1, 2, 3) for item in report_piles(
            trace, json.loads((folder / arm / f"run_{k}.json").read_text(encoding="utf-8")))]
            for arm in ("arm_a", "arm_b")}
    return out


def checks(views: dict, piles: dict, reports: dict, run: str, arm: str) -> list[str]:
    lines = []
    m4 = {c: bs.m4(v["case"], v["trace"]) if v["done"] else 0.0 for c, v in views.items()}
    m4b = {c: bs.m4b(v["case"], v["trace"]) if v["done"] else 0.0 for c, v in views.items()}
    cited = {c: bs.share(i["pile"] in COVERAGE[:3] for i in p["coverage"]) for c, p in piles.items()}
    both = {c: bs.share(i["pile"] == COVERAGE[0] for i in p["coverage"]) for c, p in piles.items()}
    if cited != m4 or both != m4b:
        raise SystemExit("STOP: the coverage piles do not add up to book_scores' M4 and M4b case by case.")
    final = (run, arm) == bs.ARMS["final"]
    for name, values, book in (("M4", cited, FINAL_M4), ("M4b", both, FINAL_M4B)):
        mean = float(np.mean(list(values.values())))
        lines.append(f"- Coverage piles: the mean per-case share of {'piles 1-3' if name == 'M4' else 'pile 1'} is "
                     f"{mean:.3f}, equal to book_scores' {name} case by case"
                     + (f"; the book prints {book}: {'match' if f'{mean:.3f}' == book else 'NO MATCH'}." if final else "."))
    done = [v for v in views.values() if v["done"]]
    claimed = sum(v["record"]["grounding"]["citations_claimed"] for v in done)
    verified = sum(v["record"]["grounding"]["citations_verified"] for v in done)
    duplicated = sum(v["record"]["grounding"].get("citations_duplicated", 0) for v in done)
    dropped = sum(i["pile"].startswith("dropped") for p in piles.values() for i in p["binder"])
    in_repeated = 0
    for v in done:
        seen = set()
        for claim in v["written"]["claims"]:
            if claim["claim_id"] in seen:
                in_repeated += sum(binder_pile(v["case"]["text"], q).startswith("dropped") for q in bs.quotes_of(claim))
            seen.add(claim["claim_id"])
    foreign = sum(c["source_id"] != "SRC-1" for v in done for claim in v["written"]["claims"]
                  for c in claim["supporting_citations"] + claim["contradicting_citations"])
    lines.append(f"- Binder piles: {dropped} written quotes dropped; M2's claimed minus verified is {claimed:,} - "
                 f"{verified:,} = {claimed - verified}: {'match' if dropped == claimed - verified else 'NO MATCH'}.")
    if dropped != claimed - verified:
        lines.append(f"  - The difference is {dropped - (claimed - verified):+d}. claimed - verified also holds the "
                     f"{duplicated} quotes the binder kept but stored once (citations_duplicated); the piles count "
                     f"{in_repeated} dropped quotes of claims whose id repeats an earlier claim, which the binder removes "
                     f"before counting; {foreign} written quotes name a source other than SRC-1.")
    for name, label, book in (("arm_a", "Arm A", "2,630/2,709"), ("arm_b", "Arm B", "2,709/2,709")):
        items = [i for r in reports.values() for i in r[name]]
        kept = f"{sum(i['pile'] == REPORT[0] for i in items):,}/{len(items):,}"
        lines.append(f"- Report piles, {label}: kept {kept}; Table 5-14 prints {book}: {'match' if kept == book else 'NO MATCH'}.")
    return lines


def samples(views: dict, piles: dict) -> str:
    pile = [(c, i) for c in sorted(piles) for i in piles[c]["coverage"] if i["pile"] == COVERAGE[2]]
    picks = np.random.default_rng(2026).choice(len(pile), size=min(20, len(pile)), replace=False)
    md = ["# Twenty samples from \"cited, not stated anywhere\" (final system, cases 151-250)", "",
          f"The pile holds {len(pile)} facts, ordered by case id and then by the gold file. "
          f"{len(picks)} were drawn with numpy default_rng(2026), without replacement, and are listed in the order drawn.",
          ""]
    rows = []
    for n, index in enumerate(picks, 1):
        case_id, item = pile[index]
        case, trace = views[case_id]["case"], views[case_id]["trace"]
        fact = next(f for f in bs.lead(case) if f["role"] == item["role"] and f["text"] == item["fact"])
        surfaces = sorted({case["text"][s:e] for s, e in fact["spans"]})
        md += [f"## {n}. Case {case_id}, {fact['role']}", "",
               f"- **Gold fact, article text at its spans:** {' | '.join(repr(s) for s in surfaces)} "
               f"(spans {', '.join(f'{s}-{e}' for s, e in fact['spans'])})"]
        for cid in item["citing"]:
            claim = next(c for c in trace["claims"] if c["claim_id"] == cid)
            over = [q for q in bs.quotes_of(claim) if bs.pointed_at(fact, bs.positions(case["text"], q))]
            md += [f"- **Citing claim {cid}:** {claim['text']}",
                   *(f"  - Quote over the span: \"{q}\"" for q in over)]
        md += [*(f"- **Article sentence:** {sentence_at(case['text'], s, e)}" for s, e in fact["spans"][:1]),
               f"- **Owner's verdict ({VERDICT}):**", ""]
        rows.append(f"| {n} | {case_id} | {fact['role']} | {surfaces[0]} | {', '.join(item['citing'])} | |")
    md += ["## Verdicts", "", f"Write one of: {VERDICT}.", "",
           "| # | Case | Role | Gold fact | Citing claims | Owner's verdict |", "|---|---|---|---|---|---|", *rows, ""]
    return "\n".join(md)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=bs.ARMS["final"][0])
    parser.add_argument("--arm", default=bs.ARMS["final"][1])
    parser.add_argument("--cases", default="")
    args = parser.parse_args()
    views = views_of(args.run, args.arm)
    if args.cases:
        for case_id in args.cases.split(","):
            item = analysis_piles({case_id: views[case_id]})[case_id]
            print(f"\n######## case {case_id}")
            for i in item["coverage"]:
                print(f"   {i['role']:17s} {i['fact'][:45]!r:48s} cited by {','.join(i.get('citing', [])) or '-':12s} "
                      f"stated by {','.join(i.get('stating', [])) or '-':10s} -> {i['pile']}")
            for pile, n in Counter(i["pile"] for i in item["binder"]).items():
                print(f"   binder: {pile:40s} {n:3d}")
        return
    piles, reports = analysis_piles(views), all_report_piles()
    totals = {"coverage": Counter(i["pile"] for p in piles.values() for i in p["coverage"]),
              "binder": Counter(i["pile"] for p in piles.values() for i in p["binder"]),
              "report, Arm A": Counter(i["pile"] for r in reports.values() for i in r["arm_a"]),
              "report, Arm B": Counter(i["pile"] for r in reports.values() for i in r["arm_b"])}
    order = {"coverage": COVERAGE, "binder": BINDER, "report, Arm A": REPORT, "report, Arm B": REPORT}
    md = [f"# Error piles: {args.arm} ({args.run}); report piles from RQ2 v2", "",
          "Every item sits in exactly one pile, by the rules of book_scores.py. No model was called.", ""]
    for name, counter in totals.items():
        md += [f"## {name.capitalize()}: {sum(counter.values()):,} items", "", "| Pile | Items |", "|---|---|"]
        md += [f"| {pile} | {counter[pile]:,} |" for pile in order[name]] + [""]
    md += ["## Checks", "", *checks(views, piles, reports, args.run, args.arm), ""]
    (bs.HERE / "results" / "error_piles.md").write_text("\n".join(md), encoding="utf-8")
    (bs.HERE / "results" / "error_piles.json").write_text(json.dumps(
        {"run": args.run, "arm": args.arm, "totals": totals, "cases": piles, "reports": reports},
        ensure_ascii=False, indent=1), encoding="utf-8")
    if (args.run, args.arm) == bs.ARMS["final"]:
        (bs.HERE / "results" / "error_piles_samples.md").write_text(samples(views, piles), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
