import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed, DEVICE
from src.datasets.wice import load_wice_split
from src.nli import NLIRunner
from src.semantic_filter import SemanticFilter

def run_efficiency_audit(champion_name="B1-LR", n_samples=100):
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 8: FINAL EFFICIENCY AUDIT (BATCH SIZE = 1)")
    print(f"Device: {DEVICE} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"Benchmarking: B0 vs original B1-LR vs {champion_name} on {n_samples} WiCE Test claims")
    print("=" * 80)

    test_ex = load_wice_split("test")
    # Deterministic subset of test examples
    np.random.seed(SEED)
    indices = np.random.choice(len(test_ex), size=n_samples, replace=False)
    sample_ex = [test_ex[i] for i in indices]

    # Preload models
    print("Loading models onto GPU...")
    sem_filter = SemanticFilter()
    nli_runner = NLIRunner()
    clf_b1_lr = joblib.load(OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")

    # Warm up GPU
    print("Warming up GPU...")
    warm_ex = sample_ex[0]
    warm_p = "This is a warm-up premise."
    warm_h = "This is a warm-up claim."
    for _ in range(5):
        _ = sem_filter.compute_similarities([warm_ex])
        _ = nli_runner.predict_probs([warm_p], [warm_h], batch_size=1)
        _ = clf_b1_lr.predict(np.array([[0.5, 0.3, 0.2]]))
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    # 1. Benchmark B0 (Full premise -> Forward NLI -> Rule Argmax)
    print("\nBenchmarking B0 (batch size = 1)...")
    b0_nli_times = []
    b0_clf_times = []
    b0_total_times = []
    b0_premise_lens = []

    for ex in sample_ex:
        p = " ".join(ex.evidence_units)
        b0_premise_lens.append(len(p))

        # NLI latency
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        probs, _ = nli_runner.predict_probs([p], [ex.claim], batch_size=1)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t1 = time.perf_counter()

        # Classifier latency (argmax)
        t_c0 = time.perf_counter()
        pred = int(np.argmax(probs[0]) == 0)
        t_c1 = time.perf_counter()

        nli_lat = (t1 - t0) * 1000.0
        clf_lat = (t_c1 - t_c0) * 1000.0
        tot_lat = nli_lat + clf_lat

        b0_nli_times.append(nli_lat)
        b0_clf_times.append(clf_lat)
        b0_total_times.append(tot_lat)

    # 2. Benchmark B1-LR (Semantic Filter tau=0.20 -> Forward NLI -> LR)
    print("Benchmarking B1-LR (batch size = 1)...")
    b1_sem_times = []
    b1_nli_times = []
    b1_clf_times = []
    b1_total_times = []
    b1_premise_lens = []
    b1_retained_counts = []

    for ex in sample_ex:
        # Semantic filtering latency
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_s0 = time.perf_counter()
        sims = sem_filter.compute_similarities([ex])[0]
        kept_units, _ = sem_filter.filter_units(ex.evidence_units, sims, threshold=0.20)
        p = " ".join(kept_units) if kept_units else (ex.evidence_units[int(np.argmax(sims))] if sims else "")
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_s1 = time.perf_counter()

        sem_lat = (t_s1 - t_s0) * 1000.0
        b1_premise_lens.append(len(p))
        b1_retained_counts.append(len(kept_units))

        # NLI latency
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_n0 = time.perf_counter()
        probs, _ = nli_runner.predict_probs([p], [ex.claim], batch_size=1)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_n1 = time.perf_counter()
        nli_lat = (t_n1 - t_n0) * 1000.0

        # Classifier latency (LR)
        t_c0 = time.perf_counter()
        pred = clf_b1_lr.predict(probs)
        t_c1 = time.perf_counter()
        clf_lat = (t_c1 - t_c0) * 1000.0

        tot_lat = sem_lat + nli_lat + clf_lat

        b1_sem_times.append(sem_lat)
        b1_nli_times.append(nli_lat)
        b1_clf_times.append(clf_lat)
        b1_total_times.append(tot_lat)

    def stats(arr):
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "p90": float(np.percentile(arr, 90)),
            "p95": float(np.percentile(arr, 95)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
        }

    audit_data = {
        "device": str(DEVICE),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "batch_size": 1,
        "n_samples": n_samples,
        "B0": {
            "avg_premise_chars": float(np.mean(b0_premise_lens)),
            "semantic_encoder_ms": {"mean": 0.0, "median": 0.0, "p90": 0.0},
            "nli_ms": stats(b0_nli_times),
            "classifier_ms": stats(b0_clf_times),
            "total_ms": stats(b0_total_times),
        },
        "B1-LR": {
            "avg_premise_chars": float(np.mean(b1_premise_lens)),
            "avg_retained_units": float(np.mean(b1_retained_counts)),
            "semantic_encoder_ms": stats(b1_sem_times),
            "nli_ms": stats(b1_nli_times),
            "classifier_ms": stats(b1_clf_times),
            "total_ms": stats(b1_total_times),
        }
    }

    print("\n" + "=" * 80)
    print("STAGE 8 AUDIT SUMMARY (BATCH SIZE = 1):")
    print("=" * 80)
    print(f"B0 (Full Premise, argmax):")
    print(f"  Premise chars:    {audit_data['B0']['avg_premise_chars']:.1f}")
    print(f"  NLI Latency:      mean={audit_data['B0']['nli_ms']['mean']:.2f} ms | median={audit_data['B0']['nli_ms']['median']:.2f} ms | p90={audit_data['B0']['nli_ms']['p90']:.2f} ms")
    print(f"  Total Latency:    mean={audit_data['B0']['total_ms']['mean']:.2f} ms | median={audit_data['B0']['total_ms']['median']:.2f} ms | p90={audit_data['B0']['total_ms']['p90']:.2f} ms")

    print(f"\nB1-LR (Semantic Filter tau=0.20 + LR):")
    print(f"  Retained units:   {audit_data['B1-LR']['avg_retained_units']:.2f}")
    print(f"  Premise chars:    {audit_data['B1-LR']['avg_premise_chars']:.1f} (reduced by {100.0 * (1.0 - audit_data['B1-LR']['avg_premise_chars']/audit_data['B0']['avg_premise_chars']):.1f}%)")
    print(f"  Semantic Filter:  mean={audit_data['B1-LR']['semantic_encoder_ms']['mean']:.2f} ms | median={audit_data['B1-LR']['semantic_encoder_ms']['median']:.2f} ms | p90={audit_data['B1-LR']['semantic_encoder_ms']['p90']:.2f} ms")
    print(f"  NLI Latency:      mean={audit_data['B1-LR']['nli_ms']['mean']:.2f} ms | median={audit_data['B1-LR']['nli_ms']['median']:.2f} ms | p90={audit_data['B1-LR']['nli_ms']['p90']:.2f} ms")
    print(f"  Classifier (LR):  mean={audit_data['B1-LR']['classifier_ms']['mean']:.4f} ms | median={audit_data['B1-LR']['classifier_ms']['median']:.4f} ms")
    print(f"  Total Latency:    mean={audit_data['B1-LR']['total_ms']['mean']:.2f} ms | median={audit_data['B1-LR']['total_ms']['median']:.2f} ms | p90={audit_data['B1-LR']['total_ms']['p90']:.2f} ms")

    out_file = OUTPUTS_DIR / "stage8_efficiency_audit.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nSaved Stage 8 audit to {out_file}")

if __name__ == "__main__":
    run_efficiency_audit()
