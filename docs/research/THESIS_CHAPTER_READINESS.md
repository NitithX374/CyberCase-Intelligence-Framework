# Thesis chapter readiness

**Status:** updated 2026-09-22 against the current checkout.

This note distinguishes what can be written from the implemented CyberCase system, what still needs an experiment, and what must remain a limitation. The core thesis scope in this note excludes `rag_service`; MITRE retrieval may be mentioned as an optional external boundary but is not used as evidence for the core contribution.

## Current implementation snapshot

The current non-RAG production path is:

```text
Case narrative / document upload
        ↓
Document extraction → native CaseSource
        ↓
CaseSourceBundle + follow-up history
        ↓
case_assessment_v1
        ↓
Deterministic gap and round policy
   ┌────┴────┐
   Ask      Proceed
   │          ↓
 Persist      main_case_analysis_v1
 question     ↓
        schema validation + source binding
                    ↓
             validated analysis
                    ↓
             deterministic report
```

Follow-up answers are stored as `ChatMessage` history rather than native `CaseSource` rows. A follow-up answer can be referenced by a synthetic QA identifier during binding, but it does not change the native `source_revision`. There is no `CaseRun` table, job resource, or polling-based execution path.

## Readiness assessment

| Chapter | Can write now | Still required before final claims |
|---|---|---|
| I Introduction | Background, target problem, general-case scope, non-goals, intended benefits, and chapter outline | Final research questions, contribution wording, evaluation population, schedule, and evidence-backed benefit claims |
| II Literature Review | Case summarization, source grounding/provenance, OCR effects, structured generation, deterministic validation, and clarification workflows | Verified references, closest-method comparison, and a research gap that matches the final experiment |
| III Methodology | Current workflow, source roles, architecture, input preparation, contracts, and a proposed evaluation protocol | Frozen baseline/treatment arms, dataset, annotations, variables, metrics, and statistical plan |
| IV System Development | Detailed code-grounded implementation chapter | Final branch/commit/configuration receipt and any diagrams or screenshots still required by the university format |
| V Experimental | Experimental design, dataset description, metrics, test fixtures, and result-table shells | Held-out runs, human or calibrated evaluation, failure accounting, and actual measurements |
| VI Conclusion | System limitations and engineering lessons | Results, research-question answers, contribution assessment, and conclusions based on data |

The strongest chapter available now is Chapter IV. Chapters I–III can be drafted around the current implementation, but their contribution and evaluation sections must stay explicitly provisional until the study design is frozen. Chapters V–VI cannot contain effectiveness findings yet.

## Chapter I boundary

Frame CyberCase as a prototype that helps a reader inspect a general case dossier, identify unresolved factual gaps, trace structured findings back to supplied sources, and assemble a preliminary report. Do not state that it reduces review time, improves legal decisions, eliminates hallucinations, or is validated for prosecutors until those outcomes are measured with an appropriate study.

The core objective does not require MITRE. If the thesis mentions MITRE, describe it as optional external technical augmentation, not as the source of case facts or as the core summarization method.

## Chapter II boundary

Use topic-based sections for:

- general case summarization and structured analysis;
- source attribution, provenance, and evidence-relative evaluation;
- OCR and downstream error propagation;
- human clarification or information-gap handling; and
- deterministic validation and report assembly.

Separate literature from implementation. Do not present SecureBERT, ChromaDB, Streamlit, DPR/BM25, Random Forest, Gradient Boosting, LSTM/GRU, Celery, RabbitMQ, or other unsupported tools as CyberCase components without current code and configuration evidence. Do not inherit claims from old drafts about FAISS, hallucination elimination, or verified professional performance.

## Chapter III proposed method description

Describe the method as a source-bounded workflow:

1. ingest a narrative or document;
2. preserve extracted text and provenance metadata as a native Case source;
3. assess unresolved gaps with a strict gaps-only contract;
4. use deterministic priority, askability, duplicate-question, and round rules;
5. call the structured main-analysis model only when the policy proceeds;
6. validate the JSON contract and resolve references against the source bundle and answered follow-up records;
7. persist a validated result with its source revision; and
8. assemble a deterministic preliminary report.

The LLM performs semantic assessment and analysis. The backend owns routing, stopping, source resolution, persistence, freshness checks, and report assembly. The thesis should call this a design and implementation boundary until comparative evaluation establishes a benefit.

## Chapter IV implementation outline

1. **Development environment and architecture** — FastAPI, PostgreSQL, Alembic, Next.js, request-scoped workflow, and module boundaries.
2. **Document intake and OCR** — PDF native extraction, OCR fallback, DOCX/image handling, page spans, warnings, and verification status.
3. **Case-source model** — narrative/document sources, `source_revision`, source bundle construction, and the separation of follow-up chat history.
4. **Pre-gap assessment** — `case_assessment_v1`, persisted assessment results, and the hand-off to deterministic policy.
5. **Follow-up workflow** — askable gaps, priority and round limits, chat routing, and re-analysis after a round is spent.
6. **Structured main analysis** — `main_case_analysis_v1`, provider validation, trace fields, and failure behavior.
7. **Source binding and traceability** — source IDs, exact quotes, QA references, grounding metadata, and unresolved-reference handling.
8. **Report generation and interface** — validated-analysis precondition, deterministic report sections, HTML/PDF rendering, and Case workspace views.

Do not make technical knowledge retrieval a required core section. If it is included for system completeness, label it as an optional external boundary and keep it separate from the non-RAG thesis method.

## Existing verification evidence

The checkout contains software-level verification for the assessment and follow-up paths, including recorded real-database assessment tests and chat-routing/concurrency tests dated 2026-09-21. The backend suite also has two Windows GTK/WeasyPrint PDF-rendering cases that are environment-dependent. These receipts verify contracts and workflow behavior; they are not summary-quality, OCR-accuracy, or user-benefit measurements.

Before final submission, record the exact branch, commit, dirty-worktree status, commands, pass/fail counts, provider configuration, and any environment-specific exclusions used to produce the thesis tables.

## Claims that must wait for Chapter V

- higher factual faithfulness or source support than a baseline;
- lower hallucination or unsupported-claim rate;
- improved OCR robustness or a measured OCR error rate;
- reduced latency, cost, or analyst workload;
- improved comprehension, trust, or task completion for prosecutors or other professionals;
- superiority of a claim-anchored, event-structured, sliding-window, or other experimental variant.

## Current deliverables and historical documents

The current English Chapter 3 and Chapter 4 DOCX deliverables are recorded in `deliverables/thesis-chapter3-2026-09-21/` and `deliverables/thesis-chapter4-2026-09-21/`. Their claims should follow this readiness note and the current implementation references.

Files under `docs/research/event-analysis-2026-09-19/`, `PHASE1_CLAIM_ANCHORED_PLAN.md`, and older migration or attribute-first notes are dated research/design or historical implementation records. They must not be cited as the current production flow without rechecking the code.
