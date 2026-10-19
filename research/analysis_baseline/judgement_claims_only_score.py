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
SEED, RESAMPLES = 2026, 2000
ARMS = ("A", "B", "C")
PAIRS = (("C", "A"), ("B", "A"), ("C", "B"))
BRACKET = re.compile(r"\[\s*(A-\d{2,}(?:\s*,\s*A-\d{2,})*)\s*\]")
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
LEADING = re.compile(r"^[\s.,;:!?)\]]+")


def stripped(summary: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", re.sub(r"\s*" + BRACKET.pattern, "", summary)).strip()


def units(summary: str) -> list[tuple[str, list[str]]]:
    out, start = [], 0
    for match in BRACKET.finditer(summary):
        text = LEADING.sub("", summary[start:match.start()]).strip()
        out.append((text, [x.strip() for x in match.group(1).split(",")]))
        start = match.end()
    tail = LEADING.sub("", summary[start:]).strip()
    if tail:
        out.append((tail, []))
    return out


def evidence(claim: dict) -> str | None:
    quotes = [c["exact_quote"] for c in claim.get("supporting_citations", [])
              if c.get("exact_quote") and not c["source_id"].startswith("QA")]
    return " ".join([claim.get("text", ""), *quotes]) if quotes else None


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--raw", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.backend)
    from app.trace.sentences import sentence_spans

    sys.path.insert(0, str(HERE))
    from rouge_score import rouge_scorer
    from pythainlp.tokenize import word_tokenize
    from scores_common import lead, v0_words
    from fivew1h import SLOT, SLOTS
    from summary_measures import matcher

    mentioned = matcher(v0_words, stemmed=True)

    class ThaiWords:
        def tokenize(self, text: str) -> list[str]:
            return [t for t in word_tokenize(text, engine="newmm") if t.strip()]

    rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], tokenizer=ThaiWords())
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    references = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            references[record["id"]] = record["summary"]

    raw = Path(args.raw)
    rows: dict[str, dict[str, dict[str, dict]]] = {"english": {}, "thai": {}}
    failures: dict[str, dict[str, int]] = {"english": {a: 0 for a in ARMS}, "thai": {a: 0 for a in ARMS}}
    for path in sorted(raw.glob("*_?.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        language, arm, key = saved["language"], saved["arm"], saved["key"]
        if "judgement" not in saved:
            failures[language][arm] += 1
            continue
        summary = saved["judgement"]["summary"]
        clean = stripped(summary)
        claims = {c["claim_id"]: c for c in saved["reading"]["claims"]}
        union = " ".join(e for e in map(evidence, claims.values()) if e)
        m: dict[str, tuple[float, float]] = {}
        sentences = [clean[a:b] for a, b in sentence_spans(clean)] or [clean]
        with_digits = [s for s in sentences if DIGITS.search(s)]
        m["digit_support"] = (sum(all(d in union for d in DIGITS.findall(s)) for s in with_digits), len(with_digits))
        m["gaps"] = (len(saved["judgement"]["gaps"]), 1)
        if language == "english":
            facts = cases[key]["gold"]
            words = len(clean.split())
            covered = [mentioned(clean, f) for f in facts]
            m["coverage_all"] = (sum(covered), len(facts))
            lead_facts = lead(cases[key])
            m["coverage_lead"] = (sum(mentioned(clean, f) for f in lead_facts), len(lead_facts))
            for slot in SLOTS:
                chosen = [hit for f, hit in zip(facts, covered) if SLOT.get(f["role"]) == slot]
                m[f"coverage_{slot}"] = (sum(chosen), len(chosen))
            texts = [e for e in map(evidence, claims.values()) if e]
            m["ceiling_all"] = (sum(any(mentioned(t, f) for t in texts) for f in facts), len(facts))
            m["words"] = (words, 1)
            m["density"] = (100 * sum(covered), words)
        else:
            m["words"] = (len(ThaiWords().tokenize(clean)), 1)
            scores = rouge.score(references[key], clean)
            for name in ("rouge1", "rouge2", "rougeL"):
                m[name] = (scores[name].fmeasure, 1)
        if arm in ("B", "C"):
            parts = units(summary)
            cited = [(t, ids) for t, ids in parts if ids]
            m["cited_chars"] = (sum(len(t) for t, _ in cited), sum(len(t) for t, _ in parts))
            all_ids = [i for _, ids in cited for i in ids]
            m["ids_exist"] = (sum(i in claims for i in all_ids), len(all_ids))
            digit_units = [(t, ids) for t, ids in cited if DIGITS.search(t)]
            m["cited_digit_support"] = (sum(all(d in " ".join(e for e in (evidence(claims[i]) if i in claims else None
                                                                              for i in ids) if e)
                                                for d in DIGITS.findall(t)) for t, ids in digit_units),
                                        len(digit_units))
            m["cites_not_confirmed"] = (sum(any(claims.get(i, {}).get("epistemic_status") == "not_confirmed"
                                                for i in ids) for _, ids in cited), len(cited))
        rows[language].setdefault(key, {})[arm] = m

    def pooled(keys: list[str], arm: str, name: str, picks: np.ndarray | None = None):
        values = np.array([rows_now[k][arm][name] for k in keys], dtype=float)
        if picks is None:
            return values[:, 0].sum() / max(values[:, 1].sum(), 1e-12)
        sums = values[picks].sum(axis=1)
        return sums[:, 0] / np.maximum(sums[:, 1], 1e-12)

    report: dict = {}
    md = ["# Claims-only judgement: result", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Raw `{raw.name}`. "
          f"Backend `{args.backend}`. Pooled ratios (sums over cases); case bootstrap {RESAMPLES}, seed {SEED}; "
          "pairs use cases completed in both arms.", ""]
    for language in ("english", "thai"):
        rows_now = rows[language]
        names = sorted({n for k in rows_now.values() for a in k.values() for n in a})
        report[language] = {"failures": failures[language], "measures": {}}
        md += [f"## {language} (cases with any output: {len(rows_now)}; failures {failures[language]})", "",
               "| Measure | A | B | C | C − A | B − A | C − B |", "|---|---|---|---|---|---|---|"]
        for name in names:
            cells, entry = [], {}
            for arm in ARMS:
                keys = [k for k, v in rows_now.items() if arm in v and name in v[arm] and v[arm][name][1] > 0]
                if not keys:
                    cells.append("–")
                    continue
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                point, boot = pooled(keys, arm, name), pooled(keys, arm, name, picks)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                entry[arm] = [round(float(point), 4), round(float(lo), 4), round(float(hi), 4), len(keys)]
                cells.append(f"{point:.3f} [{lo:.3f}, {hi:.3f}]")
            for left, right in PAIRS:
                keys = [k for k, v in rows_now.items() if left in v and right in v and name in v[left] and name in v[right]
                        and v[left][name][1] > 0 and v[right][name][1] > 0]
                if not keys:
                    cells.append("–")
                    continue
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                point = pooled(keys, left, name) - pooled(keys, right, name)
                boot = pooled(keys, left, name, picks) - pooled(keys, right, name, picks)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                entry[f"{left}-{right}"] = [round(float(point), 4), round(float(lo), 4), round(float(hi), 4), len(keys)]
                cells.append(f"{point:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            report[language]["measures"][name] = entry
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "judgement_claims_only.md").write_text("\n".join(md), encoding="utf-8")
    (HERE / "results" / "judgement_claims_only.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
