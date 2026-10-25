import json
from pathlib import Path

from research.attribution_benchmark.data import read_split
from research.attribution_benchmark.summarize_mt_th import transfer_bootstrap

RAW = Path("research/attribution_benchmark/raw")
OUT = Path("research/attribution_benchmark/results/b1_th_nfkc_20261026.json")


def load(name):
    lines = (RAW / name / "scores.jsonl").read_text(encoding="utf-8").split("\n")
    return {r["id"]: r for r in map(json.loads, filter(str.strip, lines))}


def counts(rows, supported):
    tp = fp = tn = fn = 0
    for row in rows:
        gold = row["attribution_label"] == "attributable"
        predicted = supported[row["id"]]
        tp += gold and predicted
        fp += (not gold) and predicted
        fn += gold and not predicted
        tn += (not gold) and not predicted
    return tp, fp, tn, fn


original, normalized = load("b1-mt-th"), load("b1-mt-th-normalized")
result = {
    "source": "raw/b1-mt-th (English) and raw/b1-mt-th-normalized (Thai, NLI input normalized with NFKC)",
    "method": "Paired 2000 question/response cluster bootstrap resamples within source subsets; seed 20261007",
}
for split in ("test", "test_ood"):
    rows = read_split(split)
    scores = {
        row["id"]: {
            "en_supported": original[row["id"]]["en_supported"],
            "th_supported": normalized[row["id"]]["th_supported"],
        }
        for row in rows
    }
    entry = {}
    for language in ("en", "th"):
        tp, fp, tn, fn = counts(rows, {k: v[f"{language}_supported"] for k, v in scores.items()})
        entry[language] = {
            "n": len(rows), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "false_acceptance_rate": fp / (fp + tn),
            "false_rejection_rate": fn / (tp + fn),
            "supported_f1": 2 * tp / (2 * tp + fp + fn),
        }
    entry["th_minus_en95"] = transfer_bootstrap(rows, scores)["th_minus_en95"]
    result[split] = entry
OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
print(OUT)
