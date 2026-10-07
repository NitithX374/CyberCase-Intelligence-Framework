# AttributionBench candidate evaluation

Model: `cross-encoder/nli-deberta-v3-small` @ `fa2804872c3b4bd748f38c0185cc85775361e735`.
Completed 2026-10-06T01:06:45.956920+00:00; original English dev/ID/OOD, no fine-tuning or translation.
Device `cuda`, precision `torch.float32`, batch 1; parameters 141,897,219.

## Protocol

Original-order cited references are concatenated with two newlines. The original claim is kept intact.
Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.
Adapter: `nli`. Class scores: `native_classification_logits`.
Class order: `('contradiction', 'entailment', 'neutral')`; attributable/support index 1.
Primary threshold 0.01, selected solely on 1,198 English dev rows before test inference.
Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.
Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.

## Primary results

All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.

| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| test | 1610 | 61.51 | [57.92, 64.61] | 62.07 | 62.30 | 29.94 | 45.47 | 281 |
| test_ood | 1686 | 73.08 | [69.88, 75.90] | 71.53 | 71.53 | 27.40 | 29.54 | 86 |

False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.

## Per-source results

| Split | Source | Units | Macro-F1 | False acceptance | False warning |
|---|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 75.65 | 23.48 | 25.22 |
| test | ExpertQA | 612 | 50.88 | 37.58 | 59.48 |
| test | LFQA | 168 | 48.52 | 20.24 | 75.00 |
| test | Stanford-GenSearch | 600 | 70.99 | 27.33 | 30.67 |
| test_ood | AttrScore-GenSearch | 162 | 72.12 | 11.11 | 43.21 |
| test_ood | BEGIN | 436 | 78.66 | 19.72 | 22.94 |
| test_ood | HAGRID | 1088 | 68.47 | 32.90 | 30.15 |

## Class metrics

| Split | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 60.65 | 70.06 | 65.01 | 805 |
| test | attributable | 64.56 | 54.53 | 59.12 | 805 |

test confusion [not attributable, attributable]: `[[564, 241], [366, 439]]`.
test not-attributable AUROC 0.6840; AP 0.6628.
| test_ood | not attributable | 71.08 | 72.60 | 71.83 | 843 |
| test_ood | attributable | 72.00 | 70.46 | 71.22 | 843 |

test_ood confusion [not attributable, attributable]: `[[612, 231], [249, 594]]`.
test_ood not-attributable AUROC 0.7899; AP 0.7632.

## Execution

Valid scored rows 4494/4494; failures 0.
Runner wall time 136.30s; model loading 3.35s.
Batch p50/p95 seconds `[0.023824450006941333, 0.0516816350253066]`; batch size 1.
CUDA peak allocated/reserved bytes `{'cuda_peak_allocated_bytes': 671370752, 'cuda_peak_reserved_bytes': 721420288, 'cuda_total_bytes': 4294705152}`; excludes other GPU processes and driver overhead.
First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.
Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.
Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.
These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model deberta_small --device cuda --precision float32 --batch-size 1 --output 'F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\deberta_small_cuda_float32_b1'
```
