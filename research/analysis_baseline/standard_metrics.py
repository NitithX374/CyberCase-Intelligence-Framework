from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
CLAIMS_ONLY = HERE / "results" / "raw_judgement_claims_only_main_20261004_013832"
ATTRFIRST = HERE / "results" / "raw_attrfirst_cot_main_20261004_041927"
SEED, RESAMPLES = 2026, 2000
SYSTEMS = ("A", "B", "C", "AF")
PAIRS = (("C", "A"), ("C", "B"), ("AF", "C"))
BERT_MODEL, BERT_LAYER = "bert-base-multilingual-cased", 9


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    from bert_score import score as bert_score
    from nltk.translate.meteor_score import meteor_score
    from pythainlp.tokenize import word_tokenize
    from rouge_score import rouge_scorer
    from judgement_claims_only_score import stripped

    def tokens(text: str) -> list[str]:
        return [t for t in word_tokenize(text, engine="newmm") if t.strip()]

    class ThaiWords:
        def tokenize(self, text: str) -> list[str]:
            return tokens(text)

    def cut(text: str, n: int) -> str:
        out, count = [], 0
        for token in word_tokenize(text, engine="newmm"):
            if token.strip():
                if count == n:
                    break
                count += 1
            out.append(token)
        return "".join(out).strip()

    rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], tokenizer=ThaiWords())
    references = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            references[record["id"]] = record["summary"]

    summaries: dict[str, dict[str, str]] = {}
    for path in sorted(CLAIMS_ONLY.glob("r*_?.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if "judgement" in saved:
            summaries.setdefault(saved["key"], {})[saved["arm"]] = stripped(saved["judgement"]["summary"])
    for path in sorted(ATTRFIRST.glob("r*.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("summary"):
            summaries.setdefault(saved["key"], {})["AF"] = saved["summary"]

    scores: dict[str, dict[str, dict[str, dict[str, float]]]] = {"full": {}, "at A length": {}}
    for version in scores:
        pairs = []
        for key, systems in summaries.items():
            if "A" not in systems:
                continue
            n = len(tokens(systems["A"]))
            for system, text in systems.items():
                candidate = text if version == "full" else cut(text, n)
                pairs.append((key, system, candidate))
        refs = [references[k] for k, _, _ in pairs]
        cands = [c for _, _, c in pairs]
        P, R, F = bert_score(cands, refs, model_type=BERT_MODEL, num_layers=BERT_LAYER, lang="th", verbose=False)
        for i, (key, system, candidate) in enumerate(pairs):
            r = rouge.score(references[key], candidate)
            m: dict[str, float] = {}
            for name in ("rouge1", "rouge2", "rougeL"):
                m[f"{name}_P"], m[f"{name}_R"], m[f"{name}_F1"] = r[name].precision, r[name].recall, r[name].fmeasure
            m["METEOR"] = meteor_score([tokens(references[key])], tokens(candidate))
            m["BERTScore_P"], m["BERTScore_R"], m["BERTScore_F1"] = float(P[i]), float(R[i]), float(F[i])
            scores[version].setdefault(key, {})[system] = m

    md = ["# Standard reference metrics on ThaiSum (50 articles)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. References: ThaiSum `summary`. "
          f"newmm tokens; BERTScore {BERT_MODEL} layer {BERT_LAYER}, no IDF, no rescaling. Means; article bootstrap "
          f"{RESAMPLES}, seed {SEED}.", ""]
    report: dict = {}
    for version, rows in scores.items():
        names = list(next(iter(next(iter(rows.values())).values())).keys())
        md += [f"## {version}", "", "| Metric | A | B | C | AF | C − A | C − B | AF − C |", "|---|---|---|---|---|---|---|---|"]
        report[version] = {}
        for name in names:
            cells, entry = [], {}
            for system in SYSTEMS:
                values = [rows[k][system][name] for k in rows if system in rows[k]]
                entry[system] = [round(float(np.mean(values)), 4), len(values)]
                cells.append(f"{np.mean(values):.3f}")
            for left, right in PAIRS:
                keys = [k for k in rows if left in rows[k] and right in rows[k]]
                diffs = np.array([rows[k][left][name] - rows[k][right][name] for k in keys])
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                lo, hi = np.percentile(diffs[picks].mean(axis=1), [2.5, 97.5])
                entry[f"{left}-{right}"] = [round(float(diffs.mean()), 4), round(float(lo), 4), round(float(hi), 4), len(keys)]
                cells.append(f"{diffs.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]")
            report[version][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "standard_metrics.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "standard_metrics.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
