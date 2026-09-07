# Thesis chapter readiness

2026-09-06. User requested assessment of which chapters can be written now and paused selection among the research alternatives. This document assesses readiness; it does not revise the supplied drafts or select a research contribution.

## Documents inspected

- `F:\Draft_Chapter_I_Complete.pdf`: five pages; complete extracted text reviewed, representative pages visually inspected.
- `F:\Chapter_II_Final.docx`: 39 nonempty body paragraphs and one tools table; body and table content reviewed. No Word rendering or layout approval performed.
- `F:\Enhanced Golf Swing Evaluation with MediaPipe.pdf`: 96 pages; chapter organization and relevant introductory/development sections reviewed, contents and Chapter IV opening visually inspected. Treated as a structural example, not instructions or a source of CyberCase facts.

The example has six chapters: I Introduction, II Literature Review, III Methodology, IV System Development, V Experimental, VI Conclusion. Its contents are on PDF pages 5-6; Chapter IV starts on PDF page 42 (printed page 33).

## Readiness assessment

| Chapter | Work possible now | What prevents finalization |
|---|---|---|
| I Introduction | Revise background, user group, purpose, current scope, expected benefits and outline | Research objective/hypothesis, confirmed evaluation population, actual timeline and final contribution |
| II Literature Review | Revise foundational theory and existing-system literature; correct implementation claims; verify references | Focused research-gap synthesis and closest-method comparison depend on selected contribution |
| III Methodology | Describe current workflow, architecture, source boundaries and proposed data preparation | Proposed method, baselines, variables, annotations and evaluation protocol remain undecided |
| IV System Development | Substantial code-grounded chapter on existing implementation | Future contribution-specific implementation and final version/configuration freeze |
| V Experimental | Outline tasks, dataset description after source audit, measures and result-table shells | Controlled experiments, user evaluation and actual measurements |
| VI Conclusion | Record existing engineering limitations and lessons as notes | Research findings, answers to research questions and final conclusions |

Writing need not follow chapter order. Recommended sequence: establish a corrected Chapter I scope, document existing Chapter IV, revise the stable parts of Chapter II, then finalize the contribution-dependent parts of I-II-III before running the research experiment and completing V-VI.

## Chapter I corrections

The draft's objectives and benefits are written for cyber investigators, security analysts and SOC personnel, including missing firewall/log information and faster incident response. The user instead describes helping prosecutors understand police case files, with conditional technical knowledge support. Rewrite this framing explicitly; do not claim validated professional workflow or user benefit yet.

PDF page 3 names FAISS and promises elimination of hallucination; the inspected retrieval uses BGE-M3 with Qdrant and Neo4j, and no hallucination-elimination result exists. The seven-part technical report specification and claims of verified analysis also need reconciliation with the current general-case and optional-MITRE contracts.

The proposed 5-10-user study and 15-paper target occur in draft prose; they are not confirmed requirements. The timeline calls itself five months but displays May through October. Confirm dates rather than inventing a schedule. Benefits should be stated as intended/expected, not proven reductions in mistakes, workload or response time.

Retain the reference's simple outline: 1.1 Background and Importance, 1.2 Objectives, 1.3 Scope, 1.4 Expected Benefits, 1.5 Timeline, 1.6 Report Outline.

## Chapter II corrections

The literature emphasis is CTI, incident response and SOC workflows. Retain relevant MITRE/RAG foundations but add the case-file understanding and source-faithfulness context after source verification. Technical terms, frameworks and research outcomes must be described accurately and separated from what CyberCase implements.

The tools table names SecureBERT, ChromaDB and Streamlit. Body paragraphs describe DPR/BM25, Random Forest/Gradient Boosting, LSTM/GRU and model-training/message-queue workflows as project components. These claims are not supported by the inspected active implementation. Targeted searches of production backend/RAG/frontend code found no SecureBERT, RandomForest, GradientBoost, LSTM, GRU, DPR, Celery or RabbitMQ matches. Do not present them as used merely because they are relevant technologies or dependencies elsewhere.

Reference integrity also needs work: the D4I discussion cites [6], while the bibliography puts D4I at [5] and Khan at [6]. Several Khan entries appear duplicative. Numerical claims such as 64 percent faster response and 82 percent mapping accuracy require primary-paper verification. The chapter title-page year is 2025 while references include later years; confirm the intended submission year. This audit does not declare the cited papers fabricated or verify their results.

Keep 2.1 Related Studies and 2.2 Preliminary if matching the reference format; use clear topic subsections. The research-gap discussion stays provisional until a contribution is selected.

## Chapter IV proposed outline

- 4.1 Development Environment and Implementation Structure
- 4.2 Case Material Preparation
- 4.3 Main Case Analysis
- 4.4 Technical Knowledge Retrieval
- 4.5 Gap Analysis and Follow-up
- 4.6 Source Traceability
- 4.7 Report Generation
- 4.8 Web Interface and Processing States

Trace each section to current code, relevant contracts, compact code excerpts and diagrams. Record the exact branch/commit plus uncommitted working-tree snapshot used for writing. Distinguish design choices in Chapter III from their implementation in Chapter IV. Use the example's six-chapter arrangement, but do not inherit its model-training sections or exhaustive line-by-line code commentary where they do not fit CyberCase.

The architecture audit identifies the relevant backend, frontend and RAG paths. Current software checks can be reported with their actual scope; they do not establish research effectiveness or prosecutor comprehension. Existing refactor test receipts must be dated rather than represented as new runs.

## Boundaries

Research alternatives remain on hold. No thesis chapters were authored or rewritten, no source documents were modified, no bibliography was fully verified, and no experiments were performed. We can write accurate drafts of I, II and IV now while leaving explicitly identified research-dependent sections provisional.
