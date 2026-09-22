# AnnoCTR External Validation Design

## Goal

Create a reproducible zero-adaptation external-validation experiment for the existing LADDER-trained XLM-R binary ATT&CK relevance gate. The experiment measures whether the classifier generalizes from LADDER's English CTI sentence data to AnnoCTR's independently annotated CTI corpus.

The experiment does not retrain the checkpoint, tune a threshold on AnnoCTR, use an LLM for labels or evaluation, rebalance the test set, or modify production code.

## Repository boundary

Implementation and generated outputs live in `experiments/annoctr_external_validation/` in the CyberCase repository. The AnnoCTR checkout at `F:/anno-ctr-lrec-coling-2024` is an external read-only input. The runner accepts `--annoctr-root` and defaults to that current local path so the requested one-command execution works on this machine.

## Frozen classifier contract

The experiment reuses the existing checkpoint loader and prediction path from `backend/experiments/ladder_relevance/gold_oracle_inference.py`. The checkpoint is `backend/xlmr_ladder_best/xlmr_ladder_best`.

The checkpoint card establishes output index `1` as the relevant class and records `max_tokens=316`. The existing LADDER benchmark runner evaluates with a `0.50` decision threshold, so both LADDER internal-test and AnnoCTR external-test metrics use `0.50`. The checkpoint card's operational gate threshold of `0.10` is recorded as metadata but is not substituted into the comparison or tuned during the experiment.

## Dataset conversion

The runner first searches the AnnoCTR checkout for a native sentence-level source. The inspected repository contains mention/linking, NER, text, and time resources but no sentence-classification file, so the current run uses `AnnoCTR/linking_mitre_only/test_w_neg.jsonl`.

Only the official AnnoCTR test documents are admitted. Document IDs are cross-checked against `AnnoCTR/text/train`, `dev`, and `test` to prevent split mixing or duplicate document membership.

For ordinary mention records, the sentence text is reconstructed as:

`_context_left + mention + _context_right`

Whitespace is normalized without changing other characters. `sentence_left` and `sentence_right` are never concatenated into the target sentence. The dataset's explicit synthetic negative records have empty context fields, `label_link="No Annotation"`, and the complete sentence in `mention`; that representation is accepted only after schema validation.

Rows are aggregated by `(document, normalized_sentence_text)`. A sentence is positive only when at least one contributing row has a valid `attack.mitre.org/techniques/` link. A sentence with only non-technique entities or the explicit `No Annotation` marker is negative. A positive technique annotation always overrides a negative row for the same sentence identity. Unexpected technique rows without either a valid ATT&CK technique URL or the explicit negative marker fail closed.

The converter emits `text`, `gold_label`, `document`, `has_attack_technique`, and `source_split=test` to `annoctr_test_binary.csv`.

## Validation and reporting flow

The single runner performs these stages in order:

1. Resolve and audit the AnnoCTR source.
2. Convert and aggregate the official test split.
3. Validate empty text, duplicate output identities, split isolation, annotation conflicts, and required binary classes.
4. Print reproducible dataset counts, random positive/negative examples, and shortest/longest examples.
5. Load the frozen checkpoint and run inference on AnnoCTR and the existing LADDER test split with the same tokenizer, preprocessing, max length, relevant output index, and threshold.
6. Compute binary and macro metrics, confusion matrices, false skip rate, and false invocation rate.
7. Export predictions, false negatives, false positives, deterministic error-pattern fields, and token-length distributions.
8. Generate a README containing the exact source, model, preprocessing, threshold, metrics, and conversion caveats.

The required generated files are `annoctr_test_binary.csv`, `annoctr_test_predictions.csv`, `annoctr_false_negatives.csv`, `annoctr_false_positives.csv`, `metrics.json`, `dataset_statistics.json`, `token_length_statistics.json`, and `README.md`.

False skip rate is `FN / (TP + FN)`. False invocation rate is `FP / (TN + FP)`. Error analysis is deterministic and limited to character length, tokenizer length, explicit ATT&CK terminology, a fixed action-verb lexicon, and confidence values.

Token diagnostics report content-token lengths, the configured model limit, the special-token-adjusted content limit, min/mean/median/p90/p95/max, and truncation counts for both LADDER test and AnnoCTR test. The model max length is never changed.

## Module boundaries

The implementation is split into focused files, each below the repository's 300-line code limit:

- `source.py`: source discovery and AnnoCTR path resolution.
- `conversion.py`: JSONL parsing, sentence reconstruction, and aggregation.
- `validation.py`: split and conversion sanity checks.
- `model.py`: frozen checkpoint and LADDER loading through existing helpers.
- `analysis.py`: inference, metrics, error rows, and token diagnostics.
- `reporting.py`: CSV, JSON, and README output.
- `run.py`: command-line orchestration.
- `tests/`: deterministic conversion and validation tests.

No production application module, checkpoint file, or AnnoCTR file is modified.

## Verification

Verification consists of focused unit tests for conversion and validation, Python compilation, the one-command experiment run, generated-file/schema checks, and a final diff review that confirms only the new experiment/spec files were added by this task.
