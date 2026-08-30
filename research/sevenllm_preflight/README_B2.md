# SEvenLLM B2 training

B2 fine-tunes `google/mt5-base` on the English-only subset of `SEVENLLM-Instruct/train.jsonl` for the six approved categories. The constructed source is exactly:

```text
task: <category>
instruction: <instruction>
context: <input>
```

The target is `output` only. The source field `thought` is ignored and is never copied into the training split. The complete `SEvenLLM-Bench` file is test-only. The fixed 50 IDs from Pilot-1 are frozen in `b2_config.py` and are checked against both source IDs and prompt/content fingerprints.

## Data preparation

Keep the downloaded datasets outside the repository or under an ignored persistent data mount:

```bash
hf download Multilingual-Multimodal-NLP/SEVENLLM-Dataset train.jsonl \
  --repo-type dataset --local-dir /workspace/sevenllm-data
curl -L https://raw.githubusercontent.com/CSJianYang/SEevenLLM/a84b86aabf2b5be35a2cbbac546511883cc5ff85/code/score/f1_rougel/test_all.jsonl \
  -o /workspace/sevenllm-data/test_all.jsonl
```

## Required preflight

```bash
python -m research.sevenllm_preflight.b2_preflight \
  --instruct-dataset /workspace/sevenllm-data/train.jsonl \
  --benchmark /workspace/sevenllm-data/test_all.jsonl \
  --output-dir /workspace/b2-preflight \
  --tokenizer-path /workspace/hf-cache/models--google--mt5-base/snapshots/<revision>
```

The preflight writes `b2_dataset_manifest.json`, `b2_train.jsonl`, and `b2_validation.jsonl`. It reports filtered counts, category counts, deterministic train/validation counts, input/target p50/p95/max, over-limit samples, and separate full-benchmark and fixed-50 leakage results. Training refuses a missing or non-PASS manifest and verifies the split hashes before loading model weights.

If the tokenizer is not already mounted locally, omit `--tokenizer-path` and pass `--model-revision` if a different pinned tokenizer revision is intentionally being used.

## Vast.ai training

Use a persistent mount for both the model cache and run output. The first run is one epoch with the fixed B2 settings: learning rate `2e-5`, AdamW, `warmup_ratio=0.03`, cosine scheduling, gradient checkpointing, deterministic seed `42`, and automatic bf16/fp16 selection when CUDA supports it.

```bash
python -m research.sevenllm_preflight.train_b2 \
  --preflight-manifest /workspace/b2-preflight/b2_dataset_manifest.json \
  --output-dir /workspace/persistent/b2-run \
  --cache-dir /workspace/persistent/hf-cache
```

Resume a stopped run from an explicit checkpoint or the highest numbered checkpoint in the persistent output directory:

```bash
python -m research.sevenllm_preflight.train_b2 \
  --preflight-manifest /workspace/b2-preflight/b2_dataset_manifest.json \
  --output-dir /workspace/persistent/b2-run \
  --cache-dir /workspace/persistent/hf-cache \
  --resume-latest
```

The run writes `final_model/`, `b2_training_config.json`, `b2_training_metrics.json`, `b2_dataset_manifest.json`, `trainer_state.json`, and resumable `checkpoint-*` directories. No benchmark score is read by the trainer and no best-checkpoint selection is performed.

## Fixed benchmark evaluation

Evaluation is a separate command and accepts only a supplied checkpoint/model path:

```bash
python -m research.sevenllm_preflight.evaluate_b2_benchmark \
  --model-path /workspace/persistent/b2-run/final_model \
  --benchmark /workspace/sevenllm-data/test_all.jsonl \
  --output-dir /workspace/persistent/b2-evaluation
```

It generates raw predictions and primary SEvenLLM-compatible ROUGE-L, exact-choice, and flattened extraction metrics for the fixed 50 cases. The evaluator records that checkpoint selection was not performed.
