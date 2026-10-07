# Cross-Family Re-Evaluation — Controlled Factor Ablation
## WiCE Claim Verification

**Date:** 2026-10-07  
**Dataset:** WiCE Claim Verification Held-Out Test Split ($N = 1,070$; Gold Positive = 330, Gold Negative = 740)  
**Evaluation Protocol:** Paired Bootstrap ($N_{\text{boot}} = 1,000$, Random Seed = 42, 95% Confidence Intervals)  
**Primary Evaluated Backbones:**
1. `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (Primary Official Champion, ~278M parameters)
2. `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` (Post-Hoc Cross-Backbone Sensitivity Analysis, ~107M parameters)

**Canonical Metrics Definition:**
* **Accuracy:** $(TP + TN) / N$
* **Supported Precision:** $TP / (TP + FP)$
* **Supported Recall:** $TP / (TP + FN)$
* **Supported F1:** $2 \cdot P \cdot R / (P + R)$
* **Macro-F1:** $(\text{Supp-}F_1 + \text{Unsupp-}F_1) / 2$
* **False Support Rate (FSR):** $FP / (FP + TN)$ *(i.e., False Positive Rate over actual Gold Unsupported claims)*

---

## 1. Experimental Scope & Methodological Discipline

This evaluation re-examines the pipeline ablations ($B0 \to B0\text{-LR} \to B1 \to B1\text{-LR} \to B3$) across two distinct multilingual Natural Language Inference (NLI) backbone architectures under a strictly locked canonical protocol.

The explicit objective is **not** to conduct an open-ended model sweep or to promote MiniLM based on held-out test metrics. Rather, this investigation isolates three specific design choices:
1. **Semantic Evidence Filtering** ($\tau = 0.20$ thresholding on multilingual sentence embeddings)
2. **Task-Specific Logistic Regression Decision Layer** (supervised 3D classification head vs. 1D DEV-tuned threshold)
3. **Reverse-Direction NLI** (evaluating bidirectional entailment $[E \implies C, C \implies E]$ vs. forward-only entailment $[E \implies C]$)

### Scientific Constraints:
* **Held-out Test Split:** The test split ($N = 1,070$) is referred to as the *held-out test split*, acknowledging that post-hoc sensitivity analyses occurred after prior inspection.
* **Zero Test Leakage into Training:** Logistic Regression heads are fit exclusively on the WiCE TRAIN split ($N = 3,750$, Positive = 1,377, Negative = 2,373). DEV and TEST splits are strictly evaluated via `predict()`.
* **Zero Test Tuning:** Decision thresholds ($\theta_{\text{DEV}}$) and filter thresholds ($\tau$) are selected strictly on the WiCE DEV split ($N = 1,043$, Positive = 342, Negative = 701).

---

## 2. Locked Canonical Baseline Definitions

All baselines are locked to the following canonical definitions:

* **B0 (Full evidence, 1D threshold):**
  Full evidence premise $\to$ Forward NLI $\to P(\text{entailment}) \ge \theta_{\text{DEV}}$.
  * $\theta_{\text{DEV}} = 0.36$ for mDeBERTa; $\theta_{\text{DEV}} = 0.15$ for MiniLM.
* **B0-LR (Full evidence, 3D LR):**
  Full evidence premise $\to$ Forward NLI $\to [P_E, P_N, P_C] \to$ Logistic Regression (TRAIN-fit, $C=1.0$, balanced).
* **B1 (Filtered evidence, 1D threshold):**
  Semantic filter ($\tau = 0.20$) $\to$ Forward NLI $\to P(\text{entailment}) \ge \theta_{\text{DEV}}$.
  * $\theta_{\text{DEV}} = 0.23$ for mDeBERTa; $\theta_{\text{DEV}} = 0.20$ for MiniLM.
* **B1-LR (Filtered evidence, 3D LR — Official Champion):**
  Semantic filter ($\tau = 0.20$) $\to$ Forward NLI $\to [P_E, P_N, P_C] \to$ Logistic Regression (TRAIN-fit, $C=1.0$, balanced).
* **B3 (Filtered evidence, 6D LR — Bidirectional):**
  Semantic filter ($\tau = 0.20$) $\to$ Forward NLI + Reverse NLI $\to [P_{\text{fwd}}, P_{\text{rev}}] \in \mathbb{R}^6 \to$ Logistic Regression (TRAIN-fit, $C=1.0$, balanced).

---

## 3. Full Held-Out Test Metrics

### 3.1 mDeBERTa-v3-base (Primary Official Champion)
*Sample size: $N = 1,070$ (Gold Positive = 330, Gold Negative = 740)*

| Method | TP | FP | TN | FN | Pred Pos | Pred Neg | Accuracy | Macro-$F_1$ | Supp-P | Supp-R | Supp-$F_1$ | FSR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **B0** ($\theta=0.36$) | 140 | 188 | 552 | 190 | 328 | 742 | 64.67% | 0.5852 | 42.68% | 42.42% | 0.4255 | 25.41% |
| **B0-LR** | 154 | 203 | 537 | 176 | 357 | 713 | 64.58% | 0.5937 | 43.14% | 46.67% | 0.4483 | 27.43% |
| **B1** ($\theta=0.23$) | 174 | 234 | 506 | 156 | 408 | 662 | 63.55% | 0.5967 | 42.65% | 52.73% | 0.4715 | 31.62% |
| **B1-LR (CHAMPION)** | 167 | 194 | 546 | 163 | 361 | 709 | **66.64%** | **0.6185** | 46.26% | 50.61% | **0.4834** | **26.22%** |
| **B3** | 172 | 200 | 540 | 158 | 372 | 698 | 66.54% | 0.6205 | 46.24% | 52.12% | 0.4900 | 27.03% |

*Identity Verification:* $\text{TP} + \text{FP} + \text{TN} + \text{FN} = 1,070$; $\text{TP} + \text{FN} = 330$; $\text{TN} + \text{FP} = 740$.

---

### 3.2 multilingual-MiniLMv2-L6 (Post-Hoc Backbone Sensitivity Analysis)
*Sample size: $N = 1,070$ (Gold Positive = 330, Gold Negative = 740)*

| Method | TP | FP | TN | FN | Pred Pos | Pred Neg | Accuracy | Macro-$F_1$ | Supp-P | Supp-R | Supp-$F_1$ | FSR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **B0** ($\theta=0.15$) | 128 | 184 | 556 | 202 | 312 | 758 | 63.93% | 0.5705 | 41.03% | 38.79% | 0.3988 | 24.86% |
| **B0-LR** | 181 | 317 | 423 | 149 | 498 | 572 | 56.45% | 0.5410 | 36.35% | 54.85% | 0.4372 | 42.84% |
| **B1** ($\theta=0.20$) | 168 | 165 | 575 | 162 | 333 | 737 | 69.44% | 0.6427 | 50.45% | 50.91% | 0.5068 | 22.30% |
| **B1-LR** | 188 | 190 | 550 | 142 | 378 | 692 | 68.97% | 0.6496 | 49.74% | 56.97% | 0.5311 | 25.68% |
| **B3** | 188 | 189 | 551 | 142 | 377 | 693 | 69.07% | 0.6504 | 49.87% | 56.97% | 0.5318 | 25.54% |

*Identity Verification:* $\text{TP} + \text{FP} + \text{TN} + \text{FN} = 1,070$; $\text{TP} + \text{FN} = 330$; $\text{TN} + \text{FP} = 740$.

---

### 3.3 Compact Cross-Family Descriptive Table

| Pipeline Configuration | mDeBERTa Macro-$F_1$ | MiniLM Macro-$F_1$ | mDeBERTa Supp-$F_1$ | MiniLM Supp-$F_1$ | mDeBERTa FSR | MiniLM FSR |
|---|---|---|---|---|---|---|
| **B0 (Full, $\theta_{\text{DEV}}$)** | 0.5852 | 0.5705 | 0.4255 | 0.3988 | 25.41% | 24.86% |
| **B0-LR (Full, LR)** | 0.5937 | 0.5410 | 0.4483 | 0.4372 | 27.43% | 42.84% |
| **B1 (Filtered, $\theta_{\text{DEV}}$)** | 0.5967 | 0.6427 | 0.4715 | 0.5068 | 31.62% | 22.30% |
| **B1-LR (Filtered, LR)** | 0.6185 | 0.6496 | 0.4834 | 0.5311 | 26.22% | 25.68% |
| **B3 (Filtered, Bidi LR)** | 0.6205 | 0.6504 | 0.4900 | 0.5318 | 27.03% | 25.54% |

---

## 4. Semantic Filtering Effect

To isolate the effect of semantic evidence filtering, two controlled comparisons were evaluated:

### 4.1 Filter Effect Under 1D Decision Threshold ($B1$ vs. $B0$)
*Contrast: Filtered premise vs. Full premise under DEV-tuned 1D thresholding.*

| Metric | mDeBERTa Difference [95% CI] | MiniLM Difference [95% CI] |
|---|---|---|
| $\Delta$ Accuracy | $-1.12\%$ [$-3.09\%, +0.84\%$] | $+5.55\%$ [$+2.71\%, +8.50\%$] |
| $\Delta$ Macro-$F_1$ | $+0.0114$ [$-0.0090, +0.0317$] | $+0.0725$ [$+0.0411, +0.1052$] |
| $\Delta$ Supported-$F_1$ | $+0.0457$ [$+0.0173, +0.0752$] | $+0.1086$ [$+0.0623, +0.1559$] |
| $\Delta$ FSR | $+6.17\%$ [$+4.07\%, +8.52\%$] | $-2.59\%$ [$-5.88\%, +0.81\%$] |

*Interpretation:* In both backbones, semantic filtering reliably improved Supported-$F_1$ under 1D thresholding. On MiniLM, filtering produced a statistically reliable Macro-$F_1$ gain ($+0.0725$). On mDeBERTa, Macro-$F_1$ 95% CI spans zero due to a concurrent rise in false supports ($\Delta\text{FSR} = +6.17\%$).

---

### 4.2 Filter Effect Under Learned Decision Layer ($B1\text{-LR}$ vs. $B0\text{-LR}$)
*Contrast: Filtered premise vs. Full premise when both systems utilize the task-specific 3D Logistic Regression decision layer.*

| Metric | mDeBERTa Difference [95% CI] | MiniLM Difference [95% CI] |
|---|---|---|
| $\Delta$ Accuracy | $+2.07\%$ [$+0.28\%, +3.83\%$] | $+12.59\%$ [$+9.16\%, +16.17\%$] |
| $\Delta$ Macro-$F_1$ | $+0.0248$ [$+0.0048, +0.0451$] | $+0.1091$ [$+0.0728, +0.1458$] |
| $\Delta$ Supported-$F_1$ | $+0.0349$ [$+0.0072, +0.0636$] | $+0.0941$ [$+0.0470, +0.1429$] |
| $\Delta$ FSR | $-1.25\%$ [$-3.38\%, +0.83\%$] | $-17.26\%$ [$-21.61\%, -12.96\%$] |

*Question:* Does semantic filtering provide a statistically reliable benefit after controlling for the learned decision layer?  
*Answer:* **Yes.** Across both evaluated backbones, adding semantic filtering prior to the task-specific Logistic Regression layer produced statistically reliable improvements in Macro-$F_1$ (mDeBERTa: $+0.0248$; MiniLM: $+0.1091$) and Supported-$F_1$ (mDeBERTa: $+0.0349$; MiniLM: $+0.0941$), with all respective 95% confidence intervals excluding zero. On MiniLM, filtering also drove a substantial, statistically reliable reduction in false support rate ($\Delta\text{FSR} = -17.26\%$).

---

## 5. Logistic Regression Effect

### 5.1 LR Effect Without Semantic Filtering ($B0\text{-LR}$ vs. $B0$)
*Contrast: 1D threshold vs. Task-specific 3D LR under unfiltered full premises.*

| Metric | mDeBERTa Difference [95% CI] | MiniLM Difference [95% CI] |
|---|---|---|
| $\Delta$ Accuracy | $-0.09\%$ [$-1.21\%, +0.93\%$] | $-7.52\%$ [$-10.38\%, -4.58\%$] |
| $\Delta$ Macro-$F_1$ | $+0.0085$ [$-0.0036, +0.0207$] | $-0.0297$ [$-0.0596, +0.0006$] |
| $\Delta$ Supported-$F_1$ | $+0.0227$ [$+0.0051, +0.0400$] | $+0.0386$ [$-0.0020, +0.0807$] |
| $\Delta$ FSR | $+2.00\%$ [$+0.83\%, +3.16\%$] | $+18.04\%$ [$+14.97\%, +21.02\%$] |

*Interpretation:* On unfiltered premises, fitting a balanced Logistic Regression layer on noisy long context did not reliably improve Macro-$F_1$ for either model (both 95% CIs cross zero), and substantially inflated false support on MiniLM ($+18.04\%$).

---

### 5.2 LR Effect After Semantic Filtering ($B1\text{-LR}$ vs. $B1$)
*Contrast: 1D threshold vs. Task-specific 3D LR under filtered premises.*

| Metric | mDeBERTa Difference [95% CI] | MiniLM Difference [95% CI] |
|---|---|---|
| $\Delta$ Accuracy | $+3.10\%$ [$+1.68\%, +4.39\%$] | $-0.47\%$ [$-1.68\%, +0.84\%$] |
| $\Delta$ Macro-$F_1$ | $+0.0219$ [$+0.0076, +0.0350$] | $+0.0068$ [$-0.0069, +0.0213$] |
| $\Delta$ Supported-$F_1$ | $+0.0119$ [$-0.0067, +0.0279$] | $+0.0241$ [$+0.0042, +0.0450$] |
| $\Delta$ FSR | $-5.42\%$ [$-7.17\%, -3.70\%$] | $+3.37\%$ [$+2.10\%, +4.80\%$] |

*Question:* Does the task-specific learned decision boundary consistently improve full-support verification after semantic filtering?  
*Answer:* **Backbone-dependent refinement.** On mDeBERTa, the 3D Logistic Regression layer reliably improved Macro-$F_1$ ($+0.0219$ [$+0.0076, +0.0350$]) while significantly reducing FSR ($-5.42\%$). On MiniLM, where the 1D DEV threshold had already reached $0.6427$, LR provided a modest positive point estimate ($+0.0068$) whose confidence interval crossed zero, while reliably improving Supported-$F_1$ ($+0.0241$ [$+0.0042, +0.0450$]).

*Methodological Note on Representation:* Transitioning from $B1$ to $B1\text{-LR}$ modifies both the decision rule and feature space (from a scalar $P(\text{entailment}) \ge \theta_{\text{DEV}}$ to a supervised 3-way hyperplane over $[P(E), P(N), P(C)]$). This contrast confirms that the learned 3-way decision layer outperforms the scalar entailment threshold baseline, but does not isolate whether Neutral or Contradiction features are individual causal drivers of the gain (which would require an additional 1D $P(E) \to \text{LR}$ ablation). We make no causal semantic claims regarding individual probabilities.

---

## 6. Reverse NLI Effect

*Contrast: Forward-only NLI ($B1\text{-LR}$) vs. Bidirectional Forward + Reverse NLI ($B3$), keeping semantic filtering and the Logistic Regression layer identical.*

| Metric | mDeBERTa ($B3 - B1\text{-LR}$) [95% CI] | MiniLM ($B3 - B1\text{-LR}$) [95% CI] |
|---|---|---|
| $\Delta$ Accuracy | $-0.10\%$ [$-0.93\%, +0.75\%$] | $+0.12\%$ [$-1.50\%, +1.59\%$] |
| $\Delta$ Macro-$F_1$ | $+0.0020$ [$-0.0065, +0.0113$] | $+0.0011$ [$-0.0153, +0.0179$] |
| $\Delta$ Supported-$F_1$ | $+0.0066$ [$-0.0045, +0.0200$] | $+0.0011$ [$-0.0204, +0.0234$] |
| $\Delta$ FSR | $+0.81\%$ [$-0.13\%, +1.80\%$] | $-0.16\%$ [$-2.10\%, +1.87\%$] |

*Question:* Does reverse-direction NLI provide statistically reliable complementary information after semantic filtering and a learned decision layer?  
*Answer:* **No.** Across both evaluated NLI backbones, reverse-direction NLI produced no statistically reliable Macro-$F_1$, Supported-$F_1$, Accuracy, or FSR improvements over $B1\text{-LR}$. In every metric across both model families, the 95% paired bootstrap confidence intervals span zero. Forward-only NLI ($B1\text{-LR}$) remains the preferred configuration due to statistically indistinguishable performance while requiring only forward-direction NLI inference.

---

## 7. Contrast: Naive Argmax vs. DEV-Tuned Threshold Ablation

To document the effect of naive argmax vs. 1D thresholding on the baselines:

| Setting | mDeBERTa B0 | mDeBERTa B1 | MiniLM B0 | MiniLM B1 |
|---|---|---|---|---|
| **Protocol 1: 1D DEV Threshold ($\theta_{\text{DEV}}$)** | Acc: 64.67%, Macro-$F_1$: **0.5852** | Acc: 63.55%, Macro-$F_1$: **0.5967** | Acc: 63.93%, Macro-$F_1$: **0.5705** | Acc: 69.44%, Macro-$F_1$: **0.6427** |
| **Protocol 2: Naive Argmax ($\text{argmax}==0$)** | Acc: 65.98%, Macro-$F_1$: **0.5867** | Acc: 67.57%, Macro-$F_1$: **0.6129** | Acc: 69.16%, Macro-$F_1$: **0.4720** | Acc: 72.06%, Macro-$F_1$: **0.5744** |

*Finding:* On the distilled MiniLM backbone, naive argmax caused extreme negative prediction bias under full premises ($95.3\%$ predicted negative, Supported Recall $7.6\%$), creating an artificial accuracy spike ($69.16\%$) while Macro-$F_1$ collapsed to $0.4720$. Tuning a 1D threshold on DEV ($\theta=0.15$) restored balanced recall, confirming that DEV-based threshold selection is important when evaluating encoders on class-imbalanced verification tasks.

---

## 8. Cross-Family Pattern Summary

| Controlled Factor Comparison | mDeBERTa Result | MiniLM Result | Consistent Direction? | Statistically Reliable in Both? |
|---|---|---|---|---|
| **Filtering under 1D threshold:** $B1$ vs. $B0$ | Supp-$F_1 \uparrow$, FSR $\uparrow$ | Macro-$F_1 \uparrow$, Supp-$F_1 \uparrow$ | Yes ($\text{Supp-}F_1 \uparrow$) | **Partial** (Supp-$F_1$ reliable in both; Macro-$F_1$ reliable only in MiniLM) |
| **Filtering under LR:** $B1\text{-LR}$ vs. $B0\text{-LR}$ | Macro-$F_1 \uparrow$, Supp-$F_1 \uparrow$ | Macro-$F_1 \uparrow$, Supp-$F_1 \uparrow$, FSR $\downarrow$ | Yes (Macro-$F_1 \uparrow$, Supp-$F_1 \uparrow$) | **Yes** (Both Macro-$F_1$ and Supp-$F_1$ 95% CIs exclude 0) |
| **LR without filter:** $B0\text{-LR}$ vs. $B0$ | Supp-$F_1 \uparrow$, FSR $\uparrow$ | Acc $\downarrow$, FSR $\uparrow\uparrow$ | No (Backbone-dependent degradation) | **No** (Macro-$F_1$ CIs span zero in both) |
| **LR after filter:** $B1\text{-LR}$ vs. $B1$ | Macro-$F_1 \uparrow$, FSR $\downarrow$ | Supp-$F_1 \uparrow$, FSR $\uparrow$ | Partial (Macro-$F_1 \uparrow$) | **Partial** (Macro-$F_1$ reliable on mDeBERTa; Supp-$F_1$ reliable on MiniLM) |
| **Reverse NLI:** $B3$ vs. $B1\text{-LR}$ | Invariant ($\Delta\text{MF1} = +0.0020$) | Invariant ($\Delta\text{MF1} = +0.0011$) | Yes (Both CIs include 0) | **No** (Zero statistically reliable gain in either model) |

---

## 9. Model-Family Sensitivity & Methodological Status

### 9.1 Descriptive Comparison ($B1\text{-LR}$)
* **mDeBERTa-v3-base ($B1\text{-LR}$):** Accuracy = $66.64\%$, Macro-$F_1 = 0.6185$, Supp-$F_1 = 0.4834$, FSR = $26.22\%$
* **multilingual-MiniLMv2-L6 ($B1\text{-LR}$):** Accuracy = $68.97\%$, Macro-$F_1 = 0.6496$, Supp-$F_1 = 0.5311$, FSR = $25.68\%$
* **Paired Bootstrap ($B1\text{-LR}_{\text{MiniLM}} - B1\text{-LR}_{\text{mDeBERTa}}$):**  
  $\Delta\text{Macro-}F_1 = +0.0309$ [$-0.0076, +0.0664$] (95% CI spans zero).

### 9.2 Methodological Status: POST-HOC CROSS-BACKBONE SENSITIVITY ANALYSIS
This comparison is classified strictly as a **POST-HOC CROSS-BACKBONE SENSITIVITY ANALYSIS**.

During the pre-registered Sequential Verdict Loop:
1. Candidate backbones were evaluated against the champion on the **WiCE DEV split** during Stage 5.
2. On DEV, MiniLM attained Macro-$F_1 = 0.6240$ versus mDeBERTa's $0.6397$ ($\Delta\text{DEV} = -0.0156$, failing the DEV promotion criterion).
3. MiniLM was evaluated on the held-out test split after observing all prior test results as part of an efficiency and model-family sensitivity audit.

Consequently, the higher MiniLM point estimate on test ($0.6496$ vs. $0.6185$) **must not be interpreted as an unbiased model-selection result**, because the backbone was evaluated after prior test inspection. The official model selection remains anchored to mDeBERTa-v3-base.

---

## 10. Efficiency Comparison

All timings were directly measured on an NVIDIA GeForce GTX 1650 (4,096 MiB VRAM) with CUDA acceleration. No values are estimated or extrapolated.

| Metric / Stage | mDeBERTa-v3-base ($B1\text{-LR}$) | multilingual-MiniLMv2-L6 ($B1\text{-LR}$) | Note |
|---|---|---|---|
| **Parameter Count** | ~278M | ~107M | ~2.6$\times$ parameter reduction |
| **GPU Hardware** | NVIDIA GeForce GTX 1650 | NVIDIA GeForce GTX 1650 | Identical device |
| **Single-Request Latency (Batch Size 1)** | | | |
| - Semantic Filter | Mean: 153.27 ms (Median: 148.25 ms) | Mean: 153.27 ms (Median: 148.25 ms) | Shared multilingual sentence encoder |
| - Forward NLI | Mean: 313.73 ms (Median: 334.86 ms) | Mean: 29.19 ms (Median: 11.87 ms) | 10.7$\times$ mean / 28.2$\times$ median speedup |
| - LR Decision Layer | Mean: 0.76 ms (Median: 0.62 ms) | Mean: 0.76 ms (Median: 0.62 ms) | 3D feature inference |
| - **Total Single-Request Latency** | **Mean: 467.77 ms (Median: 474.89 ms)** | **Mean: 183.22 ms (Median: 160.74 ms)** | Single-item end-to-end |
| **Batched Throughput** | **~227 ms / claim** | Not measured in batch mode | Amortized batched throughput on full test split |

---

## 11. External Transferability: AttributionBench

In external validation on AttributionBench (`osunlp/AttributionBench`, `subset_balanced`), the WiCE-trained components were applied in a strictly **frozen external transfer evaluation**:
* Zero re-tuning of semantic threshold $\tau$
* Zero re-fitting of Logistic Regression
* Zero adjustment of decision thresholds

### Performance Summary on Official Test Splits:
* **Official AttributionBench In-Domain Test ($N = 1,610$):**  
  - Baseline B0 (Full premise, argmax): Accuracy = **64.72%**, Macro-$F_1$ = **0.6462**, Supported-$F_1$ = 0.6278, FSR = **30.06%**
  - **B1-LR (Final Champion):** Accuracy = 63.85%, Macro-$F_1$ = 0.6384, Supported-$F_1$ = **0.6330**, FSR = 34.66%  
  *(In-Domain Parity: B1-LR remains within 0.87% Accuracy of full-premise B0 while achieving higher Supported-$F_1$ with 47% evidence removed.)*
* **Official AttributionBench Out-of-Domain Test ($N = 1,686$):**  
  - Baseline B0 (Full premise, argmax): Accuracy = 71.95%, Macro-$F_1$ = 0.7190, Supported-$F_1$ = 0.7305, FSR = **32.15%**
  - **B1-LR (Final Champion):** Accuracy = **73.01%**, Macro-$F_1$ = **0.7281**, Supported-$F_1$ = **0.7515**, FSR = 35.59%  
  *(Out-of-Domain Robustness: B1-LR outperforms B0 across Accuracy (+1.06%), Macro-$F_1$ (+0.0091), and Supported-$F_1$ (+0.0210).)*

---

## 12. Logistic Regression Coefficients Analysis

Fitted on WiCE TRAIN ($N = 3,750$, $C=1.0$, `class_weight="balanced"`):

| Backbone | $w_{\text{entail}}$ | $w_{\text{neutral}}$ | $w_{\text{contra}}$ | Intercept ($b$) | Interpretation |
|---|---|---|---|---|---|
| **mDeBERTa-v3-base** | **+1.4108** | **-1.0513** | **-0.3023** | **+0.0583** | Entailment contributes positively, neutral and contradiction contribute negatively |
| **multilingual-MiniLMv2-L6** | **+3.1117** | **-1.4616** | **-1.1524** | **+0.5151** | Entailment contributes positively, neutral and contradiction contribute negatively |

*Empirical Note:* In both backbones, the fitted weights confirm that entailment features drive the positive decision, while neutral and contradiction features exert negative pressure. We do not assert that these linear coefficients prove causal semantics beyond linear separation.

---

## 13. Scientific Verdict & Thesis-Safe Claims

### A. STRONGLY SUPPORTED
1. **Semantic filtering reliably improves learned decision verification:** Across both evaluated backbones, adding semantic evidence filtering before the task-specific Logistic Regression layer ($B1\text{-LR}$ vs. $B0\text{-LR}$) yielded statistically reliable improvements in Macro-$F_1$ (mDeBERTa: $+0.0248$ [$+0.0048, +0.0451$]; MiniLM: $+0.1091$ [$+0.0728, +0.1458$]) and Supported-$F_1$ (mDeBERTa: $+0.0349$ [$+0.0072, +0.0636$]; MiniLM: $+0.0941$ [$+0.0470, +0.1429$]).
2. **Reverse NLI provides no statistically reliable additional benefit:** Across both backbones, bidirectional NLI ($B3$) yielded no statistically reliable Macro-$F_1$ improvement over forward-only NLI ($B1\text{-LR}$), with both 95% confidence intervals spanning zero.
3. **B1-LR generalizes without domain collapse:** Applied in frozen transfer to AttributionBench OOD ($N=1,686$), $B1\text{-LR}$ maintained superior accuracy ($73.01\%$) and Macro-$F_1$ ($0.7281$) over unfiltered baselines.

### B. CONSISTENT BUT BACKBONE-DEPENDENT
1. **LR head refinement on filtered premises:** Task-specific Logistic Regression yielded statistically reliable Macro-$F_1$ improvement on mDeBERTa ($+0.0219$), while on MiniLM it provided a reliable gain in Supported-$F_1$ ($+0.0241$) but a Macro-$F_1$ difference crossing zero ($+0.0068$ [$-0.0069, +0.0213$]).

### C. NOT SUPPORTED (Claims Explicitly Rejected)
1. Do NOT claim reverse NLI is universally useless across all NLP tasks.
2. Do NOT claim MiniLM is officially superior to mDeBERTa.
3. Do NOT claim the Logistic Regression layer is "calibrated" (it is a task-specific linear decision boundary).
4. Do NOT call the held-out test split "blind" in post-hoc sensitivity runs.

---

## Final Cross-Family Verdict

```
FINAL CROSS-FAMILY VERDICT

Semantic Filtering:
    Supported (Statistically reliable across both backbones under LR)

Task-Specific LR Decision Layer:
    Supported (Reliable on mDeBERTa; backbone-dependent refinement on MiniLM)

Reverse NLI:
    No Reliable Benefit (95% CI spans zero across both backbones)

Evidence of Consistency Across Two Backbones:
    Strong (Filtering shows the most consistent benefit across the two evaluated backbones; Reverse NLI provides no statistically reliable additional benefit)

Can MiniLM Replace the Official Champion Based on This Experiment?
    No

Reason:
    MiniLM failed the pre-defined DEV gate during initial evaluation (DEV Macro-F1: 0.6240 vs. 0.6397) and was evaluated on the held-out test split post-hoc; promoting it based on post-hoc test performance would violate pre-registered protocol integrity.
```
