# SEvenLLM context refinement experiment

This is an isolated pre-LLM context-refinement ablation. It does not import the production CyberCase request path, change `backend/`, change `rag_service/`, run MITRE retrieval, run extraction, or fine-tune a model.

## Fixed protocol

- Conditions: B0 raw context and B1 generic refined context.
- Tasks: Threat Analysis, Summary Generation, and Impact Scope.
- Language: English.
- Dataset: the existing SEvenLLM fixed Pilot-1 50-case selection, filtered to the requested tasks. The current frozen split yields 28 cases: 15 Threat Analysis, 7 Summary Generation, and 6 Impact Scope.
- Prompt: the existing `research.sevenllm_preflight.protocol.build_b0_prompt` template. The only allowed prompt difference is the context string.
- LLM: the existing SEvenLLM pilot OpenRouter runner, `meta-llama/llama-3.1-8b-instruct`, with temperature 0, top-p 1, and max tokens 512.
- Refiner: `microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank`, generic task-agnostic LLMLingua-2, default compression rate 1.5.
- Protected spans are measured after compression only. They are not forced into the compressor in this experiment.
- Evaluation: existing SEvenLLM ROUGE-L implementation plus existing sentence-level SBERT scoring. No LLM judge is added because the existing pilot scorer does not use one; this keeps the paired comparison deterministic and avoids a third model.

The compressor model and API are documented by Microsoft at [LLMLingua](https://github.com/microsoft/LLMLingua) and on the [model card](https://huggingface.co/microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank).

## Environment

Install these dependencies into an isolated environment. Do not add them to a production image:

```powershell
python -m pip install -r experiments/context_refinement/requirements.txt
```

The first refined run downloads the compressor model and the first SBERT evaluation downloads the requested SBERT model unless both are already present in the mounted Hugging Face cache.

## Paired run

Supply a persistent output directory on Vast.ai or another mounted volume:

```powershell
$env:HF_HOME = "/workspace/persistent/hf-cache"
$env:OPENROUTER_API_KEY = "..."
python -m experiments.context_refinement run `
  --benchmark tmp/sevenllm_b2_test_all.jsonl `
  --selection research/sevenllm_preflight/results/pilot_1_en/pilot_1_en_50_selection.json `
  --output-dir /workspace/persistent/context-refinement `
  --condition both `
  --sbert-model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The command writes incrementally:

- `raw_contexts.jsonl` and `refined_contexts.jsonl`;
- `predictions.jsonl`, keyed by `(sample_id, condition)` for idempotent resume;
- `dataset_manifest.json` and `run_config.json`;
- `paired_results.jsonl`, `evaluation_summary.json`, and `report.md` after both conditions finish.

Rerun the exact command to resume. Existing records are validated against the exact dataset, prompt, model, generation, and compressor contracts. A mismatch fails instead of silently mixing runs.

Run only one condition when needed:

```powershell
python -m experiments.context_refinement run --condition raw --output-dir /workspace/persistent/context-refinement-raw
python -m experiments.context_refinement run --condition refined --output-dir /workspace/persistent/context-refinement-refined --sbert-model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Rebuild the paired artifacts after both prediction stores are complete:

```powershell
python -m experiments.context_refinement report `
  --benchmark tmp/sevenllm_b2_test_all.jsonl `
  --selection research/sevenllm_preflight/results/pilot_1_en/pilot_1_en_50_selection.json `
  --output-dir /workspace/persistent/context-refinement `
  --sbert-model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## Fairness and interpretation

The fixed 50 selection is evaluation-only. No training, prompt tuning, checkpoint selection, or hyperparameter selection is performed here. Both conditions use the same row, instruction, prompt template, general-purpose LLM, generation parameters, output limit, and metric implementation. Only the context string changes.

The report is descriptive. It does not claim that refinement improves quality unless the paired command has actually completed and the resulting artifacts are inspected.
