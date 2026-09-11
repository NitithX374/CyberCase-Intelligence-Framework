# Backend architecture simplification

Date: 2026-09-11
Branch: `codex/backend-architecture-simplification`

## Resulting production flow

```text
Document or Text Input
        ↓
Case Evidence → Direct Main Analysis LLM
        │          ├─ summary and findings
        │          ├─ material unresolved gaps
        │          └─ exact supporting/contradicting quotations validated against evidence
        │
        ├─→ Deterministic Selection over Model-Identified Gaps → Optional Question Realization
        │
        └─→ MITRE Applicability Gate ─SKIP
                         └─RETRIEVE→ rag_service → MITRE Mapping

Main Analysis + Optional MITRE Result + Limitations
        ↓
Deterministic Preliminary Report
```

## Current path and classification

| Component | Live path | Decision | Reason |
| --- | --- | --- | --- |
| Case routes and run worker | `routers/caseAnalysis.py`, `services/workflow/caseRunExecution.py` | KEEP | Stable asynchronous API, ownership, retries, and failure isolation support current UI flows. |
| Documents, OCR, evidence admission | `routers/caseMaterials.py`, `services/document_ingestion/`, `services/case_materials/` | KEEP | Required intake and thesis evaluation capability. |
| Direct Main Analysis | `services/case_analysis/caseAnalysis.py` | KEEP and SIMPLIFY | It is now the only configuration selected for new runs and emits gaps in the same structured result. |
| Claim-anchored extraction/binding/selection | `services/case_analysis/claim_anchored/` | ISOLATE AS EXPERIMENTAL | Useful for historical and research compatibility; it is not selectable for new production runs. |
| Legacy v3 prompt builder | `services/case_analysis/legacyPrompts.py` | ISOLATE AS EXPERIMENTAL | Retained for historical tests and research; no production Case import depends on it. |
| Separate Gap Analysis LLM | `services/followup/gapAnalysis.py`, `experimentalGapPrompts.py` | ISOLATE AS EXPERIMENTAL | Main Analysis now owns gap identification; the Case worker does not invoke this stage. |
| Follow-up state/history selection | `services/followup/stateful.py`, `decision.py` | KEEP and SIMPLIFY | It deterministically selects among gaps identified by Main Analysis using deduplication, unknown suppression, priority, and maximum-round rules. |
| Follow-up provider | `services/followup/policy.py` | SIMPLIFY | It receives one selected gap and only phrases a concise question. |
| MITRE applicability, retrieval, mapping | `mitreApplicabilityGate.py`, `workflow/caseMitreAugmentation.py` | KEEP | Explicit grounded gate explains invocation; SKIP and fail-open behavior preserve normal analysis. |
| Reports | `services/reports/`, `routers/caseReports.py` | KEEP | Deterministic preliminary report remains available; persistence was not expanded. |
| Historical trace readers and stable DB fields | `contracts.py`, models and migrations | KEEP | Non-destructive compatibility is cheaper and safer than schema deletion in this pass. |

## Concrete refactor

- New production runs always persist `raw_direct` / `main_case_analysis_v1`; claim-anchored is not selectable for new production runs, but remains reachable for historical and research compatibility.
- `CaseProviderAnalysis` now includes the existing compact `CaseAnalysisGap` schema.
- The worker passes model-identified `CaseAnalysisTrace.gaps` directly into deterministic follow-up selection, bypassing the second semantic Gap Analysis call.
- Direct Main Analysis continues to validate exact supporting and contradicting quotations against the admitted evidence.
- The follow-up prompt was reduced from 202 lines of policy prose to a bounded question-realization instruction; selection remains backend-owned.
- Shared active provider calls moved out of the experimental claim-anchored package.
- Active package exports no longer import legacy prompt and gap-analysis modules.
- Public routes, PostgreSQL schema, OCR, authentication, Chat history, MITRE behavior, and reports were preserved.

No destructive migration, live data mutation, `rag_service/**` edit, deployment, or paid provider call is part of this refactor.
