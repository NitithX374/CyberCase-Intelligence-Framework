import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.linear_model import LogisticRegression
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed, DEVICE
from src.datasets.wice import load_wice_split
from src.metrics import compute_classification_metrics
from src.bootstrap import paired_bootstrap_test

MINILM_MODEL_NAME = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"

def run_minilm_experiment():
    set_seed(SEED)
    print("=" * 80)
    print("BACKBONE EXPERIMENT: SPEED & SIZE FAMILY CHECK")
    print(f"Candidate: {MINILM_MODEL_NAME} (~107M params)")
    print("Comparing against Champion: MoritzLaurer/mDeBERTa-v3-base-xnli (278M params)")
    print("=" * 80)

    train_ex = load_wice_split("train")
    dev_ex = load_wice_split("dev")
    test_ex = load_wice_split("test")

    y_train = np.array([ex.gold_label_binary for ex in train_ex])
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])
    y_test = np.array([ex.gold_label_binary for ex in test_ex])

    # Load semantic scores to get filtered premises (tau=0.20)
    sims_train = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "train.jsonl", "r", encoding="utf-8") if l.strip()]
    sims_dev = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "dev.jsonl", "r", encoding="utf-8") if l.strip()]
    sims_test = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "test.jsonl", "r", encoding="utf-8") if l.strip()]

    def get_premises(examples, sims_list, tau=0.20):
        premises = []
        for ex, s_list in zip(examples, sims_list):
            kept = [i for i, val in enumerate(s_list) if val >= tau]
            if not kept and s_list:
                kept = [int(np.argmax(s_list))]
            p = " ".join([ex.evidence_units[i] for i in kept]) if kept else ""
            premises.append(p)
        return premises

    p_train = get_premises(train_ex, sims_train)
    p_dev = get_premises(dev_ex, sims_dev)
    p_test = get_premises(test_ex, sims_test)

    h_train = [ex.claim for ex in train_ex]
    h_dev = [ex.claim for ex in dev_ex]
    h_test = [ex.claim for ex in test_ex]

    cache_dir = CACHE_DIR / "backbone_minilm"
    cache_dir.mkdir(parents=True, exist_ok=True)

    def compute_or_load_probs(split_name, premises, hypotheses, batch_size=32):
        cache_file = cache_dir / f"{split_name}_probs.jsonl"
        meta_file = cache_dir / f"{split_name}_meta.json"
        if cache_file.exists():
            print(f"Loading cached {MINILM_MODEL_NAME} probabilities for {split_name}...")
            probs = np.array([json.loads(l)["probs"] for l in open(cache_file, "r", encoding="utf-8") if l.strip()], dtype=np.float32)
            meta = json.load(open(meta_file, "r", encoding="utf-8")) if meta_file.exists() else {}
            return probs, meta.get("latency_ms", 0.0)

        print(f"Computing {MINILM_MODEL_NAME} probabilities for {split_name} ({len(premises)} examples)...")
        tok = AutoTokenizer.from_pretrained(MINILM_MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MINILM_MODEL_NAME)
        if DEVICE == "cuda":
            model = model.half().to(DEVICE)
        else:
            model = model.to(DEVICE)
        model.eval()

        id2label = model.config.id2label
        label2id = {v.lower(): k for k, v in id2label.items()}
        ent_idx = label2id.get("entailment", 0)
        neu_idx = label2id.get("neutral", 1)
        con_idx = label2id.get("contradiction", 2)

        all_probs = []
        t0 = time.time()
        for i in range(0, len(premises), batch_size):
            bp = premises[i : i + batch_size]
            bh = hypotheses[i : i + batch_size]
            inputs = tok(bp, bh, padding=True, truncation=True, max_length=512, return_tensors="pt").to(DEVICE)
            with torch.inference_mode():
                logits = model(**inputs).logits
                sm = torch.softmax(logits, dim=-1).cpu().float().numpy()
            for row in sm:
                ordered = [float(row[ent_idx]), float(row[neu_idx]), float(row[con_idx])]
                all_probs.append(ordered)

        elapsed = time.time() - t0
        latency_ms = (elapsed / len(premises)) * 1000.0
        print(f"Computed {split_name} in {elapsed:.1f}s ({latency_ms:.1f} ms/claim, batch={batch_size})")

        with open(cache_file, "w", encoding="utf-8") as f:
            for prob in all_probs:
                f.write(json.dumps({"probs": prob}) + "\n")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({"elapsed_s": elapsed, "latency_ms": latency_ms, "n": len(premises)}, f)

        return np.array(all_probs, dtype=np.float32), latency_ms

    # 1. Compute features
    f_train_minilm, lat_train_minilm = compute_or_load_probs("train", p_train, h_train, batch_size=32)
    f_dev_minilm, lat_dev_minilm = compute_or_load_probs("dev", p_dev, h_dev, batch_size=32)
    f_test_minilm, lat_test_minilm = compute_or_load_probs("test", p_test, h_test, batch_size=32)

    # 2. Fit Logistic Regression on Train
    clf_minilm = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_minilm.fit(f_train_minilm, y_train)

    # 3. Load Champion Predictions
    clf_champ = joblib.load(OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")
    f_dev_champ = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                            for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "dev_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
    f_test_champ = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                             for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "test_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)

    dev_preds_champ = clf_champ.predict(f_dev_champ)
    test_preds_champ = clf_champ.predict(f_test_champ)

    m_dev_champ = compute_classification_metrics(y_dev, dev_preds_champ)
    m_test_champ = compute_classification_metrics(y_test, test_preds_champ)

    # 4. Evaluate MiniLM on DEV
    dev_preds_minilm = clf_minilm.predict(f_dev_minilm)
    m_dev_minilm = compute_classification_metrics(y_dev, dev_preds_minilm)

    print("\n" + "=" * 90)
    print("DEV COMPARISON: MiniLMv2-L6 vs mDeBERTa-v3-base (Champion)")
    print("=" * 90)
    df_dev = pd.DataFrame([
        {
            "Model": "mDeBERTa-v3-base (Champion)",
            "Params": "278M",
            "Accuracy": f"{m_dev_champ['accuracy']:.2%}",
            "Macro-F1": f"{m_dev_champ['macro_f1']:.4f}",
            "Supp-F1": f"{m_dev_champ['supported_f1']:.4f}",
            "FSR": f"{m_dev_champ['false_support_rate']:.2%}",
            "Throughput": "~227 ms/claim"
        },
        {
            "Model": "multilingual-MiniLMv2-L6",
            "Params": "~107M",
            "Accuracy": f"{m_dev_minilm['accuracy']:.2%}",
            "Macro-F1": f"{m_dev_minilm['macro_f1']:.4f}",
            "Supp-F1": f"{m_dev_minilm['supported_f1']:.4f}",
            "FSR": f"{m_dev_minilm['false_support_rate']:.2%}",
            "Throughput": f"{lat_dev_minilm:.1f} ms NLI (batch=32)"
        }
    ])
    print(df_dev.to_string(index=False))

    d_dev_macro = m_dev_minilm['macro_f1'] - m_dev_champ['macro_f1']
    d_dev_supp = m_dev_minilm['supported_f1'] - m_dev_champ['supported_f1']
    d_dev_fsr = m_dev_minilm['false_support_rate'] - m_dev_champ['false_support_rate']
    print(f"\nDelta MiniLM vs Champion on DEV: d_Macro-F1 = {d_dev_macro:+.4f}, d_Supp-F1 = {d_dev_supp:+.4f}, d_FSR = {d_dev_fsr:+.2%}")

    # 5. Evaluate MiniLM on TEST
    test_preds_minilm = clf_minilm.predict(f_test_minilm)
    m_test_minilm = compute_classification_metrics(y_test, test_preds_minilm)

    print("\n" + "=" * 90)
    print("TEST COMPARISON & PAIRED BOOTSTRAP (N=1000, Seed=42)")
    print("=" * 90)
    df_test = pd.DataFrame([
        {
            "Model": "mDeBERTa-v3-base (Champion)",
            "Params": "278M",
            "Accuracy": f"{m_test_champ['accuracy']:.2%}",
            "Macro-F1": f"{m_test_champ['macro_f1']:.4f}",
            "Supp-Prec": f"{m_test_champ['supported_precision']:.2%}",
            "Supp-Rec": f"{m_test_champ['supported_recall']:.2%}",
            "Supp-F1": f"{m_test_champ['supported_f1']:.4f}",
            "FSR": f"{m_test_champ['false_support_rate']:.2%}"
        },
        {
            "Model": "multilingual-MiniLMv2-L6",
            "Params": "~107M",
            "Accuracy": f"{m_test_minilm['accuracy']:.2%}",
            "Macro-F1": f"{m_test_minilm['macro_f1']:.4f}",
            "Supp-Prec": f"{m_test_minilm['supported_precision']:.2%}",
            "Supp-Rec": f"{m_test_minilm['supported_recall']:.2%}",
            "Supp-F1": f"{m_test_minilm['supported_f1']:.4f}",
            "FSR": f"{m_test_minilm['false_support_rate']:.2%}"
        }
    ])
    print(df_test.to_string(index=False))

    bs = paired_bootstrap_test(y_test, test_preds_minilm, test_preds_champ, n_bootstraps=1000, seed=SEED)
    print("\nPaired Bootstrap (MiniLMv2-L6 vs Champion) on WiCE TEST:")
    for metric, vals in bs.items():
        print(f"  Delta {metric}: {vals['mean_diff']:+.4f} (95% CI: [{vals['ci_lower']:+.4f}, {vals['ci_upper']:+.4f}])")

    # 6. Benchmark batch size = 1 latency comparison
    print("\nBenchmarking batch size = 1 latency on GPU (50 samples)...")
    tok = AutoTokenizer.from_pretrained(MINILM_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MINILM_MODEL_NAME).to(DEVICE)
    model.eval()

    sample_indices = np.random.RandomState(SEED).choice(len(test_ex), size=50, replace=False)
    single_lats = []
    for idx in sample_indices:
        p = p_test[idx]
        c = h_test[idx]
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        encoded = tok([p], [c], padding=True, truncation=True, max_length=512, return_tensors="pt")
        inp = {k: v.to(DEVICE) for k, v in encoded.items()}
        with torch.inference_mode():
            _ = model(**inp).logits
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        single_lats.append((t1 - t0) * 1000.0)

    minilm_b1_mean = float(np.mean(single_lats))
    minilm_b1_median = float(np.median(single_lats))
    minilm_b1_p90 = float(np.percentile(single_lats, 90))
    print(f"MiniLMv2-L6 NLI Latency (batch=1): mean={minilm_b1_mean:.2f} ms | median={minilm_b1_median:.2f} ms | p90={minilm_b1_p90:.2f} ms")

    results = {
        "model_name": MINILM_MODEL_NAME,
        "params": 107000000,
        "dev": {
            "champion": m_dev_champ,
            "minilm": m_dev_minilm,
            "deltas": {
                "macro_f1": d_dev_macro,
                "supported_f1": d_dev_supp,
                "fsr": d_dev_fsr
            }
        },
        "test": {
            "champion": m_test_champ,
            "minilm": m_test_minilm,
            "bootstrap": bs
        },
        "latency_batch1_ms": {
            "mean": minilm_b1_mean,
            "median": minilm_b1_median,
            "p90": minilm_b1_p90
        }
    }

    out_file = OUTPUTS_DIR / "stage5_minilm_backbone_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved MiniLM experiment results to {out_file}")

if __name__ == "__main__":
    run_minilm_experiment()
