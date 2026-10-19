from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from nltk.stem import PorterStemmer
from rouge_score import rouge_scorer

HERE = Path(__file__).resolve().parent
RUNS = {"confirmation": "main_20261001_021428", "development": "main_20260930_193646"}
ARM = "cybercase_nogrammar"
SEED, RESAMPLES = 2026, 2000
STEM = PorterStemmer()


def load(backend: str):
    sys.path.insert(0, backend)
    import app.trace.bind as bind
    from app.trace.sentences import sentence_spans

    if not Path(bind.__file__).resolve().is_relative_to(Path(backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    sys.path.insert(0, str(HERE))
    from scores_common import lead, v0_words

    return bind.located_quote, sentence_spans, lead, v0_words


def matcher(v0_words, stemmed: bool):
    def form(text: str) -> str:
        words = v0_words(text).split()
        return " ".join(STEM.stem(w) for w in words) if stemmed else " ".join(words)

    def mentioned(text: str, fact: dict) -> bool:
        return f" {form(fact['text'])} " in f" {form(text)} "

    return mentioned


def case_row(tools, case: dict, written: dict) -> dict:
    located_quote, sentence_spans, lead, v0_words = tools
    text = case["text"]
    checked = []
    unchecked = []
    for claim in written["claims"]:
        quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        found = [q for q in quotes if located_quote(text, q) is not None]
        (checked if found else unchecked).append(" ".join([claim.get("text", ""), *found]))
    summary = written.get("summary", "")
    facts = lead(case)
    row: dict = {}
    for label, stemmed in (("v0", False), ("stemmed", True)):
        mentioned = matcher(v0_words, stemmed)
        in_summary = [mentioned(summary, f) for f in facts]
        in_checked = [any(mentioned(t, f) for t in checked) for f in facts]
        in_unchecked = [any(mentioned(t, f) for t in unchecked) for f in facts]
        row[label] = {
            "facts": len(facts), "summary": sum(in_summary), "checked": sum(in_checked),
            "dropped": sum(c and not s for c, s in zip(in_checked, in_summary)),
            "traceable": sum(s and c for s, c in zip(in_summary, in_checked)),
            "unchecked_only": sum(s and not c and u for s, c, u in zip(in_summary, in_checked, in_unchecked)),
            "untraceable": sum(s and not c and not u for s, c, u in zip(in_summary, in_checked, in_unchecked)),
        }
        if stemmed:
            sentences = [summary[a:b] for a, b in sentence_spans(summary)] or [summary]
            keyed = traced = 0
            for sentence in sentences:
                hits = [i for i, f in enumerate(facts) if mentioned(sentence, f)]
                if hits:
                    keyed += 1
                    traced += all(in_checked[i] for i in hits)
            row["sentences"] = {"total": len(sentences), "keyed": keyed, "traced": traced}
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    row["rouge_claims"] = {k: [v.precision, v.recall] for k, v in scorer.score(" ".join(checked), summary).items()}
    row["rouge_source"] = {k: [v.precision, v.recall] for k, v in scorer.score(text, summary).items()}
    return row


def ratio(pairs: list[tuple[float, float]]) -> list:
    counts = np.array(pairs, dtype=float)
    counts = counts[counts[:, 1] > 0]
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    hits, total = counts[:, 0].sum(), counts[:, 1].sum()
    return [int(hits), int(total), round(hits / total, 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4)]


def mean(values: list[float]) -> list:
    array = np.array(values, dtype=float)
    picks = np.random.default_rng(SEED).integers(0, len(array), size=(RESAMPLES, len(array)))
    means = array[picks].mean(axis=1)
    return [round(float(array.mean()), 4), round(float(np.percentile(means, 2.5)), 4),
            round(float(np.percentile(means, 97.5)), 4)]


def shown(cell: list) -> str:
    return f"{cell[2]:.3f} [{cell[3]:.3f}, {cell[4]:.3f}] ({cell[0]}/{cell[1]})"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    tools = load(args.backend)
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    report: dict = {}
    md = ["# Summary measures 1-4", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          "No model call.", ""]
    for split, run in RUNS.items():
        rows = []
        for path in sorted((HERE / "results" / f"raw_{run}").glob(f"*_{ARM}_1.json")):
            written = json.loads(path.read_text(encoding="utf-8")).get("written")
            if written:
                rows.append(case_row(tools, cases[path.name.split("_")[0]], written))
        cell: dict = {"cases": len(rows)}
        for label in ("v0", "stemmed"):
            r = [x[label] for x in rows]
            cell[label] = {
                "coverage": ratio([(x["summary"], x["facts"]) for x in r]),
                "dropped": ratio([(x["dropped"], x["checked"]) for x in r]),
                "traceable": ratio([(x["traceable"], x["summary"]) for x in r]),
                "unchecked_only": ratio([(x["unchecked_only"], x["summary"]) for x in r]),
                "untraceable": ratio([(x["untraceable"], x["summary"]) for x in r]),
            }
        s = [x["sentences"] for x in rows]
        cell["conciseness"] = ratio([(x["keyed"], x["total"]) for x in s])
        cell["sentence_traceability"] = ratio([(x["traced"], x["keyed"]) for x in s])
        for ref in ("rouge_claims", "rouge_source"):
            cell[ref] = {k: {"precision": mean([x[ref][k][0] for x in rows]), "recall": mean([x[ref][k][1] for x in rows])}
                         for k in ("rouge1", "rouge2", "rougeL")}
        report[split] = cell
        md += [f"## {split} ({cell['cases']} cases)", "", "| Measure | V0 | stemmed |", "|---|---|---|"]
        for key, name in (("coverage", "1. summary coverage of main-event facts"),
                          ("dropped", "Q2 dropped, of facts in checked claims"),
                          ("traceable", "Q3 traceable, of summary facts"), ("unchecked_only", "Q3 unchecked only"),
                          ("untraceable", "Q3 untraceable")):
            md.append(f"| {name} | {shown(cell['v0'][key])} | {shown(cell['stemmed'][key])} |")
        md += ["", f"- 2. Conciseness (sentences mentioning a main-event fact): {shown(cell['conciseness'])}",
               f"- 3. Sentence traceability (fact sentences whose every fact is in a checked claim): "
               f"{shown(cell['sentence_traceability'])}", "",
               "| 4. ROUGE (stemmed) | precision vs checked claims (don't add) | recall vs checked claims (don't miss) | "
               "precision vs source | recall vs source |", "|---|---|---|---|---|"]
        for k in ("rouge1", "rouge2", "rougeL"):
            c, so = cell["rouge_claims"][k], cell["rouge_source"][k]
            md.append(f"| {k} | {c['precision'][0]:.3f} [{c['precision'][1]:.3f}, {c['precision'][2]:.3f}] | "
                      f"{c['recall'][0]:.3f} | {so['precision'][0]:.3f} | {so['recall'][0]:.3f} |")
        md.append("")
    (HERE / "results" / "summary_measures.md").write_text("\n".join(md), encoding="utf-8")
    (HERE / "results" / "summary_measures.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
