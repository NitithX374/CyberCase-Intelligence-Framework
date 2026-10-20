# SaT and PyThaiNLP crfcut: what was checked, 2026-10-10

Question from the owner (2026-10-10): show, if possible, why the backend splits sentences with SaT (wtpsplit) and not with PyThaiNLP `crfcut`.

## 1. No gold Thai sentence boundaries on this machine

An accuracy comparison (boundary precision, recall, F1) needs text with human sentence boundaries. None exists offline here, so no accuracy was measured and none is reported.

Searched on 2026-10-10 with `find` under `F:/` (depth 7 and 12) and `C:/Users/kkham` (depth 8 and 12), excluding `node_modules` and `.git`, for names matching `*th_pud*`, `*UD_Thai*`, `*.conllu`, `*ud-treebanks*`, `*pud*`, `*orchid*`, `*lst20*`, `*ted*thai*`, `*thai*sent*`, `*sent*seg*`, `*pythainlp-data*`, `*ersatz*`, `*opus100*`, `*nltk_data*`, `*brown*`, `*treebank*`. Also listed: the Hugging Face hub and datasets caches in `C:/Users/kkham/.cache/huggingface`, `C:/Users/kkham/pythainlp-data`, the NLTK data folders, and the caches inside the `cybercase-backend` and `cybercase-rag-service` containers.

Found: only the PyThaiNLP package files (the `crfcut` model and ORCHID part-of-speech models, no sentence corpus), `C:/Users/kkham/pythainlp-data` (`db.json`, `thai_nner_model.pth`), NLTK `wordnet`, `omw-1.4` and `punkt_tab` (no corpora with sentence boundaries), and datasets without sentence boundaries (XL-Sum, ThaiSum, Thai law corpora, Thai OCR sets, FEVER). Nothing was downloaded.

## 2. What was measured instead (descriptive only)

Because no gold exists, the run below says how differently the two splitters cut the same text and how long they take. It does not say which one is right.

Data: the first 100 rows, in file order, of the XL-Sum test splits for Thai and English (Hasan et al., Findings of ACL-IJCNLP 2021, doi 10.18653/v1/2021.findings-acl.413), read from the local Hugging Face cache, snapshot `ab04842511fc357feae53281fd104aa3c36dff07`:

| Split | File | sha256 |
|---|---|---|
| Thai test | `thai/test/0000.parquet` | `788a933a73e3502d1a7af6322cd8c576bb3a49f8d2e19a1473a02d5da1326cc7` |
| English test | `english/test/0000.parquet` | `eb4e684461594f8245d4e842579ad62c4e543d031270ee113bbff4624b6f9f1d` |

The 200 selected articles total 360,387 Thai and 290,264 English characters. Each article's `text` has no line break, so each article is one line for the backend. The article text is not copied into this folder; `prepare_inputs.py` rebuilds the input file (sha256 `008f62fe338cc40fb1a258d09dc3cc3aa4e96b2a36a5a96a52872cc118d093b8`).

How each splitter was run, as the backend at commit 72b98657 runs it (`backend/app/trace/sentences.py`):

- each text is cut at line breaks (`line_spans`), and the splitter is called once per non-empty line;
- SaT: `SaT("sat-3l-sm").split(line)` with every library default (no threshold argument, which in wtpsplit 2.2.2 means 0.25 for a model name containing "sm"; stride 64; block size 512 tokens);
- crfcut: `pythainlp.tokenize.sent_tokenize(line, engine="crfcut")` (keep_whitespace defaults to True);
- units follow the backend rule: pieces are joined until a unit has at least 25 characters once spaces at its ends are trimmed, a short remainder joins the unit before it, and a line whose pieces do not rejoin to the line becomes one unit. `line_spans`, `line_sentences`, `stripped` and `MIN_SENTENCE_CHARS` in `compare_segmenters.py` are verbatim copies of 72b98657 (checked by comparing the AST source segments). The table and row-start rule of `sources/evidence.py` does not apply, because XL-Sum text has no tables.

Measures:

- pieces per 1,000 characters: raw splitter output;
- units per 1,000 characters and median unit length: after the 25-character rule;
- boundary agreement F1: a boundary is the first non-space character after a piece; agreement F1 = 2 x shared / (SaT boundaries + crfcut boundaries). It is symmetric and is not accuracy;
- time: wall-clock seconds of the splitter call only (model loading excluded, a short untimed warm-up first).

## 3. Results

Cutting (`results/summary.json`, 100 articles per language):

| Measure | Thai SaT | Thai crfcut | English SaT | English crfcut |
|---|---|---|---|---|
| Pieces per 1,000 characters | 5.36 | 13.17 | 8.60 | 7.20 |
| Units per 1,000 characters (25-character rule) | 5.15 | 10.75 | 8.05 | 7.10 |
| Median unit length (characters) | 145.5 | 71.0 | 115.5 | 123.0 |
| Lines whose pieces did not rejoin | 0 | 0 | 0 | 0 |
| Boundaries | 1,833 | 4,645 | 2,397 | 1,991 |
| Shared boundaries | 1,101 | 1,101 | 1,974 | 1,974 |
| Boundary agreement F1 | 0.34 | | 0.90 | |
| Unit-start agreement F1 | 0.35 | | 0.93 | |

On Thai news the two splitters mostly disagree, and crfcut cuts about 2.5 times as often. On English news crfcut's boundaries are almost all SaT boundaries too (1,974 of 1,991), so crfcut does not break down on punctuated English text.

Speed, milliseconds per 1,000 characters (`results/timing_by_length.json`: 5 articles per language of at least 4,000 characters, each cut to its first N characters, fastest of 3 calls):

| Line length (characters) | Thai SaT | Thai crfcut | English SaT | English crfcut |
|---|---|---|---|---|
| 250 | 136.5 | 14.4 | 114.2 | 12.1 |
| 500 | 94.5 | 12.0 | 73.0 | 9.2 |
| 1,000 | 77.3 | 10.4 | 61.8 | 13.0 |
| 2,000 | 203.6 | 11.2 | 71.4 | 10.7 |
| 4,000 | 398.9 | 12.1 | 239.0 | 11.8 |

SaT's cost per character rises once a line passes about 510 XLM-R tokens, because wtpsplit then reads overlapping 512-token windows every 64 tokens. The model processed about 290 to 320 token positions per 1,000 Thai characters on lines up to 1,000 characters, 666 at 2,000 and 1,459 at 4,000 (`sat_token_positions_per_1000_chars`; computed from the tokenizer and the window rule in `wtpsplit/extract.py`, not from the clock).

Whole articles, one pass (`results/summary.json`, the 100-article run): SaT 1,726.9 ms per 1,000 Thai characters (median article 804.7) and 437.6 for English (median 225.0); crfcut 96.2 for Thai (median 36.9) and 19.9 for English (median 15.3). The repeated run on the first 20 articles per language (`results/timing_repeat.json`, fastest of 3) gave SaT 1,257.0 and crfcut 29.6 for Thai, SaT 903.2 and crfcut 19.3 for English. SaT model loading took 10.86 seconds.

The clock numbers vary by a factor of 2 to 4 between runs: the laptop was shared with other work (host CPU load 67 to 77 percent before and after the timing runs) and the long runs kept the CPU busy for 10 to 14 minutes. Read them as orders of magnitude. Across all runs SaT was about 5 to 47 times slower than crfcut.

## 4. Published Thai results (the accuracy side)

WtP, Minixhofer, Pfeiffer and Vulić, ACL 2023, doi 10.18653/v1/2023.acl-long.398, Table 4, p. 7220 (Thai sentence segmentation F1; ORCHID full set, UD and OPUS100 test sets; PyThaiNLP v3.1.1):

| System | ORCHID | UD | OPUS100 | Macro average |
|---|---|---|---|---|
| PyThaiNLP | 55.6 | 64.7 | 62.5 | 60.9 |
| WtP (no adaptation) | 67.9 | 69.5 | 68.8 | 68.7 |
| WtP adapted to OPUS100 | 69.2 | 78.0 | 71.5 | 72.9 |
| WtP-PUNCT adapted to OPUS100 | 51.8 | 77.1 | 72.9 | 67.3 |

The paper says WtP "consistently outperforms PyThaiNLP". It names the version (3.1.1) but not the engine; `crfcut` is the default `sent_tokenize` engine in the PyThaiNLP 3.1 documentation.

SaT, Frohmann, Sterner, Vulić, Minixhofer and Schedl, EMNLP 2024, doi 10.18653/v1/2024.emnlp-main.665, Table 31, p. 11940 (3-layer variants of all models; UD v2.13 Thai PUD, 1.0k sentences; OPUS100 Thai, 2.0k sentences, per Table 15):

| System | UD Thai | OPUS100 Thai |
|---|---|---|
| SpaCy multilingual | - | 21.7 |
| Llama 3 8B | 81.4 | 66.0 |
| Command R | 12.4 | 10.6 |
| WtP | 67.3 | 66.6 |
| WtP-T | - | 69.7 |
| WtP-PUNCT | - | 71.3 |
| SaT | 72.7 | 68.0 |
| SaT+SM (released as sat-3l-sm) | 71.2 | 72.9 |
| SaT+LoRA | - | 73.7 |

The SaT paper does not evaluate PyThaiNLP. SaT+SM continues training SaT on already-segmented sentences, sampled evenly from clean text, text with all casing and punctuation removed, and randomly corrupted text (punctuation duplicated or removed, lowercasing, spaces between sentences removed or added), "to be even less dependent on patterns such as punctuation, spaces, and casing" (Section 3; details in Appendix A.2). Its training text is the UD training set, or OPUS100 or NLLB for languages without UD data. Thai PUD is a test-only treebank, so Thai training text came from OPUS100 or NLLB; the paper does not say which (the WtP paper notes that OPUS100 has no Thai training data). The paper gives 0.5 seconds per 1,000 sentences for the 3-layer models on an Nvidia GTX 2080 Ti GPU; the backend runs on CPU.

The PyThaiNLP documentation describes `crfcut` as a conditional random field trained on the TED dataset, with space-correct accuracy of 82% on TED and 87% on ORCHID against 95% for the state of the art. Space-correct accuracy is a different measure from the F1 above.

## 5. Why the repository uses SaT

Commit 1e2ea927 (2026-10-08, "integrate SaT sentence segmenter and streamline finding traceability") added SaT with the reason "Integrate wtpsplit (SaT-3l-sm) sentence segmentation with CRF fallback for robust Thai text segmentation". `backend/requirements.txt` says "wtpsplit provides the robust SaT neural sentence segmenter; pythainlp and python-crfsuite provide fallbacks". The same commit moved `EVIDENCE_VERSION` from `evidence_units_v1` to `evidence_units_v2`. No research note, measurement or test in the repository compares the two splitters. At 72b98657, `CLAUDE.md` and `backend/ARCHITECTURE.md` still describe `crfcut` as the splitter.

## 6. Environment and commands

- Container `cybercase-backend`, image `sha256:dd51e8effb5d09c20d5c2568baf7bf425e8a8ed4df1279d1e818350b34c683b6`, created 2026-10-10T05:29:47Z from the working tree of `F:/Cybercase Framework` (its `trace/sentences.py` differs from 72b98657 in one import line only).
- Python 3.11.17, wtpsplit 2.2.2, pythainlp 5.4.0, python-crfsuite 0.9.12, torch 2.11.0+cpu (4 threads), transformers 5.8.0, numpy 2.4.6, huggingface-hub 1.33.0.
- SaT weights: `segment-any-text/sat-3l-sm` snapshot `137da054051ad9f1eac42025f758db4ac9f22535` under `HF_HOME=/app/models/hf`, read with `HF_HUB_OFFLINE=1`.
- CPU: 11th Gen Intel Core i5-11320H, 8 logical CPUs, WSL2 kernel 6.6.87.2.
- Host side: Python 3.14.0 and pyarrow 24.0.0 for `prepare_inputs.py`.

Commands (Git Bash, `MSYS_NO_PATHCONV=1`; `$S` is a scratch folder outside the book):

```
python prepare_inputs.py "$S/xlsum_th_en_100.jsonl"
docker exec cybercase-backend mkdir -p /tmp/segcmp
docker cp "$S/xlsum_th_en_100.jsonl" cybercase-backend:/tmp/segcmp/
docker cp compare_segmenters.py cybercase-backend:/tmp/segcmp/
docker cp timing_repeat.py cybercase-backend:/tmp/segcmp/
docker cp timing_by_length.py cybercase-backend:/tmp/segcmp/
ENV="-e PYTHONDONTWRITEBYTECODE=1 -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -e PYTHAINLP_DATA_DIR=/tmp/segcmp/pythainlp-data"
docker exec -w /tmp/segcmp $ENV cybercase-backend python /tmp/segcmp/compare_segmenters.py /tmp/segcmp/xlsum_th_en_100.jsonl /tmp/segcmp/out
docker exec -w /tmp/segcmp $ENV cybercase-backend python /tmp/segcmp/timing_repeat.py /tmp/segcmp/xlsum_th_en_100.jsonl /tmp/segcmp/out/timing_repeat.json
docker exec -w /tmp/segcmp $ENV cybercase-backend python /tmp/segcmp/timing_by_length.py /tmp/segcmp/xlsum_th_en_100.jsonl /tmp/segcmp/out/timing_by_length.json
docker cp cybercase-backend:/tmp/segcmp/out/. results/
docker exec cybercase-backend rm -rf /tmp/segcmp
```

Run times (UTC, 2026-10-10): `compare_segmenters.py` 05:56:07 to 06:10:05, `timing_repeat.py` 06:11:23 to 06:21:40, `timing_by_length.py` 06:22:18 to 06:23:38. An earlier attempt of `compare_segmenters.py` with three timing repeats ran slower than planned and was stopped; nothing from it is kept.

## 7. Files

| File | What it holds |
|---|---|
| `prepare_inputs.py` | builds the 200-article input file from the XL-Sum cache |
| `compare_segmenters.py` | cutting measures and one timed pass |
| `timing_repeat.py` | 20 articles per language, 3 calls each |
| `timing_by_length.py` | prefixes of 250 to 4,000 characters, 3 calls each, and SaT token positions |
| `results/input_provenance.json` | parquet paths and hashes, input hash |
| `results/summary.json` | environment and per-language results of `compare_segmenters.py` |
| `results/per_doc.jsonl` | per article: id, length, seconds, piece counts, boundary offsets, unit starts and lengths (no text) |
| `results/timing_repeat.json`, `results/timing_by_length.json` | timing results with every call's seconds |
| `results/*_stderr.txt`, `results/*_run.txt`, `results/run_times_utc.txt` | logs, run times, host CPU load |

## 8. Limits

- No accuracy on our data: agreement is not correctness, and the published F1 comes from other text (ORCHID, UD PUD, OPUS100), not case sources.
- XL-Sum articles are clean BBC news with no line breaks. Case sources have line breaks and OCR text; their lines are shorter, which makes SaT cheaper per character than the whole-article numbers.
- The two papers' numbers cannot be chained: WtP scores 69.5 (UD) and 68.8 (OPUS100) in its own paper and 67.3 and 66.6 in the SaT paper.
- Clock times are from a shared laptop CPU and vary between runs.
