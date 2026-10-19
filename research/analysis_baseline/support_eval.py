"""Support flags (branch feat/support-flags) against CASIE realis, as README.md fixes it. No model is called.

  python support_eval.py          the fixed test: main cases 1-250
  python support_eval.py --dry    the traces of pilot_20260930_060711, outside cases 1-250
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CODE = Path(os.environ.get("SUPPORT_CODE", "F:/cc-worktrees/support-flags/backend"))
sys.path.insert(0, str(CODE))
from app.sources.bundle import CaseSourceItem  # noqa: E402
from app.trace import support  # noqa: E402
from app.trace.claims import CaseAnalysisClaim  # noqa: E402
from app.trace.quotes import quote_occurrences  # noqa: E402

CASIE = Path("F:/CASIE/data/annotation")
FROZEN = "a19723d0084b99a1"
SEED, DRAWS = 2026, 2000
RUNS = {"main": ("main_20260928_081639", "main_20260930_020141", "main_20260930_062138"),
        "dry": ("pilot_20260930_060711",)}
ARMS = ("cybercase", "single")
REALIS_FLAGS = {"stronger_than_source", "hypothetical_as_fact", "polarity"}
WINDOW_GROUPS = ("uncertain", "pending", "hypothetical")
CLAIM_GROUPS = ("uncertain", "pending", "hypothetical", "negation")
SOURCE_ID = "SRC-1"


def lf_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def normalise(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


def aligned(content: str, start: int, end: int, text: str) -> tuple[int, int] | None:
    for shift in (0, -1, 1, -2, 2):
        if start + shift >= 0 and normalise(content[start + shift:end + shift]) == normalise(text):
            return start + shift, end + shift
    return None


def nuggets(case_id: str) -> tuple[str, list[tuple[int, int, str]], int]:
    doc = json.loads((CASIE / f"{case_id}.json").read_text(encoding="utf-8"))
    content = doc["content"]
    found, unaligned = [], 0
    for hopper in doc.get("cyberevent", {}).get("hopper", []):
        for event in hopper.get("events", []):
            nugget = event["nugget"]
            span = aligned(content, nugget["startOffset"], nugget["endOffset"], nugget["text"])
            if span is None:
                unaligned += 1
                continue
            found.append((span[0], span[1], event.get("realis")))
    return content, found, unaligned


def clustered(per_case: dict[str, list[float]], stat) -> tuple[float, float, float]:
    ids = sorted(per_case)
    matrix = np.array([per_case[c] for c in ids], dtype=float)
    rng = np.random.default_rng(SEED)
    with np.errstate(divide="ignore", invalid="ignore"):
        point = stat(matrix.sum(axis=0))
        draws = [stat(matrix[rng.integers(0, len(ids), len(ids))].sum(axis=0)) for _ in range(DRAWS)]
    valid = [d for d in draws if d == d]
    low, high = np.percentile(valid, [2.5, 97.5]) if valid else (float("nan"), float("nan"))
    return float(point), float(low), float(high)


def ci(values: tuple[float, float, float], signed: bool = False) -> str:
    if values[0] != values[0]:
        return "—"
    sign = "+" if signed else ""
    return f"{values[0]:{sign}.3f} [{values[1]:{sign}.3f}, {values[2]:{sign}.3f}]"


def ratio(a: int, b: int):
    return lambda v: v[a] / v[b]


def level_a(ids: list[str], texts: dict) -> tuple[list[str], dict]:
    rows = []
    for case_id in ids:
        content, found, _ = texts[case_id]
        for start, end, realis in found:
            if realis not in ("Actual", "Other"):
                continue
            window = support.sentence_window(content, start, end)
            groups = {group for group in (*WINDOW_GROUPS, "negation") if support.cues(window, group)}
            rows.append((case_id, realis == "Other", groups))
    predictors = {"uncertain, pending or hypothetical (fixed)": set(WINDOW_GROUPS),
                  **{f"{group} alone": {group} for group in (*WINDOW_GROUPS, "negation")},
                  "all four groups (descriptive)": {*WINDOW_GROUPS, "negation"}}
    other = sum(o for _, o, _ in rows)
    lines = [f"Nuggets marked Actual or Other: {len(rows)} in {len(ids)} articles; Other {other} "
             f"({other / max(1, len(rows)):.3f}, what precision would be by chance).", "",
             "| Predict Other when the sentence holds | Flagged | Precision | Recall | F1 |", "|---|---|---|---|---|"]
    report = {"nuggets": len(rows), "other": other, "predictors": {}}
    for name, groups in predictors.items():
        per_case: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        for case_id, is_other, found in rows:
            predicted = bool(found & groups)
            counts = per_case[case_id]
            counts[0] += predicted and is_other
            counts[1] += predicted
            counts[2] += is_other
            counts[3] += 1
        precision = clustered(per_case, ratio(0, 1))
        recall = clustered(per_case, ratio(0, 2))
        f1 = clustered(per_case, lambda v: 2 * v[0] / (v[1] + v[2]))
        flagged = int(sum(v[1] for v in per_case.values()))
        lines.append(f"| {name} | {flagged} | {ci(precision)} | {ci(recall)} | {ci(f1)} |")
        report["predictors"][name] = {"flagged": flagged, "precision": precision, "recall": recall, "f1": f1}
    return lines, report


def claim_rows(runs: tuple[str, ...], ids: set[str], arm: str, texts: dict) -> tuple[list[dict], int]:
    rows, failed = [], 0
    for run in runs:
        for line in (HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["arm"] != arm or record.get("run", 1) != 1 or record["case"] not in ids:
                continue
            if "error" in record:
                failed += 1
                continue
            raw = HERE / "results" / f"raw_{run}" / f"{record['case']}_{arm}_1.json"
            bound = json.loads(raw.read_text(encoding="utf-8"))["bound"]
            content, found, _ = texts[record["case"]]
            registry = {SOURCE_ID: CaseSourceItem(source_id=SOURCE_ID, source_kind="narrative", text=content)}
            claims = [CaseAnalysisClaim.model_validate(claim) for claim in bound["claims"]]
            kinds: dict[str, set[str]] = defaultdict(set)
            for flag in support.support_flags(claims, registry):
                kinds[flag.claim_id].add(flag.kind)
            source_numbers = support.numbers(content)
            for claim in claims:
                spans, repeated = [], 0
                for citation in claim.supporting_citations:
                    occurrences = quote_occurrences(content, citation.exact_quote)
                    if citation.source_id != SOURCE_ID or not occurrences:
                        continue
                    repeated += len(occurrences) > 1
                    spans.append((occurrences[0], occurrences[0] + len(citation.exact_quote)))
                row = {"case": record["case"], "claim_id": claim.claim_id, "evidence": bool(spans),
                       "kinds": sorted(kinds[claim.claim_id]), "repeated_quotes": repeated, "quotes": len(spans)}
                if spans:
                    realis = {value for start, end, value in found if value in ("Actual", "Other")
                              and any(start < q_end and q_start < end for q_start, q_end in spans)}
                    _, quotes, window = support.claim_evidence(claim, registry)
                    added = support.numbers(claim.text) - support.numbers(window)
                    row |= {
                        "label": ("Other" if realis == {"Other"} else "Actual" if realis == {"Actual"}
                                  else "mixed" if realis else "none"),
                        "asserting": claim.epistemic_status == "reported" and claim.claim_type == "reported",
                        "source_cue": bool(support.cues(window, *WINDOW_GROUPS) or support.cues(quotes, "negation")),
                        "claim_cue": bool(support.cues(claim.text, *CLAIM_GROUPS)),
                        "added_elsewhere": len(added & source_numbers),
                        "added_nowhere": len(added - source_numbers),
                    }
                rows.append(row)
    return rows, failed


def realis_flagged(row: dict) -> bool:
    return bool(REALIS_FLAGS & set(row["kinds"]))


def fate(row: dict) -> str:
    if realis_flagged(row):
        return "flagged"
    if not row["asserting"]:
        return "not asserted"
    if not row["source_cue"]:
        return "no cue in the quoted sentence"
    return "the claim kept a cue" if row["claim_cue"] else "other (should not happen)"


def level_b(arm: str, rows: list[dict], failed: int, primary: bool) -> tuple[list[str], dict]:
    evidence = [r for r in rows if r["evidence"]]
    labeled = [r for r in evidence if r["label"] in ("Actual", "Other")]
    labels = Counter(r["label"] for r in evidence)
    per_case: dict[str, list[float]] = defaultdict(lambda: [0.0] * 6)
    for r in labeled:
        counts, other, flagged = per_case[r["case"]], r["label"] == "Other", realis_flagged(r)
        counts[0] += flagged and other
        counts[1] += flagged
        counts[2] += other
        counts[3] += 1
        counts[4] += flagged and not other
        counts[5] += not other
    precision = clustered(per_case, ratio(0, 1))
    chance = clustered(per_case, ratio(2, 3))
    lift = clustered(per_case, lambda v: v[0] / v[1] - v[2] / v[3])
    separation = clustered(per_case, lambda v: v[0] / v[2] - v[4] / v[5])
    on_other = clustered(per_case, ratio(0, 2))
    on_actual = clustered(per_case, ratio(4, 5))
    kinds = Counter(kind for r in rows for kind in r["kinds"])
    flagged_claims = sum(bool(r["kinds"]) for r in rows)
    fates = Counter(fate(r) for r in labeled if r["label"] == "Other")
    by_kind = {kind: Counter(r["label"] for r in labeled if kind in r["kinds"]) for kind in sorted(REALIS_FLAGS)}
    detail = [r for r in evidence if "unsupported_detail" in r["kinds"]]
    title = f"### {arm}" + (" (primary)" if primary else " (descriptive)")
    lines = [title, "",
             f"- Traces: {len({r['case'] for r in rows})} cases ({failed} runs failed and left no trace). Claims "
             f"{len(rows)}, with a quote found in the source {len(evidence)}. Labels: Actual {labels['Actual']}, "
             f"Other {labels['Other']}, mixed {labels['mixed']}, no nugget in the quotes {labels['none']}.",
             f"- Claims with any flag: {flagged_claims} of {len(rows)} ({flagged_claims / max(1, len(rows)):.3f}). "
             f"Flags by kind: {dict(sorted(kinds.items()))}.",
             f"- **Flag precision minus chance:** {ci(lift, True)}. Precision {ci(precision)}; chance (share of Other "
             f"among {len(labeled)} labeled claims) {ci(chance)}.",
             f"- **Separation:** {ci(separation, True)}. Flag rate on Other-labeled claims {ci(on_other)}, on "
             f"Actual-labeled claims {ci(on_actual)}.",
             "- Labels of the claims each rule flagged: " + "; ".join(
                 f"{kind} Other {c['Other']}, Actual {c['Actual']}" for kind, c in by_kind.items()) + ".",
             "- Where the Other-labeled claims went: " + "; ".join(f"{k} {n}" for k, n in fates.most_common()) + ".",
             f"- unsupported_detail on {len(detail)} claims: every added number is elsewhere in the source on "
             f"{sum(r['added_nowhere'] == 0 for r in detail)}; at least one is nowhere in it on "
             f"{sum(r['added_nowhere'] > 0 for r in detail)} (numbers elsewhere "
             f"{sum(r['added_elsewhere'] for r in detail)}, nowhere {sum(r['added_nowhere'] for r in detail)}).",
             f"- Quotes that occur more than once in the source: {sum(r['repeated_quotes'] for r in evidence)} of "
             f"{sum(r['quotes'] for r in evidence)}.", ""]
    report = {"cases": len({r["case"] for r in rows}), "failed_runs": failed, "claims": len(rows),
              "with_evidence": len(evidence), "labels": dict(labels), "flagged_claims": flagged_claims,
              "flags_by_kind": dict(kinds), "precision": precision, "chance": chance, "precision_minus_chance": lift,
              "separation": separation, "flag_rate_other": on_other, "flag_rate_actual": on_actual,
              "labels_by_kind": {k: dict(v) for k, v in by_kind.items()}, "other_fates": dict(fates),
              "unsupported_detail": {"claims": len(detail),
                                     "all_elsewhere": sum(r["added_nowhere"] == 0 for r in detail),
                                     "some_nowhere": sum(r["added_nowhere"] > 0 for r in detail)}}
    return lines, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()
    checker = lf_sha(CODE / "app" / "trace" / "support.py")
    if not checker.startswith(FROZEN):
        raise SystemExit(f"support.py is {checker[:16]}, not the frozen {FROZEN}")
    sample = "dry" if args.dry else "main"
    rows = [json.loads(line) for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines()]
    ids = [r["id"] for r in rows if r["sample"] == "pilot"] if args.dry else [
        r["id"] for r in rows if r["sample"] == "main"][:250]
    texts = {case_id: nuggets(case_id) for case_id in ids}
    unaligned = sum(t[2] for t in texts.values())
    lines = [f"# Support flags against CASIE realis ({sample})", "",
             f"support.py sha256 {checker[:16]}…, support_eval.py sha256 {lf_sha(Path(__file__))[:16]}…. "
             f"Articles {len(ids)}; nuggets not realigned {unaligned}.", "", "## Level A: the cue reader alone", ""]
    a_lines, a_report = level_a(ids, texts)
    lines += a_lines + ["", "## Level B: the flags on the claims the system wrote", ""]
    report = {"sample": sample, "support_sha256": checker, "eval_sha256": lf_sha(Path(__file__)),
              "articles": len(ids), "unaligned_nuggets": unaligned, "level_a": a_report, "level_b": {}}
    for arm in ARMS:
        claim_list, failed = claim_rows(RUNS[sample], set(ids), arm, texts)
        b_lines, b_report = level_b(arm, claim_list, failed, arm == "cybercase")
        lines += b_lines
        report["level_b"][arm] = b_report
    (HERE / "results" / f"support_eval_{sample}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (HERE / "results" / f"support_eval_{sample}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
