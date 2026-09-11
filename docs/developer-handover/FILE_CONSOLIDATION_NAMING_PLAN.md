# Implementation plan: file consolidation and camelCase naming

Date: 2026-09-11
Status: DRAFT ONLY. No application renames or merges authorized by this document alone.

## 1. Goal and coordination gate

Reduce unnecessary files/indirection and make names describe actual responsibilities across frontend and backend, without changing behavior or persisted contracts.

The user reports Gemini is changing the flow. Luna was separately assigned Chat/Analysis separation. Before implementation, reconcile both working sets and completion receipts with the actual checkout. Do not assume either agent has stopped. No cleanup in their active files until ownership is released. Parent created this plan only; it does not dispatch implementation or interrupt another agent.

This plan supersedes the naming/consolidation recommendations of POST_LUNA_CLEANUP_IMPLEMENTATION_PLAN.md where they conflict. That older document describes older runtime paths and a strict 300-line threshold; neither should be treated as current proof. Legacy cutover gates remain independent. Report work stays last.

Success: fewer unnecessary indirections, coherent naming within each migrated subsystem, unchanged API/storage/prompt semantics, and tested behavior. A lower file count by itself is not success.

## 2. Naming policy — based on the installed skills

Use naming-analyzer and naming-cheatsheet: S-I-D (short, intuitive, descriptive), action + high context + optional low context; is/has/can/should for predicates; singular/plural matching values; create/delete for entities, add/remove for collection membership; handle/on for callbacks.

The user explicitly requests camelCase. Interpret this as an intentional project convention for application-owned functions and ordinary source module filenames in both TypeScript and Python. Python camelCase is a deliberate departure from customary snake_case, permitted by the installed skills. Do not install a different naming library just to do this refactor.

| Surface | Target policy | Examples / exceptions |
|---|---|---|
| TS/Python application functions and methods | camelCase, meaningful action | loadCaseAnswerContext, validateSnapshotManifest |
| Ordinary TS/Python module filenames | lower camelCase | caseClient.ts, caseAnswer.py |
| React hook filenames/functions | use + Pascal context | useCaseQueries.ts / useCaseQueries |
| React components, classes, interfaces, type aliases | PascalCase | CaseOverviewView.tsx, CaseAnalysisResult |
| Constants | UPPER_SNAKE_CASE | ANSWER_VERSION, RUN_LEASE_DURATION |
| New or directly touched local variables | camelCase where application-owned | snapshotId; no repo-wide variable churn in this phase |
| DB columns/tables, ORM fields, Pydantic wire fields, JSON metadata, enum values, error codes | Keep exact spelling | case_id, snapshot_id, question_answer, analysis_required |
| Framework/runtime entrypoints | Keep required names | __init__.py, __all__, __init__, page.tsx, layout.tsx, route.ts, middleware exports, pytest test_* and fixtures |
| Migration files/functions/revision identifiers | Keep unchanged | upgrade, downgrade, historical revision names |
| Generated type names | PascalCase, generator-owned | CaseRead; not caseRead |
| API URLs, route parameter names, localStorage/query keys | Keep existing contracts | No endpoint rename or saved-draft invalidation |

Special methods, third-party overrides, protocol methods and externally called keyword arguments need explicit exceptions. Do not rename them mechanically. Internal keyword parameters can be migrated only with every caller, including tests and callbacks, in the same batch.

Do not turn every private helper into a public function or class to remove an underscore. Use an existing cohesive module and deliberate exports. __all__ documents public API but is not access control. No one-method wrapper classes solely for naming compliance.

### 2.1. Code spacing and readability policy

Added 2026-09-11 at the user's request. Applies to handwritten frontend/backend code touched by an implementation batch; not permission for repository-wide formatting while other agents are editing.

- Separate logical stages with one blank line: input validation, context loading, transformation, side effects/persistence, and return. Keep tightly related statements together; do not insert a blank line after every statement.
- Python: two blank lines between top-level functions/classes, one between class methods. TypeScript/TSX: one blank line between top-level declarations and between logical groups inside functions/components. Do not accumulate additional blank lines for visual padding.
- Never compress multiple statements, early returns, exception handling or React effects onto a single line merely to lower physical LOC. Use normal indented blocks, including short guard clauses.
- Wrap long function signatures, calls, object literals, SQLAlchemy query chains and JSX prop lists across lines when they become difficult to scan. Use one argument/property per line in expanded blocks. Preserve readable short expressions inline.
- Expand compound conditions so their independent checks are easy to distinguish. Prefer a meaningful named predicate when wrapping alone does not make the condition understandable; do not introduce trivial variables solely for line count.
- Group imports consistently using the established formatter/import rules, with blank lines between groups where configured. Do not move side-effect imports, reorder hooks or change evaluation order for appearance.
- Preserve all whitespace inside prompts, exact quotes, evidence text, snapshots, SQL strings and serialization fixtures. Formatting source code must not rewrite runtime string content or change hashes.
- Readability takes priority over reducing physical LOC. The approximately 400–500-line guidance includes normal whitespace; do not remove blank lines, compress statements or create artificial micro-files to meet a number.
- Generated files must receive formatting through their generator, never manual edits. Their deterministic output and exact wire contracts remain mandatory.
- Use the repository's existing formatter configuration where available. If formatting tooling is absent or conflicting, record the proposed configuration for approval rather than adding a new formatter dependency or global rule silently. Formatter success does not replace a human-readable logical grouping review.

Example of the intended logical spacing (illustrative only, not an implementation change):

```python
async def loadCaseAnswerContext(db, runId):
    run = await db.get(CaseRun, runId)
    if run is None:
        raise CaseChatError("case_run_missing", "Case run is unavailable")

    result = await db.get(CaseAnalysisResult, run.context_analysis_result_id)
    if result is None:
        raise CaseChatError("analysis_required", "Analyze the Case before asking")

    return buildAnswerContext(run, result)
```

```typescript
async function handleSubmit() {
  if (!activeCaseId) {
    reportError("Open a Case before sending a message.");
    return;
  }

  const accepted = await submitQuestion(activeCaseId, question);

  await monitorCaseRun(activeCaseId, accepted.run.id);
}
```

Spacing exit gate for every merge/rename batch: inspect the changed functions for logical grouping, expanded control flow and readable multiline expressions; run the applicable existing formatting/lint checks and verify that protected string content is unchanged. Report formatting-only changes separately from renames or behavior changes.

## 3. Current inspection and limitations

Read-only inspection covered service-directory inventory, small modules, selected imports/callers, frontend hooks/clients, and the OpenAPI type generator. It is not an exhaustive reachability audit. Counts are physical lines measured during ongoing agent edits, so refresh at checkpoint A.

Backend service directories observed: auth 6 top-level Python files; case_analysis 28; case_materials 4; cases 3; chat 10; clients 2; document_ingestion 9; followup 16; llm 5; reports 26; workflow 12. Counts include __init__.py where present and exclude nested modules from these per-directory counts. No inference that a file is unused follows from these counts.

Frontend generated directory currently contains 36 TypeScript files. generate-api-types.mjs emits one schema per file and rejects >300 lines; this is a generator policy, not 36 independently authored interfaces. Its policy must be changed before grouping outputs.

Examples of current mixed names: case_run_claim.py contains claim_case_run alongside validateSnapshotManifest and recordRunFailure; chat/case_answer.py uses load_case_answer_context/request_case_answer. Plan naming against the post-Gemini behavior, not the old names alone.

No runtime tests, migration tests, browser tests or provider evaluations were executed for this planning task. Previous verification receipts are historical baselines only.

## 4. Concrete consolidation manifest

Paths below are relative to F:/Cybercase Framework. Targets are proposals, not files already created. Source LOC sums exclude import deduplication and are not final-size promises.

| ID | Sources → target | Decision | Why / gate |
|---|---|---|---|
| B1 | backend/app/services/chat/case_chat.py + case_chat_helpers.py + case_chat_errors.py → chat/caseChat.py | Candidate after flow freeze; observed 254+94+12=360 lines | One Chat admission/idempotency boundary. Inline the error and helpers only if no new cycle; update package exports, routes, patch targets. Keep Q&A generation separate. |
| B2 | backend/app/services/cases/case_management.py + case_factory.py → cases/caseService.py | Candidate; observed 145+24=169 | Case lifecycle and construction. Preserve buildCaseWithChat as explicit optional-chat constructor, never make every Case creation open Chat. Chat management currently imports factory: check cycle before merge. |
| F1 | frontend/src/lib/generated/*.ts → generated/caseTypes.ts, evidenceTypes.ts, runTypes.ts, chatTypes.ts, reportTypes.ts | Highest-value candidate, generator-first | Explicit schema ownership map, preserve exported PascalCase names and exact wire field optionality/unions. Split a domain only if emitted size/cohesion warrants it. Do not promise exactly five outputs before measuring. |
| F2 | frontend handwritten wire aliases in lib/api-types.ts → use generated domain types through apiTypes.ts | Conditional, after field-by-field comparison | Delete duplicate wire definitions only when equivalent; presentation-only types remain distinct. Do not silently narrow/widen historical payload acceptance. |
| B3 | reports/case_report_generation.py + case_report_template.py → reports/caseReportGeneration.py | Backlog LAST | Deterministic assembly may be cohesive, but status handling changed recently. Refresh size and freeze report behavior; not report redesign. |

Recommended initial hand-written reduction: B1 removes two source modules and B2 removes one, if all gates pass. Generated reduction is conditional on measured output, not a promised count. Do not add permanent one-file re-export shims for every deleted file, which would defeat the consolidation.

### Intentionally keep separate

- chat/case_answer.py: reads pinned analysis and generates Q&A; do not merge back into Case Analysis or Chat evidence admission.
- workflow claim, heartbeat, completion, failure and recovery: distinct lease/transaction responsibilities. Share naming, not necessarily files. pipeline.py is a legitimate stable worker entrypoint even at 22 lines.
- case_materials/errors.py (12 lines): shared by material service, snapshot builder, workflow and clarification; moving into material_service.py risks circular dependencies. Keep small independent error contract.
- claim_anchored/failure.py (11 lines): shared provider/binder/selector/assembly failure contract; keep leaf dependency.
- auth/passwords.py (18), jwt.py (52), request_guard.py (14): different security boundaries. Do not merge merely for file count or alter cryptographic behavior during naming cleanup.
- document ingestion segmentation/recognition interfaces and implementations: plugin boundaries are not duplicate helpers. OCR/HTR behavior is outside this cleanup.
- frontend lib/account-storage.ts (13) and hooks/use-account-state.ts (13): pure storage adapter is consumed outside React; merging makes non-React callers depend on a hook/client module.
- frontend lib/api.ts: stable consumer facade, not unnecessary duplication.
- frontend use-case-analysis-submission.ts and use-case-workspace-actions.ts: saved-retry lifecycle and broader UI orchestration differ; keep unless usage evidence supports consolidation.
- analysis citation contracts vs generated transport contracts vs UI presentation models: similar names do not establish interchangeable semantics.
- Next route leaves, migrations, package __init__.py: framework/history boundaries, not dead-file candidates.

## 5. Rename manifest

Apply source-to-target pairs only if the source still exists after Gemini/Luna completion. For files already merged, rename directly to the final target once. Avoid rename → merge → rename churn.

| Source | Target | Notes |
|---|---|---|
| backend/app/services/chat/case_answer.py | backend/app/services/chat/caseAnswer.py | Dedicated Q&A boundary |
| backend/app/services/workflow/case_run_claim.py | backend/app/services/workflow/caseRunClaim.py | Preserve transactional semantics |
| backend/app/services/workflow/case_run_execution.py | backend/app/services/workflow/caseRunExecution.py | Common run dispatch, not just main analysis |
| backend/app/services/workflow/case_ask_completion.py | backend/app/services/workflow/caseAskCompletion.py | ASK publication only |
| backend/app/services/workflow/case_run_heartbeat.py | backend/app/services/workflow/caseRunHeartbeat.py | Cancellation behavior unchanged |
| backend/app/services/case_materials/material_service.py | backend/app/services/case_materials/materialService.py | Folder rename deferred |
| backend/app/services/case_materials/snapshot_builder.py | backend/app/services/case_materials/snapshotBuilder.py | Snapshot bytes/hashes unchanged |
| frontend/src/lib/api-client.ts | frontend/src/lib/apiClient.ts | Keep facade exports stable |
| frontend/src/lib/api-types.ts | frontend/src/lib/apiTypes.ts | Generated/handwritten ownership audited first |
| frontend/src/lib/case-client.ts | frontend/src/lib/caseClient.ts | Do not merge all clients into a monolith |
| frontend/src/hooks/use-case-queries.ts | frontend/src/hooks/useCaseQueries.ts | Keep query key values unchanged |
| frontend/src/hooks/use-chat-queries.ts | frontend/src/hooks/useChatQueries.ts | Chat is still a distinct resource |
| frontend/src/hooks/use-case-run-polling.ts | frontend/src/hooks/useCaseRunPolling.ts | Poll timing/cancellation unchanged |
| frontend/src/hooks/use-case-analysis-submission.ts | frontend/src/hooks/useCaseAnalysisSubmission.ts | Storage key values unchanged |
| frontend/src/hooks/use-case-workspace-actions.ts | frontend/src/hooks/useCaseWorkspaceActions.ts | Wait for flow freeze |
| frontend/src/features/chat/runs/use-chat-submission.ts | frontend/src/features/chat/runs/useChatSubmission.ts | Explicit intent and retry preserved |
| frontend/src/features/chat/routing/chat-route.ts | frontend/src/features/chat/routing/workspaceRoutes.ts | Contains both Case routes and historical Chat redirects |
| frontend/src/lib/case-overview-native.ts | frontend/src/lib/caseOverviewNative.ts | Keep native distinction until legacy readers are independently retired |
| frontend/src/lib/technical-context.ts | frontend/src/lib/technicalContext.ts | Preserve external-context isolation |

Remaining ordinary filenames in auth, clients, followup, llm, document_ingestion, schemas, models and routers receive the same casing rule in separate subsystem batches. Checkpoint A must produce an exact path/symbol/caller manifest for each batch; do not use this rule as permission for an unreviewed global replace. Directory names are not included in the first rollout; a folder rename has broader import churn and can be considered later.

### Function naming analysis / priority matrix

These are selected reviewed examples, not a claim of an exhaustive symbol audit.

| Severity | Current → proposed | Reason |
|---|---|---|
| Major | locked_case_chat → lockCaseChat | Performs a locking read; name must reveal side effect |
| Major | existing_case_run → findCaseRunByIdempotencyKey | Lookup includes intent/fingerprint checks; document that it may reject conflicts |
| Major | request_payload → buildChatRequestPayload | Constructs a value rather than making a network request |
| Major | clarification_request → buildClarificationRequest | Request construction, not submission |
| Major | request_case_answer → generateCaseAnswer | Generates Q&A from pinned context; not main analysis |
| Minor | load_case_answer_context → loadCaseAnswerContext | Already meaningful; casing only |
| Minor | claim_case_run → claimCaseRun | Keep exact lease claim meaning |
| Minor | complete_case_ask → completeCaseAsk | Preserve operation-specific completion |
| Minor | create_case_chat_message_and_run → createCaseChatMessageAndRun | Long but honestly describes atomic creation; do not shorten to sendMessage |
| Minor | build_case_with_chat → buildCaseWithChat | In-memory construction, not DB persistence |
| Minor | serialize_case → serializeCase | Serialization, not fetch or analysis |

No Critical naming-only issue is asserted here. The known Chat implicit-analysis behavior is a functional bug owned by the flow implementation, not something renaming can fix.

## 6. Implementation checkpoints and exit gates

### A — Freeze and baseline

1. Confirm Gemini/Luna completion and released write sets. Read their receipts and current diff; record exact branch/HEAD, dirty file hashes and untracked inventory.
2. Inventory both frontend/backend: source, symbols, references, barrel exports, dynamic imports, string monkeypatch targets, test discovery, scripts, Docker entrypoints and generated ownership. Flag shared external symbols.
3. Baseline tests and OpenAPI schema including operationIds, not only paths. Default FastAPI operationIds can depend on function names; renaming route handlers may change clients despite unchanged URL.
4. Capture representative serialization, snapshot/hash, prompt and error payload fixtures. Use synthetic data, no real case content in new artifacts.

Exit: exact per-batch manifest and exception list approved; concurrent flow changes stopped; known baseline failures recorded. No mass renaming before this gate.

### B — Frontend generated consolidation

1. Update generate-api-types.mjs (rename script only with package.json references) to deterministic domain ownership, imports and output manifest.
2. Preserve type names and wire properties. Reject unassigned schemas and duplicate ownership; do not silently omit schemas.
3. Generate twice and compare byte equality. --check must detect changed, missing and obsolete generator-owned files, including stale extras.
4. Migrate imports/facade; delete only verified old generated outputs inside the exact generated directory. No broad directory delete and no handwritten generated shims.

Exit: generator repeatability, negative stale-file tests, tsc, API check and frontend tests pass. New domain files are cohesive; approximately 400–500 physical lines is acceptable, not a mandatory target or blanket hard limit.

### C — Handwritten merges

Implement B1 and B2 separately, after confirming their dependency graphs. Resolve final filenames at merge time. Do not change errors, lock order, idempotency, default actions, evidence admission or publication. If a merge creates a cycle or unsafe coupling, keep separate and record why.

Exit per merge: no stale imports/patch targets, package import smoke tests, focused API/PostgreSQL tests pass and no behavior delta. Do not combine report merges with this checkpoint.

### D — CamelCase rollout in bounded batches

Suggested sequence: frontend hooks/clients → backend cases/materials → chat → workflow → remaining analysis/followup → auth/ingestion/llm and route handlers → reports last.

Use syntax-aware symbol changes, not regex substitutions inside arbitrary text. Update Python keyword calls, __all__, decorators referring to method names, mocks and script import paths. Preserve JSON/Pydantic/ORM fields, environment variables, SQL, prompt text and historical migrations. Handle framework-required methods via exceptions.

On Windows, use a verified temporary filename for case-only renames and validate the final tracked casing on a case-sensitive Linux environment. Avoid git mv for untracked files; do not stage unrelated changes. No permanent compatibility aliases unless an actual external consumer requires one; record owner and removal gate if needed.

Exit per batch: imports resolve; API schema and operationIds unchanged or explicitly pinned to baseline; no accidental wire-key or prompt-byte change; naming scan exceptions are explicit. No unexplained old/new duplicate public functions.

### E — End-to-end verification and handoff

- Full backend pytest on real PostgreSQL disposable schemas, including idempotency, stale/pinned context, concurrent run ownership, publication and source binding.
- Frontend Vitest, TypeScript, generated API check, production build and scoped lint; report pre-existing full lint findings separately.
- Backend Ruff/compile/import checks; inspect naming rules rather than globally disabling lint to accept churn.
- Browser acceptance: Chat before analysis must not enqueue analysis; Case analysis works with Chat closed; publication appears; ASK does not mutate evidence/main result; clarification uses explicit route; lost-response retry does not duplicate work; legacy redirects respect ownership.
- If browser or Linux casing verification cannot be run, mark the gate unverified. Mocked provider tests do not establish live generation quality.
- No migration should be needed. If schema/DB migration becomes necessary, stop and separate that change. Existing legacy cutover/drain blockers remain blocked unless independently satisfied.
- Report before/after files, imports and actual LOC, removed symbols, exceptions, exact commands/results and remaining failures. Do not claim all backend code was audited from a small-file inventory.

## 7. Risk and relative complexity

| Batch | Complexity | Principal risk | Control |
|---|---|---|---|
| Frontend filename/function changes | Low–medium | import casing and mocks | tsc + build + case-sensitive check |
| Generated schema grouping | Medium | silent wire drift / stale outputs | exact ownership manifest + repeatability + schema comparison |
| B1/B2 merge | Medium | import cycles or transaction change | one merge per patch; PostgreSQL focused regressions |
| Python function/module changes | Medium–high | keyword callers, dynamic imports, route operationIds | symbol inventory + preserved contracts + full tests |
| Workflow/analysis cleanup | High while flow is moving | retry/lease/provenance regressions | wait for freeze; behavior-preserving batches |
| Auth/ingestion naming | Medium–high | security and plugin entrypoints | keep framework interfaces, focused tests |
| Reports | Deferred | persisted/export compatibility | last, independent regression gate |

Do not estimate calendar duration until the final Gemini/Luna diff is available. Start with F1 and a single safe merge, not a repository-wide rename in one patch. A plan completion does not authorize deployment, paid provider calls, commits, live DB modification or edits to rag_service/**.
