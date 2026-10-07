import json
import logging
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score

from config import (
    OUTPUTS_DIR,
    set_seed,
    SEED,
)
from src.datasets.wice import load_wice_split, WiCEExample
from src.nli import NLIRunner
from src.semantic_filter import (
    SemanticFilter,
    get_cached_semantic_scores,
    save_cached_semantic_scores,
)
from src.features import (
    get_forward_nli_all,
    get_reverse_nli_all,
    get_forward_nli_filtered,
    get_reverse_nli_filtered,
)
from src.fusion import tune_binary_threshold, FusionClassifier
from src.calibration import (
    TemperatureScaler,
    select_abstention_thresholds,
    evaluate_selective_prediction,
    compute_risk_coverage_curve,
)
from src.metrics import (
    compute_classification_metrics,
    compute_bootstrap_ci,
    compute_evidence_retrieval_metrics,
)
from src.utils import save_json, save_csv, print_markdown_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    set_seed(SEED)
    logger.info("==================================================")
    logger.info("STARTING WICE B0-B4 EXPERIMENTAL PIPELINE")
    logger.info("==================================================")

    # 1. Load Datasets
    logger.info("Loading WiCE official dataset splits...")
    train_examples = load_wice_split("train")
    dev_examples = load_wice_split("dev")
    test_examples = load_wice_split("test")

    logger.info(f"Loaded Train: {len(train_examples)} examples ({sum(ex.gold_label_binary for ex in train_examples)} positive / {len(train_examples) - sum(ex.gold_label_binary for ex in train_examples)} negative)")
    logger.info(f"Loaded Dev:   {len(dev_examples)} examples ({sum(ex.gold_label_binary for ex in dev_examples)} positive / {len(dev_examples) - sum(ex.gold_label_binary for ex in dev_examples)} negative)")
    logger.info(f"Loaded Test:  {len(test_examples)} examples ({sum(ex.gold_label_binary for ex in test_examples)} positive / {len(test_examples) - sum(ex.gold_label_binary for ex in test_examples)} negative)")

    y_train = np.array([ex.gold_label_binary for ex in train_examples])
    y_dev = np.array([ex.gold_label_binary for ex in dev_examples])
    y_test = np.array([ex.gold_label_binary for ex in test_examples])

    # 2. Initialize Models
    logger.info("Initializing Pretrained Models (Frozen, No Fine-tuning)...")
    nli_runner = NLIRunner()
    semantic_filter = SemanticFilter()

    # ----------------------------------------------------
    # PHASE 1: B0 — MULTILINGUAL NLI ONLY
    # ----------------------------------------------------
    logger.info("\n--- PHASE 1: B0 Forward NLI (All EvidenceUnits) ---")
    
    t0 = time.time()
    train_f_all, train_meta_f = get_forward_nli_all(nli_runner, train_examples, "train")
    dev_f_all, dev_meta_f = get_forward_nli_all(nli_runner, dev_examples, "dev")
    t_start_test = time.time()
    test_f_all, test_meta_f = get_forward_nli_all(nli_runner, test_examples, "test")
    test_latency_b0_ms = ((time.time() - t_start_test) / len(test_examples)) * 1000.0

    trunc_dev = sum(1 for m in dev_meta_f if m["truncated"])
    trunc_test = sum(1 for m in test_meta_f if m["truncated"])
    logger.info(f"Forward NLI Truncation: Dev={trunc_dev}/{len(dev_examples)}, Test={trunc_test}/{len(test_examples)}")

    # Tune B0 threshold on DEV only
    b0_theta, b0_dev_f1 = tune_binary_threshold(y_dev, dev_f_all[:, 0])
    logger.info(f"B0 DEV Tuned Threshold: theta={b0_theta:.4f} (DEV Macro-F1={b0_dev_f1:.4f})")

    # Evaluate B0 on TEST
    b0_test_preds = (test_f_all[:, 0] >= b0_theta).astype(int)
    b0_metrics = compute_classification_metrics(y_test, b0_test_preds)
    b0_metrics["avg_latency_ms"] = test_latency_b0_ms
    logger.info(f"B0 TEST Results: Acc={b0_metrics['accuracy']:.4f}, Macro-F1={b0_metrics['macro_f1']:.4f}, Supp-F1={b0_metrics['supported_f1']:.4f}, FSR={b0_metrics['false_support_rate']:.4f}")

    # ----------------------------------------------------
    # PHASE 2: B1 — SEMANTIC FILTER -> NLI
    # ----------------------------------------------------
    logger.info("\n--- PHASE 2: Semantic Evidence Filtering ---")
    
    # Compute or load semantic similarities
    train_sims = get_cached_semantic_scores("train")
    if train_sims is None:
        logger.info("Computing semantic similarities on Train...")
        train_sims = semantic_filter.compute_similarities(train_examples)
        save_cached_semantic_scores(train_examples, train_sims, "train")

    dev_sims = get_cached_semantic_scores("dev")
    if dev_sims is None:
        logger.info("Computing semantic similarities on Dev...")
        dev_sims = semantic_filter.compute_similarities(dev_examples)
        save_cached_semantic_scores(dev_examples, dev_sims, "dev")

    test_sims = get_cached_semantic_scores("test")
    if test_sims is None:
        logger.info("Computing semantic similarities on Test...")
        test_sims = semantic_filter.compute_similarities(test_examples)
        save_cached_semantic_scores(test_examples, test_sims, "test")

    # Sweep threshold on DEV only
    candidate_tau = [round(t, 2) for t in np.arange(0.20, 0.901, 0.05)]
    logger.info(f"Sweeping semantic filter threshold on DEV across: {candidate_tau}")

    best_tau = 0.50
    best_tau_recall = -1.0
    best_tau_f1 = -1.0

    dev_gold_indices = [ex.gold_evidence_indices for ex in dev_examples]

    for tau in candidate_tau:
        filt_units_dev = []
        sel_idx_dev = []
        for ex, sims in zip(dev_examples, dev_sims):
            units, sel = SemanticFilter.filter_units(ex.evidence_units, sims, tau)
            filt_units_dev.append(units)
            sel_idx_dev.append(sel)

        retrieval_metrics = compute_evidence_retrieval_metrics(dev_gold_indices, sel_idx_dev)
        rec = retrieval_metrics["evidence_recall"]
        
        # Priority 1: High recall (>= 0.85 if possible), Priority 2: Macro-F1
        if rec > best_tau_recall or (abs(rec - best_tau_recall) < 1e-4 and retrieval_metrics["evidence_f1"] > best_tau_f1):
            best_tau_recall = rec
            best_tau_f1 = retrieval_metrics["evidence_f1"]
            best_tau = tau

    # If all candidate thresholds have high recall, refine by checking claim Macro-F1 on dev for top recall candidates
    logger.info(f"Selected Semantic Threshold on DEV: tau={best_tau:.2f} (Gold Evidence Recall={best_tau_recall:.4f}, Evidence F1={best_tau_f1:.4f})")

    # Filter units using selected best_tau
    tau_str = f"{best_tau:.2f}".replace(".", "_")

    train_filt_units = [SemanticFilter.filter_units(ex.evidence_units, s, best_tau)[0] for ex, s in zip(train_examples, train_sims)]
    dev_filt_units = [SemanticFilter.filter_units(ex.evidence_units, s, best_tau)[0] for ex, s in zip(dev_examples, dev_sims)]
    
    test_filt_units = []
    test_sel_idx = []
    for ex, s in zip(test_examples, test_sims):
        u, idxs = SemanticFilter.filter_units(ex.evidence_units, s, best_tau)
        test_filt_units.append(u)
        test_sel_idx.append(idxs)

    # Evidence filtering metrics on TEST
    test_gold_indices = [ex.gold_evidence_indices for ex in test_examples]
    test_retrieval_metrics = compute_evidence_retrieval_metrics(test_gold_indices, test_sel_idx)
    units_before = np.mean([len(ex.evidence_units) for ex in test_examples])
    units_after = np.mean([len(u) for u in test_filt_units])
    pct_removed = ((units_before - units_after) / units_before) * 100.0

    semantic_summary = {
        "tau_selected": best_tau,
        "evidence_precision": test_retrieval_metrics["evidence_precision"],
        "evidence_recall": test_retrieval_metrics["evidence_recall"],
        "evidence_f1": test_retrieval_metrics["evidence_f1"],
        "avg_units_before": float(units_before),
        "avg_units_after": float(units_after),
        "pct_units_removed": float(pct_removed),
    }

    # B1 Forward NLI on filtered units
    dev_f_filt, _ = get_forward_nli_filtered(nli_runner, dev_examples, dev_filt_units, "dev", tau_str)
    t_start_test = time.time()
    test_f_filt, _ = get_forward_nli_filtered(nli_runner, test_examples, test_filt_units, "test", tau_str)
    test_latency_b1_ms = ((time.time() - t_start_test) / len(test_examples)) * 1000.0

    # Tune B1 threshold on DEV
    b1_theta, b1_dev_f1 = tune_binary_threshold(y_dev, dev_f_filt[:, 0])
    logger.info(f"B1 DEV Tuned Threshold: theta={b1_theta:.4f} (DEV Macro-F1={b1_dev_f1:.4f})")

    b1_test_preds = (test_f_filt[:, 0] >= b1_theta).astype(int)
    b1_metrics = compute_classification_metrics(y_test, b1_test_preds)
    b1_metrics["avg_latency_ms"] = test_latency_b1_ms
    logger.info(f"B1 TEST Results: Acc={b1_metrics['accuracy']:.4f}, Macro-F1={b1_metrics['macro_f1']:.4f}, Supp-F1={b1_metrics['supported_f1']:.4f}, FSR={b1_metrics['false_support_rate']:.4f}")

    # ----------------------------------------------------
    # PHASE 3: B0-LR and B2 — BIDIRECTIONAL NLI
    # ----------------------------------------------------
    logger.info("\n--- PHASE 3: Reverse NLI & Fusion Classifiers ---")

    # Reverse NLI on all candidate units
    train_r_all, _ = get_reverse_nli_all(nli_runner, train_examples, "train")
    dev_r_all, _ = get_reverse_nli_all(nli_runner, dev_examples, "dev")
    t_start_test = time.time()
    test_r_all, _ = get_reverse_nli_all(nli_runner, test_examples, "test")
    test_latency_b2_ms = test_latency_b0_ms + (((time.time() - t_start_test) / len(test_examples)) * 1000.0)

    # B0-LR: Forward-only Logistic Regression [F_entail, F_neutral, F_contra]
    X_train_3d = train_f_all
    X_test_3d = test_f_all

    clf_b0_lr = FusionClassifier()
    clf_b0_lr.fit(X_train_3d, y_train)
    b0_lr_preds = clf_b0_lr.predict(X_test_3d)
    b0_lr_metrics = compute_classification_metrics(y_test, b0_lr_preds)
    b0_lr_metrics["avg_latency_ms"] = test_latency_b0_ms
    logger.info(f"B0-LR TEST Results: Acc={b0_lr_metrics['accuracy']:.4f}, Macro-F1={b0_lr_metrics['macro_f1']:.4f}, Supp-F1={b0_lr_metrics['supported_f1']:.4f}, FSR={b0_lr_metrics['false_support_rate']:.4f}")

    # B2: Bidirectional 6D features [F, R]
    X_train_6d_all = np.hstack([train_f_all, train_r_all])
    X_test_6d_all = np.hstack([test_f_all, test_r_all])

    clf_b2 = FusionClassifier()
    clf_b2.fit(X_train_6d_all, y_train)
    b2_preds = clf_b2.predict(X_test_6d_all)
    b2_metrics = compute_classification_metrics(y_test, b2_preds)
    b2_metrics["avg_latency_ms"] = test_latency_b2_ms
    logger.info(f"B2 TEST Results: Acc={b2_metrics['accuracy']:.4f}, Macro-F1={b2_metrics['macro_f1']:.4f}, Supp-F1={b2_metrics['supported_f1']:.4f}, FSR={b2_metrics['false_support_rate']:.4f}")

    # ----------------------------------------------------
    # PHASE 4: B3 — SEMANTIC FILTER -> BIDIRECTIONAL NLI
    # ----------------------------------------------------
    logger.info("\n--- PHASE 4: B3 Semantic Filter -> Bidirectional NLI ---")
    train_f_filt, _ = get_forward_nli_filtered(nli_runner, train_examples, train_filt_units, "train", tau_str)
    train_r_filt, _ = get_reverse_nli_filtered(nli_runner, train_examples, train_filt_units, "train", tau_str)
    dev_r_filt, _ = get_reverse_nli_filtered(nli_runner, dev_examples, dev_filt_units, "dev", tau_str)

    t_start_test = time.time()
    test_r_filt, _ = get_reverse_nli_filtered(nli_runner, test_examples, test_filt_units, "test", tau_str)
    test_latency_b3_ms = test_latency_b1_ms + (((time.time() - t_start_test) / len(test_examples)) * 1000.0)

    X_train_6d_filt = np.hstack([train_f_filt, train_r_filt])
    X_dev_6d_filt = np.hstack([dev_f_filt, dev_r_filt])
    X_test_6d_filt = np.hstack([test_f_filt, test_r_filt])

    clf_b3 = FusionClassifier()
    clf_b3.fit(X_train_6d_filt, y_train)

    b3_preds = clf_b3.predict(X_test_6d_filt)
    b3_metrics = compute_classification_metrics(y_test, b3_preds)
    b3_metrics["avg_latency_ms"] = test_latency_b3_ms
    logger.info(f"B3 TEST Results: Acc={b3_metrics['accuracy']:.4f}, Macro-F1={b3_metrics['macro_f1']:.4f}, Supp-F1={b3_metrics['supported_f1']:.4f}, FSR={b3_metrics['false_support_rate']:.4f}")

    # ----------------------------------------------------
    # PHASE 5: B4 — B3 + CALIBRATION + ABSTENTION
    # ----------------------------------------------------
    logger.info("\n--- PHASE 5: B4 Calibration & Calibrated Abstention ---")
    dev_logits_b3 = clf_b3.decision_function(X_dev_6d_filt)
    test_logits_b3 = clf_b3.decision_function(X_test_6d_filt)

    scaler = TemperatureScaler()
    scaler.fit(dev_logits_b3, y_dev)
    logger.info(f"Fitted Temperature Scaling on DEV: Temperature={scaler.temperature:.4f}")

    p_dev_cal = scaler.predict_proba(dev_logits_b3)[:, 1]
    p_test_cal = scaler.predict_proba(test_logits_b3)[:, 1]

    # Select T_low and T_high on DEV
    t_low, t_high, dev_abstain_stats = select_abstention_thresholds(
        p_dev_cal, y_dev, target_risk=0.05
    )
    logger.info(f"Selected Abstention Thresholds on DEV: T_low={t_low:.4f}, T_high={t_high:.4f}")
    logger.info(f"DEV Abstention Stats: Coverage={dev_abstain_stats.get('coverage', 0):.4f}, Risk={dev_abstain_stats.get('selective_risk', 0):.4f}, FSR={dev_abstain_stats.get('false_support_rate', 0):.4f}")

    # Evaluate B4 on TEST
    b4_test_res = evaluate_selective_prediction(p_test_cal, y_test, t_low, t_high)
    logger.info(f"B4 TEST Results: Coverage={b4_test_res['coverage']:.4f}, Selective Acc={b4_test_res['selective_accuracy']:.4f}, Selective Risk={b4_test_res['selective_risk']:.4f}, Retained FSR={b4_test_res['false_support_rate']:.4f}")

    # Risk-coverage curve & AURC on TEST
    rc_curve_points, aurc = compute_risk_coverage_curve(p_test_cal, y_test)
    logger.info(f"TEST AURC (Area Under Risk-Coverage curve): {aurc:.4f}")

    # ----------------------------------------------------
    # BOOTSTRAP 95% CONFIDENCE INTERVALS
    # ----------------------------------------------------
    logger.info("\nComputing Bootstrap 95% Confidence Intervals for TEST results...")
    
    ci_results = {}
    methods = [
        ("B0", y_test, b0_test_preds),
        ("B0-LR", y_test, b0_lr_preds),
        ("B1", y_test, b1_test_preds),
        ("B2", y_test, b2_preds),
        ("B3", y_test, b3_preds),
    ]

    for name, yt, yp in methods:
        ci_macro_f1 = compute_bootstrap_ci(yt, yp, lambda y1, y2: f1_score(y1, y2, average="macro", zero_division=0))
        ci_supp_f1 = compute_bootstrap_ci(yt, yp, lambda y1, y2: f1_score(y1, y2, pos_label=1, zero_division=0))
        ci_fsr = compute_bootstrap_ci(yt, yp, lambda y1, y2: float(np.sum((y2 == 1) & (y1 == 0)) / max(1, np.sum(y1 == 0))))
        ci_results[name] = {
            "macro_f1_ci": ci_macro_f1,
            "supp_f1_ci": ci_supp_f1,
            "fsr_ci": ci_fsr,
        }

    # ----------------------------------------------------
    # COMPILE FINAL TABLES & SAVE OUTPUTS
    # ----------------------------------------------------
    logger.info("\nCompiling Final Results and Saving CSV/JSON artifacts...")

    results_table = [
        {
            "method": "B0",
            "accuracy": b0_metrics["accuracy"],
            "macro_f1": b0_metrics["macro_f1"],
            "supported_precision": b0_metrics["supported_precision"],
            "supported_recall": b0_metrics["supported_recall"],
            "supported_f1": b0_metrics["supported_f1"],
            "false_support_rate": b0_metrics["false_support_rate"],
            "coverage": 1.0,
            "avg_latency_ms": b0_metrics["avg_latency_ms"],
        },
        {
            "method": "B0-LR",
            "accuracy": b0_lr_metrics["accuracy"],
            "macro_f1": b0_lr_metrics["macro_f1"],
            "supported_precision": b0_lr_metrics["supported_precision"],
            "supported_recall": b0_lr_metrics["supported_recall"],
            "supported_f1": b0_lr_metrics["supported_f1"],
            "false_support_rate": b0_lr_metrics["false_support_rate"],
            "coverage": 1.0,
            "avg_latency_ms": b0_lr_metrics["avg_latency_ms"],
        },
        {
            "method": "B1",
            "accuracy": b1_metrics["accuracy"],
            "macro_f1": b1_metrics["macro_f1"],
            "supported_precision": b1_metrics["supported_precision"],
            "supported_recall": b1_metrics["supported_recall"],
            "supported_f1": b1_metrics["supported_f1"],
            "false_support_rate": b1_metrics["false_support_rate"],
            "coverage": 1.0,
            "avg_latency_ms": b1_metrics["avg_latency_ms"],
        },
        {
            "method": "B2",
            "accuracy": b2_metrics["accuracy"],
            "macro_f1": b2_metrics["macro_f1"],
            "supported_precision": b2_metrics["supported_precision"],
            "supported_recall": b2_metrics["supported_recall"],
            "supported_f1": b2_metrics["supported_f1"],
            "false_support_rate": b2_metrics["false_support_rate"],
            "coverage": 1.0,
            "avg_latency_ms": b2_metrics["avg_latency_ms"],
        },
        {
            "method": "B3",
            "accuracy": b3_metrics["accuracy"],
            "macro_f1": b3_metrics["macro_f1"],
            "supported_precision": b3_metrics["supported_precision"],
            "supported_recall": b3_metrics["supported_recall"],
            "supported_f1": b3_metrics["supported_f1"],
            "false_support_rate": b3_metrics["false_support_rate"],
            "coverage": 1.0,
            "avg_latency_ms": b3_metrics["avg_latency_ms"],
        },
        {
            "method": "B4",
            "accuracy": b4_test_res["selective_accuracy"],
            "macro_f1": np.nan,
            "supported_precision": np.nan,
            "supported_recall": np.nan,
            "supported_f1": np.nan,
            "false_support_rate": b4_test_res["false_support_rate"],
            "coverage": b4_test_res["coverage"],
            "avg_latency_ms": b3_metrics["avg_latency_ms"],
        },
    ]

    df_results = pd.DataFrame(results_table)
    save_csv(results_table, OUTPUTS_DIR / "wice_results.csv")

    # Semantic filtering table
    semantic_table = [
        {
            "method": "B1",
            "evidence_precision": test_retrieval_metrics["evidence_precision"],
            "evidence_recall": test_retrieval_metrics["evidence_recall"],
            "evidence_f1": test_retrieval_metrics["evidence_f1"],
            "avg_units_before": units_before,
            "avg_units_after": units_after,
            "pct_units_removed": pct_removed,
        },
        {
            "method": "B3",
            "evidence_precision": test_retrieval_metrics["evidence_precision"],
            "evidence_recall": test_retrieval_metrics["evidence_recall"],
            "evidence_f1": test_retrieval_metrics["evidence_f1"],
            "avg_units_before": units_before,
            "avg_units_after": units_after,
            "pct_units_removed": pct_removed,
        },
    ]
    df_semantic = pd.DataFrame(semantic_table)
    save_csv(semantic_table, OUTPUTS_DIR / "wice_semantic_filtering.csv")

    # Predictions CSV
    predictions_rows = []
    for idx, ex in enumerate(test_examples):
        predictions_rows.append({
            "example_id": ex.example_id,
            "claim_id": ex.claim_id,
            "claim": ex.claim,
            "gold_label_3class": ex.gold_label_3class,
            "gold_label_binary": ex.gold_label_binary,
            "pred_B0": int(b0_test_preds[idx]),
            "score_B0": float(test_f_all[idx, 0]),
            "pred_B0_LR": int(b0_lr_preds[idx]),
            "pred_B1": int(b1_test_preds[idx]),
            "score_B1": float(test_f_filt[idx, 0]),
            "pred_B2": int(b2_preds[idx]),
            "pred_B3": int(b3_preds[idx]),
            "calibrated_prob_B4": float(p_test_cal[idx]),
            "pred_B4": int(b4_test_res["predictions"][idx]),
        })
    save_csv(predictions_rows, OUTPUTS_DIR / "wice_predictions.csv")

    # Save Thresholds JSON
    thresholds_data = {
        "b0_threshold": b0_theta,
        "b1_support_threshold": b1_theta,
        "semantic_similarity_threshold_tau": best_tau,
        "b4_t_low": t_low,
        "b4_t_high": t_high,
    }
    save_json(thresholds_data, OUTPUTS_DIR / "wice_thresholds.json")

    # Save Calibration JSON
    calibration_data = {
        "temperature": scaler.temperature,
        "t_low": t_low,
        "t_high": t_high,
        "dev_stats": dev_abstain_stats,
        "test_selective_accuracy": b4_test_res["selective_accuracy"],
        "test_selective_risk": b4_test_res["selective_risk"],
        "test_coverage": b4_test_res["coverage"],
        "test_retained_fsr": b4_test_res["false_support_rate"],
        "aurc": aurc,
    }
    save_json(calibration_data, OUTPUTS_DIR / "wice_calibration.json")

    # Save risk coverage curve
    save_csv(rc_curve_points, OUTPUTS_DIR / "wice_risk_coverage.csv")

    # Save trained models for AttributionBench transfer
    import joblib
    models_dir = OUTPUTS_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf_b3, models_dir / "b3_classifier.joblib")
    joblib.dump(scaler, models_dir / "b4_scaler.joblib")

    # Print Final Markdown Tables
    print("\n" + "=" * 60)
    print("FINAL WICE TEST EVALUATION SUMMARY TABLE")
    print("=" * 60)
    print_markdown_table(df_results, "Primary Binary Verification Performance on WiCE Test")
    print_markdown_table(df_semantic, "Semantic Evidence Filtering Performance on WiCE Test")

    logger.info("WiCE experiment completed successfully!")

if __name__ == "__main__":
    main()
