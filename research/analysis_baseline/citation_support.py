from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

import book_scores as bs

HERE = Path(__file__).resolve().parent
JUDGE = "cross-encoder/nli-deberta-v3-small"
CLAIMS_ONLY = "raw_judgement_claims_only_main_20261004_013832"
CURRENT = "main_20261001_021428"
CACHE = HERE / "results" / "citation_support_cache.jsonl"
CONFIGURED = {"one call": (bs.DESIGN, "single"), "two calls": (bs.DESIGN, "cybercase"),
              "current": (CURRENT, "cybercase_nogrammar")}
BRACKET = re.compile("[[](A-[0-9]+(?:[ ]*,[ ]*A-[0-9]+)*)[]]")
LETTERS = re.compile("[A-Za-z]{3,}")
NL = chr(10)


class Judge:
    def __init__(self) -> None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(JUDGE)
        self.model = AutoModelForSequenceClassification.from_pretrained(JUDGE, dtype=torch.float32).eval()
        self.model.to(self.device)
        self.labels = {i: self.model.config.id2label[i].lower() for i in range(self.model.config.num_labels)}
        if set(self.labels.values()) != {"entailment", "neutral", "contradiction"}:
            raise SystemExit(f"unexpected labels: {self.labels}")
        self.cache: dict[str, dict] = {}
        if CACHE.exists():
            for line in CACHE.read_text(encoding="utf-8").split(NL):
                if line.strip():
                    record = json.loads(line)
                    self.cache[record["key"]] = record
        self.out = CACHE.open("a", encoding="utf-8")
        self.new = 0

    def record(self, premise: str, hypothesis: str) -> dict:
        key = hashlib.sha256((premise + chr(0) + hypothesis).encode("utf-8")).hexdigest()
        if key not in self.cache:
            length = len(self.tokenizer(premise, hypothesis)["input_ids"])
            try:
                batch = self.tokenizer(premise, hypothesis, truncation="only_first", max_length=512,
                                       return_tensors="pt")
                mode = "only_first"
            except Exception:
                batch = self.tokenizer(premise, hypothesis, truncation="longest_first", max_length=512,
                                       return_tensors="pt")
                mode = "longest_first"
            with self.torch.no_grad():
                logits = self.model(**batch.to(self.device)).logits
                probs = self.torch.softmax(logits, dim=-1)[0].cpu().tolist()
            record = {"key": key, "label": self.labels[int(np.argmax(probs))], "probs": probs,
                      "length": length, "truncation": mode if length > 512 else None}
            self.cache[key] = record
            self.out.write(json.dumps(record, ensure_ascii=True) + NL)
            self.out.flush()
            self.new += 1
        return self.cache[key]

    def entails(self, premise: str, hypothesis: str) -> bool:
        return self.record(premise, hypothesis)["label"] == "entailment"


def alce(judge: Judge, statement: str, citations: list[str]) -> tuple[int, int, int]:
    if not citations:
        return 0, 0, 0
    joint = judge.entails(NL.join(citations), statement)
    precise = 0
    if joint:
        if len(citations) == 1:
            precise = 1
        else:
            for i, citation in enumerate(citations):
                if judge.entails(citation, statement):
                    precise += 1
                elif not judge.entails(NL.join(citations[:i] + citations[i + 1:]), statement):
                    precise += 1
    return int(joint), precise, len(citations)


def overlap(statement: str, premise: str) -> float:
    words = bs.v0_words(statement).split()
    present = set(bs.v0_words(premise).split())
    return sum(w in present for w in words) / len(words) if words else 0.0


def verified(claim: dict) -> list[str]:
    return [c["exact_quote"] for c in claim["supporting_citations"] if c.get("exact_quote")]


def ratio(pairs: list[tuple[int, int]]) -> float | None:
    total = sum(d for _, d in pairs)
    return sum(n for n, _ in pairs) / total if total else None


def paired(a: dict, b: dict) -> tuple[list[str], tuple[float, float, float] | None]:
    keys = sorted(k for k in set(a) & set(b) if a[k] is not None and b[k] is not None)
    return keys, (bs.mean_difference(a, b, keys) if keys else None)


def shown(result) -> str:
    if result is None:
        return "-"
    return f"{bs.signed(result[0])} [{bs.signed(result[1])}, {bs.signed(result[2])}]"


def verdict(result) -> str:
    if result is None:
        return "-"
    return "excludes 0" if result[1] > 0 or result[2] < 0 else "includes 0"


def claims_part(judge: Judge) -> dict:
    views, _ = bs.analysis(CONFIGURED, tuple(CONFIGURED))
    arms, per_case = {}, {}
    for label in CONFIGURED:
        cond, recall, prec, single, noncopy = {}, {}, {}, {}, {}
        rows = []
        for case_id, view in views[label].items():
            if not view["done"]:
                continue
            c_rows = []
            for claim in view["trace"]["claims"]:
                quotes = verified(claim)
                joint, precise, total = alce(judge, claim["text"], quotes)
                premise = NL.join(quotes)
                row = {"case": case_id, "quotes": len(quotes), "entailed": joint, "precise": precise,
                       "citations": total,
                       "premise_tokens": len(judge.tokenizer(premise)["input_ids"]) if quotes else 0,
                       "overlap": overlap(claim["text"], premise) if quotes else None}
                c_rows.append(row)
            rows += c_rows
            quoted = [r for r in c_rows if r["quotes"]]
            cond[case_id] = float(np.mean([r["entailed"] for r in quoted])) if quoted else None
            recall[case_id] = float(np.mean([r["entailed"] for r in c_rows])) if c_rows else None
            prec[case_id] = ratio([(r["precise"], r["citations"]) for r in c_rows])
            ones = [r for r in quoted if r["quotes"] == 1]
            single[case_id] = float(np.mean([r["entailed"] for r in ones])) if ones else None
            loose = [r for r in quoted if r["overlap"] < 0.9]
            noncopy[case_id] = float(np.mean([r["entailed"] for r in loose])) if loose else None
        quoted_rows = [r for r in rows if r["quotes"]]
        arms[label] = {
            "claims": len(rows), "claims_with_quote": len(quoted_rows),
            "conditional_support_pooled": ratio([(r["entailed"], 1) for r in quoted_rows]),
            "alce_recall_pooled": ratio([(r["entailed"], 1) for r in rows]),
            "alce_precision_pooled": ratio([(r["precise"], r["citations"]) for r in rows]),
            "mean_premise_tokens": float(np.mean([r["premise_tokens"] for r in quoted_rows])),
            "mean_overlap": float(np.mean([r["overlap"] for r in quoted_rows])),
            "near_copies": ratio([(int(r["overlap"] >= 0.9), 1) for r in quoted_rows]),
            "single_quote_support_pooled": ratio([(r["entailed"], 1) for r in quoted_rows if r["quotes"] == 1]),
            "noncopy_support_pooled": ratio([(r["entailed"], 1) for r in quoted_rows if r["overlap"] < 0.9])}
        per_case[label] = {"conditional": cond, "recall": recall, "precision": prec, "single": single,
                           "noncopy": noncopy}
    contrasts = []
    for later, earlier in (("current", "one call"), ("two calls", "one call"), ("current", "two calls")):
        for metric in ("conditional", "recall", "precision", "single", "noncopy"):
            keys, result = paired(per_case[earlier][metric], per_case[later][metric])
            contrasts.append({"pair": f"{later} − {earlier}", "metric": metric, "cases": len(keys),
                              "difference": list(result) if result else None})
    return {"arms": arms, "contrasts": contrasts}


def units_of(summary: str, claims: dict) -> list[tuple[str, list[str]]]:
    units, start = [], 0
    for match in BRACKET.finditer(summary):
        text = summary[start:match.start()].strip().lstrip(".;,:").strip()
        ids = [i.strip() for i in match.group(1).split(",")]
        units.append((text, [i for i in ids if i in claims]))
        start = match.end()
    tail = summary[start:].strip().lstrip(".;,:").strip()
    if LETTERS.search(tail):
        units.append((tail, []))
    return [(t, ids) for t, ids in units if LETTERS.search(t)]


def summary_part(judge: Judge) -> dict:
    raw = HERE / "results" / CLAIMS_ONLY
    per_item = {arm: {"recall": {}, "precision": {}, "e2e_recall": {}} for arm in ("B", "C")}
    stats = {arm: {"items": 0, "failed": 0, "units": 0, "units_without_id": 0, "premise_tokens": [],
                   "overlap": []} for arm in ("B", "C")}
    for path in sorted(raw.glob("*_?.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        arm = saved["arm"]
        if saved["language"] != "english" or arm not in per_item:
            continue
        if "judgement" not in saved:
            stats[arm]["failed"] += 1
            continue
        stats[arm]["items"] += 1
        claims = {c["claim_id"]: c for c in saved["reading"]["claims"]}
        rows = []
        for text, ids in units_of(saved["judgement"]["summary"], claims):
            cited = [claims[i]["text"] for i in ids]
            joint, precise, total = alce(judge, text, cited)
            chained = [NL.join(verified(claims[i])) for i in ids if verified(claims[i])]
            e2e, _, _ = alce(judge, text, chained)
            rows.append((joint, precise, total, e2e))
            stats[arm]["units"] += 1
            stats[arm]["units_without_id"] += int(not ids)
            if ids:
                premise = NL.join(cited)
                stats[arm]["premise_tokens"].append(len(judge.tokenizer(premise)["input_ids"]))
                stats[arm]["overlap"].append(overlap(text, premise))
        key = saved["key"]
        per_item[arm]["recall"][key] = float(np.mean([r[0] for r in rows])) if rows else None
        per_item[arm]["precision"][key] = ratio([(r[1], r[2]) for r in rows])
        per_item[arm]["e2e_recall"][key] = float(np.mean([r[3] for r in rows])) if rows else None
    arms = {}
    for arm in ("B", "C"):
        s = stats[arm]
        arms[arm] = {"items": s["items"], "failed": s["failed"], "units": s["units"],
                     "units_without_id": s["units_without_id"],
                     "recall_mean": float(np.mean([v for v in per_item[arm]["recall"].values() if v is not None])),
                     "precision_mean": float(np.mean([v for v in per_item[arm]["precision"].values()
                                                      if v is not None])),
                     "e2e_recall_mean": float(np.mean([v for v in per_item[arm]["e2e_recall"].values()
                                                       if v is not None])),
                     "mean_premise_tokens": float(np.mean(s["premise_tokens"])),
                     "mean_overlap": float(np.mean(s["overlap"]))}
    contrasts = []
    for metric in ("recall", "precision", "e2e_recall"):
        keys, result = paired(per_item["B"][metric], per_item["C"][metric])
        contrasts.append({"pair": "C − B", "metric": metric, "items": len(keys),
                          "difference": list(result) if result else None})
    return {"arms": arms, "contrasts": contrasts}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    judge = Judge()
    claims = claims_part(judge)
    summaries = summary_part(judge)
    records = list(judge.cache.values())
    truncated = sum(1 for r in records if r["truncation"])
    out = {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "judge": JUDGE,
           "device": judge.device, "dtype": "float32", "labels": judge.labels, "pairs_judged": len(records),
           "pairs_new_this_run": judge.new, "pairs_truncated": truncated, "claims": claims, "summaries": summaries}
    (HERE / "results" / "citation_support.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    def pct(x):
        return "-" if x is None else f"{x:.3f}"

    md = ["# Estimated citation support, ALCE-style (judge: nli-deberta-v3-small)", "",
          f"Script sha256 `{out['script_sha256']}`. Judge `{JUDGE}`, {judge.device}, fp32, argmax. "
          f"{len(records)} distinct pairs judged, {truncated} over 512 tokens (premise truncated). An automatic "
          f"estimate, not human-validated. English only.", "",
          "## Part 1: claims and their verified quotes (held-out cases 51-150)", "",
          "| Arm | Claims | With a verified quote | Conditional support | ALCE recall | ALCE precision | "
          "Premise tokens | Claim-quote overlap | Near-copies | Support, one quote | Support, overlap < 0.9 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, a in claims["arms"].items():
        md.append(f"| {label} | {a['claims']} | {a['claims_with_quote']} | {pct(a['conditional_support_pooled'])} | "
                  f"{pct(a['alce_recall_pooled'])} | {pct(a['alce_precision_pooled'])} | "
                  f"{a['mean_premise_tokens']:.0f} | {a['mean_overlap']:.3f} | {pct(a['near_copies'])} | "
                  f"{pct(a['single_quote_support_pooled'])} | {pct(a['noncopy_support_pooled'])} |")
    md += ["", "Pooled over claims. Contrasts below are paired over cases (case-level means), cases completed in both.",
           "", "| Pair | Metric | Cases | Difference [95%] | Interval |", "|---|---|---|---|---|"]
    for c in claims["contrasts"]:
        md.append(f"| {c['pair']} | {c['metric']} | {c['cases']} | {shown(c['difference'])} | "
                  f"{verdict(c['difference'])} |")
    md += ["", "## Part 2: summary sentences and the claims they cite (claims-only study, English, Gemma)", "",
           "| Arm | Items | Failed | Units | Units without a valid ID | Recall (cited claims) | Precision | "
           "Recall end to end (claims' quotes) | Premise tokens | Unit-premise overlap |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for arm, a in summaries["arms"].items():
        md.append(f"| {arm} | {a['items']} | {a['failed']} | {a['units']} | {a['units_without_id']} | "
                  f"{a['recall_mean']:.3f} | {a['precision_mean']:.3f} | {a['e2e_recall_mean']:.3f} | "
                  f"{a['mean_premise_tokens']:.0f} | {a['mean_overlap']:.3f} |")
    md += ["", "Item-level means. Contrasts paired over items completed in both.", "",
           "| Pair | Metric | Items | Difference [95%] | Interval |", "|---|---|---|---|---|"]
    for c in summaries["contrasts"]:
        md.append(f"| {c['pair']} | {c['metric']} | {c['items']} | {shown(c['difference'])} | "
                  f"{verdict(c['difference'])} |")
    (HERE / "results" / "citation_support.md").write_text(NL.join(md) + NL, encoding="utf-8")
    print(NL.join(md))


if __name__ == "__main__":
    main()
