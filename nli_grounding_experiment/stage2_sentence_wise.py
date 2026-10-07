import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed, DEVICE
from src.datasets.wice import load_wice_split, WiCEExample
from src.metrics import compute_classification_metrics
from src.fusion import FusionClassifier
from src.semantic_filter import SemanticFilter
from src.nli import NLIRunner

SW_CACHE_DIR = CACHE_DIR / "sentence_wise"
SW_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def extract_sw_features(
    unit_probs_list: list[np.ndarray], # each item is (k, 3) where columns are [entail, neutral, contra]
) -> np.ndarray:
    """
    Extracts 10 deterministic aggregate features from sentence-wise NLI probabilities:
    1. max_entail
    2. mean_entail
    3. top3_mean_entail
    4. max_neutral
    5. mean_neutral
    6. max_contradiction
    7. mean_contradiction
    8. retained_unit_count
    9. fraction_entail_gt_0_5
    10. fraction_contra_gt_0_5
    """
    features = []
    for probs in unit_probs_list:
        k = len(probs)
        if k == 0:
            features.append(np.zeros(10, dtype=np.float32))
            continue

        entail = probs[:, 0]
        neutral = probs[:, 1]
        contra = probs[:, 2]

        max_e = float(np.max(entail))
        mean_e = float(np.mean(entail))

        # top3 mean entail
        sorted_e = np.sort(entail)[::-1]
        top3_e = float(np.mean(sorted_e[:min(3, k)]))

        max_n = float(np.max(neutral))
        mean_n = float(np.mean(neutral))

        max_c = float(np.max(contra))
        mean_c = float(np.mean(contra))

        ret_count = float(k)
        frac_e_gt_05 = float(np.mean(entail > 0.5))
        frac_c_gt_05 = float(np.mean(contra > 0.5))

        features.append([
            max_e, mean_e, top3_e,
            max_n, mean_n,
            max_c, mean_c,
            ret_count, frac_e_gt_05, frac_c_gt_05
        ])

    return np.array(features, dtype=np.float32)

def compute_or_load_sentence_nli(
    runner: NLIRunner,
    split_name: str,
    examples: list[WiCEExample],
    tau: float = 0.20,
    batch_size: int = 64,
) -> list[np.ndarray]:
    cache_file = SW_CACHE_DIR / f"{split_name}_sw_nli_tau_0_20.jsonl"

    if cache_file.exists():
        print(f"Loading cached sentence-wise NLI for {split_name}...")
        records = [json.loads(line) for line in open(cache_file, "r", encoding="utf-8") if line.strip()]
        if len(records) == len(examples):
            return [np.array(r["unit_probs"], dtype=np.float32) for r in records]

    print(f"Computing sentence-wise NLI for {split_name} ({len(examples)} examples)...")
    sem_cache = CACHE_DIR / "semantic_scores" / f"{split_name}.jsonl"
    sims = [json.loads(l)["similarities"] for l in open(sem_cache, "r", encoding="utf-8") if l.strip()]

    # Collect pairs
    all_premises = []
    all_hypotheses = []
    slices = []
    curr = 0

    for ex, s_list in zip(examples, sims):
        filt_u, _ = SemanticFilter.filter_units(ex.evidence_units, s_list, tau)
        n_u = len(filt_u)
        slices.append((curr, curr + n_u))
        for u in filt_u:
            all_premises.append(u)
            all_hypotheses.append(ex.claim)
        curr += n_u

    print(f"Total sentence-claim pairs to evaluate on {split_name}: {len(all_premises)}")

    # Batch prediction
    t0 = time.time()
    probs, _ = runner.predict_probs(all_premises, all_hypotheses, batch_size=batch_size)
    print(f"Sentence-wise NLI finished in {time.time() - t0:.1f}s")

    # Slice back to per-example
    unit_probs_list = []
    records = []
    for idx, (start, end) in enumerate(slices):
        ex_probs = probs[start:end]
        unit_probs_list.append(ex_probs)
        records.append({
            "example_id": examples[idx].example_id,
            "claim_id": examples[idx].claim_id,
            "unit_probs": ex_probs.tolist()
        })

    # Save cache
    with open(cache_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return unit_probs_list

def main():
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 2: SENTENCE-WISE FORWARD NLI (SW-NLI-LR) EXPERIMENT")
    print("=" * 80)

    train_ex = load_wice_split("train")
    dev_ex = load_wice_split("dev")
    y_train = np.array([ex.gold_label_binary for ex in train_ex])
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])

    runner = NLIRunner()

    # Compute/load sentence-wise NLI for train and dev
    sw_train_probs = compute_or_load_sentence_nli(runner, "train", train_ex, tau=0.20, batch_size=128)
    sw_dev_probs = compute_or_load_sentence_nli(runner, "dev", dev_ex, tau=0.20, batch_size=128)

    X_train_sw = extract_sw_features(sw_train_probs)
    X_dev_sw = extract_sw_features(sw_dev_probs)

    print(f"Feature matrix shapes: Train {X_train_sw.shape}, Dev {X_dev_sw.shape}")

    # Train Logistic Regression
    clf_sw = FusionClassifier(C=1.0, class_weight="balanced", random_state=SEED)
    clf_sw.fit(X_train_sw, y_train)

    dev_sw_preds = clf_sw.predict(X_dev_sw)
    m_dev_sw = compute_classification_metrics(y_dev, dev_sw_preds)

    # Load CURRENT_CHAMPION (B1-LR) on DEV
    clf_b1_lr = joblib.load(OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")
    dev_f_filt = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                           for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "dev_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]])
    dev_b1_lr_preds = clf_b1_lr.predict(dev_f_filt)
    m_dev_champ = compute_classification_metrics(y_dev, dev_b1_lr_preds)

    print("\n" + "=" * 80)
    print("DEV COMPARISON: SW-NLI-LR vs CURRENT_CHAMPION (B1-LR)")
    print("=" * 80)
    print(f"Metric              B1-LR (Champion)     SW-NLI-LR (Candidate)     Delta")
    print(f"-------------------------------------------------------------------------")
    print(f"Accuracy:           {m_dev_champ['accuracy']:.4%}              {m_dev_sw['accuracy']:.4%}              {m_dev_sw['accuracy'] - m_dev_champ['accuracy']:+.2%}")
    print(f"Macro-F1:           {m_dev_champ['macro_f1']:.4f}                {m_dev_sw['macro_f1']:.4f}                {m_dev_sw['macro_f1'] - m_dev_champ['macro_f1']:+.4f}")
    print(f"Supported-F1:       {m_dev_champ['supported_f1']:.4f}                {m_dev_sw['supported_f1']:.4f}                {m_dev_sw['supported_f1'] - m_dev_champ['supported_f1']:+.4f}")
    print(f"False Support Rate: {m_dev_champ['false_support_rate']:.4%}              {m_dev_sw['false_support_rate']:.4%}              {m_dev_sw['false_support_rate'] - m_dev_champ['false_support_rate']:+.2%}")

    delta_mf1 = m_dev_sw['macro_f1'] - m_dev_champ['macro_f1']
    delta_sf1 = m_dev_sw['supported_f1'] - m_dev_champ['supported_f1']
    delta_fsr = m_dev_sw['false_support_rate'] - m_dev_champ['false_support_rate']

    # Promotion criteria check:
    # Requires at least one:
    # 1. Delta Macro-F1 >= +0.01
    # 2. Delta Supported-F1 >= +0.02
    # 3. Meaningful FSR reduction (e.g. <= -2.0%) with approximately unchanged Macro-F1 (|delta_mf1| <= 0.005)
    promoted = False
    if delta_mf1 >= 0.01:
        promoted = True
        reason = "Macro-F1 gain >= +0.01"
    elif delta_sf1 >= 0.02:
        promoted = True
        reason = "Supported-F1 gain >= +0.02"
    elif delta_fsr <= -0.02 and abs(delta_mf1) <= 0.005:
        promoted = True
        reason = "Meaningful FSR reduction with stable Macro-F1"
    else:
        reason = "Failed all promotion thresholds (no meaningful gain on DEV)"

    print(f"\nPROMOTION DECISION: {'PROMOTE' if promoted else 'REJECT'}")
    print(f"Reason: {reason}")

    out_res = {
        "candidate": "SW-NLI-LR",
        "champion": "B1-LR",
        "dev_champion": m_dev_champ,
        "dev_candidate": m_dev_sw,
        "deltas": {
            "delta_accuracy": m_dev_sw['accuracy'] - m_dev_champ['accuracy'],
            "delta_macro_f1": delta_mf1,
            "delta_supported_f1": delta_sf1,
            "delta_fsr": delta_fsr,
        },
        "promoted": promoted,
        "decision_reason": reason,
    }

    if promoted:
        print("\nCandidate achieved DEV promotion criteria! Evaluating once on TEST...")
        test_ex = load_wice_split("test")
        y_test = np.array([ex.gold_label_binary for ex in test_ex])
        sw_test_probs = compute_or_load_sentence_nli(runner, "test", test_ex, tau=0.20, batch_size=128)
        X_test_sw = extract_sw_features(sw_test_probs)
        test_sw_preds = clf_sw.predict(X_test_sw)
        m_test_sw = compute_classification_metrics(y_test, test_sw_preds)
        out_res["test_candidate"] = m_test_sw
        print(f"TEST Results: Acc={m_test_sw['accuracy']:.4f}, Macro-F1={m_test_sw['macro_f1']:.4f}, Supp-F1={m_test_sw['supported_f1']:.4f}, FSR={m_test_sw['false_support_rate']:.4f}")
    else:
        print("\nCandidate REJECTED on DEV. CURRENT_CHAMPION remains B1-LR. TEST split remains untouched.")

    json.dump(out_res, open(OUTPUTS_DIR / "stage2_sw_nli_verdict.json", "w", encoding="utf-8"), indent=2)

if __name__ == "__main__":
    main()
