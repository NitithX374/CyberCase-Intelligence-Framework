"""Outcomes per target and per-arm measures (PROTOCOL.md), on the current trace shape. No model call.

  python score_current.py --run run_<stamp>
  python score_current.py --run run_<stamp> --results-dir <folder>

Writes <results>/score_<stamp>.md (counts only, no article text) and <results>/score_<stamp>.json (per target).
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import statistics  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
from pythainlp.tokenize import word_tokenize  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
sys.path.insert(0, str(EXPERIMENT))

from facts import normalized  # noqa: E402

SAMPLE_SIZE = 100
STAGE_CAPS = {"case_reading": 32_608, "case_judgement": 32_608 + 2_048, "case_views": 4_096}
CORRUPTED_ARMS = ("targeted", "realistic")
OUTCOMES = {"substitution": ("propagated", "restored", "mixed", "flagged", "omitted"),
            "deletion": ("restored", "flagged", "omitted")}
CATEGORIES = ("number", "place", "other")
CLAIM_BRACKETS = re.compile(r"\[\s*A-\d{2,}(?:\s*,\s*A-\d{2,})*\s*\]")


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def joined(parts) -> str:
    return " | ".join(normalized(part) for part in parts if part)


def summary_text(bound: dict) -> str:
    return CLAIM_BRACKETS.sub(" ", bound["summary"])


def written_statuses(reading: dict | None) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for claim in (reading or {}).get("claims", []):
        statuses.setdefault(claim["claim_id"], claim["epistemic_status"])
    return statuses


def surfaces(saved: dict, statuses: str) -> tuple[str, str, str]:
    """R (reported surface), F (flagged surface) and all model text, by the written or the bound statuses."""
    bound = saved["bound"]
    written = written_statuses(saved.get("reading"))
    status = (lambda c: written.get(c["claim_id"], c["epistemic_status"])) if statuses == "written" else (
        lambda c: c["epistemic_status"])
    structure = [summary_text(bound)]
    structure += [f"{p['name']} {p.get('role') or ''}" for p in bound["involved_parties"]]
    structure += [f"{t.get('time') or ''} {t['event']}" for t in bound["timeline"]]
    structure += [i["description"] for i in bound["impacts"]]
    reported = [c["text"] for c in bound["claims"] if status(c) == "reported"]
    other = [c["text"] for c in bound["claims"] if status(c) != "reported"]
    gaps = [part for g in bound["gaps"] for part in (g["description"], g.get("clarification_question"))]
    return joined(structure + reported), joined(other + gaps), joined(structure + reported + other)


def classify(kind: str, original: str, corrupted: str, r: str, f: str) -> str:
    if kind == "substitution":
        if corrupted in r and original in r:
            return "mixed"
        if corrupted in r:
            return "propagated"
        if original in r:
            return "restored"
        return "flagged" if corrupted in f or original in f else "omitted"
    if original in r:
        return "restored"
    return "flagged" if original in f else "omitted"


def tokens(text: str) -> list[str]:
    return [t for t in word_tokenize(normalized(text), engine="newmm", keep_whitespace=False) if t.strip()]


def rouge_l(candidate: str, reference: str) -> float:
    a, b = tokens(candidate), tokens(reference)
    if not a or not b:
        return 0.0
    previous = [0] * (len(b) + 1)
    for x in a:
        current = [0]
        for j, y in enumerate(b, 1):
            current.append(previous[j - 1] + 1 if x == y else max(previous[j], current[j - 1]))
        previous = current
    lcs = previous[-1]
    if lcs == 0:
        return 0.0
    precision, recall = lcs / len(a), lcs / len(b)
    return 2 * precision * recall / (precision + recall)


def interval(n: int, statistic) -> tuple[float, float]:
    rng = np.random.default_rng(2026)
    draws = [d for d in (statistic(rng.integers(0, n, n)) for _ in range(2000)) if d is not None]
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def shares(units: list[dict], articles: list[str], kind: str) -> dict:
    index = {a: i for i, a in enumerate(articles)}
    counts = np.zeros((len(articles), len(OUTCOMES[kind])), dtype=float)
    for unit in units:
        counts[index[unit["article"]], OUTCOMES[kind].index(unit["outcome"])] += 1
    total = counts.sum()
    out = {"n": int(total)}
    if not total:
        return out
    rng_draws = []
    rng = np.random.default_rng(2026)
    for _ in range(2000):
        picked = counts[rng.integers(0, len(articles), len(articles))].sum(axis=0)
        if picked.sum():
            rng_draws.append(picked / picked.sum())
    draws = np.array(rng_draws)
    for k, outcome in enumerate(OUTCOMES[kind]):
        out[outcome] = {"count": int(counts[:, k].sum()), "share": float(counts[:, k].sum() / total),
                        "interval": [float(np.percentile(draws[:, k], 2.5)), float(np.percentile(draws[:, k], 97.5))]}
    return out


def to_cap(call: dict) -> bool:
    cap = call.get("request_max_tokens") or STAGE_CAPS.get(call["stage"], 0)
    return call["stop_reason"] in ("max_tokens", "length") or (call["output_tokens"] or 0) >= cap > 0


def asks(record: dict) -> tuple[int, int]:
    failed = record.get("error", "").removeprefix("CaseAnalysisFailure: ")
    reasks = invalid = 0
    for stage, n in Counter(call["stage"] for call in record["calls"]).items():
        reasks += n - 1
        replies = [c for c in record["calls"] if c["stage"] == stage and c["stop_reason"] is not None]
        ended = sum(not to_cap(c) for c in replies)
        view_failed = stage == "case_views" and ((record.get("facts") or {}).get("views") or {}).get("status") == "failed"
        invalid += ended - (0 if failed.startswith(f"{stage}_") or view_failed else 1 if ended else 0)
    return reasks, invalid


def selected_unit_ids(reading: dict | None) -> int:
    return sum(len(citation["evidence_unit_ids"]) for claim in (reading or {}).get("claims", [])
               for citation in claim["supporting_citations"] + claim.get("contradicting_citations", []))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--results-dir", default=str(HERE / "results"))
    args = parser.parse_args()
    results = Path(args.results_dir)
    stamp = args.run.removeprefix("run_")
    articles = {a["id"]: a for a in jsonl(EXPERIMENT / "data" / "articles.jsonl")[:SAMPLE_SIZE]}
    records = {(r["article"], r["arm"]): r for r in jsonl(results / f"{args.run}.jsonl")}
    ran = {a for a, _ in records}
    articles = {a: articles[a] for a in articles if a in ran}
    order = list(articles)
    raw = results / f"raw_{stamp}"

    def saved(article: str, arm: str) -> dict | None:
        record = records.get((article, arm))
        if record is None or "error" in record:
            return None
        return json.loads((raw / f"{article}_{arm}.json").read_text(encoding="utf-8"))

    units = {arm: {"written": [], "bound": []} for arm in CORRUPTED_ARMS}
    excluded = Counter()
    for article_id, article in articles.items():
        clean = saved(article_id, "clean")
        for target in article["targets"]:
            original = normalized(target["surface"])
            corrupted = normalized(target["corrupted"]) if target["type"] == "substitution" else ""
            if clean is None:
                excluded["clean run failed"] += 1
                continue
            if original not in surfaces(clean, "written")[2]:
                excluded["not in clean model text"] += 1
                continue
            for arm in CORRUPTED_ARMS:
                if (article_id, arm) not in records:
                    continue
                result = saved(article_id, arm)
                for statuses in ("written", "bound"):
                    unit = {"article": article_id, "category": target["category"], "type": target["type"]}
                    if result is None:
                        unit["outcome"] = "run failed"
                    else:
                        r, f, _ = surfaces(result, statuses)
                        unit["outcome"] = classify(target["type"], original, corrupted, r, f)
                    units[arm][statuses].append(unit)

    tables = {}
    for arm in CORRUPTED_ARMS:
        for statuses in ("written", "bound"):
            scored = [u for u in units[arm][statuses] if u["outcome"] != "run failed"]
            cells = {}
            for kind in OUTCOMES:
                cells[f"{kind}|all"] = shares([u for u in scored if u["type"] == kind], order, kind)
                for name in CATEGORIES:
                    cells[f"{kind}|{name}"] = shares(
                        [u for u in scored if u["type"] == kind and u["category"] == name], order, kind)
            tables[f"{arm}|{statuses}"] = {"cells": cells, "run_failed": sum(
                u["outcome"] == "run failed" for u in units[arm][statuses])}

    measures = {}
    rouge = {}
    for arm in ("clean", *CORRUPTED_ARMS):
        rows = [r for (a, m), r in records.items() if m == arm]
        if not rows:
            continue
        done = [r for r in rows if "error" not in r]
        quotes = {"selected_unit_ids": 0, "bound_citations": 0, "bound_with_corrupted": 0, "bound_with_original": 0}
        invalid_evidence: Counter = Counter()
        verdicts: Counter = Counter()
        views: Counter = Counter()
        hedged_claims = judged = claims_total = 0
        rouge[arm] = {}
        for r in done:
            result = saved(r["article"], arm)
            bound = result["bound"]
            rouge[arm][r["article"]] = rouge_l(summary_text(bound), articles[r["article"]]["summary"])
            forms = [(normalized(t["corrupted"]), normalized(t["surface"])) for t in articles[r["article"]]["targets"]
                     if t["type"] == "substitution"]
            cited = [normalized(q["exact_quote"]) for c in bound["claims"]
                     for q in c["supporting_citations"] + c["contradicting_citations"]]
            quotes["selected_unit_ids"] += selected_unit_ids(result.get("reading"))
            quotes["bound_citations"] += len(cited)
            if arm != "clean":
                quotes["bound_with_corrupted"] += sum(any(c in q for c, _ in forms) for q in cited)
                quotes["bound_with_original"] += sum(any(o in q for _, o in forms) for q in cited)
            invalid_evidence.update(i["reason"] for c in bound["claims"] for i in c["invalid_evidence"])
            verdicts.update(f"{c['semantic_grounding']['verdict']}:{c['semantic_grounding']['reason']}"
                            for c in bound["claims"] if c.get("semantic_grounding"))
            extraction = bound.get("view_extraction") or {}
            views[extraction.get("status", "absent")] += 1
            written = written_statuses(result.get("reading"))
            claims_total += len(bound["claims"])
            hedged_claims += sum(written.get(c["claim_id"], c["epistemic_status"]) != "reported"
                                 for c in bound["claims"])
            judged += len(extraction.get("input_claim_ids") or [])
        counted = [asks(r) for r in rows]
        calls = [c for r in rows for c in r["calls"]]
        measures[arm] = {
            "runs": len(rows), "completed": len(done),
            "failures": dict(Counter(r["error"] for r in rows if "error" in r)),
            "quotes": quotes, "invalid_evidence": dict(invalid_evidence), "verdicts": dict(verdicts),
            "views": dict(views), "claims": claims_total, "hedged_claims_written": hedged_claims,
            "claims_judged": judged,
            "calls_to_cap": sum(to_cap(c) for c in calls),
            "reasks": sum(x for x, _ in counted), "invalid_replies": sum(y for _, y in counted),
            "median_model_seconds": statistics.median(sum(c["ms"] for c in r["calls"]) / 1000 for r in rows),
            "usd": sum(c["usd"] for c in calls), "usd_per_article": sum(c["usd"] for c in calls) / len(rows),
            "usd_by_stage": {s: sum(c["usd"] for c in calls if c["stage"] == s) for s in STAGE_CAPS},
            "rouge_l": float(np.mean(list(rouge[arm].values()))) if rouge[arm] else None,
        }
    for arm in CORRUPTED_ARMS:
        if arm in rouge and "clean" in rouge:
            both = sorted(set(rouge[arm]) & set(rouge["clean"]))
            if both:
                d = np.array([rouge[arm][a] - rouge["clean"][a] for a in both])
                measures[arm]["rouge_l_minus_clean"] = [float(d.mean()),
                                                        *interval(len(d), lambda i: float(d[i].mean())), len(both)]

    def verdicts(arm: str) -> dict:
        cells = tables[f"{arm}|written"]["cells"]
        sub, dele = cells["substitution|all"], cells["deletion|all"]
        share = lambda cell, name: cell[name]["share"] if name in cell else 0.0  # noqa: E731
        return {
            "H1": {"restored_propagated_mixed": share(sub, "restored") + share(sub, "propagated") + share(sub, "mixed"),
                   "omitted": share(sub, "omitted")},
            "H2": {"omitted": share(dele, "omitted")},
            "H3": {"flagged_substitution": share(sub, "flagged"), "flagged_deletion": share(dele, "flagged")},
        }

    hypotheses = {arm: verdicts(arm) for arm in CORRUPTED_ARMS if f"{arm}|written" in tables}
    for arm, h in hypotheses.items():
        h["H1"]["holds"] = h["H1"]["restored_propagated_mixed"] > 0.5 and h["H1"]["omitted"] < 0.2
        h["H2"]["holds"] = h["H2"]["omitted"] > 0.5
        h["H3"]["holds"] = h["H3"]["flagged_substitution"] < 0.1 and h["H3"]["flagged_deletion"] < 0.1

    out = {"run": args.run, "articles": len(order), "excluded_targets": dict(excluded), "tables": tables,
           "measures": measures, "hypotheses": hypotheses, "units": units}
    (results / f"score_{stamp}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    def pct(cell: dict, name: str) -> str:
        if name not in cell:
            return "-"
        x = cell[name]
        return f"{x['count']} ({x['share']:.2f} [{x['interval'][0]:.2f}, {x['interval'][1]:.2f}])"

    md = [f"# OCR errors and the downstream analysis, current backend: scores ({args.run})", "",
          f"Articles scored: {len(order)}. Targets left out before scoring: {dict(excluded)}.", ""]
    for arm in CORRUPTED_ARMS:
        for statuses in ("written", "bound"):
            key = f"{arm}|{statuses}"
            if key not in tables:
                continue
            label = "primary, the model's written statuses" if statuses == "written" else \
                "sensitivity, bound statuses (not_confirmed counts as non-reported)"
            md += [f"## {arm}: {label}", "", f"Runs failed (targets not scored): {tables[key]['run_failed']}.", ""]
            for kind, names in OUTCOMES.items():
                md += [f"**{kind}**", "", "| Category | n | " + " | ".join(names) + " |",
                       "|---|---|" + "---|" * len(names)]
                for name in ("all", *CATEGORIES):
                    cell = tables[key]["cells"][f"{kind}|{name}"]
                    md.append(f"| {name} | {cell['n']} | " + " | ".join(pct(cell, o) for o in names) + " |")
                md.append("")
    md += ["## Per arm", "", "| Arm | Completed | Failures | Views (status: runs) | Claims / written hedged / judged | "
           "Selected unit IDs | Bound citations | Invalid references | Bound citations with a corrupted form | "
           "Bound citations with the original form | Verifier verdicts | ROUGE-L F1 | ROUGE-L − clean | Calls to cap | "
           "Invalid replies | Re-asks | Median model s | USD |", "|---" * 18 + "|"]
    for arm, m in measures.items():
        q = m["quotes"]
        diff = m.get("rouge_l_minus_clean")
        rouge_cell = f"{m['rouge_l']:.3f}" if m["rouge_l"] is not None else "-"
        md.append(f"| {arm} | {m['completed']}/{m['runs']} | {m['failures'] or 'none'} | {m['views']} | "
                  f"{m['claims']} / {m['hedged_claims_written']} / {m['claims_judged']} | {q['selected_unit_ids']} | "
                  f"{q['bound_citations']} | {m['invalid_evidence'] or 'none'} | "
                  f"{q['bound_with_corrupted']}/{q['bound_citations']} | {q['bound_with_original']}/{q['bound_citations']} | "
                  f"{m['verdicts']} | {rouge_cell} | "
                  + (f"{diff[0]:+.3f} [{diff[1]:+.3f}, {diff[2]:+.3f}] (n {diff[3]})" if diff else "-")
                  + f" | {m['calls_to_cap']} | {m['invalid_replies']} | {m['reasks']} | {m['median_model_seconds']:.0f} | "
                  f"{m['usd']:.4f} |")
    md += ["", "## Predictions (judged on the point estimate, primary statuses)", ""]
    for arm, h in hypotheses.items():
        md.append(f"- {arm}: H1 restored+propagated+mixed {h['H1']['restored_propagated_mixed']:.2f}, omitted "
                  f"{h['H1']['omitted']:.2f}: {'holds' if h['H1']['holds'] else 'does not hold'}. H2 omitted "
                  f"{h['H2']['omitted']:.2f}: {'holds' if h['H2']['holds'] else 'does not hold'}. H3 flagged "
                  f"{h['H3']['flagged_substitution']:.2f} (substitution), {h['H3']['flagged_deletion']:.2f} (deletion): "
                  f"{'holds' if h['H3']['holds'] else 'does not hold'}.")
    (results / f"score_{stamp}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
