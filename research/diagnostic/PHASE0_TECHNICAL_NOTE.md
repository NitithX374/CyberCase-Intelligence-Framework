# Main Case Analysis diagnostic — Phase 0 technical note

Date: 2026-08-18

## Current production boundaries

- The canonical Case State is `CaseState` in
  `backend/app/services/extraction/llm_extraction.py`. Its production shape is
  `{entities, relationships, evidence, timeline, warnings}`. Entity,
  relationship, evidence, and timeline records carry their own IDs, confidence
  and epistemic/status fields; source-message UUIDs provide provenance.
- `backend/app/services/case_analysis/service.py` contains the current
  read-only `MainCaseAnalysisService`. It does not retrieve, mutate, persist,
  extract, or generate reports. The checked-in prompt version is
  `main_case_analysis_v2`; the case-overview mode is the five-section overview
  used for the initial Main Case Analysis.
- `backend/app/services/chat/case_state_retrieval.py` provides the current
  `project_case_state_to_retrieval_query()` projection. It normalizes the
  production Case State and sends only the retrieval projection of entities,
  relationships, evidence, and timeline; extraction/provider metadata and
  source-message IDs are excluded from the retrieval query.
- `backend/app/services/chat/outcome_mapper.py` defines the current analysis
  context boundary. `RagContextPayload.to_analysis_context()` returns:
  `retrieved_context`, `retrieval_context_id`, `mitre_table`, and
  `previous_analysis: null`. This is the exact shape the diagnostic must pass
  to Main Case Analysis. The durable `RagContext` model stores the context and
  MITRE table against a Case State version, while the RAG service also exposes
  a retrieval-context snapshot endpoint for its in-process cache.
- The current RAG HTTP route is `rag_service/app/routers/rag.py::query`, which
  calls the checked-in `GraphRAGAgent.query()`, builds the MITRE table from the
  returned GraphRAG result and answer, and returns the context/table to the
  backend. A live snapshot was attempted but was not available in this
  environment; the fallback is explicitly recorded below rather than
  represented as production RAG output.

## Existing fixtures and scope decisions

`experiments/semantic_verification/` is an offline deterministic relationship
and timeline benchmark. It is useful as a construction reference but does not
exercise the current Case State → RAG context → Main Case Analysis boundary.
The pre-existing untracked `evaluation/analysis_pilot/` directory is user-owned
work and is not modified or reused as this experiment's result set.

The new cases in `diagnostic_cases.jsonl` use the current `CaseState` shape and
keep `diagnostic_notes` outside the production input contract. The notes are
authoring/evaluation metadata only.

## Execution gate and observed environment

Read-only connectivity checks succeeded for the configured remote Qdrant and
Neo4j stores, and the configured Main Analysis target resolves to the current
OpenRouter model `openai/gpt-5.6-luna`. Docker Desktop was not running, so the
local production HTTP services were unavailable. A direct smoke invocation of
the checked-in `GraphRAGAgent` was then attempted with the current environment;
its CPU-only initialization/query path did not return within a 240-second
bound. The smoke process was stopped after confirming it was the diagnostic
probe.

Because the exact current RAG context could not be frozen in this environment,
the user authorized a no-RAG pilot. The diagnostic therefore passes an
explicit empty context (`retrieved_context: ""`, empty `mitre_table`, null
retrieval ID and null previous analysis) and labels every result
`NO_RAG_FIXED_EMPTY_CONTEXT`. No synthetic or manually curated MITRE context
is written. This fallback is useful only for the fixed Case State → Main Case
Analysis boundary; it does not establish behavior of the RAG-grounded flow.

The completed fallback run produced 12 successful Main Case Analysis calls,
570 atomic claims, 570 judge-A audits, 570 independent same-model judge-B
audits, and 49 coverage judgments. Both judges used the configured Luna model;
judge B is independent but not model-diverse. See `summary.json` and
`DIAGNOSTIC_REPORT.md` for the bounded interpretation.
