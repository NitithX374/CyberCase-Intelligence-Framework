"""Scores, report part: M6, report preservation (RQ2 v2, Table 5-14), with the evaluator's claim mapping and quote rule.
"""
from __future__ import annotations

import json
import unicodedata

from scores_common import ROOT, frac, quotes_of, row

# ================================================================================================= RULES


def normalise(text: object) -> str:
    """The report evaluator's text rule (evaluator_v2.py): NFKC, whitespace collapsed to single spaces."""
    return " ".join(unicodedata.normalize("NFKC", str(text or "")).split())


def rows_by_claim(trace: dict, report: dict) -> dict[str, list[dict]]:
    """The report rows of each trace claim: by the row's claim_ids when it has them, otherwise by normalised text."""
    ids, by_text, rows = {c["claim_id"] for c in trace["claims"]}, {}, {}
    for claim in trace["claims"]:
        by_text.setdefault(normalise(claim["text"]), []).append(claim["claim_id"])
    for row in (r for r in report.get("findings") or [] if isinstance(r, dict)):  # noqa: F402
        mapped = ([cid for cid in dict.fromkeys(row.get("claim_ids") or []) if cid in ids] if "claim_ids" in row
                  else by_text.get(normalise(row.get("text")), []))
        for cid in mapped:
            rows.setdefault(cid, []).append(row)
    return rows


def kept_by_report(trace: dict, report: object) -> tuple[int, int]:
    """Claims a report keeps (at least one row) and trace quotes it keeps among the same claim's quotes of that role."""
    if not isinstance(report, dict):
        return 0, 0
    rows, claims, quotes = rows_by_claim(trace, report), 0, 0
    for claim in trace["claims"]:
        mine = rows.get(claim["claim_id"], [])
        claims += bool(mine)
        for role, field in (("supporting_citations", "supporting_quotes"),
                            ("contradicting_citations", "contradicting_quotes")):
            shown = {normalise(q) for row in mine for q in row.get(field) or []}
            quotes += sum(normalise(c["exact_quote"]) in shown for c in claim[role])
    return claims, quotes


def identical(reports: list) -> bool:
    """A trace's reports are all present and identical as canonical JSON."""
    texts = [None if r is None else json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
             for r in reports]
    return None not in texts and len(set(texts)) == 1


def strings(node) -> list[str]:
    """Every string value in a report, depth first."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [s for value in node.values() for s in strings(value)]
    if isinstance(node, list):
        return [s for value in node for s in strings(value)]
    return []


# ================================================================================================= DATA

RQ2 = ROOT / "research" / "report_fidelity" / "runs_v2" / "main"


def report_preservation() -> None:
    folders = sorted(p for p in RQ2.iterdir() if p.is_dir())
    scored = [p for p in folders if (p / "trace.json").exists()]
    row("5-14", "traces selected, traces scored", f"{len(folders)}, {len(scored)}", "50, 48")
    book = {"arm_b": ("2,601/2,601", "2,709/2,709", "2,709/2,709", "2,709/2,709", "0/144", "48/48"),
            "arm_a": ("2,561/2,601", "2,630/2,709", "2,586/2,709 = 0.955", "2,638/2,709 = 0.974", "3/144", "0/48")}
    for name, b in book.items():
        claims = quotes = kept_claims = kept_quotes = verbatim = normalised = malformed = same = lost = 0
        for folder in scored:
            trace = json.loads((folder / "trace.json").read_text(encoding="utf-8"))
            reports = [json.loads((folder / name / f"run_{k}.json").read_text(encoding="utf-8")) for k in (1, 2, 3)]
            wanted = [q for c in trace["claims"] for q in quotes_of(c)]
            for report in reports:
                k_claims, k_quotes = kept_by_report(trace, report)
                claims, quotes = claims + len(trace["claims"]), quotes + len(wanted)
                kept_claims, kept_quotes = kept_claims + k_claims, kept_quotes + k_quotes
                malformed += not isinstance(report, dict)
                lost += 0 if isinstance(report, dict) else len(trace["claims"])
                text = "\n".join(strings(report))
                verbatim += sum(q in text for q in wanted)
                normalised += sum(normalise(q) in normalise(text) for q in wanted)
            same += identical(reports)
        full = name == "arm_b"
        row("5-14", f"{name}: claims kept", frac(kept_claims, claims, False), b[0])
        row("5-14", f"{name}: quotes kept in the claim's own row, normalised", frac(kept_quotes, quotes, False), b[1])
        row("5-14", f"{name}: quotes found verbatim anywhere", frac(verbatim, quotes, not full), b[2])
        row("5-14", f"{name}: quotes found after NFKC and whitespace", frac(normalised, quotes, not full), b[3])
        row("5-14", f"{name}: malformed reports", frac(malformed, 3 * len(scored), False), b[4])
        row("5-14", f"{name}: traces whose three reports are identical", frac(same, len(scored), False), b[5])
        if name == "arm_a":
            row("5-14", "arm_a: claims lost (of them in the malformed reports)", f"{claims - kept_claims} ({lost})",
                "40 (40)")
            row("5-14", "arm_a: quotes changed only in spacing or Unicode / cut, extended or dropped",
                f"{normalised - verbatim} / {quotes - normalised}", "52 / 71")
    for case, claim_id, b in (("10078", "A-01", "22 -> 79 (extended)"),
                              ("10081", "A-05", "340 -> 96 (cut to its end)")):
        trace = json.loads((RQ2 / case / "trace.json").read_text(encoding="utf-8"))
        report = json.loads((RQ2 / case / "arm_a" / "run_1.json").read_text(encoding="utf-8"))
        claim = next(c for c in trace["claims"] if c["claim_id"] == claim_id)
        shown = [q for r in rows_by_claim(trace, report).get(claim_id, []) for q in r.get("supporting_quotes") or []]
        changes = [f"{len(w)} -> {len(s)} (extended)" if w in s else f"{len(w)} -> {len(s)} (cut to its end)"
                   for w in quotes_of(claim) if w not in shown for s in shown if s != w and (w in s or w.endswith(s))]
        row("5-14", f"{case} {claim_id}, Arm A run 1: trace quotes changed, characters before -> after",
            "; ".join(changes), b, agrees=b in changes)
