# CyberCase Current Project Direction

This document is the canonical single source of truth for the confirmed scope, architecture, research questions, and design principles of the **CyberCase Intelligence Framework**. It supersedes all earlier audit observations and exploratory notes.

---

## 1. Confirmed Product Scope & Identity

* **Core Task**: **General Case Summarization and Grounded Analysis**.
* **Primary Objective**: Ingest general investigative case materials and produce useful, inspectable summaries and preliminary analysis for investigators and prosecutors.
* **Role of MITRE ATT&CK**: **Conditional external technical augmentation only**. MITRE ATT&CK is not the core identity of CyberCase and is never treated as incident evidence.
* **Input Model**:
  * **Current Intake**: A Case owns multiple persisted documents, extraction revisions, and explicitly admitted evidence revisions. Reviewed document-derived narratives and user-submitted case narratives remain supported; extraction is untrusted until review and admission.
  * **Target Intake Contract**: `1 Case → N Documents` remains the multi-document case-dossier direction, with future cross-document semantic clustering kept separate from deterministic evidence admission.

---

## 2. Main Use Case & Workflow

The system serves investigators and security analysts reviewing complex case materials:
1. **Intake & Preparation**: Case materials (narratives, investigative notes, OCR-extracted transcripts) are ingested.
2. **Authoritative Evidence Snapshot**: Admitted case materials are snapshotted, ordered, and hashed.
3. **Direct Main Analysis**: One structured LLM call produces the summary, key findings, material unresolved gaps, and lightweight source references.
4. **Clarification Gating**: Deterministic policy filters and prioritizes Main Analysis gaps, then an optional bounded LLM call phrases one question.
5. **Conditional Technical Augmentation**: If and only if admitted case findings describe cyber threat activity and meet the applicability threshold, external MITRE ATT&CK intelligence is retrieved and presented in an isolated, separately attributed technical section.
6. **Deterministic Preliminary Report**: A structured report is compiled from the analysis, limitations, and optional technical appendix.

---

## 3. Main Analysis Architecture

The production pipeline uses one direct structured analysis call and keeps optional technical augmentation downstream:

```text
CASE MATERIAL (User Narrative / Reviewed Document)
      ↓
Direct Main Analysis LLM (summary, findings, material gaps, source references)
      ↓
Deterministic Follow-up Policy (history, unknown status, priority, round limit)
      ↓ (conditional)
MITRE Applicability Gate → rag_service Retrieval → MITRE Mapping
      ↓
Deterministic Preliminary Report
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
3. **Traceability Boundary**:
   * Important findings retain source references and short supporting quotes where practical.
   * Claims cannot be substantiated by external RAG context.

---

## 5. Core Design Principles

The production architecture follows three practical rules:

1. Use an LLM for semantic analysis and natural-language generation.
2. Use deterministic software for validation, persistence, routing, follow-up history, priority, and stopping rules.
3. Keep Case evidence separate from external MITRE knowledge; a RAG failure never blocks general summarization.

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
| **Intake** | Case-owned multi-document persistence with explicit review/admission; optional Chat text remains a compatibility input | Rich multi-document case dossier workflows and cross-document semantic clustering |
| **Analysis Pipeline** | Direct structured Main Analysis; claim-anchored code is experimental only | Evaluate simpler models and prompt variants without adding production paths |
| **MITRE Augmentation** | Conditional applicability gate $\to$ separate technical appendix | Dynamic threat actor tracking and tactic progression |
| **Document Viewer** | Text preview with page/line citation chips | Split-pane PDF viewer with bounding-box highlight |
| **OCR Providers** | Typhoon OCR (active), Google Vision (baseline) | Calibrated multi-engine consensus |

---

## 9. Case-first implementation status (2026-09-10)

The Case-first implementation follows [`CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md`](../developer-handover/CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md). Checkpoints A–E are implemented and validated in the current checkout, and Checkpoint F's schema, migration-rehearsal, concurrency, and runtime audit is complete. `Case` is the canonical aggregate: material upload/extraction, evidence admission, immutable snapshots, `CaseRun`, `CaseAnalysisResult`, clarification state, and report binding are Case-owned. Chat is optional and lazy; a successful Case analysis creates one persisted assistant `analysis_result` message in the Case's Chat transcript so opening Chat shows the canonical result without making Chat the worker owner.

The frontend loads Case materials, latest analysis, run state, and reports independently of the Chat panel. There is no frontend history/version selector. Historical rows stay in PostgreSQL and are selected by the current API contracts; native citations resolve typed evidence source revisions and snapshot provenance. Ordinary `ask` messages, assistant output, and external RAG context are never promoted to evidence.

The live Docker PostgreSQL audit on 2026-09-10 reached migration `0010_preserve_chat_reports (head)` with 2 existing Cases and 2 ChatThreads. The new material, extraction, evidence, snapshot, CaseRun, result, clarification, and report tables contained 0 rows; FK/orphan checks and active-run checks were all 0. A separate disposable PostgreSQL migration rehearsal upgraded 0001→0010 with a synthetic populated fixture: 2 legacy reports remained, 2 were Case-bound, 1 had a proven result/snapshot binding, 1 remained unresolved, and original report IDs/hashes were preserved. The fixture was destroyed after validation and was never copied into the live database.

The implementation does not claim a historical result/source backfill for the live database because no such legacy rows were present to prove. No synthetic message IDs, provenance, snapshots, or analysis history were created. The coordinated Docker rebuild and deterministic synthetic PostgreSQL workflow/migration smoke passed; authenticated browser smoke was not completed because no signed-in browser session was available. Paid provider calls, OCR/HTR changes, and `rag_service/**` changes are outside this cutover. Detailed receipts and cutover limitations are recorded in [`CASE_FIRST_MIGRATION_AUDIT_2026-09-10.md`](../developer-handover/CASE_FIRST_MIGRATION_AUDIT_2026-09-10.md).

## 10. Explicit Non-Goals

To maintain strict research and engineering focus, the following are **explicit non-goals**:
* ❌ **Legal RAG**: Automated legal reasoning, statutory interpretation, or penal code sentencing prediction.
* ❌ **Handwritten Text Recognition (HTR)**: Processing handwritten police logbooks or signatures (disabled by policy).
* ❌ **Custom Thai-NNER Training**: Training a bespoke Thai Named Entity Recognition model from scratch.
* ❌ **Graph Database Redesign**: Replacing Neo4j or reimplementing MITRE STIX graph structures.
* ❌ **Full CAMS Reproduction**: Replicating news-specific LightGBM salience models or complex multi-document news clusters.
* ❌ **Multi-Agent Swarm Orchestration**: Autonomous agent debates or unpredictable multi-agent conversational swarms.
* ❌ **Automatic OCR Correction**: Unsupervised post-OCR spelling correction that risks hallucinating numbers or names.

---

## 11. Evaluation Plan & Related Work Positioning

* **Related Work**:
  * **CAMS (Guan et al., 2026)**: Methodological inspiration for distinguishing provenance from semantic entailment and separating claim extraction from generation. CyberCase adapts these concepts to Thai investigative documents without claiming full algorithm reproduction.
  * **Attribute-First (ACL 2024)**: Evidence-first planning paradigm.
  * **ThaiSum**: Base corpus for controlled Thai summarization experiments.
* **Evaluation Matrix**:
  * **Provenance Fidelity**: Exact match rate of citation spans against source character offsets.
  * **Factual Precision**: Claim-level entailment / contradiction rate evaluated by human expert and calibrated LLM judge.
  * **OCR Robustness**: Delta in factual accuracy between clean and corrupted input transcripts.
