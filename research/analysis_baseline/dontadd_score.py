from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED, RESAMPLES = 2026, 2000
ARMS = ("A", "B", "C")
PAIRS = (("C", "A"), ("B", "A"), ("C", "B"))
SUMMARY = ("summary_P_rouge1", "summary_P_rougeL", "summary_R_rouge1", "summary_R_rougeL")
UNIT = ("unit_P_rouge1", "unit_P_rougeL")


def interval(dist: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(dist, [2.5, 97.5])
    return float(lo), float(hi)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(HERE))
    from pythainlp.tokenize import word_tokenize
    from rouge_score import rouge_scorer
    from judgement_claims_only_score import evidence, stripped, units

    class ThaiWords:
        def tokenize(self, text: str) -> list[str]:
            return [t for t in word_tokenize(text, engine="newmm") if t.strip()]

    scorers = {"english": rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True),
               "thai": rouge_scorer.RougeScorer(["rouge1", "rougeL"], tokenizer=ThaiWords())}
    raw = Path(args.raw)
    data: dict[str, dict[str, dict[str, dict]]] = {"english": {}, "thai": {}}
    for path in sorted(raw.glob("*_?.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if "judgement" not in saved:
            continue
        language, arm, key = saved["language"], saved["arm"], saved["key"]
        scorer = scorers[language]
        claims = {c["claim_id"]: c for c in saved["reading"]["claims"]}
        checked = " ".join(c.get("text", "") for c in claims.values() if evidence(c))
        summary = saved["judgement"]["summary"]
        whole = scorer.score(checked, stripped(summary))
        row: dict = {}
        for metric in ("rouge1", "rougeL"):
            row[f"summary_P_{metric}"] = whole[metric].precision
            row[f"summary_R_{metric}"] = whole[metric].recall
        if arm in ("B", "C"):
            for metric in ("rouge1", "rougeL"):
                row[f"unit_P_{metric}"] = []
            for text, ids in units(summary):
                cited = " ".join(claims[i].get("text", "") for i in ids if i in claims)
                if ids and text and cited:
                    s = scorer.score(cited, text)
                    for metric in ("rouge1", "rougeL"):
                        row[f"unit_P_{metric}"].append(s[metric].precision)
        data[language].setdefault(key, {})[arm] = row

    md = ["# Don't Add / Don't Miss against the checked claims", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Raw `{raw.name}`. "
          f"Claim text only; case bootstrap {RESAMPLES}, seed {SEED}. Unit arm points pool units over cases; the "
          "unit contrast compares per-case unit means.", ""]
    report: dict = {}
    for language, rows in data.items():
        md += [f"## {language}", "", "| Measure | A | B | C | C − A | B − A | C − B |", "|---|---|---|---|---|---|---|"]
        report[language] = {}
        for name in SUMMARY + UNIT:
            unit = name in UNIT
            cells, entry = [], {}
            for arm in ARMS:
                keys = [k for k, v in rows.items() if arm in v and name in v[arm] and (not unit or v[arm][name])]
                if not keys:
                    cells.append("–")
                    continue
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                if unit:
                    sums = np.array([[sum(rows[k][arm][name]), len(rows[k][arm][name])] for k in keys], dtype=float)
                    point = sums[:, 0].sum() / sums[:, 1].sum()
                    b = sums[picks].sum(axis=1)
                    dist = b[:, 0] / b[:, 1]
                else:
                    values = np.array([rows[k][arm][name] for k in keys], dtype=float)
                    point, dist = values.mean(), values[picks].mean(axis=1)
                lo, hi = interval(dist)
                entry[arm] = [round(float(point), 4), round(lo, 4), round(hi, 4), len(keys)]
                cells.append(f"{point:.3f} [{lo:.3f}, {hi:.3f}]")
            for left, right in PAIRS:
                keys = [k for k, v in rows.items() if left in v and right in v and name in v[left] and name in v[right]
                        and (not unit or (v[left][name] and v[right][name]))]
                if not keys:
                    cells.append("–")
                    continue

                def value(k: str, arm: str) -> float:
                    x = rows[k][arm][name]
                    return sum(x) / len(x) if unit else x

                diffs = np.array([value(k, left) - value(k, right) for k in keys], dtype=float)
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                lo, hi = interval(diffs[picks].mean(axis=1))
                entry[f"{left}-{right}"] = [round(float(diffs.mean()), 4), round(lo, 4), round(hi, 4), len(keys)]
                cells.append(f"{diffs.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]")
            report[language][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "dontadd.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "dontadd.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
