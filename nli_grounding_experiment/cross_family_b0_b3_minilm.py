import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed, DEVICE
from src.datasets.wice import load_wice_split
from src.metrics import compute_classification_metrics
from src.bootstrap import paired_bootstrap_test

MINILM_MODEL_NAME = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"

def run_cross_family_ablation():
    set_seed(SEED)
    print("=" * 90)
    print("CROSS-FAMILY EXPERIMENT: B0 - B3 PIPELINE ABLATION ON MULTILINGUAL-MINILM-L6")
    print("Goal: Check if the ablation pattern (B0 -> B1 -> B1-LR -> B3) generalizes across backbones")
    print("=" * 90)

    train_ex = load_wice_split("train")
    dev_ex = load_wice_split("dev")
    test_ex = load_wice_split("test")

    y_train = np.array([ex.gold_label_binary for ex in train_ex])
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])
    y_test = np.array([ex.gold_label_binary for ex in test_ex])

    # 1. Full Premises (for B0)
    full_p_train = [" ".join(ex.evidence_units) for ex in train_ex]
    full_p_dev = [" ".join(ex.evidence_units) for ex in dev_ex]
    full_p_test = [" ".join(ex.evidence_units) for ex in test_ex]

    # 2. Filtered Premises (for B1, B1-LR, B3)
    sims_train = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "train.jsonl", "r", encoding="utf-8") if l.strip()]
    sims_dev = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "dev.jsonl", "r", encoding="utf-8") if l.strip()]
    sims_test = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "test.jsonl", "r", encoding="utf-8") if l.strip()]

    def get_filt_premises(examples, sims_list, tau=0.20):
        premises = []
        for ex, s_list in zip(examples, sims_list):
            kept = [i for i, val in enumerate(s_list) if val >= tau]
            if not kept and s_list:
                kept = [int(np.argmax(s_list))]
            p = " ".join([ex.evidence_units[i] for i in kept]) if kept else ""
            premises.append(p)
        return premises

    filt_p_train = get_filt_premises(train_ex, sims_train)
    filt_p_dev = get_filt_premises(dev_ex, sims_dev)
    filt_p_test = get_filt_premises(test_ex, sims_test)

    claims_train = [ex.claim for ex in train_ex]
    claims_dev = [ex.claim for ex in dev_ex]
    claims_test = [ex.claim for ex in test_ex]

    cache_dir = CACHE_DIR / "cross_family_minilm"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Helper to compute/load probabilities
    tok = AutoTokenizer.from_pretrained(MINILM_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MINILM_MODEL_NAME).to(DEVICE)
    model.eval()

    def get_nli_probs(tag, premises, hypotheses, batch_size=32):
        cache_file = cache_dir / f"{tag}_probs.jsonl"
        if cache_file.exists():
            return np.array([json.loads(l)["probs"] for l in open(cache_file, "r", encoding="utf-8") if l.strip()], dtype=np.float32)

        print(f"Computing MiniLM NLI for {tag} ({len(premises)} pairs)...")
        all_probs = []
        for i in range(0, len(premises), batch_size):
            bp = premises[i : i + batch_size]
            bh = hypotheses[i : i + batch_size]
            encoded = tok(bp, bh, padding=True, truncation=True, max_length=512, return_tensors="pt")
            inp = {k: v.to(DEVICE) for k, v in encoded.items()}
            with torch.inference_mode():
                logits = model(**inp).logits
                sm = torch.softmax(logits, dim=-1).cpu().float().numpy()
            for row in sm:
                # 0: entailment, 1: neutral, 2: contradiction
                all_probs.append([float(row[0]), float(row[1]), float(row[2])])

        with open(cache_file, "w", encoding="utf-8") as f:
            for p in all_probs:
                f.write(json.dumps({"probs": p}) + "\n")
        return np.array(all_probs, dtype=np.float32)

    # Compute Forward Full (B0)
    print("\n--- 1. Computing Forward NLI on Full Premise (B0) ---")
    f_full_train = get_nli_probs("train_full_fwd", full_p_train, claims_train)
    f_full_dev = get_nli_probs("dev_full_fwd", full_p_dev, claims_dev)
    f_full_test = get_nli_probs("test_full_fwd", full_p_test, claims_test)

    # Compute Forward Filtered (B1, B1-LR)
    print("\n--- 2. Computing Forward NLI on Filtered Premise (B1, B1-LR) ---")
    f_filt_train = get_nli_probs("train_filt_fwd", filt_p_train, claims_train)
    f_filt_dev = get_nli_probs("dev_filt_fwd", filt_p_dev, claims_dev)
    f_filt_test = get_nli_probs("test_filt_fwd", filt_p_test, claims_test)

    # Compute Reverse Filtered (B3: Claim -> Evidence)
    print("\n--- 3. Computing Reverse NLI on Filtered Premise (B3: Claim -> Evidence) ---")
    f_rev_train = get_nli_probs("train_filt_rev", claims_train, filt_p_train)
    f_rev_dev = get_nli_probs("dev_filt_rev", claims_dev, filt_p_dev)
    f_rev_test = get_nli_probs("test_filt_rev", claims_test, filt_p_test)

    # -------------------------------------------------------------
    # Evaluate Pipeline Configurations on MiniLM
    # -------------------------------------------------------------
    # B0: Full Premise + Argmax
    preds_b0_test = (np.argmax(f_full_test, axis=1) == 0).astype(int)
    m_b0 = compute_classification_metrics(y_test, preds_b0_test)

    # B0-LR: Full Premise + Logistic Regression
    clf_b0_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_b0_lr.fit(f_full_train, y_train)
    preds_b0_lr_test = clf_b0_lr.predict(f_full_test)
    m_b0_lr = compute_classification_metrics(y_test, preds_b0_lr_test)

    # B1: Filtered Premise + Argmax
    preds_b1_test = (np.argmax(f_filt_test, axis=1) == 0).astype(int)
    m_b1 = compute_classification_metrics(y_test, preds_b1_test)

    # B1-LR: Filtered Premise + Logistic Regression
    clf_b1_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_b1_lr.fit(f_filt_train, y_train)
    preds_b1_lr_test = clf_b1_lr.predict(f_filt_test)
    m_b1_lr = compute_classification_metrics(y_test, preds_b1_lr_test)

    # B3: Filtered Premise + Bidirectional NLI (6D vector: [fwd, rev]) + Logistic Regression
    f_b3_train = np.hstack([f_filt_train, f_rev_train])
    f_b3_test = np.hstack([f_filt_test, f_rev_test])
    clf_b3 = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_b3.fit(f_b3_train, y_train)
    preds_b3_test = clf_b3.predict(f_b3_test)
    m_b3 = compute_classification_metrics(y_test, preds_b3_test)

    # Load mDeBERTa results for side-by-side comparison
    mdeberta_results = json.load(open(OUTPUTS_DIR / "stage1_b1_lr_verification.json", "r", encoding="utf-8"))
    audit_data = json.load(open(OUTPUTS_DIR / "audit_results.json", "r", encoding="utf-8"))

    # Map mDeBERTa results
    mdeb_dict = {r["Method"]: r for r in audit_data["confusion_matrices"]}

    print("\n" + "=" * 105)
    print("CROSS-FAMILY ABLATION COMPARISON (WiCE TEST, N=1,070): mDeBERTa-v3-base vs multilingual-MiniLMv2-L6")
    print("=" * 105)

    rows = [
        {
            "Pipeline Stage": "B0 (Full premise, argmax)",
            "mDeBERTa Acc": f"{mdeb_dict['B0']['Reported Acc']:.2%}",
            "mDeBERTa Macro-F1": f"{mdeb_dict['B0']['Reported Macro-F1']:.4f}",
            "mDeBERTa FSR": f"{mdeb_dict['B0']['Reported FSR']:.2%}",
            "MiniLM Acc": f"{m_b0['accuracy']:.2%}",
            "MiniLM Macro-F1": f"{m_b0['macro_f1']:.4f}",
            "MiniLM FSR": f"{m_b0['false_support_rate']:.2%}",
        },
        {
            "Pipeline Stage": "B0-LR (Full premise + LR)",
            "mDeBERTa Acc": f"{mdeb_dict['B0-LR']['Reported Acc']:.2%}",
            "mDeBERTa Macro-F1": f"{mdeb_dict['B0-LR']['Reported Macro-F1']:.4f}",
            "mDeBERTa FSR": f"{mdeb_dict['B0-LR']['Reported FSR']:.2%}",
            "MiniLM Acc": f"{m_b0_lr['accuracy']:.2%}",
            "MiniLM Macro-F1": f"{m_b0_lr['macro_f1']:.4f}",
            "MiniLM FSR": f"{m_b0_lr['false_support_rate']:.2%}",
        },
        {
            "Pipeline Stage": "B1 (Semantic filter, argmax)",
            "mDeBERTa Acc": f"{mdeb_dict['B1']['Reported Acc']:.2%}",
            "mDeBERTa Macro-F1": f"{mdeb_dict['B1']['Reported Macro-F1']:.4f}",
            "mDeBERTa FSR": f"{mdeb_dict['B1']['Reported FSR']:.2%}",
            "MiniLM Acc": f"{m_b1['accuracy']:.2%}",
            "MiniLM Macro-F1": f"{m_b1['macro_f1']:.4f}",
            "MiniLM FSR": f"{m_b1['false_support_rate']:.2%}",
        },
        {
            "Pipeline Stage": "B1-LR (Semantic filter + LR)",
            "mDeBERTa Acc": "66.64%",
            "mDeBERTa Macro-F1": "0.6185",
            "mDeBERTa FSR": "26.22%",
            "MiniLM Acc": f"{m_b1_lr['accuracy']:.2%}",
            "MiniLM Macro-F1": f"{m_b1_lr['macro_f1']:.4f}",
            "MiniLM FSR": f"{m_b1_lr['false_support_rate']:.2%}",
        },
        {
            "Pipeline Stage": "B3 (Semantic + Bidi NLI + LR)",
            "mDeBERTa Acc": f"{mdeb_dict['B3']['Reported Acc']:.2%}",
            "mDeBERTa Macro-F1": f"{mdeb_dict['B3']['Reported Macro-F1']:.4f}",
            "mDeBERTa FSR": f"{mdeb_dict['B3']['Reported FSR']:.2%}",
            "MiniLM Acc": f"{m_b3['accuracy']:.2%}",
            "MiniLM Macro-F1": f"{m_b3['macro_f1']:.4f}",
            "MiniLM FSR": f"{m_b3['false_support_rate']:.2%}",
        },
    ]

    df_cross = pd.DataFrame(rows)
    print(df_cross.to_string(index=False))

    # Paired bootstrap for MiniLM B1-LR vs MiniLM B3 (does Reverse NLI help on MiniLM?)
    bs_minilm_b3_vs_b1 = paired_bootstrap_test(y_test, preds_b3_test, preds_b1_lr_test, n_bootstraps=1000, seed=SEED)
    print("\nMiniLM Paired Bootstrap: B3 vs B1-LR (Does Reverse NLI help on MiniLM?):")
    print(f"  Delta Macro-F1: {bs_minilm_b3_vs_b1['macro_f1']['mean_diff']:+.4f} (95% CI: [{bs_minilm_b3_vs_b1['macro_f1']['ci_lower']:+.4f}, {bs_minilm_b3_vs_b1['macro_f1']['ci_upper']:+.4f}])")
    print(f"  Delta FSR:      {bs_minilm_b3_vs_b1['fsr']['mean_diff']:+.4f} (95% CI: [{bs_minilm_b3_vs_b1['fsr']['ci_lower']:+.4f}, {bs_minilm_b3_vs_b1['fsr']['ci_upper']:+.4f}])")

    # Paired bootstrap for MiniLM B1-LR vs MiniLM B1 (does LR help on MiniLM?)
    bs_minilm_lr_vs_b1 = paired_bootstrap_test(y_test, preds_b1_lr_test, preds_b1_test, n_bootstraps=1000, seed=SEED)
    print("\nMiniLM Paired Bootstrap: B1-LR vs B1 (Does Logistic Regression help on MiniLM?):")
    print(f"  Delta Macro-F1: {bs_minilm_lr_vs_b1['macro_f1']['mean_diff']:+.4f} (95% CI: [{bs_minilm_lr_vs_b1['macro_f1']['ci_lower']:+.4f}, {bs_minilm_lr_vs_b1['macro_f1']['ci_upper']:+.4f}])")
    print(f"  Delta FSR:      {bs_minilm_lr_vs_b1['fsr']['mean_diff']:+.4f} (95% CI: [{bs_minilm_lr_vs_b1['fsr']['ci_lower']:+.4f}, {bs_minilm_lr_vs_b1['fsr']['ci_upper']:+.4f}])")

    results = {
        "minilm_pipeline_metrics": {
            "B0": m_b0,
            "B0-LR": m_b0_lr,
            "B1": m_b1,
            "B1-LR": m_b1_lr,
            "B3": m_b3,
        },
        "bootstrap_minilm_b3_vs_b1_lr": bs_minilm_b3_vs_b1,
        "bootstrap_minilm_b1_lr_vs_b1": bs_minilm_lr_vs_b1,
    }

    out_file = OUTPUTS_DIR / "cross_family_ablation_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved cross-family results to {out_file}")

if __name__ == "__main__":
    run_cross_family_ablation()
