# OCR Summarization Experiment: Scope & Protocol

This document defines the research protocol and experimental scope for evaluating the impact of Optical Character Recognition (OCR) quality on Thai investigative case summarization.

---

## 1. Research Motivation & Core Question

In investigative and criminal case triage, input documents frequently originate from scanned police records, investigative memos, or printed reports processed via OCR. Standard document summarization benchmarks assume clean native digital text. When OCR introduces errors, those corruptions can propagate into downstream LLM-generated summaries.

### Core Experimental Question
> **Under a fixed LLM and summary token budget, how do direct joint summarization, claim-anchored summarization, and baseline methods differ in the propagation of critical OCR errors into Thai case summaries, while preserving salient case facts and source attribution?**

---

## 2. Evaluation Metric Hierarchy

To maintain experimental clarity and avoid diffuse research goals, metrics are strictly prioritized:

### Primary: Factual Correctness & Error Propagation
* **Critical Error Propagation Rate**: The frequency with which an OCR-introduced distortion (e.g. altered monetary value, transposed suspect/victim names, corrupted dates, flipped negation) is accepted and hallucinated as a factual finding in the generated summary.
* **Factual Precision / Entailment**: Percentage of generated summary units/claims that are logically supported by the original uncorrupted source truth.
* **Contradiction / Hallucination Rate**: Count of generated assertions directly contradicted by the source facts.

### Secondary: Surface Summary Quality
* **ROUGE-1, ROUGE-2, ROUGE-L**: Word- and n-gram-level overlap against reference summaries.
* **BERTScore (Multilingual / Thai)**: Semantic similarity against gold reference summaries.

### Explicitly Not Primary Scope
* **OCR Confidence Calibration**: Fitting reliability curves or evaluating minimum word confidence scores.
* **Uncertainty UI Visualization**: Building front-end confidence heatmaps or bounding-box color gradients.

---

## 3. Experimental Datasets

### A. Controlled Synthetic Corruption Benchmark: ThaiSum
* **Base Corpus**: **ThaiSum** (standard Thai text summarization dataset).
* **Controlled Corruption Methodology**:
  * Apply systematic, parameterized OCR-like perturbations modeling realistic Thai OCR failure modes:
    1. *Tone-mark and vowel shifting/dropping* (e.g., floating vowels ` ่ `, ` ้ `, ` ิ `, ` ี `).
    2. *Similar-glyph character substitutions* (e.g., `ข` $\leftrightarrow$ `ช`, `ด` $\leftrightarrow$ `ต`, `ก` $\leftrightarrow$ `ถ`, `บ` $\leftrightarrow$ `ป`).
    3. *Numeric substitutions* (e.g., `0` $\leftrightarrow$ `O`, `1` $\leftrightarrow$ `l`, digit drop/addition).
    4. *Word segmentation and whitespace collapse/insertion* (crucial for unsegmented Thai script).
  * Control corruption rates systematically (e.g., clean, 5% corrupted, 10% corrupted, 15% corrupted).
* **Advantage**: Full access to pristine Ground Truth (GT) and human-written reference summaries for rigorous, repeatable statistical measurement.

---

## 4. Real-Case Pilot Study: Protocol & Ground Truth Discipline

To ground the synthetic taxonomy in real-world conditions, a qualitative pilot is conducted on authentic investigative case files.

### Workflow
1. **Source Material**: Sample real Thai police reports, complaint forms, and case memos.
2. **Recognition Engine**: Process through **Typhoon OCR** (primary active OCR provider).
3. **Pattern Characterization**: Identify and categorize observed failure modes across printed Thai police templates, stamps, and layout artifacts.
4. **LLM-Assisted Pilot Judge**: Utilize a frontier judge model to inspect candidate extractions against raw images/transcripts to validate the taxonomy.
5. **Derive Taxonomy**: Feed the observed real-world patterns into the ThaiSum synthetic corruption generator.

### Ground Truth (GT) Reporting Discipline
> [!IMPORTANT]
> **Real-case investigative documents lack double-keyed manual transcriptions (Ground Truth).**
>
> Therefore, experimental reports, logs, and thesis manuscripts **must strictly report**:
> * **`Observed OCR Inconsistency`**
> * **`Probable OCR-Related Variation`**
>
> Authors and assistants **must NOT** report or claim a definitive **`OCR Error Rate`** or **`Character Error Rate (CER)`** on ungrounded real-world case sets where true verbatim ground truth is absent.

---

## 5. Optional & Complementary Extensions

1. **PaddleOCR Baseline**:
   * Run an open-source, non-generative OCR baseline (PaddleOCR with Thai language support) alongside Typhoon OCR to compare OCR error profiles (traditional CNN/CRNN vs. vision-language model OCR).
2. **Downstream Real-Case Confirmation**:
   * A small-scale qualitative human evaluation (e.g., 5–10 real cases) comparing whether the claim-anchored pipeline flags or isolates observed OCR inconsistencies better than unconstrained direct generation.
