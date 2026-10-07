# AttributionBench: local candidate comparison

Created 2026-10-06T02:02:51.155527+00:00.

All attempted models use the same 1,198 EN dev / 1,610 ID / 1,686 OOD rows, 512-token cap, complete claims and ordered cited references.
No training, Thai translation, application integration or external inference API calls. Downloads are recorded separately.
Primary: unweighted mean source-subset Macro-F1, dev-selected thresholds. Test ordering is descriptive.

| Model | ID Macro-F1 | OOD Macro-F1 | Dev Macro-F1 | Threshold | ID false acceptance | OOD false acceptance | Minutes | Peak allocated GiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [deberta_small](deberta_small_cuda_float32_b1/report.md) | 61.51 | 73.08 | 66.74 | 0.01 | 29.94 | 27.40 | 2.27 | 0.63 |
| [minilm](minilm_cuda_float32_b1_retry_cache/report.md) | 62.19 | 72.31 | 61.13 | 0.27 | 42.73 | 22.89 | 0.98 | 0.41 |
| [mdeberta](mdeberta_cuda_float32_b1/report.md) | 64.36 | 69.87 | 63.78 | 0.15 | 44.22 | 44.96 | 4.84 | 1.15 |
| [minicheck](minicheck_cuda_float32_b1/report.md) | 71.80 | 79.36 | 74.40 | 0.22 | 22.86 | 27.28 | 12.76 | 1.77 |
| [xlmr](xlmr_cuda_float32_b1_retry_logging/report.md) | 65.34 | 75.20 | 67.34 | 0.05 | 32.42 | 27.88 | 8.82 | 2.12 |
| [attrscore](attrscore_cuda_float32_b1/report.md) | 66.22 | 75.70 | 66.88 | 0.23 | 48.57 | 41.16 | 23.96 | 3.13 |

## Paired differences from matched mDeBERTa

Differences and CIs are percentage points. The same cluster resamples are applied to both compared models.

| Model | ID difference [95% CI] | OOD difference [95% CI] |
|---|---|---|
| deberta_small | -2.84 [-6.63, +1.24] | +3.21 [-0.11, +6.43] |
| minilm | -2.17 [-7.22, +2.59] | +2.44 [-0.98, +5.50] |
| mdeberta | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| minicheck | +7.44 [+4.16, +10.84] | +9.49 [+6.54, +12.46] |
| xlmr | +0.98 [-2.49, +4.55] | +5.33 [+2.14, +8.39] |
| attrscore | +1.87 [-2.40, +6.01] | +5.83 [+2.36, +9.19] |

## Interpretation limits

- MiniCheck uses its binary classifier directly; its native evidence-chunk/max wrapper is deliberately absent from this fixed-context comparison.
- AttrScore uses normalized complete label-sequence likelihoods and its author prompt, not greedy generation. Prompt tokens reduce its evidence budget.
- Tokenizers and required input formats differ. A shared 512-token cap is not identical evidence coverage; each report counts truncation and discarded tokens.
- These are checkpoint/adapter comparisons. Different architectures, training corpora and input formats prevent attributing a score change to training objective alone.
- ID/OOD name the official AttributionBench splits. Earlier training-data overlap for each downloaded checkpoint has not been audited.
- Library load diagnostics remain in run.log. XLM-R's two extra pooler tensors are unused by the installed classifier path; the AttrScore loader leaves differing tied-weight values untied.
- Runtime includes loading, input inspection, inference and metrics; download time is excluded. Peak allocated CUDA memory excludes driver/other-process memory.
- DeBERTa-small and mDeBERTa execution partly overlapped checkpoint downloads. Timing is descriptive, not an isolated speed comparison.
- Each row is one frozen execution. Native Thai case-domain generalization and fine-tuning are unmeasured.
- The earlier batch-2 mDeBERTa run is preserved separately; this comparison uses the new matched batch-1 run.

## Earlier attempts

Successful retries preserve the original failures and their execution-source snapshots.

- minilm: IncompleteSnapshotError: The cached snapshot for 'MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli' (revision '0a71e92a985b6e1ad1828cf67ce9c459639c1dca', commit 0a71e92a985b6e1ad1828cf67ce9c459639c1dca) is incomplete: 8 file(s) are missing (.gitattributes, onnx/config.json, onnx/model.onnx, ... (5 more)). Outgoing traffic is disabled ('local_files_only=True'). Re-run the download with network access to complete the snapshot.; `F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\minilm_cuda_float32_b1`.
- xlmr: AttributeError: 'Tee' object has no attribute 'isatty'; `F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\xlmr_cuda_float32_b1`.