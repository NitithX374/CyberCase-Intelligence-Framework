from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
RESULTS = HERE / "results"
OLD_JUDGEMENT = RESULTS / "raw_judgement_claims_only_main_20261004_013832"
OLD_DIRECT = RESULTS / "raw_direct_summary_20261004_053633"
SEED, RESAMPLES = 2026, 2000
BERT_MODEL, BERT_LAYER = "bert-base-multilingual-cased", 9
METRICS = ("rouge1_F1", "rouge2_F1", "rougeL_F1", "rougeL_P", "rougeL_R", "BERTScore_F1", "BERTScore_P", "BERTScore_R")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--current")
    parser.add_argument("--arms", default="D,A,C,G")
    parser.add_argument("--name", default="current_design_scores")
    args = parser.parse_args()
    arms = tuple(args.arms.split(","))
    with_current = "G" in arms
    if with_current and not args.current:
        raise SystemExit("--current is required when G is scored")
    pairs = (("G", "D"), ("G", "A"), ("G", "C"), ("L", "G")) if with_current else (("A", "D"), ("C", "D"))
    sys.path.insert(0, str(HERE))
    from bert_score import score as bert_score
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
    references, articles = {}, {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            references[record["id"]] = record["summary"]
            articles[record["id"]] = record["clean"]

    summaries: dict[str, dict[str, str]] = {}
    for path in sorted(OLD_DIRECT.glob("r*.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("language") == "thai" and saved.get("summary"):
            summaries.setdefault(saved["key"], {})["D"] = saved["summary"]
    for path in sorted(OLD_JUDGEMENT.glob("r*_?.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("language") == "thai" and "judgement" in saved and saved["arm"] in ("A", "C"):
            summaries.setdefault(saved["key"], {})[saved["arm"]] = stripped(saved["judgement"]["summary"])
    missing = {}
    if with_current:
        for path in sorted(Path(args.current).glob("r[0-9]*.json")):
            saved = json.loads(path.read_text(encoding="utf-8"))
            if saved.get("judgement"):
                summaries.setdefault(saved["key"], {})["G"] = stripped(saved["judgement"]["summary"])
            else:
                missing[saved["key"]] = saved.get("error") or ("abstained" if saved.get("abstained") else "no summary")

    keys = sorted(k for k, v in summaries.items() if all(a in v for a in arms))
    shown = (*arms, "L") if with_current else arms
    versions = {"full": None, "at G length": "G", "at A length": "A"} if with_current else {"full": None}
    scores: dict[str, dict[str, dict[str, dict[str, float]]]] = {version: {} for version in versions}
    for version, anchor in versions.items():
        jobs = []
        for key in keys:
            n = len(tokens(summaries[key][anchor or "G"])) if with_current or anchor else 0
            for arm in arms:
                text = summaries[key][arm]
                jobs.append((key, arm, text if anchor is None else cut(text, n)))
            if with_current:
                jobs.append((key, "L", cut(articles[key], n)))
        P, R, F = bert_score(
            [c for _, _, c in jobs],
            [references[k] for k, _, _ in jobs],
            model_type=BERT_MODEL,
            num_layers=BERT_LAYER,
            lang="th",
            verbose=False,
        )
        for i, (key, arm, candidate) in enumerate(jobs):
            r = rouge.score(references[key], candidate)
            scores[version].setdefault(key, {})[arm] = {
                "words": float(len(tokens(candidate))),
                "rouge1_F1": r["rouge1"].fmeasure,
                "rouge2_F1": r["rouge2"].fmeasure,
                "rougeL_F1": r["rougeL"].fmeasure,
                "rougeL_P": r["rougeL"].precision,
                "rougeL_R": r["rougeL"].recall,
                "BERTScore_F1": float(F[i]),
                "BERTScore_P": float(P[i]),
                "BERTScore_R": float(R[i]),
            }

    arm_cells = " | ".join(shown)
    diff_cells = " | ".join(f"{left} − {right}" for left, right in pairs)
    md = [
        "# ThaiSum, current design vs earlier arms (Thai, same 50 articles)",
        "",
        f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. References: ThaiSum `summary`. "
        f"newmm tokens; BERTScore {BERT_MODEL} layer {BERT_LAYER}, no IDF, no rescaling. Means over articles; "
        f"paired article bootstrap {RESAMPLES}, seed {SEED}.",
        "",
        "D direct, A earlier production, C earlier claims-only (after #61), G current design (source-unit Reader, "
        "claims-only Judgement), L the first words of the article (reference only, not a system).",
        "",
        f"Articles with all arms {arms}: {len(keys)}. G missing: {missing}",
        "",
    ]
    report: dict = {"articles": len(keys), "keys": keys, "G_missing": missing}
    for version, rows in scores.items():
        md += [f"## {version}", "", f"| Metric | {arm_cells} | {diff_cells} |", "|---|" + "---|" * (len(shown) + len(pairs))]
        report[version] = {}
        for name in ("words", *METRICS):
            cells, entry = [], {}
            for arm in shown:
                values = [rows[k][arm][name] for k in keys]
                entry[arm] = round(float(np.mean(values)), 4)
                cells.append(f"{np.mean(values):.1f}" if name == "words" else f"{np.mean(values):.3f}")
            for left, right in pairs:
                diffs = np.array([rows[k][left][name] - rows[k][right][name] for k in keys])
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                lo, hi = np.percentile(diffs[picks].mean(axis=1), [2.5, 97.5])
                entry[f"{left}-{right}"] = [round(float(diffs.mean()), 4), round(float(lo), 4), round(float(hi), 4)]
                cells.append(
                    f"{diffs.mean():+.1f} [{lo:+.1f}, {hi:+.1f}]"
                    if name == "words"
                    else f"{diffs.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]"
                )
            report[version][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    reference_words = [len(tokens(references[k])) for k in keys]
    md.append(f"Reference length: mean {np.mean(reference_words):.1f} words, median {np.median(reference_words):.0f}.")
    report["reference_words_mean"] = round(float(np.mean(reference_words)), 2)
    (RESULTS / f"{args.name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (RESULTS / f"{args.name}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
