# LADDER Joint Attack-Relevance Data Audit Design

## Status

Approved design with partial-supervision modification. This work audits and prepares data only. It does not train a model, change CyberCase production code, or modify the original LADDER files.

## Goal

Determine whether LADDER sentence-level relevance labels and token-level `ATK`/`O` annotations can support a joint evidence-aware multi-task dataset while preserving the complete sentence-classification task.

The canonical dataset is partially supervised:

- Every original sentence-classification row remains in its original split.
- Exact, defensible positive alignments receive sentence and span supervision.
- Positive classification rows without defensible entity alignment remain sentence-supervised and have masked span loss.
- Negative classification rows receive all-O/no-evidence supervision only if the audit finds no semantic conflict that invalidates this assumption. Otherwise their span loss is masked.
- Entity-only rows never become sentence-classification samples without a sentence-level gold label.

## Confirmed repository contracts

The source data is under `experiments/LADDER/attack_pattern/data/`:

- Sentence classification: tab-delimited `train.csv`, `dev.csv`, and `test.csv`.
- Entity extraction: blank-line-delimited `train.txt`, `dev.txt`, and `test.txt`.
- Sentence labels: `1` is relevant and `0` is irrelevant.
- Entity labels: `ATK` and `O`.
- Classification sizes: train `2,214`, dev `568`, test `662`.
- Preliminary entity sizes: train `1,144`, dev `308`, test `348`.

The existing XLM-R experiment is under `backend/experiments/ladder_relevance/`. Its checkpoint contract is `xlm-roberta-base`, positive index `1`, and `max_tokens=316`. This audit does not import or change production model behavior.

## Package boundary

The implementation lives in `experiments/ladder_joint_detection/` and is independent of the backend runtime. Modules have one responsibility and remain below the repository's 300-line code-file limit:

- `constants.py`: source paths, label constants, output names, and schema values.
- `models.py`: immutable records for classification rows, entity sentences, matches, spans, and audit results.
- `parsing.py`: strict source readers that preserve original token sequences and source locations.
- `normalization.py`: conservative matching normalization and normalized-character provenance.
- `matching.py`: split-local exact matching, duplicate accounting, and conflict detection.
- `diagnostics.py`: diagnostic-only closest candidates and mismatch categories.
- `spans.py`: deterministic character-span derivation and validation.
- `reporting.py`: CSV, JSON, and Markdown output.
- `validation.py`: audit and joint-dataset invariants.
- `audit_alignment.py`: audit command entrypoint.
- `build_joint_dataset.py`: conditional partially supervised JSONL builder.

No model, tokenizer, training, or production module is part of this package.

## Parsing and normalization

Classification records retain `original_text`, `normalized_text`, `sentence_label`, `split`, and source row number. Entity records retain the original `(token, label)` sequence, `reconstructed_text`, `normalized_text`, `split`, block index, and source line range.

Normalization is used only for matching and diagnostics. It applies Unicode normalization when needed, trims leading and trailing whitespace, collapses repeated whitespace, and repairs spacing around punctuation without lowercasing, stemming, lemmatizing, translating, removing words, or removing punctuation. The original text and original token sequence remain unchanged.

Malformed entity rows, unknown labels, empty blocks, and missing fields fail closed and are counted with source locations. They are never silently converted into valid annotations.

## Alignment audit

Matching is performed independently within train, dev, and test. The primary key is `(split, normalized_text)` and matching is exact after the conservative normalization. Similarity is never used to create a training pair.

The audit records:

- classification totals, positive and negative totals;
- entity totals and entity sentences containing `ATK`;
- exact positive matches and unmatched positives;
- duplicate classification and entity texts;
- one-to-many and many-to-one relationships;
- entity sentences matching classification negatives;
- entity-only sentences;
- positives with and without defensible span annotations;
- malformed records and span-conversion failures;
- alignment provenance and source locations.

When duplicate entity records share a normalized text, identical annotations may be represented once with all provenance retained. Inconsistent token labels or derived spans are an annotation conflict and are not silently merged; the affected row receives masked span supervision.

## Diagnostic unmatched analysis

Each unmatched positive is exported with its original and normalized classification text. A deterministic standard-library similarity score may identify a closest entity candidate for diagnosis only. It cannot change alignment status.

Diagnostic categories are based on explicit comparisons, including punctuation/spacing differences, Unicode normalization, token reconstruction, sentence segmentation, and genuinely different text. The report labels candidates as diagnostic suggestions rather than aligned samples.

## Audit decision

The report classifies the result without an arbitrary percentage threshold:

- `SAFE`: every positive classification row has a consistent exact alignment, no unresolved conflicts exist, and there is no reason to mask negative span supervision.
- `PARTIALLY_SAFE`: exact matches are reliable and conflict-free, but the source populations or segmentation leave explicit unmatched positives that can be retained with span loss masked. Negative all-O supervision is enabled only when the audit supports it; otherwise negatives are retained with masked span loss.
- `UNSAFE`: exact matches conflict with sentence labels, annotations cannot be deterministically represented, or the mismatch evidence indicates that the two tasks describe materially different populations.

The decision is evidence-backed by the counts and examples in `alignment_report.json` and `alignment_report.md`. The builder refuses to run for `UNSAFE`.

## Partially supervised joint record

For every sentence-classification row, the builder emits a record with at least:

```json
{
  "id": "train-cls-000001",
  "text": "PowerShell executed",
  "sentence_label": 1,
  "evidence_spans": [{"start": 0, "end": 19, "text": "PowerShell executed"}],
  "split": "train",
  "source": "LADDER",
  "alignment_type": "exact_normalized",
  "has_span_annotation": true,
  "span_loss_mask": true
}
```

Aligned positives contain validated character spans derived from contiguous `ATK` token runs. Positive rows without defensible alignment contain an empty span list, `has_span_annotation=false`, and `span_loss_mask=false`; their sentence label remains active.

Negative rows remain in the original split. If the audit confirms that a negative relevance label safely implies no attack evidence, they contain an empty evidence-span list, `has_span_annotation=true`, and `span_loss_mask=true`, representing an all-O target. If the audit finds a negative/entity conflict, negative span supervision is masked instead of forcing an all-O target.

The record does not contain XLM-R token IDs or subword labels. Tokenization and offset mapping remain a future training-time concern.

## Character spans

The entity token sequence is first preserved exactly. For exact matches, normalized-character provenance maps contiguous `ATK` token runs onto the original classification text. Each emitted span is checked for text bounds and for normalized text equivalence with the intended token run. Any failed mapping downgrades the row to masked span supervision and records the reason.

## Outputs

The audit writes:

- `alignment_report.json`
- `alignment_report.md`
- `matched_samples.csv`
- `conflicts.csv`
- `unmatched_train.csv`
- `unmatched_dev.csv`
- `unmatched_test.csv`

The conditional builder writes `joint_train.jsonl`, `joint_dev.jsonl`, and `joint_test.jsonl`, plus explicit span-supervision statistics and an exclusion report only for source rows that cannot be represented because of malformed or irreconcilable records. Unaligned positives remain in the joint JSONL with span supervision masked. Entity-only rows remain in the audit report and are not added to the sentence dataset.

The Markdown report prints at least 20 matched examples, 20 unmatched examples, all conflicts when there are at most 100, and per-split statistics for total sentences, positive/negative counts, positives with/without span annotation, positive span-supervision percentage, negative conflicts, entity-only rows, exact alignments, and duplicate alignments.

## Validation

Automated tests verify:

1. Original split assignments are preserved.
2. No normalized sample crosses splits.
3. Every aligned positive has a valid span.
4. Every span is within original text bounds.
5. Span extraction reproduces the intended evidence after normalization.
6. Negative all-O supervision is enabled only when the audit permits it.
7. Unaligned positives retain sentence supervision and have masked span loss.
8. Entity-only rows never become sentence samples.
9. No source row is silently dropped; all exclusions have reasons.
10. Repeated runs are deterministic.

The test suite runs before interpreting the audit decision. A failed invariant stops dataset generation.

## Commands

```powershell
python experiments/ladder_joint_detection/audit_alignment.py
python experiments/ladder_joint_detection/build_joint_dataset.py
python -m pytest -q experiments/ladder_joint_detection/tests
```

The future joint XLM-R architecture, CRF, evidence fusion, training, and hyperparameter tuning are explicitly out of scope.
