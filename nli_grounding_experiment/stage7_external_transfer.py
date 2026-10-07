import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.attributionbench import load_attributionbench_split
from src.metrics import compute_classification_metrics

def run_stage7(champion_name="B1-LR", champion_model_path=None):
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 7: EXTERNAL TRANSFER (ATTRIBUTIONBENCH ID & OOD)")
    print(f"Comparing: B0 vs original B1-LR vs FINAL CURRENT_CHAMPION ({champion_name})")
    print("=" * 80)

    id_ex = load_attributionbench_split("id")
    ood_ex = load_attributionbench_split("ood")

    y_id = np.array([ex.gold_label_binary for ex in id_ex])
    y_ood = np.array([ex.gold_label_binary for ex in ood_ex])

    print(f"Loaded AttributionBench ID ({len(id_ex)} examples, {sum(y_id)} positive)")
    print(f"Loaded AttributionBench OOD ({len(ood_ex)} examples, {sum(y_ood)} positive)")

    # 1. Load B0 features (Forward NLI full premise)
    f_b0_id = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                        for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "attrbench_id_forward_all.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
    f_b0_ood = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                         for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "attrbench_ood_forward_all.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)

    # B0 decision rule: argmax == 0 (entailment)
    preds_b0_id = (np.argmax(f_b0_id, axis=1) == 0).astype(int)
    preds_b0_ood = (np.argmax(f_b0_ood, axis=1) == 0).astype(int)

    # 2. Load B1-LR features (Forward NLI semantic filtered tau=0.20)
    f_b1_id = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                        for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "attrbench_id_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)
    f_b1_ood = np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]]
                         for r in [json.loads(l) for l in open(CACHE_DIR / "forward_nli" / "attrbench_ood_forward_filt_0_20.jsonl", "r", encoding="utf-8") if l.strip()]], dtype=np.float32)

    clf_b1 = joblib.load(OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")
    preds_b1_id = clf_b1.predict(f_b1_id)
    preds_b1_ood = clf_b1.predict(f_b1_ood)

    # 3. Final Champion predictions
    if champion_name == "B1-LR" or champion_model_path is None:
        preds_champ_id = preds_b1_id
        preds_champ_ood = preds_b1_ood
    else:
        clf_champ = joblib.load(champion_model_path)
        # Assuming champion uses same filtered features
        preds_champ_id = clf_champ.predict(f_b1_id)
        preds_champ_ood = clf_champ.predict(f_b1_ood)

    # Compute metrics
    m_b0_id = compute_classification_metrics(y_id, preds_b0_id)
    m_b0_ood = compute_classification_metrics(y_ood, preds_b0_ood)

    m_b1_id = compute_classification_metrics(y_id, preds_b1_id)
    m_b1_ood = compute_classification_metrics(y_ood, preds_b1_ood)

    m_champ_id = compute_classification_metrics(y_id, preds_champ_id)
    m_champ_ood = compute_classification_metrics(y_ood, preds_champ_ood)

    results = {
        "attributionbench_id": {
            "B0": m_b0_id,
            "B1-LR": m_b1_id,
            champion_name: m_champ_id,
        },
        "attributionbench_ood": {
            "B0": m_b0_ood,
            "B1-LR": m_b1_ood,
            champion_name: m_champ_ood,
        }
    }

    print("\n" + "=" * 90)
    print("ATTRIBUTIONBENCH IN-DOMAIN (ID) TRANSFER RESULTS:")
    print("=" * 90)
    df_id = pd.DataFrame([
        {"Method": "B0 (Full premise, argmax)", "Accuracy": f"{m_b0_id['accuracy']:.2%}", "Macro-F1": f"{m_b0_id['macro_f1']:.4f}", "Supp-Prec": f"{m_b0_id['supported_precision']:.2%}", "Supp-Rec": f"{m_b0_id['supported_recall']:.2%}", "Supp-F1": f"{m_b0_id['supported_f1']:.4f}", "FSR": f"{m_b0_id['false_support_rate']:.2%}"},
        {"Method": "B1-LR (Filt tau=0.20 + LR)", "Accuracy": f"{m_b1_id['accuracy']:.2%}", "Macro-F1": f"{m_b1_id['macro_f1']:.4f}", "Supp-Prec": f"{m_b1_id['supported_precision']:.2%}", "Supp-Rec": f"{m_b1_id['supported_recall']:.2%}", "Supp-F1": f"{m_b1_id['supported_f1']:.4f}", "FSR": f"{m_b1_id['false_support_rate']:.2%}"},
        {"Method": f"FINAL CHAMPION ({champion_name})", "Accuracy": f"{m_champ_id['accuracy']:.2%}", "Macro-F1": f"{m_champ_id['macro_f1']:.4f}", "Supp-Prec": f"{m_champ_id['supported_precision']:.2%}", "Supp-Rec": f"{m_champ_id['supported_recall']:.2%}", "Supp-F1": f"{m_champ_id['supported_f1']:.4f}", "FSR": f"{m_champ_id['false_support_rate']:.2%}"},
    ])
    print(df_id.to_string(index=False))

    print("\n" + "=" * 90)
    print("ATTRIBUTIONBENCH OUT-OF-DOMAIN (OOD) TRANSFER RESULTS:")
    print("=" * 90)
    df_ood = pd.DataFrame([
        {"Method": "B0 (Full premise, argmax)", "Accuracy": f"{m_b0_ood['accuracy']:.2%}", "Macro-F1": f"{m_b0_ood['macro_f1']:.4f}", "Supp-Prec": f"{m_b0_ood['supported_precision']:.2%}", "Supp-Rec": f"{m_b0_ood['supported_recall']:.2%}", "Supp-F1": f"{m_b0_ood['supported_f1']:.4f}", "FSR": f"{m_b0_ood['false_support_rate']:.2%}"},
        {"Method": "B1-LR (Filt tau=0.20 + LR)", "Accuracy": f"{m_b1_ood['accuracy']:.2%}", "Macro-F1": f"{m_b1_ood['macro_f1']:.4f}", "Supp-Prec": f"{m_b1_ood['supported_precision']:.2%}", "Supp-Rec": f"{m_b1_ood['supported_recall']:.2%}", "Supp-F1": f"{m_b1_ood['supported_f1']:.4f}", "FSR": f"{m_b1_ood['false_support_rate']:.2%}"},
        {"Method": f"FINAL CHAMPION ({champion_name})", "Accuracy": f"{m_champ_ood['accuracy']:.2%}", "Macro-F1": f"{m_champ_ood['macro_f1']:.4f}", "Supp-Prec": f"{m_champ_ood['supported_precision']:.2%}", "Supp-Rec": f"{m_champ_ood['supported_recall']:.2%}", "Supp-F1": f"{m_champ_ood['supported_f1']:.4f}", "FSR": f"{m_champ_ood['false_support_rate']:.2%}"},
    ])
    print(df_ood.to_string(index=False))

    out_file = OUTPUTS_DIR / "stage7_external_transfer_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved Stage 7 external transfer results to {out_file}")

if __name__ == "__main__":
    run_stage7()
