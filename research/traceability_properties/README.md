# Traceability properties on public corpora

Deterministic measurements of the Source-unit construction used by the paper
(`paper/ubimedia2027`, Sect. 5). No model is called and no labels are needed: the
script runs the production code in `backend/app/sources/evidence.py` and
`backend/app/trace/sentences.py` on public text and records what it does.

| Measure | What is computed |
|---|---|
| Losslessness | every unit equals `S[start:end]`, units are contiguous, first starts at 0, last ends at `len(S)`, and their concatenation is `S` |
| Determinism | a second pass gives identical units and identifiers; `units_digest` lets separate runs be compared |
| Revision safety | one random single-character insertion per source (seeded by the SHA-256 of the text); every old identifier is resolved against the edited source with the production `EvidenceIndex`; compared with raw `(start, end)` offsets and position-only identifiers (`S:U003`), which would return changed text without any error |
| Boundary integrity | share of cut points that fall inside a word, for unit boundaries and for fixed-size character chunks of the same mean length; words are PyThaiNLP `newmm` tokens for Thai and `\w+` runs for English (a reference tokenizer, not gold boundaries); also cuts with a digit on both sides |
| Cost | unit counts and lengths, segmentation time per 1,000 characters on CPU |

## Corpora

* **Thai:** ThaiSum test articles (`pythainlp/thaisum`, revision `6c2928cb64cd0d8ec0f3790ce848048fde1911dd`,
  MIT licence), the first N unique bodies ordered by SHA-256 of the text.
* **English:** references of AttributionBench `test` and `test_ood`
  (`osunlp/AttributionBench`, revision `62569e644f4186606f54f742178a4517431b42e1`), the first N
  unique non-empty references ordered by SHA-256 of the text.

Both are downloaded through `huggingface_hub` at the pinned revisions; file hashes are written
into the result.

## Run

```bash
# from the repository root, with the backend requirements installed
# (pythainlp, wtpsplit and torch for SaT; asyncpg/sqlalchemy for the app imports; pyarrow)
python research/traceability_properties/run.py --thai-n 500 --en-n 1000
```

The SaT model `sat-3l-sm` is downloaded on first use. If it cannot be loaded, production falls
back to PyThaiNLP `crfcut`; the result records which segmenter ran.

## Result

`results/properties.json` (see `created_at`, `segmenter`, `environment` and `inputs` inside).

## Segmenter switch

The revision tag hashes the segmentation version and the source text, not the segmenter, and units
are recomputed rather than stored. `segmenter_switch.py` segments the same sample with SaT, then with
the PyThaiNLP `crfcut` fall-back that production uses when SaT cannot be loaded, and resolves every
SaT-era identifier against the fall-back units with the production `EvidenceIndex`. It counts
identifiers that still return their text, identifiers that return different text without an error,
and typed failures.

```bash
python research/traceability_properties/segmenter_switch.py --thai-n 500 --en-n 1000
```

Result: `results/segmenter_switch.json`. This is a limitation of the prototype (Discussion of the
paper), not a property it has.
