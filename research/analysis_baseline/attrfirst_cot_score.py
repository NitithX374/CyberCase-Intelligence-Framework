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
SEED, RESAMPLES = 2026, 2000
SYSTEMS = ("A", "C", "AF")
PAIRS = (("AF", "C"), ("AF", "A"))
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--raw", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.backend)
    sys.path.insert(0, str(HERE))
    from app.trace.sentences import sentence_spans
    from pythainlp.tokenize import word_tokenize
    from rouge_score import rouge_scorer
    from judgement_claims_only_score import evidence, stripped, units
    from scores_common import v0_words
    from summary_measures import matcher

    mentioned = matcher(v0_words, stemmed=True)

    class ThaiWords:
        def tokenize(self, text: str) -> list[str]:
            return [t for t in word_tokenize(text, engine="newmm") if t.strip()]

    scorers = {"english": rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True),
               "thai": rouge_scorer.RougeScorer(["rouge1", "rougeL"], tokenizer=ThaiWords())}

    def length(text: str, language: str) -> int:
        return len(text.split()) if language == "english" else len(ThaiWords().tokenize(text))

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

    def supported(digit: str, pool: str) -> bool:
        return digit in pool or bool(re.fullmatch(r"25\d\d", digit) and re.search(rf"(?<!\d){digit[2:]}(?!\d)", pool))

    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    references = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            references[record["id"]] = record["summary"]

    rows: dict[str, dict[str, dict[str, dict]]] = {"english": {}, "thai": {}}
    failures = {"english": 0, "thai": 0}
    validity: dict[str, dict] = {"english": {}, "thai": {}}
    a_length: dict[str, int] = {}

    def common(key: str, language: str, summary: str, pool: str, n_a: int) -> dict:
        m: dict[str, tuple[float, float]] = {"length": (length(summary, language), 1)}
        sentences = [summary[a:b] for a, b in sentence_spans(summary)] or [summary]
        with_digits = [s for s in sentences if DIGITS.search(s)]
        m["digit_support_strict"] = (sum(all(d in pool for d in DIGITS.findall(s)) for s in with_digits), len(with_digits))
        m["digit_support_years"] = (sum(all(supported(d, pool) for d in DIGITS.findall(s)) for s in with_digits),
                                    len(with_digits))
        trimmed = cut(summary, n_a, language)
        if language == "english":
            facts = cases[key]["gold"]
            m["coverage"] = (sum(mentioned(summary, f) for f in facts), len(facts))
            m["coverage_at_A_length"] = (sum(mentioned(trimmed, f) for f in facts), len(facts))
        else:
            m["rougeL_F1_vs_reference"] = (scorers[language].score(references[key], summary)["rougeL"].fmeasure, 1)
            m["rougeL_F1_vs_reference_at_A_length"] = (
                scorers[language].score(references[key], trimmed)["rougeL"].fmeasure, 1)
        return m

    for arm in ("A", "C"):
        for path in sorted(CLAIMS_ONLY.glob(f"*_{arm}.json")):
            saved = json.loads(path.read_text(encoding="utf-8"))
            if "judgement" not in saved:
                continue
            language, key = saved["language"], saved["key"]
            summary = stripped(saved["judgement"]["summary"])
            if arm == "A":
                a_length[key] = length(summary, language)
            claims = {c["claim_id"]: c for c in saved["reading"]["claims"]}
            pool = " ".join(e for e in map(evidence, claims.values()) if e)
            rows[language].setdefault(key, {})[arm] = {"summary": summary, "pool": pool, "claims": claims,
                                                       "raw": saved["judgement"]["summary"]}

    for language in rows:
        for key, systems in rows[language].items():
            for arm in ("A", "C"):
                if arm in systems and key in a_length:
                    entry = systems[arm]
                    m = common(key, language, entry["summary"], entry["pool"], a_length[key])
                    if arm == "C":
                        per_unit = [scorers[language].score(" ".join(entry["claims"][i].get("text", "") for i in ids
                                                                     if i in entry["claims"]), text)
                                    for text, ids in units(entry["raw"]) if ids and text]
                        m["dont_add_rouge1_P"] = (sum(s["rouge1"].precision for s in per_unit), len(per_unit))
                        m["dont_add_rougeL_P"] = (sum(s["rougeL"].precision for s in per_unit), len(per_unit))
                    systems[arm] = m

    for path in sorted(Path(args.raw).glob("*.json")):
        if path.name == "run.json":
            continue
        saved = json.loads(path.read_text(encoding="utf-8"))
        language, key = saved["language"], saved["key"]
        v = validity[language]
        v["selection_attempts"] = v.get("selection_attempts", 0) + len(saved["selection_log"])
        v["fic_attempts"] = v.get("fic_attempts", 0) + len(saved["fic_log"])
        v["items"] = v.get("items", 0) + 1
        if "summary" not in saved or key not in a_length:
            failures[language] += 1
            continue
        highlights = saved["highlights"]
        pool = " ".join(highlights)
        m = common(key, language, saved["summary"], pool, a_length[key])
        attributed, scores = 0, []
        for sentence in saved["alignments"]:
            cited = [highlights[i - 1] for i in sentence["highlights"] if 1 <= i <= len(highlights)]
            if cited:
                attributed += 1
                scores.append(scorers[language].score(" ".join(cited), sentence["sent_text"]))
        m["dont_add_rouge1_P"] = (sum(s["rouge1"].precision for s in scores), len(scores))
        m["dont_add_rougeL_P"] = (sum(s["rougeL"].precision for s in scores), len(scores))
        m["planning_sentences_attributed"] = (attributed, len(saved["alignments"]))
        joined = "".join(s["sent_text"] for s in saved["alignments"]).replace(" ", "").replace("\n", "")
        m["final_differs_from_planning"] = (int(joined != saved["summary"].replace(" ", "").replace("\n", "")), 1)
        m["spans_unfound"] = (saved["spans_unfound"], len(saved["spans"]))
        rows[language][key]["AF"] = m

    def pooled(keys, system, name, picks=None):
        values = np.array([rows_now[k][system][name] for k in keys], dtype=float)
        if picks is None:
            return values[:, 0].sum() / max(values[:, 1].sum(), 1e-12)
        sums = values[picks].sum(axis=1)
        return sums[:, 0] / np.maximum(sums[:, 1], 1e-12)

    md = ["# Attribute First (CoT) baseline against arms A and C", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Raw `{Path(args.raw).name}`; "
          f"claims-only raw `{CLAIMS_ONLY.name}`. Pooled; pairs use cases completed in both; case bootstrap "
          f"{RESAMPLES}, seed {SEED}.", ""]
    report: dict = {}
    for language, rows_now in rows.items():
        md += [f"## {language} (AF failures {failures[language]}; validity {validity[language]})", "",
               "| Measure | A | C | AF | AF − C | AF − A |", "|---|---|---|---|---|---|"]
        report[language] = {"failures": failures[language], "validity": validity[language], "measures": {}}
        names = sorted({n for v in rows_now.values() for s in v.values() if isinstance(s, dict) for n in s})
        for name in names:
            cells, entry = [], {}
            for system in SYSTEMS:
                keys = [k for k, v in rows_now.items() if isinstance(v.get(system), dict) and name in v[system]
                        and rows_now[k][system][name][1] > 0]
                if not keys:
                    cells.append("–")
                    continue
                point = pooled(keys, system, name)
                entry[system] = [round(float(point), 4), len(keys)]
                cells.append(f"{point:.1f}" if name == "length" else f"{point:.3f}")
            for left, right in PAIRS:
                keys = [k for k, v in rows_now.items() if all(isinstance(v.get(s), dict) and name in v[s]
                                                              and v[s][name][1] > 0 for s in (left, right))]
                if not keys:
                    cells.append("–")
                    continue
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                point = pooled(keys, left, name) - pooled(keys, right, name)
                lo, hi = np.percentile(pooled(keys, left, name, picks) - pooled(keys, right, name, picks), [2.5, 97.5])
                entry[f"{left}-{right}"] = [round(float(point), 4), round(float(lo), 4), round(float(hi), 4), len(keys)]
                fmt = "{:+.1f} [{:+.1f}, {:+.1f}]" if name == "length" else "{:+.3f} [{:+.3f}, {:+.3f}]"
                cells.append(fmt.format(point, lo, hi))
            report[language]["measures"][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "attrfirst_cot.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "attrfirst_cot.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
