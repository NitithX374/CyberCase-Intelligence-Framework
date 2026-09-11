# Post-Luna cleanup: frontend/backend audit and implementation plan

Date: 2026-09-10

Status: DRAFT. Read-only source audit and planning; no application cleanup implemented. Luna test totals are agent-reported, not independently rerun here. Preserve all existing dirty changes, including generated files, research artifacts, documentation and fixes from other work.

Revision 2 (2026-09-10): explicit source-to-target merge manifest added after inspecting backend reports. This revision includes both structural consolidation and a separately gated legacy migration track. Tables below supersede vague merge suggestions; numbers are source physical-line sums before import deduplication, not promised final LOC.

## Goal and simpler alternative

Reduce unnecessary indirection and duplicated contracts without deleting active behavior. Prefer removing unused symbols and grouping generated schemas by domain over a wholesale rename or broad merge. One small file is not inherently bad: a public boundary, framework entrypoint or independently tested stateful hook can justify it.

Maintain <=300 physical lines per touched code file. Do not merge files only to improve file count. Do not implement new report requirements, modify rag_service, deploy, alter live data, stage or commit as part of this plan.

## Evidence and scope limits

Inspected current dirty checkout: route registration, Chat message dispatch, both worker entrypoints/recovery tasks, native analysis dispatch, workspace native/legacy branches, generated type script, API facades, small-file inventory and oversized production files. No exhaustive dynamic reachability proof, authenticated browser verification, database census, migration rehearsal or independent full-suite run was performed for this plan.

An earlier failed PowerShell wildcard rg invocation was superseded by directory searches with -g patterns. Inventory is a point-in-time observation; refresh after agents finish. No file should be deleted using this document as the sole proof of being unused.

## Findings ordered by consequence

### F1. Preserve MITRE before retiring the legacy pipeline (high)

Evidence: backend/app/services/workflow/case_run_execution.py calls request_case_analysis with native source context; case_analysis_executor.py dispatches that source type to case_native_analysis.py. The native implementation constructs empty mitre_associations; case_run_completion.py records rag_invoked=False. ChatWorkspaceLayout.tsx still feeds TechnicalContextView from messages.

Conclusion: static native path inspected does not establish conditional MITRE retrieval. This is a product-completeness issue, not dead-code cleanup. Keep mitre_applicability_*, clients/rag_client.py, technical-context presentation and required legacy augmentation behavior. Before old pipeline retirement, separately trace applicable/not-applicable native runs through retrieval, result persistence, report and UI with Chat closed. Do not claim native MITRE coverage from tests of legacy process_chat_run.

### F2. Legacy Chat remains reachable; names are not deletion evidence (high)

Evidence: backend/app/routers/chat.py create_chat_message dispatches Case-linked threads to process_case_run and the alternate branch to process_chat_run. main.py registers chat routes and starts both monitor_interrupted_runs and monitor_case_runs. frontend ChatWorkspace branches on /case vs /chat; ChatWorkspaceLayout retains ChatReportView and adapters in CaseIntakeView/CaseMaterialsView.

Keep legacy workers/readers until the alternate route, existing runs, stored snapshots and external clients have been accounted for. New-thread factory building a Case does not prove all persisted old threads have one. Removing an old writer and removing historical readers are separate decisions. Preserve optional Chat Q&A and automatic analysis-result publication.

### F3. Generated one-type files are a generator policy, not hand-written fragmentation (medium)

Evidence: frontend/scripts/generate-api-types.mjs traverses referenced OpenAPI schemas and writes generated/${name}.ts, enforcing 300 lines per schema. Its --check compares expected content but does not detect extra stale files. Small CaseAnalysisAccepted/CaseRead/etc. files originate here.

Proposal: explicit domain ownership map for generated schemas: case, materials/evidence, runs/clarifications, chat/metadata, reports. Compute actual emitted LOC first and split oversized domains at semantic boundaries. Reject unassigned schemas; deterministic imports/order. No handwritten edits to generated types. Preserve stable consumer facade @/lib/api; migrate direct generated imports in the same patch. Avoid creating permanent per-type re-export shims, which would retain the file clutter.

Generator must emit/check an exact manifest, detect stale artifacts, and delete only verified generator-owned obsolete outputs after import migration. Two generate runs must be identical. Do not put all schemas into a >300-line mega-file or silently truncate them.

### F4. Handwritten report interfaces duplicate generated contracts (medium)

Evidence: frontend/src/lib/api-types.ts defines ChatReportRead, ChatStructuredReport, ChatReportSection and ChatReportClaim while generated equivalents exist. These are not identical: generated source_reference_type is required, hand-written is optional; generated section_id is a literal union; generated arrays can be optional while handwritten versions require some arrays.

Proposal: generated contracts own the wire shape. Where rendering requires normalized arrays, define an explicit UI projection/adapter and test it, rather than replacing types with casts or inventing server defaults. Audit CaseRead/PersistedChatMessage optionalization and fixtures separately. Do not tighten historical compatibility without evidence of supported payloads.

### F5. Tiny deletions and consolidation opportunities (low)

| Candidate | Current evidence | Proposed action | Gate |
|---|---|---|---|
| ChatWorkspace.tsx caseRunPhase alias | Search found only its declaration; determineCaseRunPhase is used | Delete alias | Refresh full-tree symbol search; tsc/lint |
| common/types.ts workspaceViewForRoute | Identity function, no caller in searched frontend | Delete function; consider WorkspaceRouteView alias separately | Route tests; no exported external consumer |
| common/SignOutDialog.tsx | Four-line re-export; two production consumers, no independent behavior | Consolidate in common/ConfirmationDialog.tsx by renaming current DeleteDialog implementation and updating both imports | Sign-out/cancel/delete tests; no permanent alias file |
| lib/api-types.ts report interfaces | Duplicated generated schemas with real differences | Replace wire duplication, retain explicit UI projection if necessary | Contract fixtures, render/PDF payload expectations |
| package.json @xyflow/react | Search found dependency declaration but no source usage | Candidate dependency removal, not yet certified | Config/dynamic imports/CSS scan, clean install, build; update lockfile through npm |

DeleteChatDialog.tsx is already deleted in git status. Do not restore it or count deleting it again as new cleanup. Existing scratch datasets/images are user-owned and excluded.

## Keep small files when they protect a boundary

- use-case-analysis-submission.ts (31 lines): contains persisted idempotency/admission state, not just an interface. Keep independent from the large action hook; do not regress reload/account/Case switching behavior.
- chat-workspace-types.ts: contains both pending submission and layout contracts. Current layout is already ~244 lines; inlining all props would exceed the limit. First remove duplicate props or split genuine layout responsibilities, not a new file per interface.
- case_run_contracts.py and chat_run_contracts.py: shared immutable worker DTOs. Keep them out of execution modules to prevent dependency cycles. Move RUN_LEASE_DURATION to a neutral workflow lease contract only if combined contracts under 300 lines and consumer direction improve; preserve all timing behavior.
- case_chat_errors.py / case_materials/errors.py: shared by services/helpers/router boundaries; do not inline into a module imported back by helpers. Identical-looking exceptions use different HTTP defaults; no unreviewed unification.
- cases/case_factory.py: used by chat_management and tests, not dead. Keep or colocate only after proving no circular dependency and combined size.
- api.ts, package __init__.py and Next App Router page/layout files: stable exports or framework discovery, not wasted files. Three-line page returning null can still be a required route leaf.
- heartbeat modules: similar scheduling but different lock/ownership semantics. Do not combine Case/Chat transaction code just because the loops resemble one another.
- report snapshot, generation, validation, persistence and PDF modules: preserve distinct data and side-effect boundaries; no new LLM behavior during structural cleanup.

## Oversized files need splitting, not additional merges

Measured physical lines, not claimed code-only LOC:

| File | Lines observed | Proposed boundary |
|---|---:|---|
| frontend/src/components/auth/AccountForm.tsx | 346 | Form/state flow vs presentational fields; preserve auth semantics |
| frontend/src/components/home/HomeSections.tsx | 570 | Authenticated home interaction vs static landing sections |
| backend/app/services/case_analysis/case_analysis_prompt_config.py | 340 | Stable config exports and named prompt assets; preserve exact runtime prompt bytes |
| backend/app/services/reports/report_pdf_story.py | 321 | Cohesive story-section builders; preserve rendered output |

Home/auth overlap prior work and known lint findings. Separate their cleanup patch from Case-first retirement. No micro-components for each label or field. Refresh counts before implementation.

## Implementation checkpoints and exit gates

### Concrete merge manifest: backend reports

Root for all filenames in this table: backend/app/services/reports/. Inventory observed 26 top-level Python files, including __init__.py. Their number comes from coexistence of native/legacy paths plus snapshot, generation, projection, persistence and rendering layers; it is not evidence that all 26 are necessary or disposable.

| ID | Sources -> retained target | Observed LOC sum | Recommendation and rationale | Consumers / verification |
|---|---|---:|---|
| BR1 | case_report_generation.py + case_report_template.py -> case_report_generation.py | 45 + 118 = 163 | Recommended first batch: one deterministic native report assembly module, retaining separate build and run functions | case_report_persistence.py; native report tests, successful and invalid trace results, prompt version and failure metadata unchanged |
| BR2 | report_generation.py + report_template.py -> report_generation.py | 43 + 186 = 229 | Conditional: same consolidation for legacy deterministic assembly, only if legacy generation will remain for a meaningful interval; skip this merge if retiring its writer immediately | report_persistence.py, package exports and test_chat_report.py patch targets; keep exported build_template_report and source_snapshot_hash |
| BR3 | case_report_contracts.py + report_contracts.py -> report_contracts.py | 63 + 104 = 167 | Recommended: common report boundary; retain distinct CaseReportInputSnapshot and ReportInputSnapshot types, do not turn them into one permissive schema | Both persistence/snapshot modules, validation, PDF and generation imports; identical model dumps, strict validation and historical payload tests |
| BR4 | report_finding_projection.py + report_review_projection.py -> report_finding_projection.py | 125 + 70 = 195 | Recommended if legacy view-model presentation is retained: findings, unresolved issues and corresponding review actions form one cohesive projection stage | report_view_model_builder.py imports three functions from target; keep project_review_actions name/signature; TH/EN output golden comparison |
| BR5 | case_report_pdf.py + report_pdf.py -> report_pdf.py | 177 + 67 = 244 | Optional later batch: colocate two typed PDF entrypoints, keep their distinct story builders and signatures; do not coerce native snapshot to legacy | Case and Chat persistence plus package exports; Thai/English, multipage, source appendices, pagination and old-report re-export checks |
| BR6 | pdf_chrome.py + pdf_design.py -> pdf_design.py | 93 + 120 = 213 | Defer: fits LOC but imports view-model contracts into design and mixes typography with document metadata; BR1/BR3/BR4 are better first reductions | If selected later, verify import acyclicity, report_pdf_story.py, PDF entrypoints and visual equality; not automatic |

Delete the superseded source module only after updating all imports, package exports, test patch paths, scripts and documentation. Keep package-level public names stable; do not keep one compatibility shim per deleted file indefinitely. If a module import path is a proven external contract, retain it explicitly or defer that merge; do not claim the file reduction in that case.

BR1 + BR3 + BR4 remove three files (26 -> 23) if no shims are needed. With BR2 and BR5, five files can be removed (26 -> 21). These are gross reductions before any required split of the existing 321-line PDF story; final net count must be measured. BR6 is not part of the recommended total. Do not rebuild soon-to-be-deleted legacy internals just to hit a file-count target.

### Backend pairs that must NOT be merged wholesale

| Sources | LOC sum | Decision |
|---|---:|---|
| case_report_persistence.py + report_persistence.py | 201 + 262 = 463 | Keep separate; different Case/Chat transaction and snapshot ownership. Shared serializer currently lives in report_persistence.py: preserve until legacy retirement, then relocate only serializer to schema/presentation boundary after measuring size |
| case_report_snapshot.py + report_snapshot.py | 158 + 136 = 294 | Keep separate despite fitting narrowly: native evidence revisions vs legacy messages; too little growth room and different trust contracts |
| case_report_template.py + report_template.py | 118 + 186 = 304 | Do not merge; BR1/BR2 keep one assembler per source contract |
| report_analysis_projection.py + report_finding_projection.py | 240 + 125 = 365 | Do not merge; avoid a monolithic projection module |
| report_view_model_builder.py + report_view_model_contracts.py | 200 + 86 = 286 | Keep contracts independent; builder already imports projections that also import contracts, so moving DTOs into builder risks cycles |
| report_view_model_items.py + report_view_model_text.py | 154 + 244 = 398 | Keep separate; parsers and language/text resources already have substantial content |
| report_pdf.py + report_pdf_story.py | 67 + 321 = 388 | Do not merge; split story at a cohesive section-builder boundary first |
| report_mitre_projection.py + general evidence projection | Varies | Preserve external-context boundary; no reason to mix it with incident evidence merely to reduce files |

Keep report_validation.py (75 lines) independent: generation and export both use validation. Keep report_html.py (62 lines) until export/preview and tests have been traced; test_report_view_model_and_pdf.py and package exports reference it, so it is not proven dead. Keep templates/ and their relative loading path intact if moving any renderer. Do not delete HTML templates because the PDF renderer uses ReportLab.

### Concrete merge manifest: other backend areas

| Sources -> target | Recommendation | Preconditions |
|---|---|---|
| workflow/case_run_contracts.py + workflow/chat_run_contracts.py -> workflow/run_contracts.py | Candidate, 24 + 32 = 56 lines: retain distinct immutable DTOs and one lease constant in a neutral contract module | Verify RawEvidenceSource/ClarificationExchange imports introduce no cycles; update every lease/claim/recovery consumer and run PostgreSQL lease tests; no change to six-minute lease |
| workflow/case_run_heartbeat.py + workflow/run_heartbeat.py | Do not merge DB lease functions | Locks and ownership checks differ. A callback scheduler abstraction is not justified just to save a small loop |
| chat/case_chat_errors.py + case_materials/errors.py | Keep | Similar syntax but distinct domains and default status codes; generic exception redesign is unrelated cleanup |
| cases/case_factory.py + cases/case_management.py | Defer | Shared factory used by chat_management and tests; require exact dependency/size proof before moving it into a service implementation |

No merger of native/legacy analysis source adapters or provenance validators is authorized by superficial similarity. Preserve source IDs, exact spans, snapshot versions, retry fingerprints and transaction order.

### Concrete merge manifest: frontend

Root for generated targets: frontend/src/lib/generated/. Names below are proposed module filenames, not changes to OpenAPI schema names. Generator must discover the complete current closure and assign every emitted schema explicitly, failing on missing assignment. Refresh emitted LOC: the observed generated text exceeds 300 lines in aggregate, so one generated.ts is not an option.

| Sources / schema family -> target | Action |
|---|---|
| CaseRead -> cases.ts | Case aggregate wire contract; one small domain module remains acceptable |
| CaseDocumentRead, DocumentExtractionRead, AdmitExtractionRequest, CaseEvidenceCreate, EvidenceSourceRead, EvidenceRevisionRead, CaseEvidenceSnapshotRead -> materials.ts | Consolidate native material/evidence schemas |
| CaseAnalysisCreate, CaseAnalysisAccepted, CaseAnalysisResultRead, CaseRunRead, CaseClarificationAccepted, CaseClarificationAnswer, CaseClarificationRead -> case-runs.ts | Consolidate Case operations; split analysis/clarifications only if actual generated output requires it |
| ChatThreadRead, ChatThreadDetail, ChatMessageCreate, ChatMessageRead, ChatRunRead, ChatMessageAccepted, CaseChatMessageAccepted, ChatRetryRequest -> chat.ts | Consolidate transport contracts; maintain CaseRun vs ChatRun distinction |
| MessageMetadata, FollowUpMetadata, RagAttemptMetadata, ChatActionMetadata and their emitted dependencies -> chat-metadata.ts | Group referenced metadata schemas, not a catch-all shared types module |
| CaseNarrativeDocumentSource, CaseNarrativeDocumentPageSpan, DocumentSourceMetadata -> document-provenance.ts | Preserve legacy document attribution wire shape until retirement |
| CaseReportCreate, ChatReportRead, ReportClaim, ReportSection, StructuredReport -> reports.ts | Replace handwritten wire duplicates through explicit facade mapping |
| common/DeleteDialog.tsx + common/SignOutDialog.tsx -> common/ConfirmationDialog.tsx | Rename implementation and remove four-line facade; retain ConfirmDialog, DeleteCaseDialog and SignOutDialog in one module |
| lib/api-types.ts handwritten report DTOs -> generated/reports.ts wire types plus existing facade | Do not physically paste declarations; alias generated types and keep necessary UI projection explicit |

Avoid permanent generated per-schema re-export files. Consumers import via existing api.ts/api-types.ts or domain generated modules as appropriate. Keep use-case-analysis-submission.ts independent because it owns persisted retry state. Do not inline all chat-workspace-types.ts into ChatWorkspaceLayout.tsx: combined layout and props exceed the budget. Remove redundant activeView/activeWorkspaceView only after verifying all callers supply equivalent values; do not assume it from the main caller alone.

### Explicit legacy migration track before deletion

This is a planned functional track, not behavior-preserving file consolidation. Execute only after scope approval; retaining MITRE is mandatory.

1. Native augmentation: Case evidence -> admitted findings -> applicability decision -> optional existing RAG client -> validated external associations -> persist canonical result/context -> report and technical view. Keep summary available and expose augmentation failure separately; never fabricate associations. Do not require Chat to be open.
2. Native caller cutover: route Case-linked Q&A/follow-up through CaseRun, preserve message history and atomic publication; make /chat compatibility navigation stop mounting the legacy workspace after redirect. Test legacy bookmarks explicitly, including the old chat leaf.
3. Historical policy: census unlinked threads, active/failed ChatRuns and report snapshot types. Retain readers/re-export of old reports even if writers are retired. An empty DB is not authorization to drop APIs or migrations.
4. Remove proven obsolete frontend branches: legacy portions of CaseIntakeView/CaseMaterialsView, ChatReportView and old workspace submission logic only when no supported route requires them; keep shared rendering and Q&A modules.
5. Remove proven obsolete backend execution: process_chat_run alternate dispatch, old recovery startup and ChatRun worker graph only after no supported writer/retry/recovery path needs them. Keep shared followup, MITRE, report readers, model registrations and migration history as required.

For each removal, attach an evidence row: file/symbol -> last production caller -> replacement -> data/history policy -> tests -> approved disposition. No directory-wide deletion based on prefix.

### A. Freeze baseline and prove scope (complexity M, risk high if skipped)

1. Confirm agents stopped writing; capture branch/ref, git status, diff name-status and hashes of dirty/untracked files, excluding no application files silently.
2. Record Luna receipts as reported and independently rerun targeted Case-first regressions with real isolated PostgreSQL schemas. Never use public tables as test fixtures.
3. Capture API schema, registered routes, imports/re-exports, DB migration heads, production file LOC and package usage inventory. Classify generated/framework/runtime/test-only/history readers explicitly.
4. Record current full lint failures; do not silently fix unrelated failures during low-risk deletion.

Exit: owned file list, exact baseline results and independent regression evidence. Any failing Case-first invariant blocks cleanup that touches it. No test-count claims copied from Luna as new results.

### B. Small no-behavior cleanup (S, low)

Remove verified unused aliases; consolidate confirmation dialog facade; remove verified unused dependency separately. Do not rename every Chat symbol to Case. Existing active/legacy branches remain unchanged.

Exit: no dangling imports, user menu/sign-out/delete and route tests pass, tsc/API generation check pass, diff scoped and touched code <=300 lines. No package removal without clean-install/build proof.

### C. Contract ownership and generator consolidation (M, medium)

First resolve handwritten/generated wire type overlap with tests for optional/required differences. Then implement explicit domain-group generation and stale-output manifest checking. Maintain consumer facade; do not introduce broad any or assertions to make tsc pass. Keep semantic domain chunks below 300 lines with growth headroom.

Exit: deterministic regeneration twice, --check fails for missing/changed/extra generated output, OpenAPI shape unchanged, all imports migrated, frontend tests and build pass. Report expected vs actual number of files, not an advance promise of a specific reduction.

### D. Oversized/cohesive module cleanup (M, medium)

Execute report consolidation in this order: BR3 contracts -> BR1 native assembly -> BR4 finding/review projection if retained -> optional BR2 legacy assembly -> optional BR5 PDF entrypoints. Run tests after each change, not only at the end. BR6 remains deferred. Separately decide the worker contract candidate. Import moves are not schema migrations.

Split the four measured oversized files in independent patches. Keep provider/public entrypoints stable; compare prompt strings byte-for-byte before and after. For PDF compare structured story content and render representative Thai/English/multipage reports; a passing Python import is not visual QA. Do not merge run leases, result completion and DB transaction orchestration into a generic worker.

Exit: touched files <=300 lines; no prompt/HTTP/report semantics changed; module-specific tests plus frontend build/PDF visual checks. Known lint errors either intentionally fixed with tests in this patch or explicitly remain outside its scope.

### E. Legacy retirement decision (L, high; not automatic authorization to drop APIs/data)

1. Read-only PostgreSQL census of Case-linked/unlinked ChatThreads, queued/running/failed ChatRuns, legacy report bindings and historical snapshot versions. Zero current rows alone is not proof no supported client uses the route.
2. Prove native technical augmentation parity for applicable, not-applicable, uncertain, empty retrieval and transport failure, with Chat closed and report export. Keep MITRE requirement intact. Missing parity becomes separately authorized functional work, not a cleanup shortcut.
3. Decide /chat deep-link compatibility: keep supported paths or redirect preserving semantics. Verify Back/Forward, source links and optional Chat behavior.
4. Propose precise old-writer retirement list and separate historical-reader retention list. Verify module imports, dynamic entrypoints, route decorators, ORM relationships, jobs, templates, scripts and tests.
5. Preserve migrations and historical provenance. No fabricated backfill, cascade change, schema drop or destructive migration without explicit approval and disposable populated migration rehearsal.

Exit: product/API compatibility decision, read-only census evidence, native parity tests and exact proposed deletion set reviewed. Until then legacy worker/readers are KEEP, not unused.

### F. Final verification and handoff (M, risk proportional to deleted surface)

- Backend full suite on isolated PostgreSQL; explicitly cover authenticated write transactions, superseded/active retries, fingerprints, lease loss, exact citations per role, page/hash provenance, durable bounded clarification, atomic result+assistant publication, ASK non-evidence behavior and report persistence.
- Frontend: npm test, npx tsc --noEmit, npm run check:api-types, scoped and full lint with accurate baseline accounting, npm run build.
- Backend: scoped Ruff, compile/import checks; migration head/schema expectations and populated old-report reader tests. Same schema before/after unless a separate migration is approved.
- Browser: authenticated Case upload/admit/analyze/clarify with Chat closed; open Chat and see exactly one analysis message; reload lost-response retry; account/Case switch; optional Chat deletion preserves Case; source inspection, technical context and report download.
- Confirm no unrelated dirty hashes lost, no rag_service changes, no generated orphan files, no touched code >300 lines. Report deleted/moved/retained files and reason.
- No Docker rebuild or deployment in this planning task. Future cutover is separate; preserve PostgreSQL volumes and disclose any untested live/provider path.

## Recommended first implementation batch

A -> B -> C -> D (BR3/BR1 first, BR4 if retained). This addresses frontend and backend proliferation without retiring working paths. Execute functional native parity/caller cutover under E as a separately approved batch, then remove proven legacy writers. Avoid BR2 if that writer is about to retire. Effort sizes are relative, not calendar estimates; final scope depends on baseline and contract differences.

## Verification receipt for this drafting turn

Performed source reads, symbol/caller searches and physical-line inventory. API drift check completed with exit 0 during initial drafting; not rerun in revision 2. Revision 2 inspected native/legacy report generation, contracts, template dependencies, projection callers, PDF entrypoints and persistence imports. No full suite, PostgreSQL tests, PDF visual checks or browser tests rerun in this drafting turn. No application files changed by this audit. Verdict: staged cleanup; no blanket legacy deletion, principally because live compatibility paths and conditional MITRE parity still need proof.
