"""Recounts for PROVENANCE.md, from saved files only. No model is called.

  python provenance_recount.py            all three parts
  python provenance_recount.py rq1        classifier: LADDER <-> MalwareTextDB, and the shipped checkpoint
  python provenance_recount.py m6         RQ2 v2 report preservation
  python provenance_recount.py examples   the worked cases of PROVENANCE.md
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GATE = ROOT / "experiments" / "gate_generalization"
LADDER_TEST = ROOT / "experiments" / "LADDER" / "attack_pattern" / "data" / "sentence_classification" / "test.csv"
RQ2 = ROOT / "research" / "report_fidelity" / "runs_v2" / "main"
HELDOUT = "main_20260930_020141"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def cells(y: np.ndarray, p: np.ndarray, t: float) -> tuple[int, int, int, int]:
    pred = p >= t
    return (int((pred & (y == 1)).sum()), int((pred & (y == 0)).sum()), int((~pred & (y == 1)).sum()),
            int((~pred & (y == 0)).sum()))


def rq1() -> None:
    print("== RQ1 classifier")
    with LADDER_TEST.open(encoding="utf-8") as handle:
        authors = [int(r["label"]) for r in csv.DictReader(handle, delimiter="\t")]
    shipped = jsonl(GATE / "results_run2" / "existing_xlmr_ladder" / "predictions" / "ft" / "ladder_test.jsonl")
    y = np.array([authors[int(r["id"].rsplit("-", 1)[1])] for r in shipped])
    p = np.array([r["prob"] for r in shipped])
    tp, fp, fn, tn = cells(y, p, 0.5)
    print(f"shipped checkpoint on LADDER test: {len(y)} sentences, {y.sum()} positive (authors' labels); AUROC "
          f"{roc_auc_score(y, p):.3f}; at 0.50 TP {tp} FP {fp} FN {fn} TN {tn}: precision {tp}/{tp + fp} = "
          f"{tp / (tp + fp):.3f}, recall {tp}/{tp + fn} = {tp / (tp + fn):.3f}")
    res, data = GATE / "results_xscheme", GATE / "data_xscheme"
    manifest = json.loads((res / "FROZEN_MANIFEST.json").read_text(encoding="utf-8"))
    changed = [k for k, v in manifest["files"]["data"].items()
               if hashlib.sha256((GATE / k.replace("\\", "/")).read_bytes()).hexdigest() != v]
    print(f"data files changed since the freeze: {changed or 'none'}")
    ladder = jsonl(data / "ladder_test.jsonl")
    print(f"LADDER test labels equal the authors' file: {[r['label'] for r in ladder] == authors}")

    def threshold(run: str) -> float:
        package = res / run / "model" / "gate_model.json"
        if package.exists():
            return 1 / (1 + np.exp(-json.loads(package.read_text())["source_threshold_logit"]))
        return json.loads((res / run / "config.json").read_text())["threshold_prob"]

    configs = {"E1 TF-IDF, LADDER": ["tfidf_ladder"], "E2 TF-IDF, MTDB": ["tfidf_mtdb"],
               "E3 XLM-R, LADDER": [f"xlmr_base_ladder_s{s}" for s in (42, 7, 123)],
               "E4 XLM-R, MTDB": [f"xlmr_base_mtdb_s{s}" for s in (42, 7, 123)],
               "E5 XLM-R+TAPT, LADDER": [f"xlmr_base_tapt_ladder_s{s}" for s in (42, 7, 123)]}
    for test in ("ladder_test", "mtdb_test"):
        gold = jsonl(data / f"{test}.jsonl")
        y = np.array([r["label"] for r in gold])
        print(f"-- test {test}: {len(y)} sentences, {y.sum()} positive; flag-every-sentence F1 "
              f"{2 * y.mean() / (1 + y.mean()):.3f}")
        for name, runs in configs.items():
            aucs, f1s, ps, rs, first = [], [], [], [], None
            for run in runs:
                by_id = {r["id"]: r["prob"] for r in jsonl(res / run / "predictions" / "ft" / f"{test}.jsonl")}
                prob = np.array([by_id[r["id"]] for r in gold])
                tp, fp, fn, _ = cells(y, prob, threshold(run))
                first = first or (run, tp, fp, fn)
                aucs.append(roc_auc_score(y, prob))
                ps.append(tp / (tp + fp))
                rs.append(tp / (tp + fn))
                f1s.append(2 * tp / (2 * tp + fp + fn))
            print(f"   {name:22s} AUROC {np.mean(aucs):.3f}  P {np.mean(ps):.3f}  R {np.mean(rs):.3f}  F1 {np.mean(f1s):.3f}"
                  f"   ({first[0]}: TP {first[1]} FP {first[2]} FN {first[3]})")


def strings(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [s for value in node.values() for s in strings(value)]
    if isinstance(node, list):
        return [s for value in node for s in strings(value)]
    return []


def m6() -> None:
    print("== M6 report preservation (RQ2 v2)")
    summary = json.loads((RQ2 / "summary.json").read_text(encoding="utf-8"))["arms"]
    folders = sorted(p for p in RQ2.iterdir() if (p / "scores.json").exists())
    for arm in ("arm_b", "arm_a"):
        runs = [run for f in folders for run in json.loads((f / "scores.json").read_text(encoding="utf-8"))["arms"][arm]["runs"]]
        identical = sum(json.loads((f / "scores.json").read_text(encoding="utf-8"))["arms"][arm]["agreement"]["identical"]
                        for f in folders)
        claims = (sum(r["claims_reported"] for r in runs), sum(r["claims"] for r in runs))
        quotes = (sum(r["quotes_preserved"] for r in runs), sum(r["quotes"] for r in runs))
        present = total = 0
        for folder in folders:
            trace = json.loads((folder / "trace.json").read_text(encoding="utf-8"))
            wanted = [q["exact_quote"] for c in trace["claims"]
                      for q in c["supporting_citations"] + c["contradicting_citations"]]
            for run in (1, 2, 3):
                text = "\n".join(strings(json.loads((folder / arm / f"run_{run}.json").read_text(encoding="utf-8"))))
                present += sum(q in text for q in wanted)
                total += len(wanted)
        stored = summary[arm]
        print(f"{arm}: {len(runs)} reports from {len(folders)} traces; malformed {sum(r['malformed'] for r in runs)}; "
              f"claims {claims[0]}/{claims[1]} (summary {stored['claim_preservation']['n']}/"
              f"{stored['claim_preservation']['of']}); quotes {quotes[0]}/{quotes[1]} (summary "
              f"{stored['exact_quotes']['n']}/{stored['exact_quotes']['of']}); identical reruns {identical}/{len(folders)}")
        print(f"   independent check, trace quote found verbatim anywhere in the report: {present}/{total} = "
              f"{present / total:.3f}")


def examples() -> None:
    print("== worked cases")
    cases = {r["id"]: r for r in jsonl(HERE / "data" / "cases.jsonl")}
    raw = HERE / "results" / f"raw_{HELDOUT}"
    case = cases["10049"]
    text = case["text"]
    records = {(r["case"], r["arm"]): r for r in jsonl(HERE / "results" / f"{HELDOUT}.jsonl")}
    for arm in ("prose", "single", "cybercase"):
        r = records[("10049", arm)]
        print(f"10049 {arm}: mentioned {len(r['stated_lead'])}/{r['gold_lead']}, cited "
              f"{len(r.get('grounded_lead', [])) if arm != 'prose' else '—'}/{r['gold_lead']}")
    bound = json.loads((raw / "10049_cybercase_1.json").read_text(encoding="utf-8"))["bound"]
    spans = [(text.find(q["exact_quote"]), c["claim_id"]) for c in bound["claims"] for q in c["supporting_citations"]]
    for fact in (f for f in case["gold"] if f["lead"]):
        s, e = fact["spans"][0]
        by = sorted({cid for start, cid in spans
                     for q in [next(q["exact_quote"] for c in bound["claims"] if c["claim_id"] == cid
                                    for q in c["supporting_citations"])]
                     if start >= 0 and start < e and start + len(q) > s})
        print(f"   {fact['role']:17s} {fact['text']!r:55s} [{s}, {e}] cited by {', '.join(by) or '-'}")
    data = json.loads((raw / "1271_cybercase_1.json").read_text(encoding="utf-8"))
    written = {c["claim_id"]: c for c in data["written"]["claims"]}
    demoted = [c["claim_id"] for c in data["bound"]["claims"] if c["epistemic_status"] == "not_confirmed"]
    wrapped = [cid for cid in demoted if any(q["exact_quote"].strip().startswith(('"', "“"))
                                             for q in written[cid]["supporting_citations"])]
    print(f"1271 cybercase: {len(demoted)} claims demoted to not_confirmed; {len(wrapped)} of them had every quote "
          f"wrapped in quotation marks by the model")
    data = json.loads((raw / "10086_cybercase_1.json").read_text(encoding="utf-8"))
    for c in data["written"]["claims"]:
        for q in c["supporting_citations"]:
            if "..." in q["exact_quote"].strip(" .") or "…" in q["exact_quote"].strip(" .…"):
                kept = next((b for bc in data["bound"]["claims"] if bc["claim_id"] == c["claim_id"]
                             for b in bc["supporting_citations"]), None)
                if kept and len(kept["exact_quote"]) > len(q["exact_quote"]) + 100:
                    print(f"10086 {c['claim_id']}: the model wrote {len(q['exact_quote'])} characters with a middle "
                          f"ellipsis; the binder kept a {len(kept['exact_quote'])}-character span")


if __name__ == "__main__":
    parts = sys.argv[1:] or ["rq1", "m6", "examples"]
    for part in parts:
        {"rq1": rq1, "m6": m6, "examples": examples}[part]()
