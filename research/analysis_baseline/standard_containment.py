"""Standard answer containment of README.md (M5-std and M4b), read from saved runs. No model is called.

  python standard_containment.py

Writes results/standard_containment.json and results/standard_containment.md.
"""
from __future__ import annotations

import json
import re
import string
import unicodedata
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED, DRAWS = 2026, 2000
CASES = {r["id"]: r for r in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
ARMS = (
    ("main_20260930_020141", "prose"),
    ("main_20260930_020141", "single"),
    ("main_20260930_020141", "cybercase"),
    ("main_20260930_062138", "cybercase"),
    ("main_20260930_193646", "cybercase_nogrammar"),
)
LABELS = {
    ("main_20260930_020141", "prose"): "prose, 51-150",
    ("main_20260930_020141", "single"): "single, 51-150",
    ("main_20260930_020141", "cybercase"): "cybercase, 51-150",
    ("main_20260930_062138", "cybercase"): "shipped cybercase, 151-250",
    ("main_20260930_193646", "cybercase_nogrammar"): "cybercase_nogrammar, 151-250",
}
TRACEABILITY_M4 = {
    ("main_20260930_020141", "single"): ("design", "a"),
    ("main_20260930_020141", "cybercase"): ("design", "b"),
    ("main_20260930_062138", "cybercase"): ("decoding", "a"),
    ("main_20260930_193646", "cybercase_nogrammar"): ("decoding", "b"),
}
DESIGN = [
    ("M4b", ("main_20260930_020141", "single"), ("main_20260930_020141", "cybercase")),
    ("M5std", ("main_20260930_020141", "single"), ("main_20260930_020141", "cybercase")),
    ("M5std", ("main_20260930_020141", "prose"), ("main_20260930_020141", "cybercase")),
    ("M5std", ("main_20260930_020141", "prose"), ("main_20260930_020141", "single")),
]
DECODING = [
    ("M4b", ("main_20260930_062138", "cybercase"), ("main_20260930_193646", "cybercase_nogrammar")),
    ("M5std", ("main_20260930_062138", "cybercase"), ("main_20260930_193646", "cybercase_nogrammar")),
]


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def v0_norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


def v0_contains(haystack: str, needle: str) -> bool:
    return f" {needle} " in f" {haystack} "


def records(run: str, arm: str) -> dict[str, dict]:
    rows = [json.loads(line) for line in (HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines()]
    return {r["case"]: r for r in rows if r["arm"] == arm and r.get("run", 1) == 1
            and r.get("error_kind") not in ("budget", "harness")}


def saved(run: str, arm: str, case: str) -> dict:
    return json.loads((HERE / "results" / f"raw_{run}" / f"{case}_{arm}_1.json").read_text(encoding="utf-8"))


def own_text(trace: dict) -> str:
    parts = [trace["summary"]]
    parts += [f"{p['name']} {p['role']}" for p in trace["involved_parties"]]
    parts += [f"{t['time']} {t['event']}" for t in trace["timeline"]]
    parts += [f"{c['text']} {c['reasoning_summary'] or ''}" for c in trace["claims"]]
    parts += [i["description"] for i in trace["impacts"]]
    parts += [f"{g['topic']} {g['description']}" for g in trace["gaps"]]
    return "\n".join(parts)


def written_text(run: str, arm: str, case: str) -> tuple[str, dict | None]:
    if arm == "prose":
        return (HERE / "results" / f"raw_{run}" / f"{case}_prose_1.txt").read_text(encoding="utf-8"), None
    bound = saved(run, arm, case)["bound"]
    return own_text(bound), bound


def key(fact: dict) -> str:
    return f"{fact['role']}|{fact['text']}"


def lead_facts(case_id: str) -> list[dict]:
    return [f for f in CASES[case_id]["gold"] if f["lead"]]


def surfaces(case_id: str, fact: dict) -> list[str]:
    text = CASES[case_id]["text"]
    return [normalize_answer(text[s:e]) for s, e in fact["spans"]]


def stated(normalised_text: str, forms: list[str]) -> bool:
    return any(form and form in normalised_text for form in forms)


def claim_spans(source: str, claim: dict) -> list[tuple[int, int]]:
    found = []
    for citation in claim["supporting_citations"] + claim["contradicting_citations"]:
        quote = citation["exact_quote"]
        start = source.find(quote)
        while start >= 0:
            found.append((start, start + len(quote)))
            start = source.find(quote, start + 1)
    return found


def overlaps(fact: dict, found: list[tuple[int, int]]) -> bool:
    return any(a < fe and b > fs for fs, fe in fact["spans"] for a, b in found)


def case_view(run: str, arm: str, record: dict) -> dict:
    case_id = record["case"]
    lead = lead_facts(case_id)
    forms = {key(f): surfaces(case_id, f) for f in lead}
    empty = sum(not any(forms[key(f)]) for f in lead)
    if "error" in record:
        return {"done": False, "lead": len(lead), "empty_forms": empty, "M5std": 0.0, "M5": 0.0, "M4": 0.0, "M4b": 0.0}
    text, bound = written_text(run, arm, case_id)
    v0 = sorted(key(f) for f in lead if v0_contains(v0_norm(text), f["text"]))
    standard = normalize_answer(text)
    view = {
        "done": True,
        "lead": len(lead),
        "empty_forms": empty,
        "v0": v0,
        "v0_matches_record": v0 == sorted(record["stated_lead"]),
        "M5": len(record["stated_lead"]) / record["gold_lead"],
        "stated": sorted(key(f) for f in lead if stated(standard, forms[key(f)])),
        "standard_text": standard,
    }
    view["M5std"] = len(view["stated"]) / len(lead)
    if bound is not None:
        source = CASES[case_id]["text"]
        pointing, both = {}, {}
        for claim in bound["claims"]:
            found = claim_spans(source, claim)
            says = normalize_answer(claim["text"])
            for f in lead:
                if overlaps(f, found):
                    pointing.setdefault(key(f), []).append(claim["claim_id"])
                    if stated(says, forms[key(f)]):
                        both.setdefault(key(f), []).append(claim["claim_id"])
        view.update({"M4": len(pointing) / len(lead), "M4b": len(both) / len(lead),
                     "m4_claims": pointing, "m4b_claims": both})
    return view


def floor(views: dict[str, dict]) -> dict:
    ids = sorted(views)
    scores = []
    for index, case_id in enumerate(ids):
        view = views[case_id]
        if not view["done"]:
            continue
        other = ids[(index + 1) % len(ids)]
        facts = lead_facts(other)
        scores.append(sum(stated(view["standard_text"], surfaces(other, f)) for f in facts) / len(facts))
    return {"value": float(np.mean(scores)), "n": len(scores)}


def interval(values: list[float]) -> list[float]:
    return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]


def paired(differences: np.ndarray) -> dict:
    rng = np.random.default_rng(SEED)
    draws = [differences[rng.integers(0, len(differences), len(differences))].mean() for _ in range(DRAWS)]
    return {"difference": float(differences.mean()), "ci": interval(draws), "n": len(differences)}


def compare(metric: str, a: dict[str, dict], b: dict[str, dict]) -> dict:
    ids = sorted(set(a) & set(b))
    both = [c for c in ids if a[c]["done"] and b[c]["done"]]
    out = {"failures_zero": paired(np.array([b[c][metric] - a[c][metric] for c in ids]))}
    if metric == "M4b":
        out["completed_in_both"] = paired(np.array([b[c][metric] - a[c][metric] for c in both]))
    return out


def word(interval_: list[float]) -> str:
    return "difference" if interval_[0] > 0 or interval_[1] < 0 else "not shown"


def main() -> None:
    views = {arm: {c: case_view(*arm, r) for c, r in records(*arm).items()} for arm in ARMS}
    mismatches = [f"{arm[0]} {arm[1]} {c}" for arm, vs in views.items() for c, v in vs.items()
                  if v["done"] and not v["v0_matches_record"]]
    if mismatches:
        raise SystemExit(f"V0 does not reproduce for {len(mismatches)} records: {mismatches[:20]}")
    stored = json.loads((HERE / "results" / "traceability.json").read_text(encoding="utf-8"))
    summary = {}
    for arm in ARMS:
        vs = views[arm]
        done = [v for v in vs.values() if v["done"]]
        row = {
            "cases": len(vs),
            "completed": len(done),
            "M5": float(np.mean([v["M5"] for v in vs.values()])),
            "M5std": float(np.mean([v["M5std"] for v in vs.values()])),
            "floor": floor(vs),
            "lead_facts": sum(v["lead"] for v in vs.values()),
            "empty_form_facts": sum(v["empty_forms"] for v in vs.values()),
        }
        if arm[1] != "prose":
            row["M4"] = float(np.mean([v["M4"] for v in vs.values()]))
            row["M4b"] = float(np.mean([v["M4b"] for v in vs.values()]))
            row["M4b_completed"] = float(np.mean([v["M4b"] for v in done]))
            section, side = TRACEABILITY_M4[arm]
            row["M4_equals_traceability"] = abs(row["M4"] - stored[section][side]["M4"]) < 1e-12
        summary[arm] = row
    if not all(row.get("M4_equals_traceability", True) for row in summary.values()):
        raise SystemExit("M4 from this code differs from traceability.py")
    comparisons = {name: [{"metric": metric, "a": a, "b": b, **compare(metric, views[a], views[b])}
                          for metric, a, b in pairs] for name, pairs in (("design", DESIGN), ("decoding", DECODING))}

    worked = views[("main_20260930_020141", "cybercase")]["10049"]
    record = records("main_20260930_020141", "cybercase")["10049"]
    rows_10049 = []
    for f in lead_facts("10049"):
        k = key(f)
        rows_10049.append({
            "fact": f"{f['text']} ({f['role']})",
            "normalised_gold": sorted(set(surfaces("10049", f))),
            "m4_claims": worked["m4_claims"].get(k, []),
            "m4b_claims": worked["m4b_claims"].get(k, []),
            "v0_mentioned": k in record["stated_lead"],
            "m5std_stated": k in worked["stated"],
        })

    md = ["# Standard answer containment (M5-std and M4b)", "",
          "Read from saved runs; no model was called. Fixed in README.md (2026-10-01) before any figure was computed.", "",
          f"V0 reproduced from the saved traces for every completed record of every arm "
          f"({sum(r['completed'] for r in summary.values())} records); M4 from this code equals traceability.py for the "
          "four structured arms.", "",
          "| Run | Completed | M5 mention (V0) | M5-std stated | Chance floor (n) | M4 cited | M4b cited and stated "
          "(completed only) | Lead facts with an empty normalised form |",
          "|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        r = summary[arm]
        m4 = f"{r['M4']:.3f}" if "M4" in r else "—"
        m4b = f"{r['M4b']:.3f} ({r['M4b_completed']:.3f})" if "M4b" in r else "—"
        md.append(f"| {LABELS[arm]} | {r['completed']}/{r['cases']} | {r['M5']:.3f} | {r['M5std']:.3f} | "
                  f"{r['floor']['value']:.3f} ({r['floor']['n']}) | {m4} | {m4b} | "
                  f"{r['empty_form_facts']}/{r['lead_facts']} |")
    for name, items in comparisons.items():
        md += ["", f"## {name.capitalize()}", ""]
        for item in items:
            label = f"{item['metric'].replace('M5std', 'M5-std')}, {item['b'][1]} − {item['a'][1]}"
            d = item["failures_zero"]
            md.append(f"- {label} (failures 0, n={d['n']}): {d['difference']:+.3f} "
                      f"[{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}] -> {word(d['ci'])}.")
            if "completed_in_both" in item:
                d = item["completed_in_both"]
                md.append(f"- {label} (completed in both, n={d['n']}): {d['difference']:+.3f} "
                          f"[{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}] -> {word(d['ci'])}.")
    md += ["", "## Worked case 10049 (cybercase, cases 51-150)", "",
           "| Gold fact (role) | Normalised gold | M4 claims | M4b claims | V0 mentioned | M5-std stated |",
           "|---|---|---|---|---|---|"]
    for row in rows_10049:
        md.append(f"| {row['fact']} | {', '.join(row['normalised_gold'])} | {', '.join(row['m4_claims']) or '—'} | "
                  f"{', '.join(row['m4b_claims']) or '—'} | {'yes' if row['v0_mentioned'] else 'no'} | "
                  f"{'yes' if row['m5std_stated'] else 'no'} |")
    md.append(f"| **Total** | | **{sum(bool(r['m4_claims']) for r in rows_10049)}/{len(rows_10049)}** | "
              f"**{sum(bool(r['m4b_claims']) for r in rows_10049)}/{len(rows_10049)}** | "
              f"**{sum(r['v0_mentioned'] for r in rows_10049)}/{len(rows_10049)}** | "
              f"**{sum(r['m5std_stated'] for r in rows_10049)}/{len(rows_10049)}** |")

    out = {"summary": {f"{run}|{arm}": row for (run, arm), row in summary.items()},
           "comparisons": comparisons, "worked_10049": rows_10049}
    (HERE / "results" / "standard_containment.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (HERE / "results" / "standard_containment.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
