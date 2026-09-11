# Architecture simplicity audit

Date: 2026-09-11
Scope: read-only structural audit of current frontend/backend; no implementation, deployment or agent redirection.

## Verdict

Simplify selectively. The main problem is overlapping ownership and accumulated compatibility paths, not the number of types or the existence of evidence snapshots. File consolidation/camelCase improves navigation but does not resolve those architectural costs.

The simpler target is one Case-owned state source, one run-observation mechanism, separate Analysis and Q&A operations, and explicit legacy adapters outside the native path. Keep evidence provenance, access control and transactional integrity.

## Evidence limitations

Reviewed UI composition, query/session/polling paths, Case serialization and run admission, analysis dispatcher, document ingestion construction, representative report generation paths, generated type facade and evidence/run ORM models. This is not an exhaustive line-by-line security/dead-code audit. Auth/provider internals and rag_service retrieval algorithms were not deeply audited.

Luna/Gemini work is active: files were renamed during reads (case_management.py became caseService.py; case_run_execution.py became caseRunExecution.py). These transient missing paths are not reported as permanent defects. Paths below are the observed paths; resolve their current names after the rename batch. No fresh test suite, browser reproduction, performance measurements, production census or migration rehearsal was run. Findings are structural simplification opportunities, not runtime cutover certification.

## 1. High priority: Case state still depends on optional Chat

Evidence:

- backend/app/services/cases/caseService.py:16 serializes Case state; at line 25 it prefers thread.status whenever a thread exists, while processing_status is derived separately from CaseRun.
- frontend/src/hooks/useCaseQueries.ts:83 builds a partial CaseRead from ChatThreadRead, copying thread.status and using thread.id as Case id.
- frontend/src/components/ChatWorkspace.tsx:53 sends that projection back into the Case cache when a Chat detail is read.

Consequence: Case and Chat both contribute versions of Case state. Consumers need reconciliation/fallback logic, and opening Chat can influence the visible Case projection. This contradicts the intended optional-Chat ownership boundary, even if individual values happen to agree in a particular run.

Smallest simplification: backend is the sole source of Case workflow status/freshness; Chat updates only transcript/draft state. Replace Chat-to-Case cache synthesis with targeted Case query invalidation. Distinguish ongoing ASK from main-analysis status deliberately; do not hide ASK failures as failed main analysis.

Gate: opening/closing Chat, ASK failure, new evidence and pending clarification do not incorrectly alter main-analysis state. No DB redesign is required merely to remove the frontend projection.

## 2. High priority: Two run-observation mechanisms in frontend

Evidence:

- frontend/src/hooks/useCaseRunPolling.ts:21 uses TanStack Query refetchInterval for CaseRun.
- frontend/src/features/chat/workspace/use-chat-thread-selection.ts:75 starts pollCaseRunUntilSettled for a CaseRun and manually refreshes Chat and Case queries.
- ChatWorkspace mounts the Case polling hook while Chat submission uses the session monitor.

Consequence: duplicate scheduling, cancellation and terminal-state invalidation logic. The two paths can observe the same run. Actual excess request counts were not measured.

Smallest simplification: one run query keyed by caseId/runId, shared by workspace and Chat. Keep draft/idempotency persistence and selection cancellation; those are not redundant. Publish terminal-state cache updates once. If a Promise-based caller is needed, adapt it to the shared observer rather than creating another network loop.

Gate: lost receipt, refresh, selecting another Case, run retry and Chat closed all remain correct; compare request counts in an integration test.

## 3. Medium priority: Generated contracts are weakened again in the facade

Evidence: frontend/src/lib/apiTypes.ts:16 uses Omit to replace evidence_revision, latest_analysis_result_id, processing_status and analysis_freshness with optional fields. It also locally reconstructs accepted response types and loosens message fields. Generated schemas are now grouped into domain files by ongoing work, but that does not remove the second type definition layer.

Consequence: native consumers accept partial objects and need absence checks even where the native wire contract is stronger. This also permits the Chat-to-Case synthetic object above.

Smallest simplification: native consumers use generated types unchanged. If historical payloads need looser shapes, define one explicitly named legacy input type at the legacy boundary and validate/convert it there. Keep genuine UI view models separate; do not replace everything with one huge optional-field type.

Gate: compare actual API schema and historical fixtures first. Do not blindly strengthen types and claim runtime compatibility. Update native fixtures rather than keeping production fields optional only to accommodate old tests.

## 4. Medium priority: Native and older analysis branches remain in one dispatcher

Evidence: backend/app/services/case_analysis/case_analysis_executor.py:59 dispatches native source-reference context to analyze_case_native; line 71 retains a separate claim_anchored service for other context, followed by older direct-analysis logic. Native analysis itself supports configurable analysis methods. Native/legacy report persistence likewise calls separate run_case_report_generation and run_report_generation paths.

Consequence: several contract/pipeline combinations remain in the application, increasing the number of paths a maintainer must understand. Some may be necessary research controls or historical behavior; absence of a current UI call does not prove they are dead.

Smallest simplification: map production callers versus research entrypoints versus historical read/export support. Give production one explicit native entrypoint; keep required baseline experiments behind a separate research entrypoint. Historical reading does not automatically require historical generation/execution. Retire only proven unused writers after existing retirement gates.

Gate: enumerate callers/configuration/persisted versions and run corresponding regressions. No broad deletion or removal of research baselines based on this observation. Reports remain last, per user instruction.

## 5. Conditional: Document ingestion has more routing machinery than its configured segmenter

Evidence: backend/app/routers/document_ingestion.py:_build_region_pipeline constructs WholePageRegionSegmenter with RegionRouter and htr_enabled=False plus ReviewRequiredHTRRecognizer. document_ingestion/service.py supports native PDF/DOCX and recognition; region_pipeline.py carries per-region routing, merging and recognition candidates.

Consequence: the product may carry abstractions for fine-grained regional OCR/HTR while the configured entrypoint operates at whole-page granularity. Whether this is unnecessary depends on supported configurations and planned requirements, not names alone.

Smallest simplification to evaluate: retain native extraction plus one clear whole-page recognition path for the supported product configuration; keep provider adapters. Move experimental segmentation/HTR wiring away from the default flow if no active requirement needs it. Do not remove page/source provenance or review status.

Gate: verify all supported ingestion modes, provider configurations, document fixtures and other callers first. No deletion is currently approved by this finding.

## 6. Lower priority: File/word cleanup is useful but not the core fix

The separate consolidation plan addresses tiny helper groups and generated schema files. Narrative currently labels handwritten text, document drafts and document source/page contracts; narrower names improve comprehension. Neither camelCase nor fewer files removes duplicate state ownership.

Do not create a new abstraction layer just to unify names. Do not merge request, acceptance receipt and completed result types: asynchronous processing gives them genuinely different contracts. Do not rename persisted enum/JSON values as part of presentation naming.

## Complexity that is justified

- CaseDocument / DocumentExtraction: original material and a derived extraction are not the same artifact.
- EvidenceSource / EvidenceRevision / CaseEvidenceSnapshot (models/case_materials.py): track admitted text, edits and the exact version used by a run. Keep these guarantees while simplifying service wiring.
- CaseRun / CaseAnalysisResult (models/case_run.py): operational attempt versus durable output. A failed run must not replace a valid analysis.
- Exact quote binding and source-role isolation: remove these and debugging gets easier only because correctness checks disappear.
- Transactional idempotency, locks, leases and atomic publication: necessary for retry/concurrent requests. File placement can change; guarantees must not.
- Separate Q&A and Analysis use cases sharing worker infrastructure: appropriate. Do not rebuild a separate queue system for Chat merely to separate prompts.
- Conditional MITRE service boundary: appropriate for the stated requirement. Graph/vector retrieval benefit versus a simpler retrieval baseline requires evaluation; this audit does not establish that either store should be removed.
- Small security/contract/entrypoint modules: size alone does not establish overengineering.

## Recommended order

1. Let current flow and naming changes settle; independently verify their behavior.
2. Remove Chat-derived Case state and make Case status semantics explicit.
3. Consolidate frontend run observation, retaining saved retry intent and cancellation.
4. Remove native facade type weakening; isolate historical adapters.
5. Audit production/research/legacy execution separation, then ingestion routing scope with actual requirements.
6. Report consolidation/redesign remains last.

Acceptance: fewer independent state owners, one polling mechanism, native consumers using one wire contract, explicit production operation dispatch, and unchanged evidence/run guarantees. Do not use number of files removed as the primary metric.

Final assessment: targeted architectural rework, not a rewrite. The highest-value simplification is removing duplicate ownership, not collapsing the evidence model.
