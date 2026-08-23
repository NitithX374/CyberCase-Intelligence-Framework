# SEvenLLM B0/B1/B2 representation comparison

This isolated experiment compares only the representation supplied to one fixed downstream analysis model on the exact 28 English generation cases inherited from Pilot-1: Threat Analysis (15), Summary Generation (7), and Impact Scope (6).

| Condition | Analysis input |
|---|---|
| B0 | Raw SEvenLLM narrative |
| B1 | Canonical `CaseState` JSON produced by the existing production extraction path |
| B2 | Deterministically serialized source-grounded GLiNER2 atomic events |

All conditions use `research.sevenllm_preflight.protocol.build_b0_prompt`, OpenRouter `meta-llama/llama-3.1-8b-instruct`, temperature 0, top-p 1, max 512 output tokens, English, and seed 42. Only the context changes. The `thought` field is never read.

## Reuse and boundaries

B1 directly calls `backend/app/services/extraction/extraction_runner.py::run_baseline_extraction` and serializes its validated canonical `CaseState`. It does not use the workflow/DB wrapper. B2 uses `fastino/gliner2-base-v1` with the fields actor, action, object, target, tool, time, location, and result. Values without an exact source span are omitted and recorded as rejected.

The production `MainCaseAnalysisService` was inspected but is not called because its two production tasks and `AnalysisTrace` membership contract are not compatible with these three frozen SEvenLLM tasks. Reusing the Pilot-1 prompt/client keeps the downstream analysis path identical across B0/B1/B2. No production source, database, UI, RAG, or follow-up path is modified.

## Install and run

Use Python 3.12 in an isolated environment:

```powershell
python -m venv .venv-representation
.\.venv-representation\Scripts\python -m pip install -r experiments\representation_analysis\requirements.txt
$env:OPENROUTER_API_KEY = "..."
$env:OPENROUTER_CYBERCASE = "..."
.\.venv-representation\Scripts\python -m experiments.representation_analysis --output-dir D:\persistent\sevenllm-representation
```

`OPENROUTER_CYBERCASE` is consumed by the existing production B1 extractor; `OPENROUTER_API_KEY` is consumed by the fixed downstream Pilot-1 client. They may contain the same credential. The command performs paid/model inference and was intentionally not run during implementation.

CPU is supported. CUDA is optional via `--gliner-device cuda --sbert-device cuda`. GLiNER2 is approximately 205M F32 parameters, so raw weights are about 0.82 GB; allow roughly 1–2 GB RAM/VRAM as an operational estimate. Set `HF_HOME` to a persistent mounted path if model-cache persistence is required.

Every extraction and analysis record is append-flushed with `fsync`. Rerunning the identical command resumes from `b0_analysis.jsonl`, `b1_extractions.jsonl`, `b1_analysis.jsonl`, `b2_extractions.jsonl`, and `b2_analysis.jsonl`. An existing B0 cache is reused only when sample ID, prompt, model, generation config, and success state match exactly. `run_config.json` prevents an output directory from being reused with a different contract.

Final outputs are `detailed_results.jsonl`, `evaluation_summary.json`, `report.md`, `run_config.json`, and `dataset_manifest.json`. The report includes overall/per-task metrics, pairwise deltas, representation sizes, retention diagnostics, and selected failure examples. Benchmark scores are descriptive only and select no checkpoint, prompt, or hyperparameter.

## B3 augmentation experiment

B3 preserves the complete raw narrative and appends the frozen source-grounded GLiNER2 event serialization. It reuses completed B0 and B2 artifacts and runs only the 28 new downstream analysis calls:

```powershell
$env:OPENROUTER_API_KEY = "..."
.\.venv-representation\Scripts\python -m experiments.representation_analysis.b3 --sbert-device cuda
```

Its independent resumable outputs are stored under `outputs/pilot_28_b3/` by default. The fixed context layout is `Raw narrative`, followed by `Source-grounded atomic events`; an empty extraction receives an explicit empty marker and no generated replacement content.
