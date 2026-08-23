# Pilot-1 English 10-Case Checkpoint

## Scope

This checkpoint scores only the first 10 matched English rows from the approved six-category SEvenLLM selection at dataset commit `a84b86aabf2b5be35a2cbbac546511883cc5ff85`.

- Scored IDs: `791, 901, 902, 903, 904, 906, 907, 908, 909, 910`
- B0: OpenRouter `meta-llama/llama-3.1-8b-instruct`, zero-shot, `temperature=0`, `top_p=1`, `max_tokens=512`
- B1: existing vanilla `google/mt5-base` predictions at revision `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`
- No Chinese inference, fine-tuning, RAG, examples, prompt tuning, or additional models
- The OpenRouter run was stopped after 41 successful records. All 41 are preserved, but only the first 10 are included here.

The 10-row prefix is not stratified. It contains 9 generation rows across five categories and 1 extraction row. It contains no MCQ rows and no Incident Response Planning row.

## Overall compatible results

| Format | N | Metric | B0 | B1 | Absolute gap | B1 retained |
|---|---:|---|---:|---:|---:|---:|
| Generation | 9 | ROUGE-L | 0.304225 | 0.052696 | 0.251529 | 17.32% |
| Generation | 9 | Official SBERT semantic | 0.672821 | 0.268957 | 0.403864 | 39.97% |
| Extraction | 1 | Precision | 0.000000 | 0.000000 | 0.000000 | N/A |
| Extraction | 1 | Recall | 0.000000 | 0.000000 | 0.000000 | N/A |
| Extraction | 1 | F1 | 0.000000 | 0.000000 | 0.000000 | N/A |
| MCQ | 0 | Accuracy | N/A | N/A | N/A | N/A |

Metrics remain separate; no combined overall score is calculated.

## Generation results by category

| Category | N | B0 ROUGE-L | B1 ROUGE-L | B0 Semantic | B1 Semantic |
|---|---:|---:|---:|---:|---:|
| Impact Scope | 1 | 0.560510 | 0.023529 | 0.809965 | 0.195517 |
| Incident Response Planning | 0 | N/A | N/A | N/A | N/A |
| Protection Strategy Research | 3 | 0.218731 | 0.065856 | 0.674617 | 0.257201 |
| Risk Assessment | 1 | 0.155556 | 0.046512 | 0.532869 | 0.355123 |
| Summary Generation | 2 | 0.382992 | 0.068443 | 0.706784 | 0.319163 |
| Threat Analysis | 2 | 0.299893 | 0.034884 | 0.637569 | 0.230023 |

## Generation results by sample

| ID | Category | B0 ROUGE-L | B1 ROUGE-L | B0 Semantic | B1 Semantic |
|---:|---|---:|---:|---:|---:|
| 901 | Impact Scope | 0.560510 | 0.023529 | 0.809965 | 0.195517 |
| 902 | Summary Generation | 0.310811 | 0.045977 | 0.651736 | 0.260922 |
| 903 | Protection Strategy Research | 0.242991 | 0.076336 | 0.694080 | 0.249237 |
| 904 | Threat Analysis | 0.328358 | 0.000000 | 0.717582 | 0.074352 |
| 906 | Risk Assessment | 0.155556 | 0.046512 | 0.532869 | 0.355123 |
| 907 | Summary Generation | 0.455172 | 0.090909 | 0.761832 | 0.377403 |
| 908 | Protection Strategy Research | 0.232558 | 0.022222 | 0.658144 | 0.176417 |
| 909 | Threat Analysis | 0.271429 | 0.069767 | 0.557556 | 0.385693 |
| 910 | Protection Strategy Research | 0.180645 | 0.099010 | 0.671626 | 0.345949 |

## Extraction result

The single extraction case is ID `791` in Protection Strategy Research. B0 returned parseable JSON but matched none of the official flattened gold leaves, producing precision, recall, and F1 of zero. B1 did not return parseable JSON and also scored zero.

## Qualitative checkpoint

- Both B0 and B1 succeed: no representative case was observed. B1 outputs were short fragments containing `<extra_id_0>` on the inspected generation rows.
- B0 succeeds and B1 fails: ID `903` is representative. B0 proposed concrete EHR controls including encryption, authentication, access control, and audits; B1 returned only a generic fragment.
- B1 succeeds and B0 fails: no representative case was observed.
- Both fail: ID `791` is the clearest case under official extraction scoring. B0 produced valid JSON with zero leaf overlap, while B1 failed JSON parsing.

These examples were selected from the fixed 10-row prefix after scoring. They were not used to alter prompts or generation parameters.

## Restrained verdict

Provisionally yes: vanilla mT5-base shows enough non-zero zero-shot signal to justify testing SEvenLLM fine-tuning as the next experiment, but not enough to claim useful zero-shot analytical capability. On the 9 compatible generation rows it retained 39.97% of B0 semantic performance, while its outputs were often degenerate and it failed the extraction case. Because this checkpoint is only 10 non-stratified rows and omits one category and all MCQs, it cannot support a final conclusion across all six tasks.

## Evidence artifacts

- `B0_openrouter_predictions.jsonl`: 41 preserved OpenRouter records; first 10 scored
- `B1_predictions.jsonl`: 300 unchanged mT5 records; first 10 scored
- `pilot_1_en_first10_scores.json`: recomputable row-level and aggregate metrics
