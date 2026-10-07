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

NEW_BACKBONE_NAME = "joeddav/xlm-roberta-large-xnli"

def run_stage5():
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 5: NLI BACKBONE LOOP")
    print(f"Comparing CURRENT BACKBONE (mDeBERTa-v3-base) vs CANDIDATE ({NEW_BACKBONE_NAME})")
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

    # Check cache for new backbone
    cache_dir = CACHE_DIR / "backbone_xlm_roberta"
    cache_dir.mkdir(parents=True, exist_ok=True)

    def compute_or_load_backbone_probs(split_name, premises, hypotheses, batch_size=16):
        cache_file = cache_dir / f"{split_name}_probs.jsonl"
        meta_file = cache_dir / f"{split_name}_meta.json"
        if cache_file.exists():
            print(f"Loading cached {NEW_BACKBONE_NAME} probabilities for {split_name}...")
            probs = np.array([json.loads(l)["probs"] for l in open(cache_file, "r", encoding="utf-8") if l.strip()], dtype=np.float32)
            latency_ms = json.load(open(meta_file, "r", encoding="utf-8")).get("latency_ms", 0.0) if meta_file.exists() else 0.0
            return probs, latency_ms

        print(f"Computing {NEW_BACKBONE_NAME} probabilities for {split_name} ({len(premises)} examples)...")
        tok = AutoTokenizer.from_pretrained(NEW_BACKBONE_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(NEW_BACKBONE_NAME)
        if DEVICE == "cuda":
            model = model.half().to(DEVICE)
        else:
            model = model.to(DEVICE)
        model.eval()

        id2label = model.config.id2label
        label2id = {v.lower(): k for k, v in id2label.items()}
        # joeddav/xlm-roberta-large-xnli labels: contradiction, neutral, entailment
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
        print(f"Computed {split_name} in {elapsed:.1f}s ({latency_ms:.1f} ms/claim)")
        with open(cache_file, "w", encoding="utf-8") as f:
            for prob in all_probs:
                f.write(json.dumps({"probs": prob}) + "\n")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({"elapsed_s": elapsed, "latency_ms": latency_ms, "n": len(premises)}, f)

        return np.array(all_probs, dtype=np.float32), latency_ms

    # Compute DEV first to see if it even makes sense to train
    # Load CURRENT_CHAMPION DEV metrics
    f_dev_champ = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                            for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "dev_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
    clf_champ = joblib.load(OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")
    dev_preds_champ = clf_champ.predict(f_dev_champ)
    m_dev_champ = compute_classification_metrics(y_dev, dev_preds_champ)

    print("\nCURRENT CHAMPION (mDeBERTa-v3-base: 278M params, ~1.1GB) ON DEV:")
    print(f"Accuracy:     {m_dev_champ['accuracy']:.2%}")
    print(f"Macro-F1:     {m_dev_champ['macro_f1']:.4f}")
    print(f"Supported-F1: {m_dev_champ['supported_f1']:.4f}")
    print(f"FSR:          {m_dev_champ['false_support_rate']:.2%}")

    # Compute new backbone features
    f_train_new, lat_train = compute_or_load_backbone_probs("train", p_train, h_train, batch_size=16)
    f_dev_new, lat_dev = compute_or_load_backbone_probs("dev", p_dev, h_dev, batch_size=16)

    # Train classifier head on new backbone features
    clf_new = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_new.fit(f_train_new, y_train)

    dev_preds_new = clf_new.predict(f_dev_new)
    m_dev_new = compute_classification_metrics(y_dev, dev_preds_new)

    print(f"\nCANDIDATE BACKBONE ({NEW_BACKBONE_NAME}: 560M params, ~2.24GB) ON DEV:")
    print(f"Accuracy:     {m_dev_new['accuracy']:.2%}")
    print(f"Macro-F1:     {m_dev_new['macro_f1']:.4f}")
    print(f"Supported-F1: {m_dev_new['supported_f1']:.4f}")
    print(f"FSR:          {m_dev_new['false_support_rate']:.2%}")
    print(f"DEV Latency:  {lat_dev:.1f} ms/claim (batch=16)")

    delta_macro = m_dev_new['macro_f1'] - m_dev_champ['macro_f1']
    delta_supp = m_dev_new['supported_f1'] - m_dev_champ['supported_f1']
    print(f"\nDelta candidate vs champion on DEV: d_Macro-F1 = {delta_macro:+.4f}, d_Supp-F1 = {delta_supp:+.4f}")

    stage5_results = {
        "dev": {
            "current_champion": m_dev_champ,
            "candidate_backbone": m_dev_new,
            "delta_macro_f1": delta_macro,
            "delta_supported_f1": delta_supp,
        }
    }

    if delta_macro < 0.01 and delta_supp < 0.02:
        print(f"\nDECISION ON DEV: Candidate backbone gain is trivial (d_Macro-F1 = {delta_macro:+.4f} < +0.01).")
        print("VERDICT: REJECT alternative backbone. KEEP MoritzLaurer/mDeBERTa-v3-base-xnli.")
        stage5_results["verdict"] = "REJECT_NEW_BACKBONE"
    else:
        print(f"\nDECISION ON DEV: Candidate backbone showed meaningful gain. Evaluating ONCE on TEST...")
        f_test_new, lat_test = compute_or_load_backbone_probs("test", p_test, h_test, batch_size=16)
        test_preds_new = clf_new.predict(f_test_new)

        f_test_champ = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                                 for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "test_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
        test_preds_champ = clf_champ.predict(f_test_champ)

        m_test_champ = compute_classification_metrics(y_test, test_preds_champ)
        m_test_new = compute_classification_metrics(y_test, test_preds_new)

        bs = paired_bootstrap_test(y_test, test_preds_new, test_preds_champ, n_bootstraps=1000, seed=SEED)
        print("\nTEST EVALUATION:")
        print(f"Champion:  Macro-F1 = {m_test_champ['macro_f1']:.4f}, Supp-F1 = {m_test_champ['supported_f1']:.4f}")
        print(f"Candidate: Macro-F1 = {m_test_new['macro_f1']:.4f}, Supp-F1 = {m_test_new['supported_f1']:.4f}")
        for k, v in bs.items():
            print(f"  Delta {k}: {v['mean_diff']:+.4f} [{v['ci_lower']:+.4f}, {v['ci_upper']:+.4f}]")

        ci_macro = bs["macro_f1"]
        if ci_macro["ci_lower"] > 0 and ci_macro["mean_diff"] >= 0.005:
            print("VERDICT: PROMOTE new backbone to CURRENT_CHAMPION.")
            stage5_results["verdict"] = "PROMOTE_NEW_BACKBONE"
        else:
            print("VERDICT: REJECT new backbone. TEST evidence does not support promotion. REVERT to mDeBERTa-v3-base.")
            stage5_results["verdict"] = "REVERT_TO_CURRENT_CHAMPION"

        stage5_results["test"] = {
            "champion": m_test_champ,
            "candidate": m_test_new,
            "bootstrap": bs
        }

    with open(OUTPUTS_DIR / "stage5_backbone_results.json", "w", encoding="utf-8") as f:
        json.dump(stage5_results, f, indent=2)

if __name__ == "__main__":
    run_stage5()
