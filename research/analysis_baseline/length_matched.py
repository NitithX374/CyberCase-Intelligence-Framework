from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
SEED, RESAMPLES = 2026, 2000
VERSIONS = ("A", "B", "C", "B-trunc", "C-trunc")
PAIRS = (("B", "A"), ("C", "A"), ("B-trunc", "A"), ("C-trunc", "A"), ("C-trunc", "B-trunc"))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(HERE))
    from pythainlp.tokenize import word_tokenize
    from rouge_score import rouge_scorer
    from fivew1h import SLOT, SLOTS
    from judgement_claims_only_score import evidence, stripped
    from scores_common import v0_words
    from summary_measures import matcher

    mentioned = matcher(v0_words, stemmed=True)

    class ThaiWords:
        def tokenize(self, text: str) -> list[str]:
            return [t for t in word_tokenize(text, engine="newmm") if t.strip()]

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

    scorers = {"english": rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True),
               "thai": rouge_scorer.RougeScorer(["rouge1", "rougeL"], tokenizer=ThaiWords())}
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    references = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            references[record["id"]] = record["summary"]

    saved: dict[tuple[str, str], dict] = {}
    for path in sorted(Path(args.raw).glob("*_?.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if "judgement" in record:
            saved[(record["key"], record["arm"])] = record

    rows: dict[str, dict[str, dict[str, dict]]] = {"english": {}, "thai": {}}
    for (key, arm), record in saved.items():
        if arm != "A":
            continue
        language = record["language"]
        n = length(stripped(record["judgement"]["summary"]), language)
        texts = {"A": stripped(record["judgement"]["summary"])}
        for other in ("B", "C"):
            if (key, other) in saved:
                full = stripped(saved[(key, other)]["judgement"]["summary"])
                texts[other], texts[f"{other}-trunc"] = full, cut(full, n, language)
        claims = record["reading"]["claims"]
        checked = " ".join(c.get("text", "") for c in claims if evidence(c))
        scorer = scorers[language]
        for version, text in texts.items():
            m: dict[str, tuple[float, float]] = {"length": (length(text, language), 1)}
            vs_claims = scorer.score(checked, text)
            m["F1_rouge1_vs_claims"] = (vs_claims["rouge1"].fmeasure, 1)
            m["F1_rougeL_vs_claims"] = (vs_claims["rougeL"].fmeasure, 1)
            if language == "english":
                facts = cases[key]["gold"]
                hits = [mentioned(text, f) for f in facts]
                m["coverage_all"] = (sum(hits), len(facts))
                for slot in SLOTS:
                    chosen = [h for f, h in zip(facts, hits) if SLOT.get(f["role"]) == slot]
                    if chosen:
                        m[f"coverage_{slot}"] = (sum(chosen), len(chosen))
            else:
                m["F1_rougeL_vs_reference"] = (scorer.score(references[key], text)["rougeL"].fmeasure, 1)
            rows[language].setdefault(key, {})[version] = m

    def pooled(keys, version, name, picks=None):
        values = np.array([rows_now[k][version][name] for k in keys], dtype=float)
        if picks is None:
            return values[:, 0].sum() / values[:, 1].sum()
        sums = values[picks].sum(axis=1)
        return sums[:, 0] / sums[:, 1]

    md = ["# Length-matched comparison", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Raw `{Path(args.raw).name}`. "
          f"B and C cut to each case's A length. Pooled; case bootstrap {RESAMPLES}, seed {SEED}. "
          "Decided after the results were seen.", ""]
    report = {}
    for language, rows_now in rows.items():
        names = sorted({n for v in rows_now.values() for m in v.values() for n in m})
        header = " | ".join(VERSIONS) + " | " + " | ".join(f"{a} − {b}" for a, b in PAIRS)
        md += [f"## {language}", "", f"| Measure | {header} |", "|---" * (1 + len(VERSIONS) + len(PAIRS)) + "|"]
        report[language] = {}
        for name in names:
            cells, entry = [], {}
            for version in VERSIONS:
                keys = [k for k, v in rows_now.items() if version in v and name in v[version]]
                if not keys:
                    cells.append("–")
                    continue
                point = pooled(keys, version, name)
                entry[version] = round(float(point), 4)
                cells.append(f"{point:.1f}" if name == "length" else f"{point:.3f}")
            for left, right in PAIRS:
                keys = [k for k, v in rows_now.items() if left in v and right in v and name in v[left] and name in v[right]]
                if not keys:
                    cells.append("–")
                    continue
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                point = pooled(keys, left, name) - pooled(keys, right, name)
                lo, hi = np.percentile(pooled(keys, left, name, picks) - pooled(keys, right, name, picks), [2.5, 97.5])
                entry[f"{left}-{right}"] = [round(float(point), 4), round(float(lo), 4), round(float(hi), 4), len(keys)]
                fmt = "{:+.1f} [{:+.1f}, {:+.1f}]" if name == "length" else "{:+.3f} [{:+.3f}, {:+.3f}]"
                cells.append(fmt.format(point, lo, hi))
            report[language][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "length_matched.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "length_matched.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
