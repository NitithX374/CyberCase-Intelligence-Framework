from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
CLAIMS_ONLY = HERE / "results" / "raw_judgement_claims_only_main_20261004_013832"
ATTRFIRST = HERE / "results" / "raw_attrfirst_cot_main_20261004_041927"
SEED, RESAMPLES = 2026, 2000
SYSTEMS = ("D", "A", "C", "AF")
PAIRS = (("C", "D"), ("AF", "D"), ("C", "AF"))
CALLS = {"D": 1.0, "A": 2.0, "C": 2.0}
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
BERT_MODEL, BERT_LAYER = "bert-base-multilingual-cased", 9


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--direct", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.backend)
    sys.path.insert(0, str(HERE))
    from bert_score import score as bert_score
    from nltk.translate.meteor_score import meteor_score
    from pythainlp.tokenize import word_tokenize
    from rouge_score import rouge_scorer
    from judgement_claims_only import sample
    from judgement_claims_only_score import stripped, units
    from scores_common import v0_words
    from summary_measures import matcher

    mentioned = matcher(v0_words, stemmed=True)
    texts = {i["key"]: i["text"] for i in sample("main")}
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    references = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            references[record["id"]] = record["summary"]

    def tokens(text: str) -> list[str]:
        return [t for t in word_tokenize(text, engine="newmm") if t.strip()]

    class ThaiWords:
        def tokenize(self, text: str) -> list[str]:
            return tokens(text)

    def length(text: str, language: str) -> int:
        return len(text.split()) if language == "english" else len(tokens(text))

    def cut(text: str, n: int, language: str) -> str:
        if language == "english":
            return " ".join(text.split()[:n])
        out, count = [], 0
        for token in word_tokenize(text, engine="newmm"):
            if token.strip():
                if count == n:
                    break
                count += 1
            out.append(token)
        return "".join(out).strip()

    def in_source(digit: str, source: str, years: bool) -> bool:
        return digit in source or (years and bool(re.fullmatch(r"25\d\d", digit))
                                   and bool(re.search(rf"(?<!\d){digit[2:]}(?!\d)", source)))

    rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], tokenizer=ThaiWords())
    summaries: dict[str, dict[str, dict]] = {}
    for path in sorted(CLAIMS_ONLY.glob("*_?.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if "judgement" in saved and saved["arm"] in ("A", "C"):
            raw = saved["judgement"]["summary"]
            cited = (sum(1 for t, ids in units(raw) if ids and any(i in {c["claim_id"] for c in saved["reading"]["claims"]}
                                                                  for i in ids)), len(units(raw)))
            summaries.setdefault(saved["key"], {})[saved["arm"]] = {
                "language": saved["language"], "text": stripped(raw),
                "cited": cited if saved["arm"] == "C" else (0, max(1, len(units(raw))))}
    for path in sorted(ATTRFIRST.glob("*.json")):
        if path.name == "run.json":
            continue
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("summary"):
            n_h = len(saved["highlights"])
            attributed = sum(1 for s in saved["alignments"] if any(1 <= i <= n_h for i in s["highlights"]))
            summaries.setdefault(saved["key"], {})["AF"] = {"language": saved["language"], "text": saved["summary"],
                                                            "cited": (attributed, max(1, len(saved["alignments"]))),
                                                            "calls": len(saved["calls"])}
    direct_calls = {}
    for path in sorted(Path(args.direct).glob("*.json")):
        if path.name == "run.json":
            continue
        saved = json.loads(path.read_text(encoding="utf-8"))
        direct_calls[saved["key"]] = len(saved["calls"])
        if saved.get("summary"):
            summaries.setdefault(saved["key"], {})["D"] = {"language": saved["language"], "text": saved["summary"],
                                                           "cited": (0, 1)}

    rows: dict[str, dict[str, dict[str, tuple[float, float]]]] = {"english": {}, "thai": {}}
    bert_jobs = []
    for key, systems in summaries.items():
        if "A" not in systems:
            continue
        language = systems["A"]["language"]
        n_a = length(systems["A"]["text"], language)
        source = texts[key]
        for system, entry in systems.items():
            text = entry["text"]
            m: dict[str, tuple[float, float]] = {"words": (length(text, language), 1)}
            digits = DIGITS.findall(text)
            m["NumPrec_vs_source"] = (sum(in_source(d, source, False) for d in digits), len(digits))
            m["NumPrec_vs_source_BE_years"] = (sum(in_source(d, source, True) for d in digits), len(digits))
            m["citation_share"] = entry["cited"]
            trimmed = cut(text, n_a, language)
            if language == "english":
                facts = cases[key]["gold"]
                m["key_fact_coverage"] = (sum(mentioned(text, f) for f in facts), len(facts))
                m["key_fact_coverage_at_A_length"] = (sum(mentioned(trimmed, f) for f in facts), len(facts))
            else:
                for version, candidate in (("", text), ("_at_A_length", trimmed)):
                    r = rouge.score(references[key], candidate)
                    for name in ("rouge1", "rouge2", "rougeL"):
                        m[f"{name}_F1{version}"] = (r[name].fmeasure, 1)
                    m[f"METEOR{version}"] = (meteor_score([tokens(references[key])], tokens(candidate)), 1)
                    bert_jobs.append((key, system, f"BERTScore_F1{version}", candidate, references[key]))
            rows[language].setdefault(key, {})[system] = m
    if bert_jobs:
        _, _, F = bert_score([j[3] for j in bert_jobs], [j[4] for j in bert_jobs], model_type=BERT_MODEL,
                             num_layers=BERT_LAYER, lang="th", verbose=False)
        for (key, system, name, _, _), f in zip(bert_jobs, F):
            rows["thai"][key][system][name] = (float(f), 1)

    completed = {s: {lang: sum(1 for v in rows[lang].values() if s in v) for lang in rows} for s in SYSTEMS}
    calls = {"D": round(sum(direct_calls.values()) / max(1, len(direct_calls)), 2), "A": 2.0, "C": 2.0,
             "AF": round(np.mean([v["AF"]["calls"] for v in summaries.values() if "AF" in v]), 2)}

    def pooled(keys, system, name, picks=None):
        values = np.array([rows_now[k][system][name] for k in keys], dtype=float)
        if picks is None:
            return values[:, 0].sum() / max(values[:, 1].sum(), 1e-12)
        sums = values[picks].sum(axis=1)
        return sums[:, 0] / np.maximum(sums[:, 1], 1e-12)

    md = ["# Pipeline comparison: direct (D), production (A), ours after #61 (C), Attribute First (AF)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Direct raw `{Path(args.direct).name}`. "
          f"Pooled ratios; per-item metrics (ROUGE, METEOR, BERTScore) are means. Article bootstrap {RESAMPLES}, seed {SEED}.",
          "", f"Completed items: {completed}. Model calls per item: {calls}.", ""]
    report: dict = {"completed": completed, "calls_per_item": calls}
    for language, rows_now in rows.items():
        names = sorted({n for v in rows_now.values() for s in v.values() for n in s})
        md += [f"## {language}", "", "| Measure | D | A | C | AF | C − D | AF − D | C − AF |", "|---|---|---|---|---|---|---|---|"]
        report[language] = {}
        for name in names:
            cells, entry = [], {}
            for system in SYSTEMS:
                keys = [k for k, v in rows_now.items() if system in v and name in v[system] and v[system][name][1] > 0]
                if not keys:
                    cells.append("–")
                    continue
                point = pooled(keys, system, name)
                entry[system] = [round(float(point), 4), len(keys)]
                cells.append(f"{point:.1f}" if name == "words" else f"{point:.3f}")
            for left, right in PAIRS:
                keys = [k for k, v in rows_now.items() if all(s in v and name in v[s] and v[s][name][1] > 0 for s in (left, right))]
                if not keys:
                    cells.append("–")
                    continue
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                point = pooled(keys, left, name) - pooled(keys, right, name)
                lo, hi = np.percentile(pooled(keys, left, name, picks) - pooled(keys, right, name, picks), [2.5, 97.5])
                entry[f"{left}-{right}"] = [round(float(point), 4), round(float(lo), 4), round(float(hi), 4), len(keys)]
                fmt = "{:+.1f} [{:+.1f}, {:+.1f}]" if name == "words" else "{:+.3f} [{:+.3f}, {:+.3f}]"
                cells.append(fmt.format(point, lo, hi))
            report[language][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "pipeline_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "pipeline_table.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
