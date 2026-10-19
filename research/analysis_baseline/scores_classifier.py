"""Scores, classifier part (RQ1): AUROC and the decisions at a threshold, then the datasets (Tables 5-1 to 5-3), model
selection (Table 5-5) and the five configurations with the shipped checkpoint (Tables 5-8 to 5-10).
"""
from __future__ import annotations

import json

import numpy as np
from sklearn.metrics import roc_auc_score

from scores_common import CASES, HERE, ROOT, jsonl, lead, row, share

# ================================================================================================= RULES


def auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    """Area under the ROC curve: how well the scores rank positive sentences above negative ones."""
    return float(roc_auc_score(labels, scores))


def decisions(labels: np.ndarray, scores: np.ndarray, threshold: float) -> tuple[int, int, int, int]:
    """TP, FP, FN and TN when every sentence scoring at least the threshold is flagged."""
    flagged, positive = scores >= threshold, labels == 1
    return (int((flagged & positive).sum()), int((flagged & ~positive).sum()),
            int((~flagged & positive).sum()), int((~flagged & ~positive).sum()))


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    """Precision, recall and F1 of the flagged sentences."""
    return tp / (tp + fp), tp / (tp + fn), 2 * tp / (2 * tp + fp + fn)


def flag_every_f1(labels: np.ndarray) -> float:
    """F1 of flagging every sentence: precision is the positive share p and recall is 1, so F1 = 2p / (1 + p)."""
    return float(2 * labels.mean() / (1 + labels.mean()))


# ================================================================================================= DATA

GATE = ROOT / "experiments" / "gate_generalization"
SEEDS = (42, 7, 123)
CONFIGS = {"E1": ["tfidf_ladder"], "E2": ["tfidf_mtdb"], "E3": [f"xlmr_base_ladder_s{s}" for s in SEEDS],
           "E4": [f"xlmr_base_mtdb_s{s}" for s in SEEDS], "E5": [f"xlmr_base_tapt_ladder_s{s}" for s in SEEDS]}


def datasets() -> None:
    manifest = json.loads((HERE / "data" / "manifest.json").read_text(encoding="utf-8"))
    row("5-1", "CASIE articles", f"{manifest['articles']:,}", "1,000")
    main = [c for c in CASES.values() if c["sample"] == "main"]
    for label, cases, book in (("cases 51-150", main[50:150], ("776", "6 (3 to 32)")),
                               ("cases 151-250", main[150:250], ("832", "7 (3 to 32)"))):
        counts = [len(lead(c)) for c in cases]
        mid, low, high = np.median(counts), min(counts), max(counts)
        row("5-2", f"{label}: cases", len(cases), "100")
        row("5-2", f"{label}: main-event facts", sum(counts), book[0])
        row("5-2", f"{label}: facts per case, median (range)",
            f"{mid:.0f} ({low} to {high})" if mid == int(mid) else f"{mid} ({low} to {high})",
            book[1])
    data = GATE / "data_xscheme"
    books = {"ladder": ("2,214", "568", "662", "0.500", "0.500", "0.500"),
             "mtdb": ("4,437", "698", "1,831", "0.258", "0.362", "0.288")}
    for corpus, book in books.items():
        splits = [jsonl(data / f"{corpus}_{split}.jsonl") for split in ("train", "dev", "test")]
        for name, rows, size, positive in zip(("train", "dev", "test"), splits, book[:3], book[3:], strict=True):
            row("5-3", f"{corpus} {name}: sentences", f"{len(rows):,}", size)
            row("5-3", f"{corpus} {name}: positive share", f"{share(r['label'] for r in rows):.3f}", positive)
        if corpus == "mtdb":
            row("5-3", "mtdb test: positive sentences", sum(r["label"] for r in splits[2]), "527")
            row("5-3", "mtdb reports train/dev/test", "/".join(str(len({r["document"] for r in s})) for s in splits),
                "23/8/8")


def classifier() -> dict:
    data, results = GATE / "data_xscheme", GATE / "results_xscheme"
    gold = {test: jsonl(data / f"{test}.jsonl") for test in ("ladder_test", "mtdb_test")}

    def threshold(run: str) -> float:
        package = results / run / "model" / "gate_model.json"
        if package.exists():
            return float(1 / (1 + np.exp(-json.loads(package.read_text())["source_threshold_logit"])))
        return json.loads((results / run / "config.json").read_text())["threshold_prob"]

    book = {"ladder_test": {"E1": "0.881 0.795 0.834 0.814", "E2": "0.735 0.714 0.535 0.611",
                            "E3": "0.920 0.833 0.849 0.839", "E4": "0.762 0.737 0.558 0.635",
                            "E5": "0.923 0.848 0.854 0.851"},
            "mtdb_test": {"E1": "0.781 0.608 0.541 0.572", "E2": "0.832 0.640 0.617 0.628",
                          "E3": "0.844 0.753 0.481 0.579", "E4": "0.893 0.705 0.701 0.702",
                          "E5": "0.847 0.734 0.518 0.605"}}
    out = {}
    for test, table in (("ladder_test", "5-8"), ("mtdb_test", "5-9")):
        labels = np.array([r["label"] for r in gold[test]])
        row("5.3.1", f"{test}: F1 of flagging every sentence", f"{flag_every_f1(labels):.3f}",
            "0.667" if test == "ladder_test" else "0.447")
        for config, runs in CONFIGS.items():
            cells = []
            for run in runs:
                by_id = {r["id"]: r["prob"] for r in jsonl(results / run / "predictions" / "ft" / f"{test}.jsonl")}
                scores = np.array([by_id[r["id"]] for r in gold[test]])
                tp, fp, fn, _ = decisions(labels, scores, threshold(run))
                cells.append((auroc(labels, scores), *prf(tp, fp, fn)))
                out[(test, run)] = cells[-1]
            ours = " ".join(f"{v:.3f}" for v in np.mean(cells, axis=0))
            row(table, f"{config}: AUROC, precision, recall, F1 (mean over seeds)", ours, book[test][config])
    row("5-9", "E3 seed 42 recall on MalwareTextDB", f"{out[('mtdb_test', 'xlmr_base_ladder_s42')][2]:.3f}", "0.583")
    shipped = jsonl(GATE / "results_run2" / "existing_xlmr_ladder" / "predictions" / "ft" / "ladder_test.jsonl")
    authors = {r["id"]: r["label"] for r in gold["ladder_test"]}
    labels, scores = np.array([authors[r["id"]] for r in shipped]), np.array([r["prob"] for r in shipped])
    tp, fp, fn, tn = decisions(labels, scores, 0.5)
    row("5-10", "shipped checkpoint AUROC", f"{auroc(labels, scores):.3f}", "0.917")
    row("5-10", "TP / FN / FP / TN at 0.50", f"{tp} / {fn} / {fp} / {tn}", "278 / 53 / 44 / 287")
    row("5-10", "precision", f"{tp}/{tp + fp} = {tp / (tp + fp):.3f}", "278/322 = 0.863")
    row("5-10", "recall", f"{tp}/{tp + fn} = {tp / (tp + fn):.3f}", "278/331 = 0.840")
    return out


def model_selection() -> None:
    run2 = GATE / "results_run2"
    lr = json.loads((run2 / "lr_choice.json").read_text(encoding="utf-8"))
    groups = {"XLM-R base": ([f"xlmr_base_lr{lr['xlmr_base']['lr']}_s{s}" for s in SEEDS], "0.915 ± 0.005"),
              "XLM-R large": ([f"xlmr_large_lr{lr['xlmr_large']['lr']}_s{s}" for s in SEEDS], "0.943 ± 0.006"),
              "BGE-M3": ([f"bge_m3_lr{lr['bge_m3']['lr']}_s{s}" for s in SEEDS], "0.943 ± 0.004"),
              "the checkpoint the system runs": (["existing_xlmr_ladder"], "0.917"),
              "TF-IDF and logistic regression": (["tfidf_lr"], "0.881"),
              "TF-IDF and linear SVM": (["tfidf_svm"], "0.881")}
    means = {}
    for name, (runs, book) in groups.items():
        aucs = []
        for run in runs:
            rows = jsonl(run2 / run / "predictions" / "ft" / "ladder_test.jsonl")
            rows = [r for r in rows if not r.get("ladder_dup")]
            aucs.append(auroc(np.array([r["label"] for r in rows]), np.array([r["prob"] for r in rows])))
        means[name] = np.mean(aucs)
        row("5-5", f"{name}: LADDER test AUROC", f"{np.mean(aucs):.3f} ± {np.std(aucs):.3f}" if len(aucs) > 1
            else f"{aucs[0]:.3f}", book)
    row("5-5", "larger encoders minus XLM-R base, 'about'",
        f"{min(means['XLM-R large'], means['BGE-M3']) - means['XLM-R base']:.2f}", "0.03")
