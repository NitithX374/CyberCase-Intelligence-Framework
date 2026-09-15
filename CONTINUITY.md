# Continuity Ledger

## Snapshot

- 2026-09-14 [USER] Approved the CyberCase compatibility-ghost cutover: preserve Case-owned evidence, analysis, follow-up, Chat, report, and optional MITRE behavior; remove snapshot/SHA/ChatThread/standalone Gap Analysis/fake lease compatibility.
- 2026-09-14 [CODE] Superseded on 2026-09-15: checkout was `main` at baseline `50edf7e`; implementation was intentionally uncommitted and no push, deploy, or live database migration was authorized.
- 2026-09-15 [TOOL] Current checkout is `main` at `b3ce734`, matching `origin/main`; implementation commit `8fcff59` and the publication ledger are pushed, with no deploy or live database migration performed.
- 2026-09-14 [CODE] Canonical evidence state is `Case.evidence_revision`; `CaseRun` captures that revision and no result may become current unless the revision is unchanged before assembly and before persistence.
- 2026-09-14 [CODE] Authoritative evidence remains raw user-admitted `EvidenceSource` content with existing exact-quote/document/page provenance; assistant, chat, and MITRE context remain non-authoritative.
- 2026-09-14 [CODE] Chat is Case-owned `ChatMessage`; there is no persisted `ChatThread` aggregate or `/api/v1/chats` route surface.
- 2026-09-14 [CODE] Follow-up selects only canonical Main Analysis gaps deterministically, phrases one question, persists the answer as `EvidenceSource`, increments revision, and re-runs analysis; no Case-wide fallback Gap Analysis remains.
- 2026-09-14 [TOOL] Final verification is green: backend 169 passed/4 skipped/2 subtests; frontend 33 files/112 tests; TypeScript, API drift, build, import, compile, route smoke, and diff checks passed.
- 2026-09-15 [TOOL] Final Case Chat cleanup verification is green: backend 164 passed/4 skipped/2 subtests; frontend 33 files/112 tests; generated API types, TypeScript, production build, and diff checks passed.
- 2026-09-15 [CODE] Report output is now framed as general Case analysis: neutral case-evidence wording, no report-only chat citations or unsupported support types, and no report query hash.
- 2026-09-14 [CODE] `rag_service/**` and `backend/app/services/document_ingestion/**` were not changed; document-ingestion `text_sha256` remains an intentional out-of-scope provenance field.

## Done (recent)

- 2026-09-14 [CODE/TOOL] Fixed startup import failure caused by deleted follow-up prompt files by resolving the active prompt contract in `followup/prompts.py`; removed standalone gap prompt/analyzer modules.
- 2026-09-14 [CODE/TOOL] Implemented revision-guarded CaseRun claim/completion; stale runs fail as `case_run_superseded` and do not create or promote a current `CaseAnalysisResult`.
- 2026-09-14 [CODE/TOOL] Removed ORM/schema/report/frontend snapshot, SHA, ChatThread, legacy chat-route, and fake lease/fingerprint compatibility; regenerated frontend API contracts.
- 2026-09-14 [CODE/TOOL] Preserved deterministic follow-up, clarification evidence admission, ordinary Ask freshness, optional MITRE augmentation, and report validation semantics.
- 2026-09-14 [CODE/TOOL] Split touched backend modules into focused files; every changed code file is at or below the 300-line workspace limit.
- 2026-09-15 [CODE] Removed duplicate follow-up `GapAnalysis`/`GapItem` contracts, test-only follow-up context, stale clarification aliases, and unused follow-up fields while keeping canonical `CaseAnalysisGap` and active contracts.
- 2026-09-15 [CODE] Removed additional unreferenced backend helpers/modules and the orphaned frontend clarification component/test; renamed and simplified the live Case Chat submission boundary without changing CaseRun, polling, idempotency, or clarification evidence flow; normalized persisted action metadata to top-level `conversation` or `follow_up`, slimmed MessageMetadata to action/trace/follow-up data, removed legacy chat metadata plus dead chat-level MITRE/evidence helpers, cleaned the Report contract and historical full-forensics sample, and rebuilt report presentation around readable sections 1–7.

## Decisions

- 2026-09-14 [USER] D001 ACTIVE: Do not modify `rag_service/**`, document ingestion, deployment, or live data for this cutover.
- 2026-09-14 [USER] D002 ACTIVE: Raw user-admitted case material is the only authoritative incident evidence.
- 2026-09-14 [CODE] D003 ACTIVE: RAG/MITRE/model output is isolated external analytical context, never case evidence.
- 2026-09-14 [USER] D004 ACTIVE: Do not retain compatibility shims for deleted snapshot, SHA, ChatThread, standalone Gap Analysis, lease, or fingerprint architecture.
- 2026-09-14 [CODE] D005 ACTIVE: Reports remain result-bound, evidence-validated, deterministic/template-first, and optional MITRE-aware.
- 2026-09-14 [CODE] D006 ACTIVE: Generated frontend API types are the wire-contract source; Case routes and Case-owned chat are canonical.
- 2026-09-15 [CODE] D007 ACTIVE: Persisted Case Chat metadata uses top-level `action` values `conversation` and `follow_up`; internal follow-up decisions remain workflow controls `ask_followup` and `proceed`.
- 2026-09-15 [CODE] D008 ACTIVE: ChatMessage metadata retains only `action`, response `analysis_trace`, and minimal `chat_followup`; evidence, freshness, RAG, provider, and source linkage live in canonical Case entities or result metadata.
- 2026-09-15 [USER] D009 ACTIVE: Do not preserve legacy `clarification_answer` or `explicit_chat_addition` aliases; canonical contracts use `followup_answer` and `narrative`.
- 2026-09-15 [USER] D010 ACTIVE: Reports must present general Case analysis, not a full digital-forensics dossier; retain raw evidence references, revision binding, claims/gaps, and optional MITRE context.
- 2026-09-15 [CODE] D011 ACTIVE: Report HTML preview and PDF export use the same deterministic report/display data; presentation headings are sections 1–7 and raw source text is not dumped into the report body.

## State (Done/Now/Next)

- 2026-09-14 [CODE/TOOL] Done: approved cutover implemented and verified in the dirty worktree.
- 2026-09-14 [CODE/TOOL] Done: exact production ghost inventory is empty except the explicitly out-of-scope document-ingestion `text_sha256` field.
- 2026-09-14 [CODE/TOOL] Done: final backend/frontend validation completed; ESLint has 0 errors and 2 existing warnings (`HomeSections.tsx` image optimization and `useCaseWorkspaceActions.ts` dependency list).
- 2026-09-15 [CODE/TOOL] Done: current in-repo production-path audit found no remaining orphan support files or unreferenced service definitions; dynamic chat loading is an intentional live entrypoint and historical documentation references remain outside production code.
- 2026-09-14 [TOOL] Incident: live Case `47b3be55-ee99-438d-b2ec-fa6f3531f765` report POST/PDF return 409 because persisted analysis trace still has removed `source_revision`/`evidence_sha256` fields; revisions are both 2, so this is not a revision mismatch.
- 2026-09-14 [CODE] Done: `/case` is now a NotebookLM-inspired Case Library with latest-case continuation, search, sort, grid/list views, empty/error states, and explicit New Case navigation.
- 2026-09-15 [CODE] Done: Case Library remains frontend-only; `useCaseChatSubmission` is the cleaned live Case Chat boundary; legacy evidence/chat aliases and report-only forensic framing are removed from the wire contract; report 409 diagnosis remains unchanged; readable Jinja2 HTML/PDF presentation is implemented and no live data mutation was performed.
- 2026-09-15 [USER] Next: review the Case Library and new report preview in the running app; implementation is published, with no deploy or live database migration performed.
- 2026-09-15 [TOOL] Published: implementation commit `8fcff59` and ledger commit `b3ce734` are on `main` and `origin/main`; user-owned instruction, translation, and output files remain intentionally outside version control.

## Working set

- 2026-09-14 [CODE] `backend/app/models/`, `backend/app/schemas/`, `backend/app/routers/cases.py`
- 2026-09-14 [CODE] `backend/app/services/workflow/caseRunClaim.py`, `caseRunCompletion.py`, `caseRunExecution.py`, and focused helper modules
- 2026-09-14 [CODE] `backend/app/services/followup/`, `case_materials/`, `case_analysis/`, `reports/`
- 2026-09-14 [CODE] `backend/alembic/baseline_versions/0001_canonical_case_system.py`
- 2026-09-14 [CODE] `frontend/src/lib/`, generated API types, Case routes, and Case-owned chat components/hooks
- 2026-09-14 [CODE] `frontend/src/app/case/page.tsx`, `frontend/src/components/case-library/`, and Case Library tests
- 2026-09-14 [CODE] `backend/tests/` canonical analysis/provenance/route tests and `frontend/src/test/` Case/chat contract tests
- 2026-09-14 [DOC] `docs/superpowers/specs/2026-09-14-compatibility-ghost-removal-design.md`
- 2026-09-14 [USER] User-owned untracked instruction files `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, `frontend/AGENTS.md`, and `frontend/CLAUDE.md` are preserved.

## Receipts

- 2026-09-14 [TOOL] Backend pytest: `169 passed, 4 skipped, 1 warning, 2 subtests passed in 5.20s`.
- 2026-09-14 [TOOL] Frontend Vitest: `33 files passed, 112 tests passed`.
- 2026-09-14 [TOOL] `npx tsc --noEmit`, `npm run check:api-types`, and `npm run build` passed; Next.js generated the current Case routes.
- 2026-09-14 [TOOL] `npm run lint` passed with 0 errors and the two warnings recorded above.
- 2026-09-14 [TOOL] Backend import, `compileall`, and OpenAPI smoke passed; OpenAPI exposes 30 paths, including Case chat and no `/api/v1/chats` path.
- 2026-09-14 [TOOL] `git diff --check` passed after removing three whitespace-only residues.
- 2026-09-14 [TOOL] Ghost search over `backend/app`, `backend/alembic`, and `frontend/src` found no forbidden production symbols; only document-ingestion `text_sha256` remains.
- 2026-09-14 [TOOL] The first post-modularization backend run exposed Pydantic forward-reference failures; importing `Literal` in the extracted evidence contract fixed the root cause and later full validation passed.
- 2026-09-15 [TOOL] Follow-up contracts audit confirms `backend/app/services/followup/contracts.py` is active production code, imported by decision, policy, stateful selection, context, helpers, clarification history, and the package facade; no deletion performed.
- 2026-09-15 [TOOL] Symbol audit found all contract validators/helper logic active directly or through Pydantic validation; only `FollowUpReasonCode` has no in-repo caller beyond declaration/export and is a cleanup candidate.
- 2026-09-15 [TOOL] Delete-impact audit: removing `followup/contracts.py` without relocating its active symbols causes import-time failure through `main.py` and breaks CaseRun follow-up, clarification history, Case Chat clarification handling, and direct follow-up tests; no database migration is implicated.
- 2026-09-15 [TOOL] Current-main follow-up audit: `GapAnalysis`/`GapItem` duplicate canonical `CaseAnalysisGap`; `context.py` is test-only, `clarification_answer_context` and `find_answered_clarification` have no current callers, camelCase clarification aliases are compatibility exports, and `FollowUpResolution.gap_analysis` has no read site.
- 2026-09-15 [TOOL] Case Chat cleanup removed deprecated action state/transport, server retry metadata, unused document-source input, always-null clarification-id plumbing, unreachable validation, and first-chat title mutation; current submission posts only Case Chat intents.
- 2026-09-15 [TOOL] Removed-file checks confirm follow-up context/gap-analysis/experimental prompt modules, LLM token-budget module, and orphaned frontend clarification files are absent; no deleted-symbol matches remain in backend/app, backend/tests, or frontend/src.
- 2026-09-15 [TOOL] Backend pytest excluding the known out-of-scope ingestion-evaluation test: `161 passed, 4 skipped, 1 warning, 2 subtests passed`; full collection remains blocked by that test importing the intentionally deleted ingestion evaluation module.
- 2026-09-15 [TOOL] Full backend Ruff reports only the two pre-existing out-of-scope unused imports in `document_ingestion/contracts.py`; no commit, push, deployment, or live data mutation performed.
- 2026-09-15 [TOOL] Final `git diff --check` passed after removing two new EOF blank-line residues in the model-registry files.
- 2026-09-15 [TOOL] Message metadata cleanup verification: backend `161 passed, 4 skipped, 2 subtests`; frontend `30 files/99 tests`; TypeScript, API generation, production build, compileall, action-writer audit, and diff checks passed.
- 2026-09-15 [TOOL] Legacy alias cutover verification: backend `161 passed, 4 skipped, 2 subtests`; frontend `30 files/99 tests`; TypeScript, API drift, build, lint, compileall, and diff checks passed; no alias enum values remain in app/test/e2e code.
- 2026-09-15 [TOOL] Report cleanup verification: backend `162 passed, 4 skipped`; frontend `30 files/99 tests`; generated API types, TypeScript, API drift, production build, compileall, strict-contract smoke, and diff checks passed; lint retained only the two pre-existing warnings.
- 2026-09-15 [CODE] Retired `research/render_sample_report.py` after confirming it was a broken historical sample with no production caller and full-forensics-only output; historical handover references remain intentionally untouched.
- 2026-09-15 [TOOL] Readable report presentation verification: backend `165 passed, 4 skipped, 2 subtests`; frontend `30 files/99 tests`; focused presentation tests `3 passed`; scoped Ruff, TypeScript, production build, compileall, route checks, and diff checks passed; lint retains only the two pre-existing warnings.
- 2026-09-15 [TOOL] `git ls-remote origin refs/heads/main` verified SHA `b3ce734` after the ledger push.
