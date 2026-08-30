# Pilot-1 English Stratified 50-Case Report

## Scope and selection

This run evaluates 50 English rows from the approved six-category SEvenLLM selection at commit `a84b86aabf2b5be35a2cbbac546511883cc5ff85`. Selection is deterministic: the lowest English dataset IDs within each requested category.

| Category | Requested | Selected | Format count |
|---|---:|---:|---|
| Threat Analysis | 15 | 15 | 15 generation |
| Protection Strategy Research | 8 | 8 | 1 extraction, 7 generation |
| Summary Generation | 7 | 7 | 7 generation |
| Incident Response Planning | 7 | 7 | 7 generation |
| Risk Assessment | 7 | 7 | 7 generation |
| Impact Scope | 6 | 6 | 6 generation |
| **Total** | **50** | **50** | **1 extraction, 49 generation** |

No Chinese rows were inferred or scored. No MCQ row occurs in this category-balanced selection, so MCQ accuracy is not represented.

The B0 output contains 39 reused records from the prior exact-condition OpenRouter run and 11 newly requested records. The prior 41-record file was preserved unchanged. B1 uses the already completed mT5 predictions filtered to these same 50 IDs.

## Model conditions

| Condition | Model | Provider | Generation |
|---|---|---|---|
| B0 | `meta-llama/llama-3.1-8b-instruct` | OpenRouter | `temperature=0`, `top_p=1`, `max_tokens=512` |
| B1 | `google/mt5-base` revision `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f` | local | Existing deterministic predictions, unchanged |

This is a capability-reference comparison, not a parameter-matched or architecture-controlled comparison. Neither condition uses fine-tuning, RAG, MITRE augmentation, few-shot examples, or external tools.

## Overall results

| Format | N | Metric | B0 | B1 | Absolute gap | B1 retained |
|---|---:|---|---:|---:|---:|---:|
| Generation | 49 | ROUGE-L | 0.278951 | 0.049092 | 0.229859 | 17.60% |
| Generation | 49 | Official SBERT semantic | 0.672995 | 0.284877 | 0.388118 | 42.33% |
| Extraction | 1 | Precision | 0.000000 | 0.000000 | 0.000000 | N/A |
| Extraction | 1 | Recall | 0.000000 | 0.000000 | 0.000000 | N/A |
| Extraction | 1 | F1 | 0.000000 | 0.000000 | 0.000000 | N/A |
| MCQ | 0 | Accuracy | N/A | N/A | N/A | N/A |

Metrics are reported separately; no incompatible metrics are combined into one score.

## Generation results by category

| Category | N | B0 ROUGE-L | B1 ROUGE-L | B0 Semantic | B1 Semantic |
|---|---:|---:|---:|---:|---:|
| Threat Analysis | 15 | 0.234084 | 0.044678 | 0.670406 | 0.315827 |
| Protection Strategy Research | 7 | 0.270997 | 0.058470 | 0.692142 | 0.293872 |
| Summary Generation | 7 | 0.415968 | 0.044030 | 0.702801 | 0.262055 |
| Incident Response Planning | 7 | 0.237735 | 0.041497 | 0.657106 | 0.225567 |
| Risk Assessment | 7 | 0.221799 | 0.060852 | 0.627812 | 0.337988 |
| Impact Scope | 6 | 0.355307 | 0.050232 | 0.693608 | 0.230865 |

## Extraction

The single extraction row is ID `791` in Protection Strategy Research. Both models scored precision, recall, and F1 as zero. B0 returned parseable structured output but had no official flattened-leaf overlap; B1 did not produce an acceptable structured result.

## Qualitative observations

- B0 generally produced complete task-directed English responses across all six categories.
- B1 frequently produced short mT5 sentinel fragments such as `<extra_id_0>` instead of completing the requested task.
- The semantic gap is consistent across categories: B0 is highest on Summary Generation (`0.702801`), while B1 is highest on Risk Assessment (`0.337988`), but B1 remains well below B0 in every category.
- The extraction failure is shared at the metric level and should not be generalized beyond the single selected row.

No prompts or generation parameters were changed after inspecting outputs.

## Restrained verdict

Vanilla mT5-base demonstrates a measurable but limited zero-shot signal on this 50-case English stratified checkpoint. The 42.33% semantic retention is sufficient to justify proceeding to SEvenLLM fine-tuning as the next experiment, but the much lower ROUGE-L retention and zero extraction F1 do not support a claim of strong zero-shot capability.

## Evidence artifacts

- [Selection manifest](pilot_1_en_50_selection.json)
- [B0 OpenRouter predictions](B0_openrouter_predictions_50_stratified.jsonl)
- [B1 predictions](B1_predictions.jsonl)
- [Official score data](pilot_1_en_50_scores.json)
