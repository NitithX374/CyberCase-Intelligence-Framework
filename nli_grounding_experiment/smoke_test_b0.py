import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import set_seed
from src.datasets.wice import load_wice_split
from src.nli import NLIRunner
from src.metrics import compute_classification_metrics

set_seed(42)

def run_smoke_test():
    print("Loading WiCE dev split (5 examples)...")
    dev_examples = load_wice_split("dev")[:5]
    print(f"Loaded {len(dev_examples)} examples.")

    runner = NLIRunner()
    
    premises = ["\n".join(ex.evidence_units) for ex in dev_examples]
    hypotheses = [ex.claim for ex in dev_examples]
    y_true = [ex.gold_label_binary for ex in dev_examples]

    probs, meta = runner.predict_probs(premises, hypotheses, batch_size=2)
    print("\nInference Results:")
    for i, ex in enumerate(dev_examples):
        print(f"Example {i+1}: ID={ex.example_id}, Gold={ex.gold_label_binary} ({ex.gold_label_3class})")
        print(f"  P(entail)={probs[i, 0]:.4f}, P(neutral)={probs[i, 1]:.4f}, P(contra)={probs[i, 2]:.4f}")
        print(f"  Tokens={meta[i]['num_tokens']}, Truncated={meta[i]['truncated']}")

    # Check metrics
    preds = (probs[:, 0] >= 0.5).astype(int)
    metrics = compute_classification_metrics(y_true, preds)
    print(f"\nSmoke Test Metrics: Acc={metrics['accuracy']:.4f}, Macro-F1={metrics['macro_f1']:.4f}")
    print("Smoke test completed successfully!")

if __name__ == "__main__":
    run_smoke_test()
