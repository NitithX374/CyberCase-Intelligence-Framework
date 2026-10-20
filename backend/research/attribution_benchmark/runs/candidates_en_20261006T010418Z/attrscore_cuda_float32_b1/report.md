# AttributionBench candidate evaluation

Model: `osunlp/attrscore-flan-t5-large` @ `282eb2ab5d537f5badf5fa33008d96abff34607b`.
Completed 2026-10-06T01:50:41.751201+00:00; original English dev/ID/OOD, no fine-tuning or translation.
Device `cuda`, precision `torch.float32`, batch 1; parameters 783,150,080.

## Protocol

Original-order cited references are concatenated with two newlines. The original claim is kept intact.
Maximum model input is 512 tokens. Only evidence is truncated from the right; no evidence retrieval or chunk aggregation.
Adapter: `sequence_label_likelihood`. Class scores: `sum_autoregressive_label_token_log_probabilities_including_EOS`.
Class order: `('Attributable', 'Contradictory', 'Extrapolatory')`; attributable/support index 0.
Primary threshold 0.23, selected solely on 1,198 English dev rows before test inference.
Threshold grid 0.01..0.99 maximizes mean source-subset Macro-F1; ties nearest 0.5, then lower threshold.
Source-subset averaging, class-conditional errors and 2,000 question+response cluster-bootstrap replicates match the first baseline protocol.

AttrScore uses the author's attribution instruction and full claim followed by cited references.
Each of Attributable, Contradictory and Extrapolatory is scored with teacher forcing, including EOS.
Complete label token log probabilities are summed without length normalization, then normalized across the three label sequences.
The resulting supported score is relative among these labels; it is not a calibrated probability or greedy free-text generation.
Prompt tokens consume part of the 512-token budget, and evidence loss is recorded. Binary not attributable combines Contradictory/Extrapolatory.

## Primary results

All scores are percentages. Mean source Macro-F1 is the unweighted average across the paper's source subsets.

| Split | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance | False warning | Truncated |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| test | 1610 | 66.22 | [62.72, 69.20] | 64.49 | 65.16 | 48.57 | 21.12 | 374 |
| test_ood | 1686 | 75.70 | [73.04, 78.10] | 73.46 | 74.08 | 41.16 | 10.68 | 252 |

False acceptance: unsupported gold accepted / unsupported gold. False warning: supported gold rejected / supported gold.

## Per-source results

| Split | Source | Units | Macro-F1 | False acceptance | False warning |
|---|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 79.97 | 34.78 | 4.35 |
| test | ExpertQA | 612 | 56.89 | 54.58 | 30.39 |
| test | LFQA | 168 | 61.56 | 28.57 | 47.62 |
| test | Stanford-GenSearch | 600 | 66.47 | 53.33 | 10.67 |
| test_ood | AttrScore-GenSearch | 162 | 75.72 | 33.33 | 14.81 |
| test_ood | BEGIN | 436 | 82.57 | 16.51 | 18.35 |
| test_ood | HAGRID | 1088 | 68.81 | 52.21 | 6.99 |

## Class metrics

| Split | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 70.89 | 51.43 | 59.61 | 805 |
| test | attributable | 61.89 | 78.88 | 69.36 | 805 |

test confusion [not attributable, attributable]: `[[414, 391], [170, 635]]`.
test not-attributable AUROC 0.7357; AP 0.7105.
| test_ood | not attributable | 84.64 | 58.84 | 69.42 | 843 |
| test_ood | attributable | 68.45 | 89.32 | 77.51 | 843 |

test_ood confusion [not attributable, attributable]: `[[496, 347], [90, 753]]`.
test_ood not-attributable AUROC 0.8501; AP 0.8463.

## Execution

Valid scored rows 4494/4494; failures 0.
Runner wall time 1437.78s; model loading 5.64s.
Batch p50/p95 seconds `[0.308539049961837, 0.40393133501638656]`; batch size 1.
CUDA peak allocated/reserved bytes `{'cuda_peak_allocated_bytes': 3362387456, 'cuda_peak_reserved_bytes': 3393191936, 'cuda_total_bytes': 4294705152}`; excludes other GPU processes and driver overhead.
First-use kernel initialization is included; no warm-up rows are omitted. Download time is excluded.
Raw rows, class scores, input token IDs, evidence loss, revisions and execution-source hashes are saved.
Class-argmax reference metrics are descriptive and do not replace the dev-selected primary threshold.
These are new English measurements of the recorded adapters, not paper-result replications or Thai case-domain validation.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run_candidate.py' --model attrscore --device cuda --precision float32 --batch-size 1 --output 'F:\Cybercase Framework\research\attribution_benchmark\runs\candidates_en_20261006T010418Z\attrscore_cuda_float32_b1'
```
