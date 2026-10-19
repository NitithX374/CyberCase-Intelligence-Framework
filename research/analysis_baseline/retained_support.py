from __future__ import annotations

import gc
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

import binding_downstream as bd

HERE = Path(__file__).resolve().parent
BACKEND = "F:/cc-worktrees/measure-e35e558/backend"
JUDGES = {"English": "cross-encoder/nli-deberta-v3-small",
          "Thai": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"}
SAMPLE, BATCH, RESAMPLES = 150, 32, 2000
NL = chr(10)


class Judge:
    def __init__(self, name: str) -> None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.name = name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForSequenceClassification.from_pretrained(name, dtype=torch.float32).eval()
        self.model.to(self.device)
        labels = {i: self.model.config.id2label[i].lower() for i in range(self.model.config.num_labels)}
        if set(labels.values()) != {"entailment", "neutral", "contradiction"}:
            raise SystemExit(f"unexpected labels: {labels}")
        self.entail = next(i for i, label in labels.items() if label == "entailment")
        self.pairs = 0
        self.truncated = 0

    def any_entails(self, windows: list[str], hypothesis: str) -> bool:
        for start in range(0, len(windows), BATCH):
            chunk = windows[start:start + BATCH]
            self.truncated += sum(len(self.tokenizer(w, hypothesis)["input_ids"]) > 512 for w in chunk)
            try:
                batch = self.tokenizer(chunk, [hypothesis] * len(chunk), truncation="only_first", max_length=512,
                                       padding=True, return_tensors="pt")
            except Exception:
                batch = self.tokenizer(chunk, [hypothesis] * len(chunk), truncation="longest_first",
                                       max_length=512, padding=True, return_tensors="pt")
            with self.torch.no_grad():
                logits = self.model(**batch.to(self.device)).logits
            self.pairs += len(chunk)
            if bool((logits.argmax(dim=-1) == self.entail).any().item()):
                return True
        return False

    def close(self) -> None:
        del self.model
        gc.collect()
        if self.device == "cuda":
            self.torch.cuda.empty_cache()


def windows_of(text: str, sentence_spans) -> list[str]:
    spans = list(sentence_spans(text))
    out = []
    for i, (a, b) in enumerate(spans):
        out.append(text[a:b])
        if i + 1 < len(spans):
            out.append(text[a:spans[i + 1][1]])
    return [w for w in out if w.strip()]


def clustered(demoted: list[tuple[int, bool]], confirmed: list[tuple[int, bool]]) -> list[float] | None:
    if not demoted or not confirmed:
        return None
    cases = sorted({c for c, _ in demoted} | {c for c, _ in confirmed})
    by_d = {c: [] for c in cases}
    by_c = {c: [] for c in cases}
    for c, s in demoted:
        by_d[c].append(s)
    for c, s in confirmed:
        by_c[c].append(s)
    rng = np.random.default_rng(2026)
    diffs = []
    for _ in range(RESAMPLES):
        pick = rng.choice(cases, len(cases), replace=True)
        d = [s for c in pick for s in by_d[c]]
        k = [s for c in pick for s in by_c[c]]
        if d and k:
            diffs.append(np.mean(d) - np.mean(k))
    point = float(np.mean([s for _, s in demoted]) - np.mean([s for _, s in confirmed]))
    return [point, float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]


def rate(units: list[tuple[int, bool]]) -> str:
    if not units:
        return "-"
    hits = sum(s for _, s in units)
    return f"{hits}/{len(units)} = {hits / len(units):.3f}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    located_quote, quotes = bd.binder(BACKEND)
    from app.trace.sentences import sentence_spans

    check = bd.checkers(located_quote, quotes)["production"]
    data = bd.readings()
    report: dict = {"sets": {}, "judges": {}}
    md = ["# Retained unconfirmed claims: support elsewhere in the source (automatic)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{BACKEND}`. "
          f"Windows of one or two source sentences; supported when any window's argmax is entailment. "
          f"Confirmed claims sampled ({SAMPLE} per set, seed 2026). Case-clustered bootstrap ({RESAMPLES}). "
          "An automatic estimate, not human-validated.", "",
          "| Set | Judge | Demoted supported | Confirmed supported | Demoted − confirmed [95%] | "
          "Floor, demoted | Floor, confirmed |", "|---|---|---|---|---|---|---|"]
    for language in ("English", "Thai"):
        judge = Judge(JUDGES[language])
        for name, items in data.items():
            if not name.startswith(language):
                continue
            demoted, confirmed = [], []
            for idx, (_, text, reading) in enumerate(items):
                status = bd.bound_claims(check, text, reading)
                for claim in reading.get("claims", []):
                    s = status[claim["claim_id"]]
                    if s == "demoted":
                        demoted.append((idx, claim["text"]))
                    elif s == "bound" and claim.get("epistemic_status") == "reported":
                        confirmed.append((idx, claim["text"]))
            rng = np.random.default_rng(2026)
            if len(confirmed) > SAMPLE:
                confirmed = [confirmed[i] for i in sorted(rng.choice(len(confirmed), SAMPLE, replace=False))]
            cache: dict[int, list[str]] = {}

            def windows(i: int) -> list[str]:
                if i not in cache:
                    cache[i] = windows_of(items[i][1], sentence_spans)
                return cache[i]

            n = len(items)
            scored = {}
            for group, units in (("demoted", demoted), ("confirmed", confirmed)):
                own = [(i, judge.any_entails(windows(i), text)) for i, text in units]
                floor = [(i, judge.any_entails(windows((i + 1) % n), text)) for i, text in units]
                scored[group] = {"own": own, "floor": floor}
            diff = clustered(scored["demoted"]["own"], scored["confirmed"]["own"])
            report["sets"][name] = {
                "demoted": {"supported": sum(s for _, s in scored["demoted"]["own"]), "n": len(demoted),
                            "floor": sum(s for _, s in scored["demoted"]["floor"])},
                "confirmed": {"supported": sum(s for _, s in scored["confirmed"]["own"]), "n": len(confirmed),
                              "floor": sum(s for _, s in scored["confirmed"]["floor"])},
                "difference": diff, "demoted_claims": [[items[i][0], t] for i, t in demoted]}
            shown = "-" if diff is None else f"{diff[0]:+.3f} [{diff[1]:+.3f}, {diff[2]:+.3f}]"
            md.append(f"| {name} | {JUDGES[language]} | {rate(scored['demoted']['own'])} | "
                      f"{rate(scored['confirmed']['own'])} | {shown} | {rate(scored['demoted']['floor'])} | "
                      f"{rate(scored['confirmed']['floor'])} |")
            print(md[-1], flush=True)
        report["judges"][language] = {"model": judge.name, "device": judge.device, "pairs": judge.pairs,
                                      "truncated": judge.truncated}
        judge.close()
    md += ["", "Pairs judged and truncated: " + "; ".join(
        f"{k} {v['pairs']} pairs, {v['truncated']} over 512 tokens ({v['device']})" for k, v in report["judges"].items())]
    (HERE / "results" / "retained_support.json").write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                                           encoding="utf-8")
    (HERE / "results" / "retained_support.md").write_text(NL.join(md) + NL, encoding="utf-8")
    print(NL.join(md))


if __name__ == "__main__":
    main()
