from __future__ import annotations

import argparse
import asyncio
import json
import random
from pathlib import Path

import nltk
import numpy as np
import torch
from pydantic import BaseModel, ConfigDict, Field
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig, configured_pipeline, provider_order
from scores_common import jsonl, lead, share, v0_words

RUN, ARM = "main_20261001_021428", "cybercase_nogrammar"


def arm(run: str, name: str) -> dict[str, dict]:
    views = {}
    for record in jsonl(HERE / "results" / f"{run}.jsonl"):
        if record["arm"] != name or record.get("run", 1) != 1 or record.get("error_kind") in ("budget", "harness"):
            continue
        view = {"record": record, "case": CASES[record["case"]], "done": "error" not in record}
        if view["done"]:
            stem = HERE / "results" / f"raw_{run}" / f"{record['case']}_{name}_1"
            view["trace"] = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))["bound"]
        views[record["case"]] = view
    return dict(sorted(views.items()))


def m5_v0(text: str, case: dict) -> float:
    return share(f" {fact['text']} " in f" {v0_words(text)} " for fact in lead(case))
MODEL = "google/gemma-4-26b-a4b-it"
PROVIDERS = "nextbit/bf16,coreweave/bf16"
MINICHECK = "lytang/MiniCheck-DeBERTa-v3-Large"
MINICHECK_REVISION = "2f2d01a54fa022a7ffadb76260e1ea8bc88c82bb"
THRESHOLD = 0.5
WINDOW, STRIDE = 6, 3
SEED = 2026
RESAMPLES = 2000
PRICE_IN, PRICE_OUT = 0.09e-6, 0.30e-6
HERE = Path(__file__).resolve().parent
CASES = {case["id"]: case for case in jsonl(HERE / "data" / "cases.jsonl")}
OUT = HERE / "results" / "summary_level_en"

SYSTEM = "You summarize a criminal case document for an investigator. Use only facts stated in the document. Keep attribution: say who reported or alleged something when the document does. Do not add analysis, classification, or recommendations. Write plain English prose without bullets or headings."


class DirectSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(max_length=4000)


def words_target(view: dict) -> int:
    return len(view["trace"]["summary"].split())


def direct_prompt(text: str, words: int) -> str:
    return f"Summarize the document in about {words} words.\n\nDocument:\n{text}"


async def generate(views: dict[str, dict], config: AnalysisPipelineConfig, concurrency: int) -> None:
    (OUT / "direct").mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(concurrency)

    async def one(case_id: str, view: dict) -> None:
        path = OUT / "direct" / f"{case_id}.json"
        if path.exists():
            return
        calls: list = []
        async with semaphore:
            try:
                reply = await request_stage(config=config, stage="direct_summary", system=SYSTEM, content=direct_prompt(view["case"]["text"], words_target(view)), schema=DirectSummary, calls=calls)
                record = {"summary": reply.summary, "error": None, "calls": calls}
            except Exception as error:
                record = {"summary": None, "error": f"{type(error).__name__}: {str(error)[:300]}", "calls": calls}
        path.write_text(json.dumps(record, ensure_ascii=False, default=str), encoding="utf-8")
        print(case_id, "ok" if record["summary"] else "failed", flush=True)

    await asyncio.gather(*(one(case_id, view) for case_id, view in views.items()))


def load_judge(device: str):
    tokenizer = AutoTokenizer.from_pretrained(MINICHECK, revision=MINICHECK_REVISION, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(MINICHECK, revision=MINICHECK_REVISION, local_files_only=True).to(device).eval()
    return tokenizer, model


def support_scores(tokenizer, model, device: str, article: str, sentences: list[str], batch: int = 8) -> list[float]:
    article_sentences = nltk.sent_tokenize(article)
    windows = [" ".join(article_sentences[start:start + WINDOW]) for start in range(0, max(1, len(article_sentences) - WINDOW + STRIDE), STRIDE)] or [article]
    pairs = [(window, sentence) for sentence in sentences for window in windows]
    probabilities: list[float] = []
    for start in range(0, len(pairs), batch):
        chunk = pairs[start:start + batch]
        encoded = tokenizer([p for p, _ in chunk], [h for _, h in chunk], truncation="only_first", max_length=512, padding=True, return_tensors="pt").to(device)
        with torch.inference_mode():
            logits = model(**encoded).logits.float()
        probabilities.extend(logits.softmax(dim=-1)[:, 1].tolist())
    per_sentence = [max(probabilities[index * len(windows):(index + 1) * len(windows)]) for index in range(len(sentences))]
    return per_sentence


def score_summary(tokenizer, model, device: str, case: dict, summary: str) -> dict:
    sentences = [s for s in nltk.sent_tokenize(summary) if s.strip()]
    if not sentences:
        return {"sentences": 0, "unsupported": None, "coverage": m5_v0(summary, case), "words": len(summary.split())}
    scores = support_scores(tokenizer, model, device, case["text"], sentences)
    return {"sentences": len(sentences), "unsupported": float(np.mean([s < THRESHOLD for s in scores])), "coverage": m5_v0(summary, case), "words": len(summary.split())}


def mean_ci(values: list[float], rng: np.random.RandomState) -> dict:
    array = np.asarray(values, dtype=float)
    draws = rng.randint(0, len(array), size=(RESAMPLES, len(array)))
    means = array[draws].mean(axis=1)
    return {"n": int(len(array)), "mean": float(array.mean()), "low": float(np.percentile(means, 2.5)), "high": float(np.percentile(means, 97.5))}


def score_all(views: dict[str, dict], device: str) -> dict:
    tokenizer, model = load_judge(device)
    rows = {}
    for case_id, view in views.items():
        saved = json.loads((OUT / "direct" / f"{case_id}.json").read_text(encoding="utf-8"))
        judgement = score_summary(tokenizer, model, device, view["case"], view["trace"]["summary"])
        direct = None if saved["summary"] is None else score_summary(tokenizer, model, device, view["case"], saved["summary"])
        rows[case_id] = {"judgement": judgement, "direct": direct, "failed": saved["summary"] is None, "calls": saved["calls"]}
        print(case_id, "scored", flush=True)
    return rows


def summarise(rows: dict[str, dict]) -> dict:
    paired = [(c, r) for c, r in rows.items() if r["direct"] is not None and r["direct"]["unsupported"] is not None and r["judgement"]["unsupported"] is not None]
    rng = np.random.RandomState(SEED)
    result = {
        "run": RUN,
        "arm": ARM,
        "cases": len(rows),
        "direct_failed": sum(r["failed"] for r in rows.values()),
        "paired": len(paired),
        "words": {
            "judgement_median": float(np.median([r["judgement"]["words"] for r in rows.values()])),
            "direct_median": float(np.median([r["direct"]["words"] for r in rows.values() if r["direct"]])),
        },
        "unsupported_judgement": mean_ci([r["judgement"]["unsupported"] for _, r in paired], rng),
        "unsupported_direct": mean_ci([r["direct"]["unsupported"] for _, r in paired], rng),
        "unsupported_diff_direct_minus_judgement": mean_ci([r["direct"]["unsupported"] - r["judgement"]["unsupported"] for _, r in paired], rng),
        "coverage_judgement": mean_ci([r["judgement"]["coverage"] for _, r in paired], rng),
        "coverage_direct": mean_ci([r["direct"]["coverage"] for _, r in paired], rng),
        "coverage_diff_direct_minus_judgement": mean_ci([r["direct"]["coverage"] - r["judgement"]["coverage"] for _, r in paired], rng),
    }
    usage = [call for r in rows.values() for call in r["calls"]]
    tokens_in = sum(call.get("input_tokens") or 0 for call in usage)
    tokens_out = sum((call.get("output_tokens") or 0) + (call.get("thinking_tokens") or 0) for call in usage)
    result["usage"] = {"calls": len(usage), "input_tokens": tokens_in, "output_tokens_incl_thinking": tokens_out, "usd_estimate": tokens_in * PRICE_IN + tokens_out * PRICE_OUT}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--score-only", action="store_true")
    args = parser.parse_args()
    views = {case_id: view for case_id, view in arm(RUN, ARM).items() if view["done"]}
    views = dict(list(views.items())[: args.limit] if args.limit else views.items())
    OUT.mkdir(parents=True, exist_ok=True)
    if not args.score_only:
        config = AnalysisPipelineConfig.model_validate({**configured_pipeline().model_dump(), "model": MODEL, "providers": provider_order(PROVIDERS)})
        asyncio.run(generate(views, config, args.concurrency))
    rows = score_all(views, args.device)
    (OUT / "per_case.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    result = summarise(rows)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
