from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
THAI = HERE.parents[1] / "evaluation" / "ocr_downstream" / "thaisum_ocr"
ENGLISH = {"confirmation": "main_20261001_021428", "development": "main_20260930_193646"}
ARM = "cybercase_nogrammar"
SEED, RESAMPLES, TOP = 2026, 2000, 5
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"


def backend(path: str):
    sys.path.insert(0, path)
    import app.trace.bind as bind
    from app.trace.sentences import sentence_spans

    if not Path(bind.__file__).resolve().is_relative_to(Path(path).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    return bind.located_quote, sentence_spans


def items() -> dict[str, list[dict]]:
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    out: dict[str, list[dict]] = {}
    for split, run in ENGLISH.items():
        for path in sorted((HERE / "results" / f"raw_{run}").glob(f"*_{ARM}_1.json")):
            written = json.loads(path.read_text(encoding="utf-8")).get("written")
            if written and written.get("summary"):
                case = path.name.split("_")[0]
                out.setdefault(f"English {split}", []).append(
                    {"key": case, "text": cases[case]["text"], "claims": written["claims"], "summary": written["summary"]})
    articles = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if line.strip():
            record = json.loads(line)
            articles[record["id"]] = record
    for path in sorted((THAI / "results" / "raw_20261001_223057").glob("*_clean.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("reading") and saved.get("bound") and saved["bound"].get("summary"):
            article = path.name.split("_")[0]
            out.setdefault("Thai clean", []).append({"key": article, "text": articles[article]["clean"],
                                                     "claims": saved["reading"]["claims"],
                                                     "summary": saved["bound"]["summary"]})
    return out


def perturbed(sentence: str) -> str | None:
    groups = list(DIGITS.finditer(sentence))
    if not groups:
        return None
    last = groups[-1]
    digits = [i for i in range(last.start(), last.end()) if sentence[i].isdigit()]
    at = digits[-1]
    return sentence[:at] + str((int(sentence[at]) + 1) % 10) + sentence[at + 1:]


def auroc(pos: list[float], neg: list[float]) -> float:
    scores = np.array(pos + neg)
    labels = np.array([1] * len(pos) + [0] * len(neg))
    order = scores.argsort()
    ranks = np.empty(len(scores))
    ranks[order] = np.arange(1, len(scores) + 1)
    return float((ranks[labels == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def share(rows: list[dict], key: str) -> list:
    by_case: dict[str, list[int]] = {}
    for r in rows:
        by_case.setdefault(r["case"], [0, 0])
        by_case[r["case"]][0] += int(bool(r[key]))
        by_case[r["case"]][1] += 1
    counts = np.array(list(by_case.values()), dtype=float)
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / sums[:, 1]
    hits, total = int(counts[:, 0].sum()), int(counts[:, 1].sum())
    return [hits, total, round(hits / total, 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4)]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    located_quote, sentence_spans = backend(args.backend)
    import torch
    from sentence_transformers import CrossEncoder, SentenceTransformer
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    encoder = SentenceTransformer("BAAI/bge-m3", device="cpu")
    reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", device="cpu")
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    nli = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    entail = {v.lower(): k for k, v in nli.config.id2label.items()}["entailment"]

    def entailment(premise: str, hypothesis: str) -> float:
        batch = tokenizer(premise, hypothesis, truncation="only_first", max_length=512, return_tensors="pt")
        with torch.no_grad():
            return float(torch.softmax(nli(**batch).logits[0], dim=-1)[entail])

    rows_by: dict[str, list[dict]] = {}
    for name, data in items().items():
        rows = []
        for item in data:
            claims = []
            for claim in item["claims"]:
                quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
                located = [q for q in quotes if located_quote(item["text"], q) is not None]
                claims.append({"id": claim["claim_id"], "text": claim.get("text", ""), "checked": bool(located),
                               "evidence": " ".join([claim.get("text", ""), *located])})
            if not claims:
                continue
            sentences = [item["summary"][a:b] for a, b in sentence_spans(item["summary"])] or [item["summary"]]
            claim_vectors = encoder.encode([c["text"] for c in claims], normalize_embeddings=True)
            sentence_vectors = encoder.encode(sentences, normalize_embeddings=True)
            for s_at, sentence in enumerate(sentences):
                top = np.argsort(-(claim_vectors @ sentence_vectors[s_at]))[:TOP]
                scores = reranker.predict([(sentence, claims[i]["text"]) for i in top])
                best = claims[int(top[int(np.argmax(scores))])]
                digits = DIGITS.findall(sentence)
                row = {"case": item["key"], "sentence": sentence, "claim": best["text"], "claim_id": best["id"],
                       "checked": best["checked"], "digits_ok": all(d in best["evidence"] for d in digits),
                       "entail": entailment(best["evidence"], sentence)}
                row["traceable"] = row["checked"] and row["digits_ok"]
                negative = perturbed(sentence)
                if negative:
                    row["entail_negative"] = entailment(best["evidence"], negative)
                rows.append(row)
        rows_by[name] = rows
        print(name, len(rows), "sentences", flush=True)

    dev = rows_by["English development"]
    pos = [r["entail"] for r in dev if "entail_negative" in r]
    neg = [r["entail_negative"] for r in dev if "entail_negative" in r]
    grid = np.linspace(0.01, 0.99, 99)
    threshold = float(max(grid, key=lambda t: (np.mean(np.array(pos) >= t) + np.mean(np.array(neg) < t)) / 2))
    report: dict = {"threshold (English development)": round(threshold, 2), "datasets": {}}
    md = ["# Summary sentence traceability: encoder + reranker + rule, and NLI", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          f"Local models, CPU. NLI threshold, chosen on English development by balanced accuracy: {threshold:.2f}.", "",
          "| Data | Sentences | Best claim checked | Traceable (checked + digits) | NLI entailed ≥ threshold | "
          "NLI AUROC, digit change (n pairs) |", "|---|---|---|---|---|---|"]
    for name, rows in rows_by.items():
        for r in rows:
            r["entailed"] = r["entail"] >= threshold
        paired = [r for r in rows if "entail_negative" in r]
        area = auroc([r["entail"] for r in paired], [r["entail_negative"] for r in paired]) if paired else None
        cell = {"sentences": len(rows), "checked": share(rows, "checked"), "traceable": share(rows, "traceable"),
                "entailed": share(rows, "entailed"), "auroc": round(area, 3) if area else None, "pairs": len(paired)}
        report["datasets"][name] = cell
        shown = lambda c: f"{c[2]:.3f} [{c[3]:.3f}, {c[4]:.3f}]"
        md.append(f"| {name} | {len(rows)} | {shown(cell['checked'])} | {shown(cell['traceable'])} | "
                  f"{shown(cell['entailed'])} | {cell['auroc']} ({len(paired)}) |")
        sheet_dir = THAI / "results" if name.startswith("Thai") else HERE / "results"
        sample = random.Random(SEED).sample(rows, min(30, len(rows)))
        lines = [f"# Pairing check, {name}: is the claim the one the sentence rests on? Mark yes/no.", "",
                 "| # | Case | Summary sentence | Best claim | checked | NLI | Right pair? |", "|---|---|---|---|---|---|---|"]
        for n, r in enumerate(sample, 1):
            lines.append(f"| {n} | {r['case']} | {r['sentence'].replace('|', '/')} | {r['claim'].replace('|', '/')} | "
                         f"{r['checked']} | {r['entail']:.2f} |  |")
        (sheet_dir / f"summary_pairing_check_{name.replace(' ', '_')}.md").write_text("\n".join(lines), encoding="utf-8")
    (HERE / "results" / "summary_encoder_nli.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "summary_encoder_nli.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
