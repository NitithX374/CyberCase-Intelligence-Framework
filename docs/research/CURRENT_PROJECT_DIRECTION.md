# CyberCase Current Project Direction

**Status:** current product and thesis boundary as of 2026-09-22.

This document describes the runtime that is currently in the checkout and separates implemented behavior from optional integrations and research proposals. Dated audits, migration receipts, and experiment plans remain historical records; they are not used to override the current code path.

## 1. Confirmed product scope

- **Core task:** general case summarization and preliminary case analysis.
- **Primary input:** one Case with one or more native Case sources. A source may be a user-authored narrative or text extracted from an uploaded document.
- **Document intake:** PDF, DOCX, and image uploads are converted to text. PDFs use native extraction when usable and OCR fallback when needed. OCR provenance, warnings, extraction method, verification status, and page spans are retained with the document source.
- **Follow-up input:** clarification answers are persisted as Case chat messages. They are included in later analysis as separate follow-up history and may receive synthetic QA identifiers for traceability; they are not native Case sources and do not increment `source_revision`.
- **Technical augmentation:** MITRE ATT&CK retrieval through `rag_service` is optional external context. It is not required for the core workflow, is outside the non-RAG thesis scope, and is never treated as a Case source.

The product is a prototype for inspectable analysis. It does not make legal decisions, determine guilt, establish that an allegation is true, or replace professional review of the original documents.

## 2. Current production workflow

```text
Case narrative / document upload
              ↓
Document extraction → native CaseSource + source_revision
              ↓
Read CaseSourceBundle + follow-up history
              ↓
Gap-only assessment (case_assessment_v1)
              ↓
Deterministic follow-up policy
       ┌──────┴──────────┐
       │                 │
       Ask               Proceed
       │                 ↓
Persist assessment       Optional MITRE augmentation
and focused question             ↓
       │                Main structured analysis
       │                 (main_case_analysis_v1)
       │                          ↓
       └──────────────→ Deterministic source binding
                                  ↓
                         Validated analysis result
                                  ↓
                    Deterministic template-first report
```

The core workflow without `rag_service` is:

```text
CASE SOURCES + FOLLOW-UP HISTORY
              ↓
Gap assessment → follow-up decision
              ↓
Ask and stop, or proceed
              ↓
One structured main-analysis call
              ↓
Schema validation and source binding
              ↓
Validated analysis → report
```

An askable gap stops the request before the full main-analysis call and source binding. After the user answers the selected question, the next chat request either asks the next gap or starts another analysis when the round is complete. Ordinary Case Ask questions use a separate answer path and do not silently create a new Case analysis.

## 3. Current implementation boundary

### Language-model responsibilities

- Assess unresolved factual gaps using the strict `case_assessment_v1` contract.
- Produce the structured `main_case_analysis_v1` result when the deterministic policy permits full analysis.
- Answer ordinary Case Ask questions using the selected analysis context.
- Optionally classify MITRE applicability when the external augmentation path is enabled.

### Deterministic backend responsibilities

- Load and validate the Case source bundle.
- Track `source_revision`, follow-up history, asked gap keys, round limits, and stopping decisions.
- Validate structured provider output.
- Resolve source identifiers and verify literal quotations against native sources or answered follow-up records.
- Persist assessment and validated results with explicit statuses.
- Reject a result if the native Case source revision changed during model work.
- Assemble and validate the preliminary report and render HTML/PDF.

The analysis steps do not access the database. The workflow reads the Case in a short transaction, performs model or external-service work without holding that transaction, and stores the result in a second short transaction. There is no `CaseRun` table, run-status endpoint, job queue, or frontend polling loop.

## 4. Source roles and trust boundary

Only native Case sources support incident facts, timelines, parties, impacts, and findings. A follow-up answer is information supplied by the reader and is carried separately from the native source bundle. Assistant output and external MITRE/RAG context are not admitted Case facts.

The system preserves reported, suspected, contradicted, unknown, and not-established distinctions where the analysis contract provides them. A valid exact quote is evidence that a string occurs in a source; it is not by itself proof that the model's larger claim is semantically correct.

## 5. Current code contracts

| Concern | Current contract or boundary |
|---|---|
| Analysis pipeline | `raw_direct` / `main_case_analysis_v1` |
| Pre-analysis assessment | `case_assessment_v1` |
| Native input | `CaseSourceBundle(revision, sources)` |
| Follow-up state | `ChatMessage` history, gap keys, round budget |
| Full-analysis output | `CaseAnalysisTrace` with summary, claims, timeline, parties, impacts, gaps, grounding, and optional technical associations |
| Report | Deterministic structured report from a validated analysis |
| Technical context | Optional external augmentation, isolated from Case facts |

The production configuration currently exposes `raw_direct` only. Claim-anchored, split, revise, event-structured, and other alternative compositions belong to experiment or planning areas unless a separate implementation receipt explicitly promotes one to production.

## 6. Thesis scope that is supportable now

The current implementation supports a code-grounded system-development chapter on:

1. document ingestion, OCR fallback, and extraction provenance;
2. native Case-source persistence and source revision tracking;
3. pre-gap assessment and bounded deterministic clarification;
4. structured main analysis and provider/schema validation;
5. deterministic source binding and traceability metadata;
6. request-scoped persistence and stale-source protection;
7. Case chat/follow-up interaction; and
8. deterministic report assembly and HTML/PDF rendering.

These are implementation capabilities. They do not establish higher factual accuracy, lower hallucination, OCR robustness, professional usefulness, prosecutor comprehension, or superiority over a baseline until a separately designed evaluation is run.

## 7. Research status

The following are candidate research directions, not completed findings:

- evaluate whether source-bounded structured analysis and deterministic binding improve source-relative support or inspectability compared with a clearly defined baseline;
- measure how OCR corruption propagates into case summaries using verified clean text, cached OCR text, and independent annotations;
- evaluate the usability of the core Case workflow with a defined participant population and protocol.

No current implementation receipt is a substitute for human semantic evaluation. Software tests establish route, schema, persistence, and workflow behavior; they do not prove summary quality or research effectiveness.

## 8. Explicit non-goals

- Legal reasoning, statutory interpretation, charging, sentencing, or guilt decisions.
- Handwritten text recognition (HTR).
- Automatic OCR correction that may alter names, numbers, or negation.
- Training a custom Thai NER model as part of the core system.
- Replacing the external MITRE knowledge base or redesigning `rag_service`.
- Multi-agent debate or unbounded self-reflection loops.
- Claiming a full CAMS or other published-method reproduction without a separate verified implementation and evaluation.
- Treating external knowledge, assistant text, or a follow-up answer as a native Case source merely because it appears in the UI.

## 9. Canonical implementation references

- Analysis orchestration: `backend/app/services/analysis/pipeline.py`
- Case workflow and persistence: `backend/app/services/workflow/run_analysis.py` and `analysis_storage.py`
- Gap policy: `backend/app/services/analysis/clarification.py`
- Document ingestion: `backend/app/services/document_ingestion/`
- Native source bundle: `backend/app/services/sources/`
- Source binding: `backend/app/services/analysis/steps/bind.py`
- Report assembly: `backend/app/services/reports/`
- Route boundary: `backend/tests/test_route_surface.py`
