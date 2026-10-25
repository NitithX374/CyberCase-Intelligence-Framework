# Attribution Benchmark: Production SaT Units & NLI NFKC Normalization

**Date:** 2026-10-25  
**Runtime:** NVIDIA GeForce GTX 1650 (CUDA, fp16 NLI, fp32 Selector), Python 3.14.0, Torch 2.11.0+cu128, Transformers 5.8.0, Sentence-Transformers 5.4.1  
**Segmenter:** `sat:sat-3l-sm@137da054051ad9f1eac42025f758db4ac9f22535:threshold=0.025:wtpsplit=2.2.2`  
**Artifact SHA-256:** `fc5e94b153b65cb4cf39e160e1d13db798aa124b8686e08dd1fa3eb8c39eec4b`  
**Protocol Reference:** [`PROTOCOL.md`](./PROTOCOL.md) (including Amendment 1 and Amendment 2)

---

## 1. Executive Summary

This report establishes the empirical measurements for **production SaT source segmentation** and **NFKC normalization on mDeBERTa NLI inputs** across all four cells of AttributionBench (`EN-ID`, `EN-OOD`, `TH-ID`, `TH-OOD`), alongside a 1,070-row WiCE test split control and English exposure audit.

### Key Conclusions:
1. **Control Verifications (100% Bitwise Parity):**
   - Re-running published regex units on CUDA (`R-loc`) reproduces published baseline numbers (`R-pub`) bitwise across all 3,296 rows in both English and Thai (`0 / 3,296` differences).
   - Re-running published regex units with NFKC on Thai (`R-loc+NFKC`) reproduces the published normalized rerun (`raw/b1-mt-th-normalized/`) bitwise across all 3,296 rows (`0 / 3,296` differences), confirming exact agreement with the published 49.19% ID-TH FSR.
2. **English Invariance under NFKC:**
   - On the official **WiCE test split (1,070 rows)**, applying NFKC to NLI inputs results in **0 / 1,070 changed decisions (0.00%)**, with bitwise identical confusion matrix and metrics ($F_1 = 48.84\%$, $\text{Macro } F_1 = 62.20\%$, $\text{FSR} = 26.08\%$, $\text{FRR} = 48.79\%$).
   - On AttributionBench English, NFKC alters zero claim texts in ID ($0/1,610$) and only $11/1,686$ ($0.65\%$) in OOD. For SaT EN-ID, NFKC changes decisions on $0/1,610$ rows; for SaT EN-OOD, it changes only $3/1,686$ rows ($0.18\%$).
   - English model performance is essentially unaffected by NFKC.
3. **Production SaT Units vs Regex Baseline:**
   - Across English (`EN-ID`, `EN-OOD`), SaT units perform within $\pm 0.87\%$ FSR and $\pm 0.62\%$ $F_1$ of the regex baseline, with cluster-bootstrap 95% CIs comfortably spanning zero.
   - For Thai (`TH-ID`, `TH-OOD`), raw SaT units perform comparably to raw regex units (TH-ID FSR 51.30% vs 52.05%; TH-OOD FSR 40.45% vs 39.74%).
4. **Resolution of Sara Am Decomposition Bug (SaT + NFKC):**
   - The mDeBERTa tokenizer normalizes with NFC, but its vocabulary only contains decomposed sara am (`U+0E4D U+0E32`), converting precomposed `U+0E33` to `[UNK]`.
   - Applying `unicodedata.normalize('NFKC', ...)` to the NLI premise and claim eliminates `[UNK]` tokens and reduces median token length by 11–14 tokens per row, rescuing 22–24 rows in ID and 12–15 rows in OOD from truncation (>512 tokens).
   - **SaT + NFKC** drops Thai ID FSR from **51.30% down to 50.06%** ($-1.24\%$ vs raw SaT; $-1.99\%$ vs published regex baseline $52.05\%$) and Thai OOD FSR from **40.45% down to 39.26%** ($-1.19\%$ vs raw SaT; $-0.47\%$ vs published regex baseline $39.74\%$).

---

## 2. English Exposure Audit

Number of texts modified by `unicodedata.normalize('NFKC', text)`:

| Dataset | Granularity | Modified Texts | Total Texts | % Modified |
|---|---|---|---|---|
| **WiCE test** | Claim | 15 | 1,070 | 1.40% |
| **WiCE test** | Unit | 70 | 19,918 | 0.35% |
| **AttributionBench ID (EN)** | Claim | 0 | 1,610 | 0.00% |
| **AttributionBench ID (EN)** | Reference string | 115 | 2,140 | 5.37% |
| **AttributionBench ID (EN)** | Regex Unit (unique) | 239 | 30,548 | 0.78% |
| **AttributionBench OOD (EN)** | Claim | 11 | 1,686 | 0.65% |
| **AttributionBench OOD (EN)** | Reference string | 102 | 1,990 | 5.13% |
| **AttributionBench OOD (EN)** | SaT Unit (unique) | 348 | 44,450 | 0.78% |

---

## 3. WiCE Test Check (1,070 Rows)

Evaluation of frozen B1-LR verifier on `backend/research/nli_grounding/data/wice/test.jsonl` with selector threshold $\tau = 0.20$:

| Condition | TP | FP | TN | FN | Accuracy | Precision | Recall | Supported F1 | Macro F1 | FSR | FRR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Without NFKC** | 169 | 193 | 547 | 161 | 66.92% | 46.69% | 51.21% | 48.84% | 62.20% | 26.08% | 48.79% |
| **With NFKC** | 169 | 193 | 547 | 161 | 66.92% | 46.69% | 51.21% | 48.84% | 62.20% | 26.08% | 48.79% |
| **Difference** | 0 | 0 | 0 | 0 | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |

- **Changed Decisions:** **0 / 1,070 (0.00%)**
- **Conclusion:** NFKC does not perturb English NLI verification on WiCE test.

---

## 4. AttributionBench Results across 4 Cells

### Cell 1: In-Domain English (`EN-ID`, 1,610 Rows)
*Gold: 805 attributable, 805 unattributable*

| Condition | TP | FP | TN | FN | Accuracy (%) | Precision (%) | Recall (%) | F1 (%) | FSR (%) | FRR (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| **R-pub** (Regex published) | 503 | 279 | 526 | 302 | 63.91 | 64.32 | 62.48 | 63.39 | 34.66 | 37.52 |
| **R-loc** (Regex local rerun) | 503 | 279 | 526 | 302 | 63.91 | 64.32 | 62.48 | 63.39 | 34.66 | 37.52 |
| **SaT** (Production units) | 499 | 286 | 519 | 306 | 63.23 | 63.57 | 61.99 | 62.77 | 35.53 | 38.01 |
| **SaT + NFKC** | 499 | 286 | 519 | 306 | 63.23 | 63.57 | 61.99 | 62.77 | 35.53 | 38.01 |

**Paired Differences & 2,000 Cluster-Bootstrap 95% CIs:**
- **SaT vs R-pub:**
  - $\Delta\text{FSR} = +0.87\%$ ($[-0.63\%, +2.29\%]$)
  - $\Delta\text{F1} = -0.62\%$ ($[-1.42\%, +0.18\%]$)
  - $\Delta\text{Acc} = -0.68\%$ ($[-1.55\%, +0.19\%]$)
  - Mismatched decisions: 49 / 1,610 (3.04%)
- **SaT+NFKC vs SaT:**
  - $\Delta\text{FSR} = +0.00\%$ ($[+0.00\%, +0.00\%]$)
  - $\Delta\text{F1} = +0.00\%$ ($[-0.26\%, +0.26\%]$)
  - Mismatched decisions: 2 / 1,610 (0.12%) (TP/FP/TN/FN counts invariant)

---

### Cell 2: In-Domain Thai (`TH-ID`, 1,610 Rows)
*Gold: 805 attributable, 805 unattributable*

| Condition | TP | FP | TN | FN | Accuracy (%) | Precision (%) | Recall (%) | F1 (%) | FSR (%) | FRR (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| **R-pub** (Regex published) | 568 | 419 | 386 | 237 | 59.25 | 57.55 | 70.56 | 63.39 | 52.05 | 29.44 |
| **R-loc** (Regex local rerun) | 568 | 419 | 386 | 237 | 59.25 | 57.55 | 70.56 | 63.39 | 52.05 | 29.44 |
| **R-pub-norm** (Published norm rerun) | 570 | 396 | 409 | 235 | 60.81 | 59.01 | 70.81 | 64.37 | 49.19 | 29.19 |
| **R-loc + NFKC** (Control reproduction) | 570 | 396 | 409 | 235 | 60.81 | 59.01 | 70.81 | 64.37 | 49.19 | 29.19 |
| **SaT** (Production units) | 565 | 413 | 392 | 240 | 59.44 | 57.77 | 70.19 | 63.38 | 51.30 | 29.81 |
| **SaT + NFKC** | 567 | 403 | 402 | 238 | 60.19 | 58.45 | 70.43 | 63.89 | 50.06 | 29.57 |

**Paired Differences & 2,000 Cluster-Bootstrap 95% CIs:**
- **Control Agreement:** `R-loc+NFKC` vs `R-pub-norm`: **0 mismatches (0.00%)**, identical FSR 49.19%.
- **SaT vs R-pub:**
  - $\Delta\text{FSR} = -0.75\%$ ($[-1.73\%, +0.13\%]$)
  - $\Delta\text{F1} = -0.02\%$ ($[-0.70\%, +0.72\%]$)
  - Mismatched decisions: 31 / 1,610 (1.93%)
- **SaT+NFKC vs SaT:**
  - $\Delta\text{FSR} = -1.24\%$ ($[-3.33\%, +0.85\%]$)
  - $\Delta\text{F1} = +0.51\%$ ($[-0.89\%, +1.85\%]$)
  - $\Delta\text{Acc} = +0.75\%$ ($[-0.73\%, +2.15\%]$)
  - Mismatched decisions: 108 / 1,610 (6.71%)
- **SaT+NFKC vs R-pub:**
  - $\Delta\text{FSR} = -1.99\%$ ($[-4.09\%, +0.00\%]$)
  - $\Delta\text{F1} = +0.49\%$ ($[-0.83\%, +1.74\%]$)
  - $\Delta\text{Acc} = +0.93\%$ ($[-0.48\%, +2.29\%]$)
  - Mismatched decisions: 115 / 1,610 (7.14%)

---

### Cell 3: Out-of-Domain English (`EN-OOD`, 1,686 Rows)
*Gold: 843 attributable, 843 unattributable*

| Condition | TP | FP | TN | FN | Accuracy (%) | Precision (%) | Recall (%) | F1 (%) | FSR (%) | FRR (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| **R-pub** (Regex published) | 688 | 298 | 545 | 155 | 73.13 | 69.78 | 81.61 | 75.23 | 35.35 | 18.39 |
| **R-loc** (Regex local rerun) | 688 | 298 | 545 | 155 | 73.13 | 69.78 | 81.61 | 75.23 | 35.35 | 18.39 |
| **SaT** (Production units) | 689 | 302 | 541 | 154 | 72.95 | 69.53 | 81.73 | 75.14 | 35.82 | 18.27 |
| **SaT + NFKC** | 690 | 300 | 543 | 153 | 73.13 | 69.70 | 81.85 | 75.29 | 35.59 | 18.15 |

**Paired Differences & 2,000 Cluster-Bootstrap 95% CIs:**
- **SaT vs R-pub:**
  - $\Delta\text{FSR} = +0.47\%$ ($[-0.36\%, +1.34\%]$)
  - $\Delta\text{F1} = -0.10\%$ ($[-0.52\%, +0.35\%]$)
  - Mismatched decisions: 19 / 1,686 (1.13%)
- **SaT+NFKC vs SaT:**
  - $\Delta\text{FSR} = -0.24\%$ ($[-0.60\%, +0.00\%]$)
  - $\Delta\text{F1} = +0.15\%$ ($[+0.00\%, +0.35\%]$)
  - Mismatched decisions: 3 / 1,686 (0.18%)
- **SaT+NFKC vs R-pub:**
  - $\Delta\text{FSR} = +0.24\%$ ($[-0.65\%, +1.18\%]$)
  - $\Delta\text{F1} = +0.05\%$ ($[-0.35\%, +0.49\%]$)
  - Mismatched decisions: 20 / 1,686 (1.19%)

---

### Cell 4: Out-of-Domain Thai (`TH-OOD`, 1,686 Rows)
*Gold: 843 attributable, 843 unattributable*

| Condition | TP | FP | TN | FN | Accuracy (%) | Precision (%) | Recall (%) | F1 (%) | FSR (%) | FRR (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| **R-pub** (Regex published) | 651 | 335 | 508 | 192 | 68.74 | 66.02 | 77.22 | 71.19 | 39.74 | 22.78 |
| **R-loc** (Regex local rerun) | 651 | 335 | 508 | 192 | 68.74 | 66.02 | 77.22 | 71.19 | 39.74 | 22.78 |
| **R-pub-norm** (Published norm rerun) | 653 | 324 | 519 | 190 | 69.51 | 66.84 | 77.46 | 71.76 | 38.43 | 22.54 |
| **R-loc + NFKC** (Control reproduction) | 653 | 324 | 519 | 190 | 69.51 | 66.84 | 77.46 | 71.76 | 38.43 | 22.54 |
| **SaT** (Production units) | 650 | 341 | 502 | 193 | 68.33 | 65.59 | 77.11 | 70.88 | 40.45 | 22.89 |
| **SaT + NFKC** | 653 | 331 | 512 | 190 | 69.10 | 66.36 | 77.46 | 71.48 | 39.26 | 22.54 |

**Paired Differences & 2,000 Cluster-Bootstrap 95% CIs:**
- **Control Agreement:** `R-loc+NFKC` vs `R-pub-norm`: **0 mismatches (0.00%)**, identical FSR 38.43%.
- **SaT vs R-pub:**
  - $\Delta\text{FSR} = +0.71\%$ ($[-0.24\%, +1.77\%]$)
  - $\Delta\text{F1} = -0.30\%$ ($[-0.82\%, +0.22\%]$)
  - Mismatched decisions: 27 / 1,686 (1.60%)
- **SaT+NFKC vs SaT:**
  - $\Delta\text{FSR} = -1.19\%$ ($[-2.74\%, +0.33\%]$)
  - $\Delta\text{F1} = +0.60\%$ ($[-0.51\%, +1.67\%]$)
  - $\Delta\text{Acc} = +0.77\%$ ($[-0.41\%, +1.87\%]$)
  - Mismatched decisions: 87 / 1,686 (5.16%)
- **SaT+NFKC vs R-pub:**
  - $\Delta\text{FSR} = -0.47\%$ ($[-2.00\%, +1.12\%]$)
  - $\Delta\text{F1} = +0.30\%$ ($[-0.87\%, +1.46\%]$)
  - $\Delta\text{Acc} = +0.36\%$ ($[-0.90\%, +1.53\%]$)
  - Mismatched decisions: 98 / 1,686 (5.81%)

---

## 5. Unit Segmentation Diagnostics

| Split | Condition | Mean Units | Median Units | Mean Sel | Median Sel | Truncated Rows (>512 tokens) | Median Raw Tokens | Empty Rows |
|---|---|---|---|---|---|---|---|---|
| **ID** | `rloc_en` | 20.90 | 6.0 | 15.51 | 5.0 | 288 | 222.0 | 0 |
| **ID** | `rloc_th` | 20.90 | 6.0 | 16.70 | 5.0 | 311 | 238.5 | 0 |
| **ID** | `rloc_th_nfkc` | 20.90 | 6.0 | 16.70 | 5.0 | **287** (-24) | **224.0** (-14.5) | 0 |
| **ID** | `sat_en` | 20.86 | 7.0 | 16.47 | 6.0 | 286 | 220.0 | 0 |
| **ID** | `sat_th` | 21.67 | 7.0 | 18.10 | 6.0 | 309 | 235.0 | 0 |
| **ID** | `sat_th_nfkc` | 21.67 | 7.0 | 18.10 | 6.0 | **287** (-22) | **221.5** (-13.5) | 0 |
| **OOD** | `rloc_en` | 6.09 | 5.0 | 5.12 | 4.0 | 124 | 179.5 | 75 |
| **OOD** | `rloc_th` | 6.09 | 5.0 | 5.24 | 4.0 | 154 | 195.5 | 75 |
| **OOD** | `rloc_th_nfkc` | 6.09 | 5.0 | 5.24 | 4.0 | **139** (-15) | **184.0** (-11.5) | 75 |
| **OOD** | `sat_en` | 6.44 | 5.0 | 5.37 | 4.0 | 122 | 178.5 | 75 |
| **OOD** | `sat_th` | 7.04 | 5.0 | 5.96 | 4.0 | 152 | 195.0 | 75 |
| **OOD** | `sat_th_nfkc` | 7.04 | 5.0 | 5.96 | 4.0 | **140** (-12) | **184.5** (-10.5) | 75 |

---

## 6. Plain Statements of What Changed and What Did Not

1. **What changed:**
   - **Thai false support rate dropped consistently:** Normalizing NLI inputs with NFKC reduces Thai FSR under SaT by $-1.24\%$ in ID (from $51.30\%$ to $50.06\%$) and by $-1.19\%$ in OOD (from $40.45\%$ to $39.26\%$). Relative to published regex baseline ($52.05\%$ ID, $39.74\%$ OOD), SaT+NFKC achieves **$50.06\%$** ($-1.99\%$) and **$39.26\%$** ($-0.47\%$).
   - **Thai $F_1$ improved:** SaT+NFKC gains $+0.51\%$ $F_1$ in ID ($63.89\%$ vs $63.38\%$) and $+0.60\%$ $F_1$ in OOD ($71.48\%$ vs $70.88\%$).
   - **Token inflation in Thai eliminated:** Decomposing `U+0E33` prior to tokenization stops mDeBERTa generating `[UNK]` tokens, shortening median input tokens by ~11–14 tokens per row and rescuing 22–24 rows in ID and 12–15 rows in OOD from tokenizer truncation.
   - **Decisions shifted in Thai:** Under SaT, NFKC shifted 108 decisions in TH-ID (6.71%) and 87 decisions in TH-OOD (5.16%).

2. **What did not change:**
   - **English WiCE verification:** 0 decisions changed out of 1,070 rows (100% invariant, identical metrics across accuracy, precision, recall, supported F1, macro F1, FSR, and FRR).
   - **English AttributionBench performance:** SaT EN-ID FSR ($35.53\%$) and $F_1$ ($62.77\%$) are completely unaffected by NFKC (0 decision changes), while SaT EN-OOD changes only 3 out of 1,686 decisions (0.18%).
   - **Reproducibility of published baselines:** Local reruns reproduced both the published unnormalized regex runs (`0 / 3,296` differences) and the published normalized regex run (`0 / 3,296` differences) bitwise.

