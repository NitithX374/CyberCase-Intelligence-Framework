import logging
import time
from pathlib import Path
import numpy as np
import pandas as pd
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score

from config import (
    OUTPUTS_DIR,
    SEED,
    set_seed,
    FORWARD_NLI_CACHE_DIR,
)
from src.nli import NLIRunner
from src.utils import save_csv, print_markdown_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def evaluate_xnli_language(runner: NLIRunner, lang: str, split: str = "test", max_samples: int | None = 1000):
    logger.info(f"Loading XNLI for language: {lang} (split: {split})...")
    ds = load_dataset("xnli", lang, split=split)
    
    if max_samples is not None and len(ds) > max_samples:
        ds = ds.select(range(max_samples))
        
    logger.info(f"Evaluating {len(ds)} samples for language: {lang}")
    
    premises = [ex["premise"] for ex in ds]
    hypotheses = [ex["hypothesis"] for ex in ds]
    y_true = np.array([ex["label"] for ex in ds])
    
    t0 = time.time()
    probs, meta = runner.predict_probs(premises, hypotheses, batch_size=16)
    elapsed = time.time() - t0
    
    preds = np.argmax(probs, axis=1)
    
    acc = accuracy_score(y_true, preds)
    macro_f1 = f1_score(y_true, preds, average="macro")
    # Entailment is label 0
    entail_f1 = f1_score(y_true, preds, labels=[0], average=None)[0]
    
    logger.info(f"XNLI [{lang.upper()}] Results: Accuracy={acc:.4f}, Macro-F1={macro_f1:.4f}, Entailment-F1={entail_f1:.4f} (Elapsed={elapsed:.1f}s)")
    
    return {
        "language": lang,
        "split": split,
        "num_samples": len(ds),
        "accuracy": acc,
        "macro_f1": macro_f1,
        "entailment_f1": entail_f1,
        "avg_latency_ms": (elapsed / len(ds)) * 1000.0,
    }

def main():
    set_seed(SEED)
    logger.info("==================================================")
    logger.info("STARTING XNLI MULTILINGUAL SANITY TEST (EN vs TH)")
    logger.info("==================================================")
    
    runner = NLIRunner()
    
    results = []
    # Test on standard test split (1000 sample subset for fast sanity check)
    res_en = evaluate_xnli_language(runner, "en", split="test", max_samples=1000)
    results.append(res_en)
    
    res_th = evaluate_xnli_language(runner, "th", split="test", max_samples=1000)
    results.append(res_th)
    
    df = pd.DataFrame(results)
    save_csv(results, OUTPUTS_DIR / "xnli_results.csv")
    
    print("\n" + "=" * 60)
    print("XNLI MULTILINGUAL SANITY TEST SUMMARY TABLE")
    print("=" * 60)
    print_markdown_table(df, "XNLI English vs Thai Evaluation (Pretrained mDeBERTa-v3)")

if __name__ == "__main__":
    main()
