# AttributionBench candidate evaluation

Model: `joeddav/xlm-roberta-large-xnli` @ `b227ee8435ceadfa86dc1368a34254e2838bf242`.
Completed 2026-10-06T02:02:07.850496+00:00; original English dev/ID/OOD, no fine-tuning or translation.
Device `cuda`, precision `torch.float32`, batch 1; parameters 559,893,507.

## Protocol

Original-order cited references are concatenated with two newlines. The original claim is kept intact.
Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.
Adapter: `nli`. Class scores: `native_classification_logits`.
Class order: `('contradiction', 'neutral', 'entailment')`; attributable/support index 2.
Primary threshold 0.05, selected solely on 1,198 English dev rows before test inference.
Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.
Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.

## Primary results

All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.

| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| test | 1610 | 65.34 | [61.86, 68.52] | 65.20 | 65.22 | 32.42 | 37.14 | 315 |
| test_ood | 1686 | 75.20 | [71.99, 78.07] | 74.19 | 74.20 | 27.88 | 23.72 | 132 |

False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.

## Per-source results

| Split | Source | Units | Macro-F1 | False acceptance | False warning |
|---|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 80.30 | 27.83 | 11.30 |
| test | ExpertQA | 612 | 54.74 | 44.44 | 46.08 |
| test | LFQA | 168 | 54.15 | 14.29 | 70.24 |
| test | Stanford-GenSearch | 600 | 72.16 | 27.00 | 28.67 |
| test_ood | AttrScore-GenSearch | 162 | 74.26 | 12.35 | 38.27 |
| test_ood | BEGIN | 436 | 79.35 | 22.48 | 18.81 |
| test_ood | HAGRID | 1088 | 72.00 | 32.35 | 23.53 |

## Class metrics

| Split | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 64.53 | 67.58 | 66.02 | 805 |
| test | attributable | 65.97 | 62.86 | 64.38 | 805 |

test confusion [not attributable, attributable]: `[[544, 261], [299, 506]]`.
test not-attributable AUROC 0.7114; AP 0.6661.
| test_ood | not attributable | 75.25 | 72.12 | 73.65 | 843 |
| test_ood | attributable | 73.23 | 76.28 | 74.72 | 843 |

test_ood confusion [not attributable, attributable]: `[[608, 235], [200, 643]]`.
test_ood not-attributable AUROC 0.8243; AP 0.8018.

## Execution

Valid scored rows 4494/4494; failures 0.
Runner wall time 529.35s; model loading 5.41s.
Batch p50/p95 seconds `[0.10843269998440519, 0.22530664999794678]`; batch size 1.
CUDA peak allocated/reserved bytes `{'cuda_peak_allocated_bytes': 2271246848, 'cuda_peak_reserved_bytes': 2306867200, 'cuda_total_bytes': 4294705152}`; excludes other GPU processes and driver overhead.
First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.
Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.
Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.
These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model xlmr --device cuda --precision float32 --batch-size 1 --output 'F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\xlmr_cuda_float32_b1_retry_logging'
```
