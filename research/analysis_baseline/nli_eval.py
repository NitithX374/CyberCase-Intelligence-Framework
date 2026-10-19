"""NLI as the support check, against CASIE realis, in the two stages README.md fixes. Local weights, no model API call.

  python nli_eval.py dry       the traces of pilot_20260930_060711, outside every stage: mechanics only
  python nli_eval.py choose    stage 1, main cases 1-250: pick the premise
  python nli_eval.py confirm   stage 2, main cases 251-330: confirm the premise stage 1 picked

Premises: sentence (the quoted sentences), local (each quoted sentence with up to two sentences before it), article (the
article up to the end of the quoted sentence, cut from the left to 512 tokens), either (flag only when neither sentence
nor local is entailment). The quote alone is reported, never chosen.
Reuses support_eval.py (frozen) for the cases, nuggets, bootstrap and the checker's evidence windows.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
sys.argv, _args = sys.argv[:1], sys.argv[1:]
import numpy as np  # noqa: E402
import torch  # noqa: E402
import transformers  # noqa: E402

import support_eval as se  # noqa: E402

MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
REVISION = "b5113eb38ab63efdd7f280f8c144ea8b13f978ce"
MAX_TOKENS = 512
BATCH_TOKENS = 1024
MAX_BATCH = 16
STAGES = {
    "dry": (("pilot_20260930_060711",), ("cybercase", "single"), "pilot", 0, 3),
    "choose": (("main_20260928_081639", "main_20260930_020141", "main_20260930_062138"), ("cybercase", "single"),
               "main", 0, 250),
    "confirm": (("main_20260930_101517", "main_20260930_110757"), ("cybercase_nonull", "cybercase_reorder"),
                "main", 250, 330),
}
PREMISES = ("sentence", "local", "article", "either")
PRIMARY_ARMS = {"dry": ("cybercase",), "choose": ("cybercase",), "confirm": ("cybercase_nonull", "cybercase_reorder")}


def local_span(content: str, q_start: int, q_end: int) -> tuple[int, int]:
    sentence = se.support.sentence_window(content, q_start, q_end)
    start = content.find(sentence, max(0, q_start - se.support.WINDOW_CHARS - 5))
    start = q_start if start < 0 else start
    ends = [match.end() for match in se.support.SENTENCE_END.finditer(content, 0, start)]
    return (ends[-3] if len(ends) >= 3 else 0), start + len(sentence)


def claim_texts(runs: tuple[str, ...], ids: set[str], arms: tuple[str, ...], texts: dict) -> tuple[list[dict], Counter]:
    rows, failed = [], Counter()
    for run in runs:
        for line in (se.HERE / "results" / f"{run}.jsonl").read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["arm"] not in arms or record.get("run", 1) != 1 or record["case"] not in ids:
                continue
            if "error" in record:
                failed[record["arm"]] += 1
                continue
            raw = se.HERE / "results" / f"raw_{run}" / f"{record['case']}_{record['arm']}_1.json"
            bound = json.loads(raw.read_text(encoding="utf-8"))["bound"]
            content, found, _ = texts[record["case"]]
            registry = {se.SOURCE_ID: se.CaseSourceItem(source_id=se.SOURCE_ID, source_kind="narrative", text=content)}
            claims = [se.CaseAnalysisClaim.model_validate(claim) for claim in bound["claims"]]
            kinds: dict[str, set[str]] = defaultdict(set)
            for flag in se.support.support_flags(claims, registry):
                kinds[flag.claim_id].add(flag.kind)
            for claim in claims:
                spans = []
                for citation in claim.supporting_citations:
                    occurrences = se.quote_occurrences(content, citation.exact_quote)
                    if citation.source_id == se.SOURCE_ID and occurrences:
                        spans.append((occurrences[0], occurrences[0] + len(citation.exact_quote)))
                if not spans:
                    continue
                realis = {value for start, end, value in found if value in ("Actual", "Other")
                          and any(start < q_end and q_start < end for q_start, q_end in spans)}
                _, quotes, window = se.support.claim_evidence(claim, registry)
                local = [local_span(content, q_start, q_end) for q_start, q_end in spans]
                rows.append({
                    "arm": record["arm"], "case": record["case"], "claim_id": claim.claim_id,
                    "label": ("Other" if realis == {"Other"} else "Actual" if realis == {"Actual"}
                              else "mixed" if realis else "none"),
                    "cue_flag": bool(se.REALIS_FLAGS & kinds[claim.claim_id]),
                    "hypothesis": claim.text,
                    "text": {"sentence": window,
                             "local": "\n".join(content[a:b].strip() for a, b in local),
                             "article": content[:max(b for _, b in local)],
                             "quote": quotes},
                })
    return rows, failed


@torch.no_grad()
def predict(model, tokenizer, device: str, premises: list[str], hypotheses: list[str]) -> tuple[list[str], int]:
    names = {int(k): v.lower() for k, v in model.config.id2label.items()}
    lengths = [len(ids) for ids in tokenizer(premises, hypotheses, truncation=False)["input_ids"]]
    cut = sum(n > MAX_TOKENS for n in lengths)
    order = list(np.argsort(lengths))
    labels: list[str] = [""] * len(premises)
    done = 0
    while order:
        width = min(MAX_TOKENS, lengths[order[0]])
        size = max(1, min(MAX_BATCH, len(order), BATCH_TOKENS // max(1, width)))
        while size > 1 and min(MAX_TOKENS, lengths[order[size - 1]]) * size > BATCH_TOKENS:
            size -= 1
        idx, order = order[:size], order[size:]
        batch = tokenizer([premises[i] for i in idx], [hypotheses[i] for i in idx], truncation="longest_first",
                          max_length=MAX_TOKENS, padding=True, return_tensors="pt").to(device)
        for i, top in zip(idx, model(**batch).logits.argmax(-1).tolist()):
            labels[i] = names[top]
        done += len(idx)
        if done // 1000 != (done - len(idx)) // 1000:
            print(f"  {done} of {len(premises)}", flush=True)
    return labels, cut


def metrics(rows: list[dict], premise: str) -> dict:
    per_case: dict[str, list[float]] = defaultdict(lambda: [0.0] * 8)
    for r in rows:
        if r["label"] not in ("Actual", "Other"):
            continue
        counts, other = per_case[r["case"]], r["label"] == "Other"
        flagged = r["flag"][premise] if premise != "cue" else r["cue_flag"]
        counts[0] += flagged and other
        counts[1] += flagged
        counts[2] += other
        counts[3] += 1
        counts[4] += flagged and not other
        counts[5] += not other
        counts[6] += r["cue_flag"] and other
        counts[7] += r["cue_flag"]
    return {
        "flagged_labeled": int(sum(v[1] for v in per_case.values())),
        "flagged_all": sum(r["flag"][premise] if premise != "cue" else r["cue_flag"] for r in rows),
        "precision": se.clustered(per_case, se.ratio(0, 1)),
        "chance": se.clustered(per_case, se.ratio(2, 3)),
        "precision_minus_chance": se.clustered(per_case, lambda v: v[0] / v[1] - v[2] / v[3]),
        "separation": se.clustered(per_case, lambda v: v[0] / v[2] - v[4] / v[5]),
        "flag_rate_other": se.clustered(per_case, se.ratio(0, 2)),
        "flag_rate_actual": se.clustered(per_case, se.ratio(4, 5)),
        "minus_cue_precision": se.clustered(per_case, lambda v: v[0] / v[1] - v[6] / v[7]),
        "labeled": int(sum(v[3] for v in per_case.values())),
        "other": int(sum(v[2] for v in per_case.values())),
    }


def table(rows: list[dict], names: tuple[str, ...]) -> tuple[list[str], dict]:
    lines = ["| Premise | Flags, all claims | Flags, labeled | Precision | Precision − chance | Separation | "
             "Precision − cue rules |", "|---|---|---|---|---|---|---|"]
    found = {}
    for name in names:
        m = metrics(rows, name)
        found[name] = m
        lines.append(f"| {name} | {m['flagged_all']} of {len(rows)} | {m['flagged_labeled']} | {se.ci(m['precision'])} | "
                     f"{se.ci(m['precision_minus_chance'], True)} | {se.ci(m['separation'], True)} | "
                     + ("—" if name == "cue" else se.ci(m["minus_cue_precision"], True)) + " |")
    return lines, found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=tuple(STAGES))
    args = parser.parse_args(_args)
    checker = se.lf_sha(se.CODE / "app" / "trace" / "support.py")
    if not checker.startswith(se.FROZEN):
        raise SystemExit(f"support.py is {checker[:16]}, not the frozen {se.FROZEN}")
    runs, arms, sample, first, last = STAGES[args.stage]
    chosen = None
    if args.stage == "confirm":
        choice = se.HERE / "results" / "nli_eval_choose.json"
        if not choice.exists():
            raise SystemExit("stage 1 has not run: results/nli_eval_choose.json is missing")
        chosen = json.loads(choice.read_text(encoding="utf-8"))["chosen"]
    cases = [json.loads(line) for line in (se.HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines()]
    ids = [c["id"] for c in cases if c["sample"] == sample][first:last]
    texts = {case_id: se.nuggets(case_id) for case_id in ids}
    rows, failed = claim_texts(runs, set(ids), arms, texts)
    device = os.environ.get("NLI_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    left = transformers.AutoTokenizer.from_pretrained(MODEL, revision=REVISION, truncation_side="left")
    model = transformers.AutoModelForSequenceClassification.from_pretrained(MODEL, revision=REVISION)
    model = model.float().eval().to(device)
    hypotheses = [r["hypothesis"] for r in rows]
    labels, cut = {}, {}
    for name in ("sentence", "local", "article", "quote"):
        labels[name], cut[name] = predict(model, left if name == "article" else tokenizer, device,
                                          [r["text"][name] for r in rows], hypotheses)
    for i, r in enumerate(rows):
        r["nli"] = {name: labels[name][i] for name in labels}
        r["flag"] = {name: labels[name][i] != "entailment" for name in labels}
        r["flag"]["either"] = r["flag"]["sentence"] and r["flag"]["local"]
    lines = [f"# NLI as the support check, against CASIE realis ({args.stage})", "",
             f"{MODEL} @ {REVISION[:8]}, fp32 on {device}; torch {torch.__version__}, transformers "
             f"{transformers.__version__}. support.py {checker[:16]}…, nli_eval.py {se.lf_sha(Path(__file__))[:16]}…, "
             f"support_eval.py {se.lf_sha(se.HERE / 'support_eval.py')[:16]}….", "",
             f"Cases {first + 1}-{last} of the {sample} sample; runs {', '.join(runs)}; failed runs with no trace "
             f"{dict(failed) or 'none'}. Premises cut at {MAX_TOKENS} tokens: {cut}.", ""]
    report = {"stage": args.stage, "model": MODEL, "revision": REVISION, "device": device,
              "nli_eval_sha256": se.lf_sha(Path(__file__)), "support_sha256": checker, "failed_runs": dict(failed),
              "cut": cut, "groups": {}}
    groups = [("primary: " + " + ".join(PRIMARY_ARMS[args.stage]), [r for r in rows if r["arm"] in PRIMARY_ARMS[args.stage]])]
    groups += [(f"descriptive: {arm}", [r for r in rows if r["arm"] == arm]) for arm in arms
               if arm not in PRIMARY_ARMS[args.stage]]
    for title, group in groups:
        if not group:
            continue
        labeled = [r for r in group if r["label"] in ("Actual", "Other")]
        lines += [f"## {title}", "",
                  f"Claims with a quote found in the source {len(group)} in {len({r['case'] for r in group})} traces; "
                  f"labeled {len(labeled)}, Other {sum(r['label'] == 'Other' for r in labeled)}.", ""]
        body, found = table(group, (*PREMISES, "quote", "cue"))
        lines += body + [""]
        for name in (*PREMISES, "quote"):
            source = "sentence" if name == "either" else name
            lines.append(f"- {name}: labels {dict(Counter(r['nli'][source] for r in group))}" if name != "either" else
                         f"- either: flags where sentence and local both disagree {sum(r['flag']['either'] for r in group)}")
        agreement = Counter((r["flag"][chosen or "either"], r["cue_flag"]) for r in group)
        lines += [f"- Agreement of {chosen or 'either'} with the cue flags (NLI, cue): both {agreement[(True, True)]}, NLI only "
                  f"{agreement[(True, False)]}, cue only {agreement[(False, True)]}, neither {agreement[(False, False)]}.", ""]
        report["groups"][title] = {"claims": len(group), "labeled": len(labeled), "metrics": found}
    if args.stage in ("choose", "dry"):
        primary_metrics = report["groups"][groups[0][0]]["metrics"]
        pick = max(PREMISES, key=lambda name: primary_metrics[name]["precision_minus_chance"][0])
        report["chosen"] = pick
        lines += [f"**Chosen for stage 2 (highest precision minus chance on the primary group): {pick}.**", ""]
    else:
        report["chosen"] = chosen
        lines += [f"**Premise under confirmation (chosen in stage 1): {chosen}.**", ""]
    out = se.HERE / "results" / f"nli_eval_{args.stage}"
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (se.HERE / "results" / f"nli_eval_{args.stage}_claims.jsonl").open("w", encoding="utf-8") as handle:
        for r in rows:
            handle.write(json.dumps({k: r[k] for k in ("arm", "case", "claim_id", "label", "cue_flag", "nli")}) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
