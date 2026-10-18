import json
import logging
import time
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score

from config import (
    OUTPUTS_DIR,
    FORWARD_NLI_CACHE_DIR,
    REVERSE_NLI_CACHE_DIR,
    SEMANTIC_CACHE_DIR,
    set_seed,
    SEED,
)
from src.datasets.attributionbench import load_attributionbench_split, AttributionBenchExample
from src.datasets.wice import WiCEExample
from src.nli import NLIRunner
from src.semantic_filter import SemanticFilter
from src.features import load_or_compute_nli
from src.calibration import evaluate_selective_prediction
from src.metrics import compute_classification_metrics
from src.utils import save_csv, load_json, print_markdown_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def evaluate_split(
    split_name: str,
    examples: list[AttributionBenchExample],
    nli_runner: NLIRunner,
    semantic_filter: SemanticFilter,
    thresholds: dict,
    calibration_data: dict,
    clf_b3,
    scaler_b4,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    logger.info(f"\n--- Evaluating AttributionBench {split_name.upper()} ({len(examples)} examples) ---")
    y_true = np.array([ex.gold_label_binary for ex in examples])

    # Convert to WiCEExample format for feature pipelines
    dummy_examples = [
        WiCEExample(
            example_id=ex.example_id,
            claim_id=ex.example_id,
            claim=ex.claim,
            evidence_units=ex.evidence_units,
            gold_label_3class="supported" if ex.gold_label_binary == 1 else "not_supported",
            gold_label_binary=ex.gold_label_binary,
            gold_evidence_indices=[],
            meta={"src_dataset": ex.src_dataset},
        )
        for ex in examples
    ]

    # B0: Forward NLI on all units
    premises_all = ["\n".join(ex.evidence_units) for ex in examples]
    hypotheses = [ex.claim for ex in examples]
    probs_f_all, _ = load_or_compute_nli(
        nli_runner,
        premises_all,
        hypotheses,
        dummy_examples,
        FORWARD_NLI_CACHE_DIR,
        f"attrbench_{split_name}_forward_all",
        batch_size=8,
    )
    b0_theta = thresholds["b0_threshold"]
    b0_preds = (probs_f_all[:, 0] >= b0_theta).astype(int)
    b0_metrics = compute_classification_metrics(y_true, b0_preds)

    # Semantic filtering with frozen WiCE tau
    tau = thresholds["semantic_similarity_threshold_tau"]
    tau_str = f"{tau:.2f}".replace(".", "_")
    logger.info(f"Computing semantic similarities and filtering with WiCE tau={tau}...")
    sims = semantic_filter.compute_similarities(dummy_examples)

    filt_units = []
    for ex, s in zip(dummy_examples, sims):
        u, _ = SemanticFilter.filter_units(ex.evidence_units, s, tau)
        filt_units.append(u)

    # B1: Forward NLI on filtered units
    premises_filt = ["\n".join(u) for u in filt_units]
    probs_f_filt, _ = load_or_compute_nli(
        nli_runner,
        premises_filt,
        hypotheses,
        dummy_examples,
        FORWARD_NLI_CACHE_DIR,
        f"attrbench_{split_name}_forward_filt_{tau_str}",
        batch_size=8,
    )
    b1_theta = thresholds["b1_support_threshold"]
    b1_preds = (probs_f_filt[:, 0] >= b1_theta).astype(int)
    b1_metrics = compute_classification_metrics(y_true, b1_preds)

    # Reverse NLI on filtered units
    probs_r_filt, _ = load_or_compute_nli(
        nli_runner,
        hypotheses,
        premises_filt,
        dummy_examples,
        REVERSE_NLI_CACHE_DIR,
        f"attrbench_{split_name}_reverse_filt_{tau_str}",
        batch_size=8,
    )

    # B3: Frozen 6D Logistic Regression on filtered units
    X_6d_filt = np.hstack([probs_f_filt, probs_r_filt])
    b3_preds = clf_b3.predict(X_6d_filt)
    b3_metrics = compute_classification_metrics(y_true, b3_preds)

    # B4: Frozen Calibration and Abstention
    logits_b3 = clf_b3.decision_function(X_6d_filt)
    p_cal = scaler_b4.predict_proba(logits_b3)[:, 1]

    t_low = calibration_data["t_low"]
    t_high = calibration_data["t_high"]
    b4_res = evaluate_selective_prediction(p_cal, y_true, t_low, t_high)

    results = {
        "split": split_name,
        "B0_accuracy": b0_metrics["accuracy"],
        "B0_macro_f1": b0_metrics["macro_f1"],
        "B0_false_support_rate": b0_metrics["false_support_rate"],
        "B1_accuracy": b1_metrics["accuracy"],
        "B1_macro_f1": b1_metrics["macro_f1"],
        "B1_false_support_rate": b1_metrics["false_support_rate"],
        "B3_accuracy": b3_metrics["accuracy"],
        "B3_macro_f1": b3_metrics["macro_f1"],
        "B3_false_support_rate": b3_metrics["false_support_rate"],
        "B4_selective_accuracy": b4_res["selective_accuracy"],
        "B4_coverage": b4_res["coverage"],
        "B4_false_support_rate": b4_res["false_support_rate"],
    }

    pred_records = []
    for idx, ex in enumerate(examples):
        pred_records.append({
            "split": split_name,
            "id": ex.example_id,
            "claim": ex.claim,
            "src_dataset": ex.src_dataset,
            "gold_label": ex.gold_label_binary,
            "pred_B0": int(b0_preds[idx]),
            "pred_B1": int(b1_preds[idx]),
            "pred_B3": int(b3_preds[idx]),
            "calibrated_prob": float(p_cal[idx]),
            "pred_B4": int(b4_res["predictions"][idx]),
        })

    return results, pred_records

def main():
    set_seed(SEED)
    logger.info("==================================================")
    logger.info("STARTING ATTRIBUTIONBENCH EXTERNAL/OOD EVALUATION")
    logger.info("==================================================")

    # Load frozen WiCE artifacts
    thresholds_path = OUTPUTS_DIR / "wice_thresholds.json"
    calibration_path = OUTPUTS_DIR / "wice_calibration.json"
    model_path = OUTPUTS_DIR / "models" / "b3_classifier.joblib"
    scaler_path = OUTPUTS_DIR / "models" / "b4_scaler.joblib"

    if not thresholds_path.exists() or not model_path.exists():
        logger.error("WiCE artifacts not found! Please run run_wice.py first.")
        return

    thresholds = load_json(thresholds_path)
    calibration_data = load_json(calibration_path)
    clf_b3 = joblib.load(model_path)
    scaler_b4 = joblib.load(scaler_path)

    logger.info(f"Loaded frozen WiCE thresholds: {thresholds}")
    logger.info(f"Loaded frozen WiCE calibration: Temp={calibration_data['temperature']}, T_low={calibration_data['t_low']}, T_high={calibration_data['t_high']}")

    # Load AttributionBench splits
    id_examples = load_attributionbench_split("id")
    ood_examples = load_attributionbench_split("ood")
    logger.info(f"Loaded AttributionBench ID (In-Domain): {len(id_examples)} examples")
    logger.info(f"Loaded AttributionBench OOD (Out-of-Domain): {len(ood_examples)} examples")

    nli_runner = NLIRunner()
    semantic_filter = SemanticFilter()

    all_results = []
    all_preds = []

    # Evaluate ID
    id_res, id_preds = evaluate_split("id", id_examples, nli_runner, semantic_filter, thresholds, calibration_data, clf_b3, scaler_b4)
    all_results.append(id_res)
    all_preds.extend(id_preds)

    # Evaluate OOD
    ood_res, ood_preds = evaluate_split("ood", ood_examples, nli_runner, semantic_filter, thresholds, calibration_data, clf_b3, scaler_b4)
    all_results.append(ood_res)
    all_preds.extend(ood_preds)

    # Save outputs
    save_csv(all_results, OUTPUTS_DIR / "attributionbench_results.csv")
    save_csv(all_preds, OUTPUTS_DIR / "attributionbench_predictions.csv")

    df_res = pd.DataFrame(all_results)
    print("\n" + "=" * 60)
    print("ATTRIBUTIONBENCH TRANSFER EVALUATION SUMMARY TABLE")
    print("=" * 60)
    print_markdown_table(df_res, "AttributionBench Generalization (Frozen WiCE Pipeline)")

if __name__ == "__main__":
    main()
