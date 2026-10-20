# AttributionBench candidate evaluation

Model: `lytang/MiniCheck-DeBERTa-v3-Large` @ `2f2d01a54fa022a7ffadb76260e1ea8bc88c82bb`.
Completed 2026-10-06T01:25:57.337696+00:00; original English dev/ID/OOD, no fine-tuning or translation.
Device `cuda`, precision `torch.float32`, batch 1; parameters 435,063,810.

## Protocol

Original-order cited references are concatenated with two newlines. The original claim is kept intact.
Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.
Adapter: `support_classifier`. Class scores: `native_classification_logits`.
Class order: `('unsupported', 'supported')`; attributable/support index 1.
Primary threshold 0.22, selected solely on 1,198 English dev rows before test inference.
Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.
Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.

## Primary results

All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.

| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| test | 1610 | 71.80 | [69.12, 74.30] | 68.14 | 68.39 | 22.86 | 40.37 | 281 |
| test_ood | 1686 | 79.36 | [76.36, 82.02] | 78.51 | 78.59 | 27.28 | 15.54 | 86 |

False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.

## Per-source results

| Split | Source | Units | Macro-F1 | False acceptance | False warning |
|---|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 81.30 | 20.00 | 17.39 |
| test | ExpertQA | 612 | 53.49 | 33.01 | 58.50 |
| test | LFQA | 168 | 77.26 | 15.48 | 29.76 |
| test | Stanford-GenSearch | 600 | 75.13 | 15.67 | 33.67 |
| test_ood | AttrScore-GenSearch | 162 | 77.68 | 3.70 | 39.51 |
| test_ood | BEGIN | 436 | 84.28 | 24.31 | 6.88 |
| test_ood | HAGRID | 1088 | 76.12 | 31.99 | 15.44 |

## Class metrics

| Split | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 65.64 | 77.14 | 70.93 | 805 |
| test | attributable | 72.29 | 59.63 | 65.35 | 805 |

test confusion [not attributable, attributable]: `[[621, 184], [325, 480]]`.
test not-attributable AUROC 0.7388; AP 0.7045.
| test_ood | not attributable | 82.39 | 72.72 | 77.25 | 843 |
| test_ood | attributable | 75.58 | 84.46 | 79.78 | 843 |

test_ood confusion [not attributable, attributable]: `[[613, 230], [131, 712]]`.
test_ood not-attributable AUROC 0.8450; AP 0.8465.

## Execution

Valid scored rows 4494/4494; failures 0.
Runner wall time 765.68s; model loading 4.72s.
Batch p50/p95 seconds `[0.13859964997391216, 0.34687533497053663]`; batch size 1.
CUDA peak allocated/reserved bytes `{'cuda_peak_allocated_bytes': 1903982080, 'cuda_peak_reserved_bytes': 1973420032, 'cuda_total_bytes': 4294705152}`; excludes other GPU processes and driver overhead.
First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.
Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.
Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.
These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model minicheck --device cuda --precision float32 --batch-size 1 --output 'F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\minicheck_cuda_float32_b1'
```
