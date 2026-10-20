"""Outcomes per target and per-arm measures (README.md protocol). No model call.

  python score.py --run run_<stamp>

Writes results/score_<stamp>.md (counts only, no article text) and results/score_<stamp>.json (per target).
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

import numpy as np
from pythainlp.tokenize import word_tokenize

from facts import normalized

HERE = Path(__file__).resolve().parent
TOKEN_CAP = 40_800
CORRUPTED_ARMS = ("targeted", "realistic")
OUTCOMES = {"substitution": ("propagated", "restored", "mixed", "flagged", "omitted"),
            "deletion": ("restored", "flagged", "omitted")}
CATEGORIES = ("number", "place", "other")


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def joined(parts) -> str:
    return " | ".join(normalized(part) for part in parts if part)


def surfaces(saved: dict, statuses: str) -> tuple[str, str, str]:
    """R (reported surface), F (flagged surface) and all model text, by the written or the bound statuses."""
    bound, reading = saved["bound"], saved.get("reading") or {}
    written = {c["claim_id"]: c["epistemic_status"] for c in reading.get("claims", [])}
    status = (lambda c: written.get(c["claim_id"], c["epistemic_status"])) if statuses == "written" else (
        lambda c: c["epistemic_status"])
    structure = [bound["summary"]]
    structure += [f"{p['name']} {p['role']}" for p in bound["involved_parties"]]
    structure += [f"{t['time']} {t['event']}" for t in bound["timeline"]]
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


def asks(record: dict) -> tuple[int, int]:
    failed = record.get("error", "").removeprefix("CaseAnalysisFailure: ")
    reasks = invalid = 0
    for stage, n in Counter(call["stage"] for call in record["calls"]).items():
        reasks += n - 1
        replies = [c for c in record["calls"] if c["stage"] == stage and c["stop_reason"] is not None]
        ended = sum(c["stop_reason"] not in ("max_tokens", "length") and (c["output_tokens"] or 0) < TOKEN_CAP
                    for c in replies)
        invalid += ended - (0 if failed.startswith(f"{stage}_") else 1 if ended else 0)
    return reasks, invalid


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    stamp = args.run.removeprefix("run_")
    articles = {a["id"]: a for a in jsonl(HERE / "data" / "articles.jsonl")}
    order = list(articles)
    records = {(r["article"], r["arm"]): r for r in jsonl(HERE / "results" / f"{args.run}.jsonl")}
    raw = HERE / "results" / f"raw_{stamp}"

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
        claimed = sum(r["grounding"]["citations_claimed"] for r in done)
        verified = sum(r["grounding"]["citations_verified"] for r in done)
        quotes = {"written": 0, "written_with_corrupted": 0, "written_with_original": 0, "verified": 0,
                  "verified_with_corrupted": 0}
        rouge[arm] = {}
        for r in done:
            result = saved(r["article"], arm)
            rouge[arm][r["article"]] = rouge_l(result["bound"]["summary"], articles[r["article"]]["summary"])
            forms = [(normalized(t["corrupted"]), normalized(t["surface"])) for t in articles[r["article"]]["targets"]
                     if t["type"] == "substitution"]
            written = [normalized(q["exact_quote"]) for c in (result["reading"] or {}).get("claims", [])
                       for q in c["supporting_citations"] + c["contradicting_citations"]]
            bound = [normalized(q["exact_quote"]) for c in result["bound"]["claims"]
                     for q in c["supporting_citations"] + c["contradicting_citations"]]
            quotes["written"] += len(written)
            quotes["verified"] += len(bound)
            if arm != "clean":
                quotes["written_with_corrupted"] += sum(any(c in q for c, _ in forms) for q in written)
                quotes["written_with_original"] += sum(any(o in q for _, o in forms) for q in written)
                quotes["verified_with_corrupted"] += sum(any(c in q for c, _ in forms) for q in bound)
        counted = [asks(r) for r in rows]
        calls = [c for r in rows for c in r["calls"]]
        measures[arm] = {
            "runs": len(rows), "completed": len(done),
            "failures": dict(Counter(r["error"] for r in rows if "error" in r)),
            "m2": [verified, claimed, verified / claimed if claimed else None], "quotes": quotes,
            "calls_to_cap": sum(c["stop_reason"] in ("max_tokens", "length") or (c["output_tokens"] or 0) >= TOKEN_CAP
                                for c in calls),
            "reasks": sum(x for x, _ in counted), "invalid_replies": sum(y for _, y in counted),
            "median_model_seconds": statistics.median(sum(c["ms"] for c in r["calls"]) / 1000 for r in rows),
            "usd": sum(c["usd"] for c in calls), "usd_per_article": sum(c["usd"] for c in calls) / len(rows),
            "rouge_l": float(np.mean(list(rouge[arm].values()))) if rouge[arm] else None,
        }
    for arm in CORRUPTED_ARMS:
        if arm in rouge and "clean" in rouge:
            both = sorted(set(rouge[arm]) & set(rouge["clean"]))
            d = np.array([rouge[arm][a] - rouge["clean"][a] for a in both])
            measures[arm]["rouge_l_minus_clean"] = [float(d.mean()), *interval(len(d), lambda i: float(d[i].mean())),
                                                    len(both)]

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

    out = {"run": args.run, "excluded_targets": dict(excluded), "tables": tables, "measures": measures,
           "hypotheses": hypotheses, "units": units}
    (HERE / "results" / f"score_{stamp}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                         encoding="utf-8")

    def pct(cell: dict, name: str) -> str:
        if name not in cell:
            return "-"
        x = cell[name]
        return f"{x['count']} ({x['share']:.2f} [{x['interval'][0]:.2f}, {x['interval'][1]:.2f}])"

    md = [f"# OCR errors and the downstream analysis: scores ({args.run})", "",
          f"Targets left out before scoring: {dict(excluded)}.", ""]
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
    md += ["## Per arm", "", "| Arm | Completed | Failures | M2 verified quotes | Written quotes with a corrupted form | "
           "Written quotes with the original form | Bound-trace quotes with a corrupted form | ROUGE-L F1 | ROUGE-L − clean "
           "| Calls to cap | Invalid replies | Re-asks | Median model s | USD |", "|---" * 14 + "|"]
    for arm, m in measures.items():
        q = m["quotes"]
        diff = m.get("rouge_l_minus_clean")
        md.append(f"| {arm} | {m['completed']}/{m['runs']} | {m['failures'] or 'none'} | "
                  f"{m['m2'][0]}/{m['m2'][1]} = {m['m2'][2]:.3f} | {q['written_with_corrupted']}/{q['written']} | "
                  f"{q['written_with_original']}/{q['written']} | {q['verified_with_corrupted']}/{q['verified']} | "
                  f"{m['rouge_l']:.3f} | "
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
    (HERE / "results" / f"score_{stamp}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
