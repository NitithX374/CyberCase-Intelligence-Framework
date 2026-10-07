import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import xgboost as xgb
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.wice import load_wice_split
from src.metrics import compute_classification_metrics
from src.bootstrap import paired_bootstrap_test

class TinyMLP(nn.Module):
    def __init__(self, in_features=3, hidden_dim=8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)

def train_tiny_mlp(X_train, y_train, X_dev, y_dev, max_epochs=200, patience=15, lr=0.01):
    torch.manual_seed(SEED)
    model = TinyMLP(in_features=X_train.shape[1], hidden_dim=8)
    
    # Class weights for BCE
    pos_weight = torch.tensor([(len(y_train) - sum(y_train)) / sum(y_train)], dtype=torch.float32)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    X_dev_t = torch.tensor(X_dev, dtype=torch.float32)
    y_dev_t = torch.tensor(y_dev, dtype=torch.float32)

    best_dev_f1 = -1.0
    best_weights = None
    best_epoch = 0
    patience_counter = 0

    for epoch in range(max_epochs):
        model.train()
        optimizer.zero_grad()
        logits = model(X_train_t)
        loss = criterion(logits, y_train_t)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            dev_logits = model(X_dev_t)
            dev_preds = (torch.sigmoid(dev_logits) >= 0.5).long().numpy()
            m = compute_classification_metrics(y_dev, dev_preds)
            dev_f1 = m["macro_f1"]

        if dev_f1 > best_dev_f1:
            best_dev_f1 = dev_f1
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_epoch = epoch
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    model.load_state_dict(best_weights)
    model.eval()
    return model, best_epoch, best_dev_f1

def evaluate_stage4():
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 4: CLASSIFIER HEAD LOOP (LR vs XGBOOST vs TINY MLP)")
    print("=" * 80)

    train_ex = load_wice_split("train")
    dev_ex = load_wice_split("dev")
    test_ex = load_wice_split("test")

    y_train = np.array([ex.gold_label_binary for ex in train_ex])
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])
    y_test = np.array([ex.gold_label_binary for ex in test_ex])

    # Load B1-LR features: [p_entail, p_neutral, p_contra]
    f_train = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                        for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "train_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
    f_dev = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                      for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "dev_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
    f_test = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                       for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "test_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)

    # 1. Model A: Logistic Regression (Current Champion)
    clf_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_lr.fit(f_train, y_train)
    dev_preds_lr = clf_lr.predict(f_dev)
    m_dev_lr = compute_classification_metrics(y_dev, dev_preds_lr)

    print("\n--- MODEL A: LOGISTIC REGRESSION (CURRENT CHAMPION) ---")
    print(f"DEV: Acc={m_dev_lr['accuracy']:.2%}, Macro-F1={m_dev_lr['macro_f1']:.4f}, Supp-F1={m_dev_lr['supported_f1']:.4f}, FSR={m_dev_lr['false_support_rate']:.2%}")

    # 2. Model B: XGBoost Search
    print("\n--- MODEL B: XGBOOST SEARCH ON DEV ---")
    xgb_results = []
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)

    for depth in [2, 3]:
        for lr in [0.03, 0.10]:
            for n_est in [50, 100]:
                model_xgb = xgb.XGBClassifier(
                    max_depth=depth,
                    learning_rate=lr,
                    n_estimators=n_est,
                    scale_pos_weight=scale_pos_weight,
                    random_state=SEED,
                    eval_metric="logloss"
                )
                model_xgb.fit(f_train, y_train)
                dev_preds_xgb = model_xgb.predict(f_dev)
                m_xgb = compute_classification_metrics(y_dev, dev_preds_xgb)
                xgb_results.append({
                    "params": f"depth={depth}, lr={lr}, n_est={n_est}",
                    "model": model_xgb,
                    "accuracy": m_xgb["accuracy"],
                    "macro_f1": m_xgb["macro_f1"],
                    "supported_f1": m_xgb["supported_f1"],
                    "fsr": m_xgb["false_support_rate"],
                    "preds": dev_preds_xgb
                })

    df_xgb = pd.DataFrame(xgb_results).sort_values(by="macro_f1", ascending=False)
    for _, row in df_xgb.iterrows():
        print(f"XGB ({row['params']}): Macro-F1={row['macro_f1']:.4f}, Supp-F1={row['supported_f1']:.4f}, FSR={row['fsr']:.2%}")

    best_xgb = df_xgb.iloc[0]

    # 3. Model C: Tiny MLP
    print("\n--- MODEL C: TINY MLP (d -> 8 -> 1) ---")
    mlp_model, best_epoch, best_dev_f1 = train_tiny_mlp(f_train, y_train, f_dev, y_dev)
    with torch.no_grad():
        mlp_logits = mlp_model(torch.tensor(f_dev, dtype=torch.float32))
        dev_preds_mlp = (torch.sigmoid(mlp_logits) >= 0.5).long().numpy()
    m_dev_mlp = compute_classification_metrics(y_dev, dev_preds_mlp)
    print(f"Tiny MLP (best epoch {best_epoch}): Macro-F1={m_dev_mlp['macro_f1']:.4f}, Supp-F1={m_dev_mlp['supported_f1']:.4f}, FSR={m_dev_mlp['false_support_rate']:.2%}")

    # Compare Candidates against LR
    print("\n" + "=" * 80)
    print("STAGE 4 HEAD COMPARISON ON DEV:")
    print("=" * 80)
    print(f"1. Logistic Regression: Macro-F1 = {m_dev_lr['macro_f1']:.4f}, Supp-F1 = {m_dev_lr['supported_f1']:.4f}, FSR = {m_dev_lr['false_support_rate']:.2%}")
    print(f"2. Best XGBoost:        Macro-F1 = {best_xgb['macro_f1']:.4f}, Supp-F1 = {best_xgb['supported_f1']:.4f}, FSR = {best_xgb['fsr']:.2%}")
    print(f"3. Tiny MLP:            Macro-F1 = {m_dev_mlp['macro_f1']:.4f}, Supp-F1 = {m_dev_mlp['supported_f1']:.4f}, FSR = {m_dev_mlp['false_support_rate']:.2%}")

    delta_xgb_macro = best_xgb['macro_f1'] - m_dev_lr['macro_f1']
    delta_xgb_supp = best_xgb['supported_f1'] - m_dev_lr['supported_f1']
    delta_mlp_macro = m_dev_mlp['macro_f1'] - m_dev_lr['macro_f1']
    delta_mlp_supp = m_dev_mlp['supported_f1'] - m_dev_lr['supported_f1']

    print(f"\nDelta XGB vs LR on DEV: d_Macro-F1 = {delta_xgb_macro:+.4f}, d_Supp-F1 = {delta_xgb_supp:+.4f}")
    print(f"Delta MLP vs LR on DEV: d_Macro-F1 = {delta_mlp_macro:+.4f}, d_Supp-F1 = {delta_mlp_supp:+.4f}")

    # Promotion criteria: >= +0.01 Macro-F1 OR >= +0.02 Supported-F1 OR clear FSR reduction without losing Macro-F1
    promote_xgb = (delta_xgb_macro >= 0.01) or (delta_xgb_supp >= 0.02) or (best_xgb['fsr'] < m_dev_lr['false_support_rate'] - 0.03 and delta_xgb_macro >= -0.005)
    promote_mlp = (delta_mlp_macro >= 0.01) or (delta_mlp_supp >= 0.02) or (m_dev_mlp['false_support_rate'] < m_dev_lr['false_support_rate'] - 0.03 and delta_mlp_macro >= -0.005)

    stage4_results = {
        "dev": {
            "logistic_regression": m_dev_lr,
            "best_xgboost": {k: v for k, v in best_xgb.items() if k not in ["model", "preds"]},
            "tiny_mlp": m_dev_mlp,
            "promote_xgb": bool(promote_xgb),
            "promote_mlp": bool(promote_mlp),
        }
    }

    if not promote_xgb and not promote_mlp:
        print("\nDECISION ON DEV: Neither XGBoost nor Tiny MLP achieved >= +0.01 Macro-F1 or >= +0.02 Supp-F1 over Logistic Regression.")
        print("VERDICT: REJECT non-linear heads. KEEP Logistic Regression.")
        stage4_results["verdict"] = "KEEP_LOGISTIC_REGRESSION"
    else:
        # Determine candidate to evaluate on TEST
        candidate_name = "XGBoost" if promote_xgb else "Tiny MLP"
        print(f"\nDECISION ON DEV: Promoted {candidate_name} for TEST evaluation.")
        # Evaluate on TEST
        test_preds_lr = clf_lr.predict(f_test)
        if promote_xgb:
            test_preds_cand = best_xgb["model"].predict(f_test)
        else:
            with torch.no_grad():
                cand_logits = mlp_model(torch.tensor(f_test, dtype=torch.float32))
                test_preds_cand = (torch.sigmoid(cand_logits) >= 0.5).long().numpy()

        m_test_lr = compute_classification_metrics(y_test, test_preds_lr)
        m_test_cand = compute_classification_metrics(y_test, test_preds_cand)

        print("\nTEST EVALUATION:")
        print(f"LR:        Acc={m_test_lr['accuracy']:.2%}, Macro-F1={m_test_lr['macro_f1']:.4f}, Supp-F1={m_test_lr['supported_f1']:.4f}, FSR={m_test_lr['false_support_rate']:.2%}")
        print(f"{candidate_name}: Acc={m_test_cand['accuracy']:.2%}, Macro-F1={m_test_cand['macro_f1']:.4f}, Supp-F1={m_test_cand['supported_f1']:.4f}, FSR={m_test_cand['false_support_rate']:.2%}")

        bs = paired_bootstrap_test(y_test, test_preds_cand, test_preds_lr, n_bootstraps=1000, seed=SEED)
        print(f"\nPaired Bootstrap {candidate_name} vs LR on TEST:")
        for metric, vals in bs.items():
            print(f"  Delta {metric}: {vals['mean_diff']:+.4f} (95% CI: [{vals['ci_lower']:+.4f}, {vals['ci_upper']:+.4f}])")

        ci_macro = bs["macro_f1"]
        if ci_macro["ci_lower"] > 0 and ci_macro["mean_diff"] >= 0.005:
            print(f"VERDICT: PROMOTE {candidate_name} to CURRENT_CHAMPION.")
            stage4_results["verdict"] = f"PROMOTE_{candidate_name.upper()}"
        else:
            print(f"VERDICT: REJECT {candidate_name}. TEST evidence is weak or CI spans zero. REVERT to Logistic Regression.")
            stage4_results["verdict"] = "REVERT_TO_LOGISTIC_REGRESSION"

        stage4_results["test"] = {
            "logistic_regression": m_test_lr,
            "candidate": m_test_cand,
            "bootstrap": bs
        }

    with open(OUTPUTS_DIR / "stage4_classifier_heads_results.json", "w", encoding="utf-8") as f:
        json.dump(stage4_results, f, indent=2)

if __name__ == "__main__":
    evaluate_stage4()
