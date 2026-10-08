# BGE-M3 original EN / Google MT-TH similarity — 2026-10-07

Completed and independently checked: **33,583 unique text pairs**, covering the same **3,296 AttributionBench rows** (1,610 ID / 1,686 OOD) used in the frozen B1-LR transfer evaluation.

Unique-text cosine mean **0.8455**, median **0.8503**; P05 **0.7227**, P95 **0.9592**. This gives each distinct text one weight rather than repeatedly weighting shared references.

There are 1,125 exact-identical EN/TH strings. Excluding these, 32,458 changed pairs have mean 0.8402 and median 0.8477. Exact-identical strings are retained in the complete result and reported separately.

| Split / text | Occurrences | Mean cosine | Median | P05 | P95 |
|---|---:|---:|---:|---:|---:|
| ID / Claims | 1,610 | 0.8558 | 0.8671 | 0.7375 | 0.9385 |
| ID / Source units | 33,644 | 0.8428 | 0.8496 | 0.7070 | 0.9772 |
| OOD / Claims | 1,686 | 0.8657 | 0.8714 | 0.7539 | 0.9570 |
| OOD / Source units | 10,270 | 0.8377 | 0.8420 | 0.7312 | 0.9321 |

The table uses occurrences: repeated reference units are counted in each row where they occur. Per-unique Claim/Source-unit statistics are also saved in the compact JSON. Claims and Source units may share identical text; role counts are not disjoint. Empty reference bundles retain null Source metrics.

## Measurement contract

- Pinned local `BAAI/bge-m3` revision `5617a9f61b028005a4858fdac845db406aefb181`, dense CLS pooling, 1,024 dimensions, no query instruction.
- Explicit CUDA fp16 weights on GTX 1650; vectors converted to float32 and L2-normalized before paired dot product. Encoder inputs alternate original EN and its existing Thai translation.
- The frozen English Claim/reference-unit segmentation is reused. Each original unit maps one-to-one to its cached Thai translation; row IDs, reference order and gold are unchanged. This is not a concatenated whole-document or whole-row comparison.
- Maximum raw token length 432, model limit 8,192; zero EN or TH inputs truncated. No new Google calls, threshold filtering, translation/gold repair, training or production changes.
- Same Google Translation Basic v2 `nmt` cache from the completed B1-LR study. Input/model/code hashes and exact execution-source snapshots are preserved.

## Runtime and validation

Run timestamps (UTC): started 2026-10-07T15:03:24.897144+00:00; completed 2026-10-07T16:13:38.304213+00:00. Artifact filenames use the 2026-10-07 run date.

Tokenization/scoring took 70.22 minutes after model loading (final report writing excluded). Peak PyTorch-allocated VRAM: 1.24 GiB; this excludes driver and other-process memory.

Wall time is descriptive; this was not an isolated comparative speed benchmark.

Seven focused harness tests pass. Independent stdlib recomputation matches all saved means, medians, population standard deviations and linear quantiles. All 33,583 score/CSV pairs and 3,296 row mappings match the original inputs, gold and ordered unit IDs; scores are finite and unique. Dataset, translation, frozen B1 artifacts and source snapshots pass their recorded hash checks. Full embedding inference was not rerun in the independent check.

## Interpretation

These results measure cross-language embedding proximity only. High cosine does not establish faithful preservation of names, amounts, negation, legal roles, Claim support or inherited English gold. Low-scoring texts are review candidates, not automatically mistranslated examples. No acceptance threshold is applied, and the diagnostic neither repairs translations nor modifies verifier decisions.

The complete measured corpus is described without an inferential significance claim. Shared texts/rows are dependent; no iid confidence interval or claim of downstream improvement is made from these cosine scores. Human translation-fidelity labels and an analysis of verifier-error association remain unmeasured.

## Saved artifacts

- [Compact aggregate/provenance receipt](results/bge_mt_th_20261007.json)
- [Full EN/TH pair CSV](../../tmp/bge-m3-mt-th/pairs.csv)
- [Row-aligned scores](../../tmp/bge-m3-mt-th/rows.jsonl)
- [Lowest 100 review candidates](../../tmp/bge-m3-mt-th/lowest_100.json)
- [Runtime manifest](../../tmp/bge-m3-mt-th/manifest.json)
- [Independent verification](../../tmp/bge-m3-mt-th/independent-verification.json)

Large raw artifacts remain local under ignored `tmp/`; code, this report and the compact receipt are reviewable in the working tree. They have not been committed or pushed.

Method reference: [BGE-M3 model card](https://huggingface.co/BAAI/bge-m3). This diagnostic is separate from [the frozen B1-LR EN/MT-TH results](B1_RESULTS_2026-10-07.md).
