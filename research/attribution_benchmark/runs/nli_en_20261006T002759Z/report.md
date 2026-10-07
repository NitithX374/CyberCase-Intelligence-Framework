# AttributionBench: local multilingual NLI baseline

Run completed 2026-10-06T00:32:42.760301+00:00. English original inputs; no translation or fine-tuning.

Model: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` @ `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`; torch.float32 on cuda (NVIDIA GeForce GTX 1650).
Dataset: `osunlp/AttributionBench` / subset_balanced @ `62569e644f4186606f54f742178a4517431b42e1`.

Cited references are concatenated in their original order with two newlines as premise; the original claim is the hypothesis.
The native 512-token input truncates only the premise from the right. The hypothesis is preserved. Empty cited-reference bundles remain in evaluation.
Predict attributable when p(entailment) >= 0.15; threshold chosen solely on 1,198 EN development units.
Selection maximizes mean source-subset Macro-F1 on a predeclared 0.01..0.99 grid; ties closest to 0.5 then lower threshold.

## Primary results

Scores are percentages. ID/OOD Avg is the unweighted mean of source-subset Macro-F1, matching the paper's aggregation.
Pooled Macro-F1 is shown separately and weights subsets by their observed units. CI resamples question+response clusters within each source subset, 2,000 replicates, seed 20261006.

| Test | Units | Mean source Macro-F1 | 95% CI | Pooled Macro-F1 | Accuracy | False acceptance rate | False warning rate |
|---|---:|---:|---|---:|---:|---:|---:|
| ID | 1610 | 64.36 | [61.16, 67.18] | 62.73 | 62.92 | 44.22 | 29.94 |
| OOD | 1686 | 69.87 | [66.70, 72.70] | 70.02 | 70.76 | 44.96 | 13.52 |

False acceptance = gold not attributable predicted attributable / all gold not attributable. False warning = gold attributable predicted not attributable / all gold attributable.
These class-conditional rates have different denominators from paper-style FP/FN percentages over all test units, which are also saved in summary.json.

## Per-source results

| Test | Source | Units | Macro-F1 | 95% CI | Accuracy | False acceptance | False warning | Truncated |
|---|---|---:|---:|---|---:|---:|---:|---:|
| test | AttributedQA | 230 | 77.18 | [71.24, 82.42] | 77.39 | 32.17 | 13.04 | 3 |
| test | ExpertQA | 612 | 54.03 | [49.63, 57.88] | 54.25 | 52.61 | 38.89 | 99 |
| test | LFQA | 168 | 59.15 | [49.62, 67.78] | 59.52 | 50.00 | 30.95 | 132 |
| test | Stanford-GenSearch | 600 | 67.05 | [62.93, 71.05] | 67.17 | 38.67 | 27.00 | 90 |
| test_ood | AttrScore-GenSearch | 162 | 69.56 | [61.92, 76.40] | 69.75 | 22.22 | 38.27 | 0 |
| test_ood | BEGIN | 436 | 70.46 | [66.25, 75.19] | 72.02 | 50.92 | 5.05 | 47 |
| test_ood | HAGRID | 1088 | 69.59 | [66.35, 72.59] | 70.40 | 45.96 | 13.24 | 113 |

## Class metrics and score ranking

| Test | Gold class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| test | not attributable | 65.07 | 55.78 | 60.07 | 805 |
| test | attributable | 61.30 | 70.06 | 65.39 | 805 |
| test_ood | not attributable | 80.28 | 55.04 | 65.31 | 843 |
| test_ood | attributable | 65.79 | 86.48 | 74.73 | 843 |

test confusion rows/columns [not attributable, attributable]: `[[449, 356], [241, 564]]`.
test score ranking, not attributable positive: AUROC=0.6856, AP=0.6534.

test_ood confusion rows/columns [not attributable, attributable]: `[[464, 379], [114, 729]]`.
test_ood score ranking, not attributable positive: AUROC=0.7836, AP=0.7708.

## Descriptive NLI argmax reference

The same cached logits are mapped entailment -> attributable, neutral/contradiction -> not attributable; no second model inference or selection on test labels.
- test: mean source Macro-F1 66.46, pooled Macro-F1 64.69.
- test_ood: mean source Macro-F1 70.86, pooled Macro-F1 71.72.

## Execution and limitations

- Valid outputs: 4494/4494; failures 0.
- Total dev+test runner wall time 283.03s; model load 5.53s.
- Batch latency p50/p95: [0.10469520004699007, 0.2117741800029762]; amortized batch-time/unit p50/p95: [0.05234760002349503, 0.10588970000389963] seconds. Batch size 2. This is amortized throughput timing, not single-request latency.
- Local inference only; external model API calls/charges = 0. GPU/energy ownership cost is not monetized.
- Full evidence beyond the native context window is discarded and counted. Scores measure the specified truncated-input NLI baseline, not full-document verification.
- Binary not attributable combines partial, absent and contradictory support. Source support does not establish source truth.
- No Thai inputs, native Thai case labels or downstream CyberCase report evaluation in this run.
- This checkpoint is not one of AttributionBench's reported baselines; its results are a new measurement under the recorded input/decision protocol.

## Reproduction

```powershell
& '.\env_mitre\Scripts\python.exe' -u 'research/attribution_benchmark/run.py' --device cuda --batch-size 2
```

Dataset/model revisions, source and score hashes, package versions and input lengths are stored in the manifests and score JSONL. Threshold selection is recorded before test inference.

Sources: [official dataset](https://huggingface.co/datasets/osunlp/AttributionBench), [AttributionBench paper](https://aclanthology.org/2024.findings-acl.886.pdf), [model card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7).
