# AttributionBench candidate evaluation

Model: `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` @ `0a71e92a985b6e1ad1828cf67ce9c459639c1dca`.
Completed 2026-10-06T01:52:47.012488+00:00; original English dev/ID/OOD, no fine-tuning or translation.
Device `cuda`, precision `torch.float32`, batch 1; parameters 106,995,075.

## Protocol

Original-order cited references are concatenated with two newlines. The original claim is kept intact.
Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.
Adapter: `nli`. Class scores: `native_classification_logits`.
Class order: `('entailment', 'neutral', 'contradiction')`; attributable/support index 0.
Primary threshold 0.27, selected solely on 1,198 English dev rows before test inference.
Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.
Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.

## Primary results

All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.

| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| test | 1610 | 62.19 | [58.41, 65.52] | 62.32 | 62.42 | 42.73 | 32.42 | 315 |
| test_ood | 1686 | 72.31 | [69.06, 75.12] | 71.81 | 71.89 | 22.89 | 33.33 | 132 |

False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.

## Per-source results

| Split | Source | Units | Macro-F1 | False acceptance | False warning |
|---|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 75.18 | 20.87 | 28.70 |
| test | ExpertQA | 612 | 55.74 | 55.56 | 31.70 |
| test | LFQA | 168 | 51.16 | 59.52 | 36.90 |
| test | Stanford-GenSearch | 600 | 66.67 | 33.33 | 33.33 |
| test_ood | AttrScore-GenSearch | 162 | 72.00 | 9.88 | 44.44 |
| test_ood | BEGIN | 436 | 74.35 | 12.39 | 38.07 |
| test_ood | HAGRID | 1088 | 70.59 | 29.04 | 29.78 |

## Class metrics

| Split | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 63.85 | 57.27 | 60.38 | 805 |
| test | attributable | 61.26 | 67.58 | 64.26 | 805 |

test confusion [not attributable, attributable]: `[[461, 344], [261, 544]]`.
test not-attributable AUROC 0.6920; AP 0.6595.
| test_ood | not attributable | 69.82 | 77.11 | 73.28 | 843 |
| test_ood | attributable | 74.44 | 66.67 | 70.34 | 843 |

test_ood confusion [not attributable, attributable]: `[[650, 193], [281, 562]]`.
test_ood not-attributable AUROC 0.8086; AP 0.7754.

## Execution

Valid scored rows 4494/4494; failures 0.
Runner wall time 58.62s; model loading 3.85s.
Batch p50/p95 seconds `[0.008028250013012439, 0.01314239001367241]`; batch size 1.
CUDA peak allocated/reserved bytes `{'cuda_peak_allocated_bytes': 445169664, 'cuda_peak_reserved_bytes': 473956352, 'cuda_total_bytes': 4294705152}`; excludes other GPU processes and driver overhead.
First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.
Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.
Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.
These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model minilm --device cuda --precision float32 --batch-size 1 --output 'F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\minilm_cuda_float32_b1_retry_cache'
```
