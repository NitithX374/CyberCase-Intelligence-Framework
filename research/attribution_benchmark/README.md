# AttributionBench local baseline

The user's 2026-10-06 request selects a first local multilingual NLI measurement on original English AttributionBench. This isolated research runner uses existing `env_mitre` dependencies and cached model weights. It does not call the CyberCase application or external model APIs.

## Fixed protocol

- Dataset: `osunlp/AttributionBench`, `subset_balanced`, revision `62569e644f4186606f54f742178a4517431b42e1`.
- Download all four official raw JSONL files; preserve fields/rows and verify published counts. No train inference or training in this baseline.
- Model: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`, cached revision `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`, fp32.
- Premise: original cited references joined with two newlines. Hypothesis: original `claim`.
- Max input 512 tokens; `only_first` truncates evidence from the right and preserves the claim. Fail explicitly if a complete claim cannot fit; no automatic alternative context policy.
- Select p(entailment) threshold only on English dev, maximizing the unweighted mean of source-subset Macro-F1. Grid 0.01 through 0.99, step 0.01; ties closest to 0.5 then lower threshold. Freeze the selection before test inference.
- Primary results: per-source Macro-F1, ID mean and OOD mean. Pooled scores, per-class precision/recall/F1, confusion counts, false acceptance/warning rates and AUROC/AP are saved separately.
- Confidence intervals: 2,000 bootstrap replicates, seed 20261006, resampling question+response clusters within source subsets. This captures test-sample uncertainty, not model training variability.
- Empty cited-reference bundles remain in the benchmark; no labels or failed units are silently removed.
- NLI argmax mapping is a descriptive reference from identical logits; neutral/contradiction map to not attributable. No test-selected decision rule or extra model inference.

## Run from repository root

```powershell
$env:PYTHONUTF8 = '1'
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/data.py'
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run.py' --device cuda --batch-size 2
```

Each run creates a new UTC-stamped directory under `runs/`, preserving previous results. `run_manifest.json` records model/data/source hashes, runtime versions and input-length diagnostics; `source_snapshot/` preserves the exact four execution modules. `selection.json` records English-dev threshold choice before test inference. Scores are saved per original row in JSONL, and `summary.json`/`report.md` contain the recomputable evaluation.

`verify.py <run-directory>` independently recomputes metrics and dev threshold selection from saved raw scores, checks every row against original dataset text/labels, and validates recorded hashes/probabilities. It writes `verification.json` only after all checks pass; it does not run model inference.

Dataset/raw-score JSONL and progress logs are ignored by Git to avoid accidentally publishing large downloaded artifacts. The data manifest, code and compact result reports remain reviewable.

Local execution failure stops the run with a nonzero exit and `failure.json`; it does not emit a successful benchmark report or replace a failure with a semantic verdict. Only a complete run has `status: complete` in its manifest.

Scores measure this checkpoint and visible-evidence policy. They do not establish Thai-language transfer, native case-domain accuracy, source truth or downstream report improvement.

Sources: [AttributionBench dataset](https://huggingface.co/datasets/osunlp/AttributionBench), [official code](https://github.com/OSU-NLP-Group/AttributionBench), [paper](https://aclanthology.org/2024.findings-acl.886.pdf), [model card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7).

## Candidate checkpoint comparison

The candidate suite adds DeBERTa-small, multilingual MiniLMv2-L6, MiniCheck-DeBERTa-v3-Large, XLM-R-large-XNLI and AttrScore-FLAN-T5-Large. The existing mDeBERTa baseline is also rerun at batch size 1. Model identities, revisions, label order and support mapping are pinned in `candidate_models.py`.

All candidates receive the original English claim and cited reference bundle from the same official dev/ID/OOD splits. Claims remain intact; evidence is truncated from the right under a 512-token input cap. MiniCheck runs its binary head directly without its native evidence chunk aggregation. AttrScore uses the author's attribution instruction and complete three-label sequence likelihoods including EOS, normalized across labels without length normalization. It is a constrained label scorer, not greedy generation; prompt tokens reduce its evidence budget.

`run_candidate.py` evaluates one explicit checkpoint/device/precision/batch configuration in a new output directory, selects its threshold on EN dev, freezes that choice before testing and saves raw class scores, actual input token IDs, source snapshots, resource peaks and all metrics. Errors produce a failed-attempt artifact and a nonzero exit; device and precision do not change automatically. `verify_candidate.py` independently checks every original input, tokenization, probabilities, class mapping and sklearn metrics.

```powershell
$env:PYTHONUTF8='1'
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model minilm --device cuda --precision float32 --batch-size 1 --output 'research/attribution_benchmark/runs/my_minilm_run'
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/verify_candidate.py' 'research/attribution_benchmark/runs/my_minilm_run'
```

`run_candidates.py` executes a declared suite sequentially; `compare_candidates.py` creates the comparison and paired cluster-bootstrap differences from the matched mDeBERTa run. The suite manifest and per-model reports retain commands and receipts. Test rankings are descriptive. These runs establish English checkpoint performance under their recorded input adapters, not Thai case-domain transfer or a causal training-objective effect.

Completed 2026-10-06: [six-model comparison](runs/candidates_en_20261006T010418Z/comparison.md). All six independently verified 4,494 rows each on GTX 1650, CUDA float32, batch 1. Original MiniLM cache and XLM-R logging failures are retained alongside successful explicit retries. Per-model reports include class errors, input loss, confidence intervals and resource measurements.

Sources: [MiniCheck](https://huggingface.co/lytang/MiniCheck-DeBERTa-v3-Large), [AttrScore](https://github.com/OSU-NLP-Group/AttrScore), [XLM-R XNLI](https://huggingface.co/joeddav/xlm-roberta-large-xnli), [multilingual MiniLM](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli), [DeBERTa-small NLI](https://huggingface.co/cross-encoder/nli-deberta-v3-small).
