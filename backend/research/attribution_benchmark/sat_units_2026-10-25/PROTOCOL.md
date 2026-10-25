# B1-LR on AttributionBench with production SaT source units

Fixed 2026-10-25 06:46 Asia/Bangkok (2026-10-24T22:46Z), before any inference in this folder.

## Question

The 2026-10-07 run (`../B1_RESULTS_2026-10-07.md`, "AttributionBench EN → Google MT-TH")
fed the frozen B1-LR verifier the research regex units (`champion.reference_units`). Production
feeds it the units `app.sources.evidence.evidence_units` cuts with the SaT splitter. This run
measures the same rows, gold and verifier with the production cut instead. Nothing is fitted,
tuned or translated. No network call of any kind is made.

## Rows and gold

All 1,610 ID rows (`data/test_all_subset_balanced.jsonl`) and 1,686 OOD rows
(`data/test_ood_all_subset_balanced.jsonl`), in `translate_th.plan()` order, dataset manifest
hashes checked. Gold = `attribution_label == "attributable"`. Thai gold inherits English gold, as
in the original run.

## Conditions

- **R-pub** (regex, published): the per-row decisions `en_supported` / `th_supported` in
  `raw/b1-mt-th/scores.jsonl`, the run whose summary gives the published numbers
  (GPU, fp16 NLI, torch 2.6.0, transformers 5.15.1, sentence-transformers 6.0.0). Not re-scored.
- **R-loc** (regex, re-run here): the same regex units as R-pub (the plan's `unit_keys`, English
  texts and cached Thai translations), scored again here with the same call the original made.
  This is a control, so the SaT effect can be read without the environment change (CPU instead of
  GPU, newer libraries).
- **S** (SaT, production units):
  - **EN**: each string in the row's `references` is one source text, held verbatim (production
    stores the source text as given). Each is cut by `evidence_units(CaseSourceItem(source_id=
    f"ref{i:02d}", source_kind="narrative", text=reference))`, which runs the production
    `SentenceIndex` / SaT path (sat-3l-sm @ 137da054…, threshold 0.025, line by line, 25-character
    joining rule, table rows, 2,000-character cap). Each unit's `text` is passed verbatim, with its
    trailing separators, as production's `direct_citation` passes `exact_quote`. Whitespace-only
    units are dropped, as binding rejects them (`empty_unit`). The units of all references of the
    row are pooled in reference order then unit order, as the regex run pooled its units.
  - **TH**: no new translation. Each English reference is re-split with the regex rule, keeping
    which units came from which `\n`-paragraph (the units are checked to equal the plan's
    `unit_keys` in order). A Thai reference is rebuilt by joining the cached Thai translations of
    one paragraph's units with a single space, and the paragraphs with a single `\n`. Reason: the
    English units were separated by whitespace inside a paragraph and by a newline between
    paragraphs; a space is also how Thai marks a sentence break, and keeping the newline keeps the
    line structure SaT is run on (production splits line by line). Pieces the regex dropped
    (3 characters or fewer) have no translation and are absent from the Thai text; the English S
    text keeps them. The Thai reference is then cut and pooled exactly as EN.
  - Claim: EN `row["claim"].strip()`; TH the cached translation of that claim.
- All conditions call `B1Verifier.verify(claim, units)` of the production verifier
  (`app.trace.b1_verifier`, `b1_lr.json`, local `models/nli_mdeberta` and
  `models/source_selector_mpnet`, hashes checked by the loader).

## Empty references

The 75 OOD rows whose `references` list is empty get the original protocol: the empty premise is
scored, `verifier.nli.predict("", claim)` then the frozen LR, in every condition and language.
Any other row whose pooled S units come out empty is scored the same way and counted.

## Metrics

Per split × language × condition: N, TP/FP/TN/FN, accuracy, precision, recall, supported F1,
FSR (false support rate = FP / gold negatives; the original's FAR) and FRR (FN / gold positives),
using `paired_statistics.confusion`.

Uncertainty: the original scheme of `summarize_mt_th.transfer_bootstrap`: 2,000 resamples of
question/response clusters (`data.cluster_key`) within each source subset, subsets in sorted
order, one `numpy.random.default_rng(20261007)` generator, one index draw per subset shared by
all conditions (so the draws are the original ones and R-pub intervals must reproduce the
published intervals). Reported: 95% percentile intervals per condition and for the paired
differences S − R-pub (primary) and S − R-loc (control), for accuracy, precision, recall, F1,
FSR and FRR. Row-wise exact McNemar on correctness, descriptive only.

Also: units per row (median, and mean) for regex and S, EN and TH; selected units per row (median);
rows whose NLI input exceeds 512 tokens (`truncated`) per condition; decision agreement R-loc vs
R-pub; runtime.

## Compute

CPU only (`CUDA_VISIBLE_DEVICES=""`): the GPU is held by the OCR re-run in `cybercase-backend`
(3.8 of 4 GB in use at the time of fixing). The production verifier also runs on CPU (the loader
never moves it). SaT also runs on CPU. Environment: venv `C:/Users/kkham/venvs/cc-gpu-vram`
(torch 2.11.0+cu128, transformers 5.8.0, wtpsplit 2.2.2, pythainlp 5.3.7; sentence-transformers
5.4.1, where production pins 6.0.0, which the R-loc control covers),
`HF_HOME=backend/models/hf`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`.

A 20-row smoke (the first 20 plan rows) runs first and is checked before the full run.

## Files

`run_sat.py` scores, `summarize_sat.py` summarizes. Per-row outputs (`scores*.jsonl`, logs) are
git-ignored; `summary.json` and `RESULTS.md` are the results.

## Amendment 1, 2026-10-25 07:05 Asia/Bangkok (after the smoke, before the full run)

The 20-row CPU smoke (`smoke/`) passed its checks: every R-loc decision equals the published
decision on those rows, the regex units and Thai inputs match the published input hashes, and the
SaT units look as expected. But CPU throughput with the stored fp16 NLI is about 20 seconds per
row (four verifications), about 18 hours for 3,296 rows. Changed, nothing else:

- SaT cutting stays on CPU and runs first, for all rows, into `units.jsonl` (`--cut-only`).
- The verifier (selector and NLI, all four conditions) runs on CUDA, the device of the published
  run, once the OCR re-run in `cybercase-backend` has finished and freed the GPU. The R-loc
  control is then also a same-device reproduction of R-pub. The production server runs the
  verifier on CPU; the CPU smoke rows are kept to compare CPU and CUDA decisions on 20 rows.
- A 20-row CUDA smoke runs and is checked before the full CUDA run.

## Amendment 2, 2026-10-25 08:22 Asia/Bangkok (Owner additions approved 2026-10-25, before new inference)

The owner adds two conditions to this re-measurement (approved 2026-10-25), with the GPU now
freed following completion of the OCR downstream run at 07:59.

### Background and Normalization Rule

The mDeBERTa NLI tokenizer normalizes with NFC, but its vocabulary contains only the decomposed form
of the Thai vowel sara am (`U+0E4D U+0E32`), converting every precomposed `U+0E33` to `[UNK]` (id 3).
The MPNet selector tokenizer does not suffer from this issue (producing `'ทํางาน'`, no `[UNK]`).
Applying `unicodedata.normalize('NFKC', ...)` directly to the NLI premise and hypothesis immediately
prior to the mDeBERTa tokenizer eliminates the `[UNK]` tokens while preserving the selector input.
This reproduces the exact normalization rule of `raw/b1-mt-th-normalized/` (confirmed on row 0:
raw tokens 277, p_supported 0.8121760492171165, matching `raw/b1-mt-th-normalized/scores.jsonl` to 16 decimal places).

### Added Conditions

1. **NFKC on NLI Inputs across AttributionBench:**
   - Evaluated on premise and hypothesis immediately prior to mDeBERTa tokenizer, keeping selector inputs unchanged.
   - Run with SaT units across all four split × language cells: `EN-ID`, `EN-OOD`, `TH-ID`, `TH-OOD` (`sat_nfkc`).
   - Run with regex units on `TH-ID` and `TH-OOD` (`rloc_th_nfkc`) as an exact reproduction control against the
     published normalized rerun (`raw/b1-mt-th-normalized/`, ID-TH FSR 49.19% vs 52.05% baseline).
2. **WiCE Test Check (1,070 rows):**
   - Run frozen B1-LR on the official WiCE test split (1,070 rows, located locally at `backend/research/nli_grounding/data/wice/test.jsonl`).
   - Run under two conditions: without NFKC and with NFKC on the NLI inputs, holding all else identical (selector threshold $\tau=0.20$,
     same candidate sentence units, same frozen WiCE TRAIN logistic regression).
   - Report decision changes, confusion matrices, accuracy, precision, recall, supported F1, FSR, and FRR for both.
3. **English Exposure Count:**
   - Count for each English set (`WiCE test`, `EN-ID`, `EN-OOD`) how many claim and unit texts are actually altered by
     `unicodedata.normalize('NFKC', text)` to quantify whether English texts are affected.
4. **Combined Reporting:**
   - Report per condition and cell: metrics, paired differences vs published regex baseline and vs SaT-without-NFKC
     with cluster-bootstrap 95% CIs, decision change counts, and WiCE before/after metrics.

