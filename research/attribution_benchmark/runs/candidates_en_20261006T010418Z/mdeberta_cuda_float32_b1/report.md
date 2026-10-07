# AttributionBench candidate evaluation

Model: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` @ `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`.
Completed 2026-10-06T01:12:27.927227+00:00; original English dev/ID/OOD, no fine-tuning or translation.
Device `cuda`, precision `torch.float32`, batch 1; parameters 278,811,651.

## Protocol

Original-order cited references are concatenated with two newlines. The original claim is kept intact.
Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.
Adapter: `nli`. Class scores: `native_classification_logits`.
Class order: `('entailment', 'neutral', 'contradiction')`; attributable/support index 0.
Primary threshold 0.15, selected solely on 1,198 English dev rows before test inference.
Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.
Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.

## Primary results

All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.

| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| test | 1610 | 64.36 | [61.16, 67.18] | 62.73 | 62.92 | 44.22 | 29.94 | 324 |
| test_ood | 1686 | 69.87 | [66.70, 72.70] | 70.02 | 70.76 | 44.96 | 13.52 | 160 |

False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.

## Per-source results

| Split | Source | Units | Macro-F1 | False acceptance | False warning |
|---|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 77.18 | 32.17 | 13.04 |
| test | ExpertQA | 612 | 54.03 | 52.61 | 38.89 |
| test | LFQA | 168 | 59.15 | 50.00 | 30.95 |
| test | Stanford-GenSearch | 600 | 67.05 | 38.67 | 27.00 |
| test_ood | AttrScore-GenSearch | 162 | 69.56 | 22.22 | 38.27 |
| test_ood | BEGIN | 436 | 70.46 | 50.92 | 5.05 |
| test_ood | HAGRID | 1088 | 69.59 | 45.96 | 13.24 |

## Class metrics

| Split | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 65.07 | 55.78 | 60.07 | 805 |
| test | attributable | 61.30 | 70.06 | 65.39 | 805 |

test confusion [not attributable, attributable]: `[[449, 356], [241, 564]]`.
test not-attributable AUROC 0.6856; AP 0.6534.
| test_ood | not attributable | 80.28 | 55.04 | 65.31 | 843 |
| test_ood | attributable | 65.79 | 86.48 | 74.73 | 843 |

test_ood confusion [not attributable, attributable]: `[[464, 379], [114, 729]]`.
test_ood not-attributable AUROC 0.7836; AP 0.7708.

## Execution

Valid scored rows 4494/4494; failures 0.
Runner wall time 290.58s; model loading 5.16s.
Batch p50/p95 seconds `[0.05325890000676736, 0.10599915500206407]`; batch size 1.
CUDA peak allocated/reserved bytes `{'cuda_peak_allocated_bytes': 1231943168, 'cuda_peak_reserved_bytes': 1293942784, 'cuda_total_bytes': 4294705152}`; excludes other GPU processes and driver overhead.
First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.
Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.
Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.
These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model mdeberta --device cuda --precision float32 --batch-size 1 --output 'F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\mdeberta_cuda_float32_b1'
```
