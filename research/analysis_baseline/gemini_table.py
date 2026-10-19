from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
CLAIMS_ONLY = HERE / "results" / "raw_judgement_claims_only_main_20261004_013832"
C_GEMINI = HERE / "results" / "raw_c_pipeline_gemini-2.5-flash-lite_main_20261004_061915"
AF_GEMINI = HERE / "results" / "raw_attrfirst_cot_gemini-2.5-flash-lite_main_20261004_060104"
SEED, RESAMPLES = 2026, 2000
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
BERT_MODEL, BERT_LAYER = "bert-base-multilingual-cased", 9


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    from bert_score import score as bert_score
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

    scorers = {"english": rouge_scorer.RougeScorer(["rouge1"], use_stemmer=True),
               "thai": rouge_scorer.RougeScorer(["rouge1", "rougeL"], tokenizer=ThaiWords())}
    a_length, entries, failures = {}, {}, {"C": {}, "AF": {}}
    for path in CLAIMS_ONLY.glob("*_A.json"):
        saved = json.loads(path.read_text(encoding="utf-8"))
        a_length[saved["key"]] = length(stripped(saved["judgement"]["summary"]), saved["language"])
    for path in C_GEMINI.glob("*_C.json"):
        saved = json.loads(path.read_text(encoding="utf-8"))
        lang = saved["language"]
        if "judgement" not in saved:
            failures["C"][lang] = failures["C"].get(lang, 0) + 1
            continue
        claims = {c["claim_id"]: c for c in saved["reading"]["claims"]}
        parts = [(t, ids) for t, ids in units(saved["judgement"]["summary"]) if t]
        cited = [(t, " ".join(claims[i].get("text", "") for i in ids if i in claims)) for t, ids in parts
                 if any(i in claims for i in ids)]
        entries.setdefault(saved["key"], {})["C"] = {"language": lang, "text": stripped(saved["judgement"]["summary"]),
                                                     "cited": cited, "units": len(parts)}
    for path in AF_GEMINI.glob("*.json"):
        if path.name == "run.json":
            continue
        saved = json.loads(path.read_text(encoding="utf-8"))
        lang = saved["language"]
        if not saved.get("summary"):
            failures["AF"][lang] = failures["AF"].get(lang, 0) + 1
            continue
        hs = saved["highlights"]
        cited = [(s["sent_text"], " ".join(hs[i - 1] for i in s["highlights"] if 1 <= i <= len(hs)))
                 for s in saved["alignments"] if any(1 <= i <= len(hs) for i in s["highlights"])]
        entries.setdefault(saved["key"], {})["AF"] = {"language": lang, "text": saved["summary"], "cited": cited,
                                                      "units": max(1, len(saved["alignments"]))}

    rows: dict[str, dict[str, dict]] = {"english": {}, "thai": {}}
    jobs = []
    for key, systems in entries.items():
        for system, e in systems.items():
            lang, text, n = e["language"], e["text"], a_length[key]
            m = {"words": (length(text, lang), 1)}
            digits = DIGITS.findall(text)
            m["NumPrec_vs_source"] = (sum(d in texts[key] for d in digits), len(digits))
            m["citation_share"] = (len(e["cited"]), e["units"])
            scored = [scorers[lang].score(ref, t)["rouge1"].precision for t, ref in e["cited"] if ref]
            m["dont_add_rouge1_P"] = (sum(scored), len(scored))
            if lang == "english":
                facts = cases[key]["gold"]
                m["key_fact_coverage"] = (sum(mentioned(text, f) for f in facts), len(facts))
                m["key_fact_coverage_at_A_length"] = (sum(mentioned(cut(text, n, lang), f) for f in facts), len(facts))
            else:
                for version, cand in (("", text), ("_at_A_length", cut(text, n, lang))):
                    m[f"rougeL_F1{version}"] = (scorers[lang].score(references[key], cand)["rougeL"].fmeasure, 1)
                    jobs.append((key, system, f"BERTScore_F1{version}", cand, references[key]))
            rows[lang].setdefault(key, {})[system] = m
    _, _, F = bert_score([j[3] for j in jobs], [j[4] for j in jobs], model_type=BERT_MODEL, num_layers=BERT_LAYER,
                         lang="th", verbose=False)
    for (key, system, name, _, _), f in zip(jobs, F):
        rows["thai"][key][system][name] = (float(f), 1)

    def pooled(rows_now, keys, system, name, picks=None):
        values = np.array([rows_now[k][system][name] for k in keys], dtype=float)
        if picks is None:
            return values[:, 0].sum() / max(values[:, 1].sum(), 1e-12)
        sums = values[picks].sum(axis=1)
        return sums[:, 0] / np.maximum(sums[:, 1], 1e-12)

    md = ["# C and AF on Gemini 2.5 Flash-Lite", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Failures: {failures}. "
          f"Truncation length = Gemma A's length per item. Pooled; paired over items completed in both; bootstrap "
          f"{RESAMPLES}, seed {SEED}.", ""]
    report = {"failures": failures}
    for lang, rows_now in rows.items():
        names = sorted({n for v in rows_now.values() for s in v.values() for n in s})
        md += [f"## {lang}", "", "| Measure | C | AF | C − AF |", "|---|---|---|---|"]
        report[lang] = {}
        for name in names:
            keys = [k for k, v in rows_now.items() if all(s in v and v[s][name][1] > 0 for s in ("C", "AF"))]
            c, af = pooled(rows_now, keys, "C", name), pooled(rows_now, keys, "AF", name)
            picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
            lo, hi = np.percentile(pooled(rows_now, keys, "C", name, picks) - pooled(rows_now, keys, "AF", name, picks),
                                   [2.5, 97.5])
            report[lang][name] = [round(float(c), 4), round(float(af), 4), round(float(c - af), 4), round(float(lo), 4),
                                  round(float(hi), 4), len(keys)]
            fmt = "{:.1f}" if name == "words" else "{:.3f}"
            md.append(f"| {name} | {fmt.format(c)} | {fmt.format(af)} | {c - af:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
        md.append("")
    (HERE / "results" / "gemini_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "gemini_table.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
