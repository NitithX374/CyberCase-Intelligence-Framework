# Empirical Evaluation & Audit Report: Evidence-Grounded Claim Verification

**Author:** CyberCase AI Research Experiment
**Configuration:** MoritzLaurer/mDeBERTa-v3-base-xnli + paraphrase-multilingual-mpnet-base-v2 (Frozen Encoders)
**Seed:** 42 | **Hardware:** NVIDIA GeForce GTX 1650 (CUDA)

## Executive Summary

We evaluated an end-to-end evidence-grounded claim verification pipeline across progressive ablations (**B0** to **B4**, including the **B1-LR missing control**) on the gold **WiCE** dataset (claim-level oracle setting, 1,070 test examples) and **AttributionBench** (In-Domain 1,610 examples, Out-of-Domain 1,686 examples). Zero generative LLMs, zero fine-tuning, and zero test-set threshold tuning were employed.

## 1. WiCE Test Evaluation (Primary Factorial Ablation Table)

| Method   | Accuracy   | Macro-F1 (95% CI)     | Supp-Precision   | Supp-Recall   | Supp-F1 (95% CI)      | False Support Rate (95% CI)   | Coverage   | Real Latency (GPU)   |
|:---------|:-----------|:----------------------|:-----------------|:--------------|:----------------------|:------------------------------|:-----------|:---------------------|
| B0       | 64.67%     | 0.5852 [0.554, 0.615] | 42.68%           | 42.42%        | 0.4255 [0.378, 0.473] | 25.41% [22.3%, 28.5%]         | 100.00%    | ~413 ms              |
| B0-LR    | 64.58%     | 0.5937 [0.564, 0.624] | 43.14%           | 46.67%        | 0.4483 [0.404, 0.494] | 27.43% [24.4%, 30.6%]         | 100.00%    | ~413 ms              |
| B1       | 63.55%     | 0.5967 [0.567, 0.627] | 42.65%           | 52.73%        | 0.4715 [0.426, 0.515] | 31.62% [28.3%, 34.9%]         | 100.00%    | ~227 ms              |
| B1-LR    | 66.64%     | 0.6185 [0.587, 0.650] | 46.26%           | 50.61%        | 0.4834 [0.438, 0.530] | 26.22% [22.9%, 29.2%]         | 100.00%    | ~227 ms              |
| B2       | 64.30%     | 0.5957 [0.565, 0.627] | 43.05%           | 48.79%        | 0.4574 [0.410, 0.502] | 28.78% [25.6%, 32.0%]         | 100.00%    | ~824 ms              |
| B3       | 66.54%     | 0.6205 [0.588, 0.651] | 46.24%           | 52.12%        | 0.4900 [0.443, 0.534] | 27.03% [23.8%, 30.2%]         | 100.00%    | ~449 ms              |
| B4       | 83.33%     | N/A                   | N/A              | N/A           | N/A                   | 0.00%                         | 5.05%      | ~449 ms              |

## 2. Evidence Filtering Quality (B1, B1-LR, B3)

| method   |   evidence_precision |   evidence_recall |   evidence_f1 |   avg_units_before |   avg_units_after |   pct_units_removed |
|:---------|---------------------:|------------------:|--------------:|-------------------:|------------------:|--------------------:|
| B1       |             0.295279 |          0.956075 |      0.421702 |            18.6065 |           10.0897 |             45.7733 |
| B3       |             0.295279 |          0.956075 |      0.421702 |            18.6065 |           10.0897 |             45.7733 |

*Note:* Mean per-example Evidence F1 is **0.4217** (micro-averaged sentence F1 is **0.4091**; harmonic mean of aggregate mean precision and recall is **0.4512**). The semantic filter ($	au=0.20$) eliminates **45.77%** of candidate sentences while maintaining **95.61%** recall of gold supporting evidence.

## 3. Calibrated Selective Prediction (B4 Audit & Reality Check)

- **Calibration Method:** Temperature Scaling on decision logits (T = 1.0490, fitted on DEV only)
- **DEV Operating Bounds:** T_low = 0.2800, T_high = 0.8100
- **Target Selective Risk:** <= 5% (Constraint)
- **DEV Achieved Selective Risk:** **17.86%** (at 5.37% coverage; target of <= 5% could NOT be achieved)
- **TEST Achieved Selective Risk:** **16.67%** (at 5.05% coverage; target of <= 5% was NOT met)
- **Test Retained Breakdown ($N=54$):** TP = 0, FP = 0, TN = 45, FN = 9
- **Observed Retained False Support Rate:** **0.00%** (0 false admissions out of 45 retained negative claims)
- **Exact Clopper-Pearson 95% Binomial CI:** **[0.0000%, 7.8705%]** (Rule of Three upper bound = 6.67%)
- **Admission Count (pred=SUPPORTED):** **0 claims admitted** (100% downstream starvation)
- **Area Under Risk-Coverage Curve (AURC):** **0.3611** vs unselective B3 error baseline **0.3346**

> **Critical Narrative Finding:** B4 did NOT function as an admission gate because zero claims reached $T_{high}=0.81$. Instead, at this operating point, B4 acted as a **high-confidence rejection mechanism for unsupported claims**, achieving 83.33% selective accuracy on retained rejections. Furthermore, because AURC ($0.3611$) is higher than the unselective baseline error rate ($0.3346$), selective prediction fails to order difficulty across intermediate coverages, only reducing risk at the extreme low-coverage tail (5%).

## 4. Causal Ablation Audit: Isolating Reverse NLI (B3 vs B1-LR)

To isolate whether reverse-direction NLI genuinely contributes complementary signal beyond forward NLI, we evaluated **B1-LR** (Semantic Filtering + Forward NLI 3D + Logistic Regression) as the direct control:
- **B1-LR Test Performance:** Accuracy = 66.64%, Macro-F1 = 0.6185, Supp-F1 = 0.4834, FSR = 26.22%, Latency = ~227 ms
- **B3 Test Performance:**   Accuracy = 66.54%, Macro-F1 = 0.6205, Supp-F1 = 0.4900, FSR = 27.03%, Latency = ~449 ms
- **Paired Delta Accuracy:**     -0.10% [-0.93%, +0.75%]
- **Paired Delta Macro-F1:**     +0.0020 [-0.0065, +0.0113] (CI spans zero -> **NOT statistically significant**)
- **Paired Delta Supported-F1:** +0.0066 [-0.0045, +0.0200] (CI spans zero -> **NOT statistically significant**)
- **Paired Delta FSR:**          +0.81% [-0.13%, +1.80%]

> **Decisive Causal Conclusion:** When forward features are properly calibrated via Logistic Regression (B1-LR), adding reverse NLI (B3) yields an insignificant Macro-F1 gain of only **+0.0020**, while doubling NLI inference time ($227$ ms vs $449$ ms). **The true drivers of pipeline success are Semantic Evidence Filtering + Learned Decision Boundary.**

## 5. External Generalization: AttributionBench

| split   |   B0_accuracy |   B0_macro_f1 |   B0_false_support_rate |   B1_accuracy |   B1_macro_f1 |   B1_false_support_rate |   B3_accuracy |   B3_macro_f1 |   B3_false_support_rate |   B4_selective_accuracy |   B4_coverage |   B4_false_support_rate |
|:--------|--------------:|--------------:|------------------------:|--------------:|--------------:|------------------------:|--------------:|--------------:|------------------------:|------------------------:|--------------:|------------------------:|
| id      |      0.637267 |      0.637105 |                0.341615 |      0.636025 |      0.635484 |                0.402484 |      0.640373 |      0.640311 |                0.346584 |                0.631579 |     0.047205  |                       0 |
| ood     |      0.715896 |      0.714223 |                0.360617 |      0.723013 |      0.719784 |                0.384342 |      0.73191  |      0.72994  |                0.353499 |                0.861111 |     0.0213523 |                       0 |

## 6. Claims Governance for Thesis & Academic Publications


### Claims SAFE to State:
1. **Semantic filtering ($	au=0.20$) significantly improves Supported Recall by +10.31 pp** (42.42% to 52.73%) on WiCE Test while eliminating 45.77% of distractor sentences with 95.61% gold evidence recall.
2. **Semantic filtering reduces premise length, cutting forward NLI latency by ~45%** (from 413 ms in B0 to 227 ms in B1-LR).
3. **The full B3 pipeline significantly outperforms raw standalone NLI (B0)** in Macro-F1 (+0.0352, 95% paired CI: [+0.0148, +0.0551]) and Supported-F1 (+0.0642, 95% paired CI: [+0.0337, +0.0923]).
4. **B1-LR (Filter + Forward 3D + LR) captures 99.7% of B3's Macro-F1** (0.6185 vs 0.6205) at half the latency (~227 ms vs ~449 ms) and with a lower False Support Rate (26.22% vs 27.03%).
5. **At the selected thresholds, B4 acted as a high-confidence rejection mechanism rather than an admission gate**, observing zero false admissions among retained negative claims (Clopper-Pearson 95% CI: [0.00%, 7.87%]) while admitting 0 positive claims downstream.
6. **Frozen WiCE parameters transfer effectively out-of-domain**, achieving 64.04% Accuracy on AttributionBench ID and 73.19% on AttributionBench OOD.

### Claims that must NOT be Stated:
1. **DO NOT claim:** *"Reverse NLI adds substantial complementary value."* (B3 vs B1-LR paired delta is only +0.0020 Macro-F1 and is not statistically significant).
2. **DO NOT claim:** *"B3 reduces False Support Rate compared to standalone B0."* (B0 FSR is 25.41%; B3 FSR is 27.03%).
3. **DO NOT claim:** *"B4 achieved the 5% selective risk target."* (The target could not be achieved on DEV [17.86%] or TEST [16.67%]).
4. **DO NOT claim:** *"B4 is a functional claim-admission gate."* (It admitted 0 claims, causing 100% downstream starvation).
5. **DO NOT claim:** *"Selective prediction ranking works well based on AURC."* (AURC 0.3611 is worse than the 0.3346 unselective baseline error rate).
6. **DO NOT claim:** *"The verifier runs in 0.01–0.03 ms."* (That is LR CPU decision time; true GPU end-to-end latency is ~227 ms for B1-LR and ~449 ms for B3).

