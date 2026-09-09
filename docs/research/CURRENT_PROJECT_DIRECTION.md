# CyberCase Current Project Direction

This document is the canonical single source of truth for the confirmed scope, architecture, research questions, and design principles of the **CyberCase Intelligence Framework**. It supersedes all earlier audit observations and exploratory notes.

---

## 1. Confirmed Product Scope & Identity

* **Core Task**: **General Case Summarization and Grounded Analysis**.
* **Primary Objective**: Ingest criminal and cybersecurity case materials, extract an inspectable evidence layer, and generate factually faithful, citation-grounded case findings.
* **Role of MITRE ATT&CK**: **Conditional external technical augmentation only**. MITRE ATT&CK is not the core identity of CyberCase and is never treated as incident evidence.
* **Input Model**:
  * **Current Intake**: Supports one reviewed document-derived narrative or user-submitted case narrative.
  * **Target Intake Contract**: `1 Case → N Documents` (multi-document case dossier).

---

## 2. Main Use Case & Workflow

The system serves investigators and security analysts reviewing complex case materials:
1. **Intake & Preparation**: Case materials (narratives, investigative notes, OCR-extracted transcripts) are ingested.
2. **Authoritative Evidence Snapshot**: Admitted case materials are snapshotted, ordered, and hashed.
3. **Claim-Anchored Case Analysis**: The analysis engine decomposes the evidence into atomic, source-bound claims, resolves exact unique spans, filters by explicit selection policy, and generates grounded case findings.
4. **Clarification Gating**: If critical case indicators or facts are missing, the backend gates the run and asks a targeted clarification question before proceeding.
5. **Conditional Technical Augmentation**: If and only if admitted case findings describe cyber threat activity and meet the applicability threshold, external MITRE ATT&CK intelligence is retrieved and presented in an isolated, separately attributed technical section.
6. **Deterministic Case Report**: An immutable, structured report is compiled from grounded case findings and optional technical appendices.

---

## 3. Main Analysis Architecture

The core analysis pipeline enforces a strict separation between evidence extraction, provenance resolution, selection, and generation:

```text
CASE MATERIAL (User Narrative / Reviewed Document)
      ↓
Learned Semantic Decomposition (LLM Claim Extraction: atomic claims, quotes, uncertainty)
      ↓
Deterministic Provenance Binding (Exact literal span & page resolution; reject ambiguous)
      ↓
Explicit Evidence Selection (Deterministic coverage policy, budget limits, omission log)
      ↓
Grounded Generation (Constrained LLM generation referencing admitted claim IDs only)
      ↓
GROUNDED CASE FINDINGS (AnalysisTraceV3: answer, summary, attributed claims, gaps)
      ↓ (conditional)
Separate Technical Augmentation (Isolated MITRE ATT&CK retrieval via rag_service)
```

### Contrast with Legacy Runtime
* **Legacy Flow**: Raw evidence $\to$ `rag_service` $\to$ joint prompt generation (where external RAG context risked contaminating case facts).
* **Current Direction**: Case analysis is performed strictly on case evidence first. External knowledge retrieval is downstream, conditional, and source-isolated.

---

## 4. Trust Boundaries & Source-Role Isolation

1. **Admitted Case Evidence**:
   * Initial case narrative, user clarification answers, and explicitly submitted case documents.
   * Only admitted case evidence may support incident facts, timelines, entities, and case findings.
2. **External Knowledge (Non-Evidence Context)**:
   * MITRE ATT&CK descriptions, graph relationships, RAG retrieval chunks, and general LLM pretraining knowledge.
   * External knowledge provides analytical context or threat actor profiling; it **never** becomes an admitted case fact.
3. **Traceability Guarantee**:
   * Every admitted claim must resolve to exact character spans in the admitted case snapshot.
   * Claims cannot be substantiated by external RAG context.

---

## 5. Core Design Principles

The architecture follows four foundational axioms:

1. **Learned semantics $\neq$ structural guarantees**:
   * LLMs handle semantic decomposition, extraction, and drafting.
   * The backend deterministically enforces offsets, hashes, referential integrity, and pipeline boundaries.
2. **Provenance $\neq$ semantic entailment**:
   * Verifying that a quote exists in the source document (provenance) does not prove that the generated sentence is logically entailed by that quote.
3. **Selection $\neq$ generation**:
   * Deciding which evidence items to include is governed by an explicit, auditable selection policy, not hidden LLM attention.
4. **Case evidence $\neq$ external knowledge**:
   * Incident materials and external knowledge taxonomies occupy distinct trust domains and must never be co-mingled in the core factual representation.

---

## 6. Research Questions

* **RQ1 (Claim-Anchored Faithfulness)**: How does a claim-anchored, evidence-first generation pipeline compare to standard end-to-end LLM summarization in terms of factual faithfulness, hallucination reduction, and source attribution in Thai investigative case analysis?
* **RQ2 (OCR Error Propagation)**: Under controlled text corruption, how do critical OCR errors (character substitutions, entity corruption, negation flips, numeric shifts) propagate into downstream Thai case summaries across different generation strategies?

---

## 7. OCR Experiment Direction

The experimental study focuses on the **downstream impact of OCR quality on Thai summarization**:

* **Primary Metric**: Factual correctness and critical OCR error propagation (e.g., entity name distortion, altered financial amounts, inverted polarities).
* **Secondary Metric**: Standard surface summary metrics (ROUGE-1, ROUGE-2, ROUGE-L, BERTScore).
* **Out of Primary Scope**: OCR confidence calibration curves, OCR uncertainty heatmaps, and UI confidence badges.
* **Controlled Dataset**: Synthetic corruption applied to the **ThaiSum** dataset, modeling realistic Thai OCR error patterns.
* **Real-Case Pilot**:
  * Run real Thai police/investigative case PDFs through **Typhoon OCR**.
  * Characterize observed OCR error patterns and inconsistencies.
  * Use an LLM-assisted evaluation judge to validate error taxonomy.
  * **Ground Truth Discipline**: Real-case pilot documents lack double-keyed manual transcriptions. Therefore, reports and thesis text must characterize findings as **observed OCR inconsistency** or **probable OCR-related variation**, NOT a definitive "OCR error rate."

---

## 8. Current vs. Future Scope

| Dimension | Current Implementation | Target / Future Scope |
| :--- | :--- | :--- |
| **Intake** | Single reviewed document narrative or chat text | Multi-document case dossier (`1 Case → N Documents`) |
| **Analysis Pipeline** | Claim-anchored v1 (`CASE_ANALYSIS_PIPELINE=claim_anchored`) | Learned NLI verification and cross-document claim clustering |
| **MITRE Augmentation** | Conditional applicability gate $\to$ separate technical appendix | Dynamic threat actor tracking and tactic progression |
| **Document Viewer** | Text preview with page/line citation chips | Split-pane PDF viewer with bounding-box highlight |
| **OCR Providers** | Typhoon OCR (active), Google Vision (baseline) | Calibrated multi-engine consensus |

---

## 9. Explicit Non-Goals

To maintain strict research and engineering focus, the following are **explicit non-goals**:
* ❌ **Legal RAG**: Automated legal reasoning, statutory interpretation, or penal code sentencing prediction.
* ❌ **Handwritten Text Recognition (HTR)**: Processing handwritten police logbooks or signatures (disabled by policy).
* ❌ **Custom Thai-NNER Training**: Training a bespoke Thai Named Entity Recognition model from scratch.
* ❌ **Graph Database Redesign**: Replacing Neo4j or reimplementing MITRE STIX graph structures.
* ❌ **Full CAMS Reproduction**: Replicating news-specific LightGBM salience models or complex multi-document news clusters.
* ❌ **Multi-Agent Swarm Orchestration**: Autonomous agent debates or unpredictable multi-agent conversational swarms.
* ❌ **Automatic OCR Correction**: Unsupervised post-OCR spelling correction that risks hallucinating numbers or names.

---

## 10. Evaluation Plan & Related Work Positioning

* **Related Work**:
  * **CAMS (Guan et al., 2026)**: Methodological inspiration for distinguishing provenance from semantic entailment and separating claim extraction from generation. CyberCase adapts these concepts to Thai investigative documents without claiming full algorithm reproduction.
  * **Attribute-First (ACL 2024)**: Evidence-first planning paradigm.
  * **ThaiSum**: Base corpus for controlled Thai summarization experiments.
* **Evaluation Matrix**:
  * **Provenance Fidelity**: Exact match rate of citation spans against source character offsets.
  * **Factual Precision**: Claim-level entailment / contradiction rate evaluated by human expert and calibrated LLM judge.
  * **OCR Robustness**: Delta in factual accuracy between clean and corrupted input transcripts.
