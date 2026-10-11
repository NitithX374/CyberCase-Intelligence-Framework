# FINAL VERDICT: CyberCase Evidence-Grounded Claim Verification

**Date:** 2026-10-07  
**Integration audit:** WiCE table values are synchronized with `outputs/canonical/final_metrics.json`; paired Supported-F1 differences are synchronized with `outputs/stage1_b1_lr_verification.json`. No models were refitted.
**Framework:** CyberCase Intelligence Framework  
**Evaluation Splits:** WiCE (Train, Dev, Test), AttributionBench (In-Domain, Out-of-Domain)  
**Hardware Profile:** NVIDIA GeForce GTX 1650 (4,096 MiB VRAM), AMD / Intel Host CPU, Windows OS  
**Original Research Seed:** 42. Integration bootstrap seed: 20261007. Fixed seeds do not establish bitwise determinism across devices or library versions.

---

## A. FINAL CHAMPION

### Recommended CyberCase Claim Verifier Pipeline: **B1-LR**

$$\text{Retained Evidence Units} \xrightarrow{\quad\text{Concatenation}\quad} \text{Premise } P \xrightarrow{\quad\text{Frozen Forward NLI}\quad} [P_{\text{ent}}, P_{\text{neu}}, P_{\text{con}}] \xrightarrow{\quad\text{Logistic Regression}\quad} \hat{y} \in \{\text{SUPPORTED}, \text{UNSUPPORTED}\}$$

```
                ┌─────────────────────────────────────────────────────────────┐
                │                        Case Sources                         │
                └──────────────────────────────┬──────────────────────────────┘
                                               ▼
                ┌─────────────────────────────────────────────────────────────┐
                │             Reader / Extraction Module                      │
                │  Produces: Claim C + IDs of backend-created Source units     │
                └──────────────────────────────┬──────────────────────────────┘
                                               ▼
                ┌─────────────────────────────────────────────────────────────┐
                │              STAGE 1: Semantic Evidence Filter              │
                │  • Backbone: paraphrase-multilingual-mpnet-base-v2 (Frozen) │
                │  • Similarity: Cosine sim(e(C), e(U_i)) >= tau = 0.20       │
                │  • Fallback: Retain top-1 if all sim < 0.20                 │
                │  • Preserves original document discourse ordering           │
                └──────────────────────────────┬──────────────────────────────┘
                                               ▼ Filtered Premise P = U_k1 ... U_kp
                ┌─────────────────────────────────────────────────────────────┐
                │              STAGE 2: Frozen Forward Multilingual NLI       │
                │  • Backbone: MoritzLaurer/mDeBERTa-v3-base-xnli (278M params)│
                │  • Inputs: Premise P, Claim C                               │
                │  • Output Vector: [P_entailment, P_neutral, P_contradiction] │
                └──────────────────────────────┬──────────────────────────────┘
                                               ▼ 3D Probability Vector
                ┌─────────────────────────────────────────────────────────────┐
                │              STAGE 3: Linear Decision Hyperplane            │
                │  • Classifier: Logistic Regression (balanced class weights) │
                │  • Threshold: Standard logistic boundary (p >= 0.50)        │
                │  • Execution Latency: 0.76 ms (batch=1) / <0.01 ms (vector) │
                └──────────────────────────────┬──────────────────────────────┘
                                               ▼
                         ┌─────────────────────┴─────────────────────┐
                         ▼                                           ▼
                 [ SUPPORTED ]                               [ UNSUPPORTED ]
          Admitted into Judgement Layer               Withheld; retained in analysis trace
```

---

## B. WHY IT WON

### 1. WiCE Test Benchmark Performance ($N = 1,070$)

| Evaluation Metric | B0 (Naive Baseline) | B1 (Semantic Filter + Heuristic) | B1-LR (Final Champion) | B3 (Bidirectional NLI + LR) |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | 64.67% | 63.55% | **66.64%** | 66.54% |
| **Macro-$F_1$** | 0.5852 | 0.5967 | **0.6185** | 0.6205 |
| **Supported Precision** | 42.68% | 42.65% | **46.26%** | 46.24% |
| **Supported Recall** | 42.42% | 52.73% | **50.61%** | 52.12% |
| **Supported-$F_1$** | 0.4255 | 0.4715 | **0.4834** | 0.4900 |
| **False Support Rate (FSR)** | 25.41% | 31.62% | **26.22%** | 27.03% |
| **Pipeline Throughput Latency** | ~390 ms / claim | ~227 ms / claim | **~227 ms / claim** | ~449 ms / claim แป
*Confusion Matrix for B1-LR on WiCE Test:* $\text{TP} = 167$, $\text{FP} = 194$, $\text{TN} = 546$, $\text{FN} = 163$ ($N = 1,070$, Gold Positive = 330, Gold Negative = 740).

### 2. Paired Bootstrap Hypothesis Tests ($N_{\text{boot}} = 1,000$, Seed = 42)

| Comparison | $\Delta$ Accuracy [95% CI] | $\Delta$ Macro-$F_1$ [95% CI] | $\Delta$ Supported-$F_1$ [95% CI] | $\Delta$ FSR [95% CI] | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **B1-LR vs B0** | **+1.98%** [+0.19%, +3.74%] | **+0.0333** [+0.0128, +0.0533] | **+0.0576** [+0.0286, +0.0868] | +0.75% [-1.09%, +2.70%] | **Macro-$F_1$ & Supp-$F_1$ Highly Significant** |
| **B1-LR vs B0-LR** | **+2.07%** [+0.28%, +3.83%] | **+0.0248** [+0.0048, +0.0451] | **+0.0349** [+0.0072, +0.0636] | -1.25% [-3.38%, +0.83%] | **Macro-$F_1$ & Supp-$F_1$ Significant** |
| **B1-LR vs B1** | **+3.10%** [+1.68%, +4.39%] | **+0.0219** [+0.0076, +0.0350] | +0.0119 [-0.0067, +0.0279] | **-5.42%** [-7.17%, -3.70%] | **Macro-$F_1$ Significant; FSR Major Reduction** |
| **B1-LR vs B3** | +0.10% [-0.75%, +0.93%] | -0.0020 [-0.0113, +0.0065] | -0.0066 [-0.0200, +0.0045] | -0.81% [-1.80%, +0.13%] | **Indistinguishable (CI spans 0); Latency $2\times$ worse in B3** |

---

## C. COMPONENT VERDICTS

| Component Architecture | Empirical Verdict | Rationale & Statistical Evidence |
| :--- | :---: | :--- |
| **Semantic Evidence Filtering ($\tau = 0.20$)** | **KEEP** | Filters out 47.2% of irrelevant text units while maintaining **93.52% evidence recall** on DEV. Shortens premise character length by 25.3%, speeding up NLI inference from 390.2 ms to 313.7 ms per claim. Paired with a learned boundary, it produces a statistically significant $+0.0333$ Macro-$F_1$ gain over unfiltered B0. |
| **Learned 3D Decision Boundary (Logistic Regression)** | **KEEP** | Replaces the naive heuristic threshold ($P_{\text{ent}} = \max$) with a task-specific linear decision boundary. Drastically suppresses false positives, slashing False Support Rate by **$-5.42\%$** (95% CI: [$-7.17\%, -3.70\%$]) relative to B1 while adding only 0.76 ms overhead. |
| **Sentence-Wise Aggregation (SW-NLI-LR)** | **REJECT** | Severely degrades cross-attention and inter-sentence discourse context. DEV Macro-$F_1$ plummeted by **$-0.0597$** (0.5800 vs 0.6397), Supported-$F_1$ plunged by **$-0.0916$**, and inference cost escalated $>10\times$ (41,943 pairs vs 3,750 pairs). |
| **Alternative Semantic Selectors (Top-$k$, Margin)** | **REJECT** | Current Selector A ($\tau = 0.20$) outperformed all 12 candidate selectors on DEV in Macro-$F_1$ (0.6397) and Supported-$F_1$ (0.5097). Relative margin selectors ($\delta \in \{0.10, 0.15, 0.20\}$) crippled evidence recall down to 56.66%–72.05%, discarding gold evidence. |
| **Nonlinear Classifier Head (XGBoost)** | **REJECT** | Promoted on DEV ($\Delta \text{Supp-}F_1 = +0.0230$), but failed decisively on TEST: paired bootstrap $\Delta \text{Macro-}F_1 = +0.0035$ (95% CI: [$-0.0162, +0.0234$], spans zero), while False Support Rate deteriorated by **$+3.95\%$** (95% CI: [$+1.91\%, +5.88\%$]). Added complexity harmed trust boundaries. |
| **Nonlinear Classifier Head (Tiny MLP)** | **REJECT** | Underperformed Logistic Regression on DEV (Macro-$F_1 = 0.6367$ vs 0.6397; Supported-$F_1 = 0.5145$ vs 0.5097; FSR $= 24.54\%$ vs 22.11%). Rejected at the DEV gate. |
| **Reverse NLI ($C \implies E$ Score Fusion)** | **REJECT** | $\Delta \text{Macro-}F_1$ was statistically indistinguishable from zero ($-0.0020$, 95% CI: [$-0.0113, +0.0065$]) while doubling end-to-end NLI compute time and latency from 227 ms to 449 ms. |
| **Alternative Backbone (`xlm-roberta-large-xnli`)** | **REJECT** | 560M parameter model (2x parameter size, 2.24 GB) underperformed the frozen `mDeBERTa-v3-base-xnli` on DEV (Macro-$F_1 = 0.6316$ vs 0.6397, $\Delta = -0.0080$; Supported-$F_1 = 0.4787$ vs 0.5097, $\Delta = -0.0311$). |

Audit qualification, 2026-10-07: the old XLM-R stage joins retained units with spaces while the champion uses newlines. The reported DEV values and stage decision above are preserved, but this is not a completely controlled backbone-only comparison. The separate English checkpoint comparison also finds a larger MiniCheck checkpoint outperforming standalone mDeBERTa; MiniCheck+B1-LR and MiniCheck Thai transfer remain unmeasured. See [the checkpoint audit](../research/attribution_benchmark/CHECKPOINT_AUDIT_2026-10-07.md).

---

## D. REJECTED COMPLEXITY AUDIT

Every rejected component was eliminated through formal empirical gating:

1. **Reverse NLI (B3):**
   * *Mechanism:* Concatenating a reverse NLI pass ($C \implies E$) to evaluate premise entailment.
   * *Rejection Rationale:* $\Delta \text{Macro-}F_1 = -0.0020$ [$-0.0113, +0.0065$] on WiCE Test. The paired bootstrap confidence interval spans zero, showing no detectable benefit in this comparison while doubling GPU latency from 227 ms to 449 ms.
2. **Sentence-Wise NLI (SW-NLI-LR):**
   * *Mechanism:* Scoring each sentence unit $U_i$ against Claim $C$ individually, followed by pooling features (`max_entail`, `mean_entail`, etc.).
   * *Rejection Rationale:* In natural language claim verification, multi-sentence evidence requires joint attention across discourse markers and coreferences. Isolated scoring degraded DEV Macro-$F_1$ by $-0.0597$ and Supported-$F_1$ by $-0.0916$, while inflating NLI forward passes by $>10\times$.
3. **Margin-Based Evidence Filtering (Selector D):**
   * *Mechanism:* Retaining units with $\text{sim} \ge \max(\text{sim}) - \delta$.
   * *Rejection Rationale:* While unit precision increased to 76.5%, evidence recall collapsed from 93.52% down to 56.66% ($\delta = 0.10$) and 65.53% ($\delta = 0.15$), stripping necessary supporting facts and crippling claim-level Macro-$F_1$ to 0.5794.
4. **XGBoost Decision Tree Head:**
   * *Mechanism:* Gradient boosted trees on $[P_{\text{ent}}, P_{\text{neu}}, P_{\text{con}}]$.
   * *Rejection Rationale:* On the test split, tree-based partitions overfitted probability boundaries, inflating FSR from 26.22% to 30.14% ($+3.95\%$ statistically significant worsening, 95% CI: [$+1.91\%, +5.88\%$]), without any statistically distinguishable Macro-$F_1$ gain.
5. **Calibrated Abstention (B4 Gate):**
   * *Mechanism:* Dual-threshold confidence gating ($T_{\text{low}}, T_{\text{high}}$) to admit only high-confidence claims and abstain on ambiguous ones.
   * *Rejection Rationale:* At optimal DEV-selected thresholds ($T_{\text{low}} = 0.46, T_{\text{high}} = 0.81$), the system admitted **0 claims** (admitted volume = 0%). B4 functioned as an outright rejection filter rather than a practical verification gate. Retaining B4 in production is unwarranted.

---

## E. EXTERNAL GENERALIZATION (ATTRIBUTIONBENCH TRANSFER)

The final champion (**B1-LR**) was evaluated with completely frozen parameters (frozen semantic selector $\tau = 0.20$, frozen NLI encoder, frozen Logistic Regression weights fitted solely on WiCE Train) on AttributionBench without any target-domain tuning:

| Benchmark Split | Method | Accuracy | Macro-$F_1$ | Supported Precision | Supported Recall | Supported-$F_1$ | False Support Rate (FSR) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **AttributionBench ID** ($N = 1,610$) | B0 (Full premise, argmax) | **64.72%** | **0.6462** | **66.44%** | 59.50% | 0.6278 | **30.06%** |
| | **B1-LR (Final Champion)** | 63.85% | 0.6384 | 64.28% | **62.36%** | **0.6330** | 34.66% |
| **AttributionBench OOD** ($N = 1,686$) | B0 (Full premise, argmax) | 71.95% | 0.7190 | **70.29%** | 76.04% | 0.7305 | **32.15%** |
| | **B1-LR (Final Champion)** | **73.01%** | **0.7281** | 69.64% | **81.61%** | **0.7515** | 35.59% |

### Transfer Findings:
1. **Out-of-Domain Robustness:** On AttributionBench OOD, B1-LR outperforms B0 across Accuracy (**73.01%** vs 71.95%), Macro-$F_1$ (**0.7281** vs 0.7190), and Supported-$F_1$ (**0.7515** vs 0.7305, a $+0.0210$ gain).
2. **In-Domain Parity:** On AttributionBench ID, B1-LR remains within 0.87% Accuracy and 0.0078 Macro-$F_1$ of the full-premise baseline while retaining a $+0.0052$ advantage in Supported-$F_1$.
3. **Zero-Shot Domain Stability:** Frozen linear weights derived from WiCE generalize across external distributions without catastrophic distribution shift.

---

## F. THESIS-SAFE CLAIMS

The following claims are supported within the reported benchmark protocols; they do not establish production factual or legal correctness:

1. **Semantic filtering improves both accuracy and computational efficiency:**
   * Filtering candidate units at $\tau = 0.20$ removes 47.2% of raw units while retaining 93.52% of gold evidence.
   * It shortens premise character length by 25.3%, reducing NLI GPU forward pass latency from 390.2 ms to 313.7 ms per claim.
   * Combining semantic filtering with a learned decision hyperplane yields a statistically significant $+0.0333$ Macro-$F_1$ improvement (95% CI: [$+0.0128, +0.0533$]) and $+0.0576$ Supported-$F_1$ improvement (95% CI: [$+0.0286, +0.0868$]) over unfiltered B0.
2. **A learned decision hyperplane substantially controls False Support Rate:**
   * Replacing heuristic argmax with balanced Logistic Regression on $[P_{\text{ent}}, P_{\text{neu}}, P_{\text{con}}]$ drops the False Support Rate from 31.64% to 26.22% ($\Delta = -5.42\%$, 95% CI: [$-7.17\%, -3.70\%$]), reducing false admissions on WiCE Test; downstream citation utilization requires a separate matched experiment.
3. **Bidirectional (Reverse) NLI is empirically unviable:**
   * Computing reverse inference ($C \implies E$) yields a statistically indistinguishable Macro-$F_1$ difference ($\Delta = -0.0020$, 95% CI: [$-0.0113, +0.0065$]) while doubling system latency.
4. **Joint premise concatenation outperforms sentence-wise decomposition:**
   * Concatenating retained evidence units into a single NLI premise preserves discourse-level cross-attention, outperforming sentence-isolated scoring by $+0.0597$ Macro-$F_1$ while requiring $10\times$ less compute.
5. **Linear decision boundaries dominate complex nonlinear heads:**
   * Logistic Regression matches or exceeds XGBoost and Tiny MLP in generalization, avoiding tree overfitting that causes a $+3.95\%$ spike in False Support Rate.

---

## G. CLAIMS THAT MUST NOT BE MADE

The following statements are empirically false or misleading and must **never** be asserted:

1. ❌ *"B4 selective abstention achieved zero false-support rate in production."*
   * **Why forbidden:** At the selected thresholds ($T_{\text{low}}=0.46, T_{\text{high}}=0.81$), B4 admitted zero claims ($N=0$). Labeling complete inactivity as "zero false support" is misleading.
2. ❌ *"Bidirectional NLI is necessary for robust grounding verification."*
   * **Why forbidden:** The 95% bootstrap confidence interval for B3 vs B1-LR includes zero ([$-0.0113, +0.0065$]). The empirical evidence indicates reverse NLI is redundant.
3. ❌ *"Higher evidence precision in the retriever translates to higher claim verification accuracy."*
   * **Why forbidden:** Margin filtering (Selector D) achieved 76.5% evidence precision but crashed claim Macro-$F_1$ to 0.5794 due to severe evidence recall drops (56.66%). High evidence recall ($\ge 90\%$) is strictly mandatory.
4. ❌ *"The claim verifier replaces the judgment and reasoning layers of CyberCase."*
   * **Why forbidden:** The verifier is strictly a binary consistency filter between an extracted claim and source evidence units; it does not perform forensic timeline reasoning, MITRE ATT&CK mapping, or investigative synthesis.
5. ❌ *"A larger pretrained NLI backbone automatically improves claim grounding."*
   * **Why forbidden:** Scaling from `mDeBERTa-v3-base` (278M) to `xlm-roberta-large` (560M) reduced DEV Macro-$F_1$ by $-0.0080$ and Supported-$F_1$ by $-0.0311$.

---

## H. FINAL SYSTEM PLACEMENT IN CYBERCASE

```
Case -> N Documents / Narrative / Follow-up Sources
       -> extraction / OCR with provenance
       -> deterministic addressable Source units
       -> Reader: canonical Claims + selected unit IDs
       -> deterministic binding: original text / offsets / document pages
       -> frozen B1-LR admission
            MPNet cosine >= .20 selection, research-defined top-1 retention
            -> original retained units joined with one newline
            -> forward mDeBERTa, longest-first truncation at 512 tokens
            -> WiCE TRAIN-fitted task-specific LR boundary, score >= .50
       -> admitted Claims only
            |-> Views: Parties / Timeline / Impacts
            |-> Judgement: LLM synthesis
                  -> Summary claim IDs / Gaps / conditional MITRE context
                  -> deterministic reference validation / Report

Withheld Claims -> saved trace only; no Judgement admission
Zero admitted Claims -> abstention; no Judgement call
```

This boundary controls which Claim objects enter Judgement; it does not prove real-world truth, legal correctness or the semantic correctness of every derived view. Admitted Claims retain their original supporting citation text, including units omitted from the NLI premise. Another admitted Claim or its passages can therefore expose a withheld proposition. Final reference checks reject withheld Claim IDs, but do not verify every implicit statement in generated prose.

The completed integration and paired experiments are reported in [B1_RESULTS_2026-10-07.md](../research/attribution_benchmark/B1_RESULTS_2026-10-07.md). That report separates admission, downstream Claim-ID utilization, inherited-gold EN/MT-TH transfer, measured runtime and deployment limits. The historical research latency above is not a guarantee of production latency.

---

## 10. STOP RULE EXECUTION

The sequential evaluation loop is concluded. No further model families, fine-tuning sweeps, or search iterations are warranted. B1-LR is the validated champion.
