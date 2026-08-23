# Continuity Ledger

## Snapshot

- 2026-08-23 [USER] Goal: aggressively simplify the demo to raw user-authored messages as authoritative evidence; delete canonical Case State, versions, deltas, extraction, entity/relationship UI, and compatibility schema.
- 2026-08-23 [USER] Preserve initial analysis, clarification, add-information vs ask semantics, external RAG, Main Case Analysis, follow-up, reports, and source traceability.
- 2026-08-23 [USER] Existing demo data and old-schema compatibility may be discarded.
- 2026-08-23 [CODE] Raw evidence includes initial, clarification-answer, and explicit add-information messages; ordinary asks and all assistant/RAG text are excluded.
- 2026-08-23 [CODE] Fresh-evidence runs invoke RAG; ordinary asks reuse the latest completed run-bound RagContext without invoking RAG.
- 2026-08-23 [CODE] `analysis_trace_v2` binds source message IDs, evidence SHA-256, retrieval context, and candidate-only MITRE associations.
- 2026-08-23 [CODE] Report generation is deterministic from raw evidence, latest grounded analysis, matching RagContext, MITRE rows, and unresolved gaps.
- 2026-08-23 [CODE] Persistence is reduced to chat_threads, chat_messages, chat_runs, rag_contexts, and chat_reports.
- 2026-08-23 [CODE] Frontend product routes are Chat and Report only.
- 2026-08-23 [TOOL] Backend tests and compile, frontend tests/lint/build, obsolete-symbol scan, and production file-size scan are green.
- 2026-08-23 [CODE] Follow-up backend package restored after all tracked files appeared as unstaged deletions; raw-evidence inputs and frontend clarification presentation are intact.
- 2026-08-23 [USER] `rag_service/**` remains outside this architecture change.

- 2026-08-24 [CODE] Implemented New Case Intake experience (`CaseIntakeView`) with optional title, required description, disabled attachment control, and direct navigation to Case Overview upon analysis.
- 2026-08-24 [CODE] Redesigned Report Workspace (`ChatReportView`, `PersistedReportCard`, `ReportHistory`) around the PDF viewer as the primary hero content with compact version controls and removal of internal UUIDs/metadata.
- 2026-08-24 [CODE] Removed standalone "Investigation Issues" workspace feature (deleted route `/chat/[threadId]/issues`, component hierarchy, view model, tests, and sidebar entry). Unresolved information and points for further investigation remain contained within Case Overview.
- 2026-08-24 [CODE] Redesigned Technical Context (`TechnicalContextView`, `technical-context.ts`) from AI SaaS dashboard cards to quiet, flattened investigative reference notes:
  - Replaced card-per-technique wrappers with simple typography separated by thin horizontal rules.
  - Removed "techniques referenced" dashboard metric badge and "Open Chat" header action.
  - Replaced purple trust-boundary banner with a quiet 2-line external reference notice under header.
  - Switched from repetitive bilingual English+Thai labels to single-language Thai section headings (`ความหมายโดยย่อ`, `เหตุผลที่เกี่ยวข้องกับคดี`, `แหล่งข้อมูล`, `คำอธิบายทางเทคนิค ▾`).
  - Ensured case-specific relevance reasoning without verbose filler text, with conservative short fallback.
  - Extracted concise plain-language summary for primary reading flow and tucked full MITRE definitions into an expandable `คำอธิบายทางเทคนิค ▾` drawer.
  - Replaced bright blue buttons with quiet document-annotated source references (`Source — Initial case description ↗`) preserving anchored popovers.
  - Reduced violet usage by ~70%, reserving it strictly for tiny MITRE ID accents.
- 2026-08-24 [TOOL] Frontend tests (18 files / 49 tests), ESLint (0 errors, 0 warnings), Next.js production build (5/5 static pages), and Backend pytest suite (65 passed) all green.

## Done (recent)

- 2026-08-24 [CODE] Deleted `frontend/src/app/chat/[threadId]/issues`, `frontend/src/components/issues`, `frontend/src/lib/investigation-issues.ts`, and associated tests.
- 2026-08-24 [CODE] Refactored `frontend/src/lib/technical-context.ts` and `frontend/src/components/technical/TechnicalContextView.tsx`.
- 2026-08-24 [CODE] Updated `WorkspaceSidebar.tsx`, `ChatWorkspaceLayout.tsx`, `ChatWorkspace.tsx`, `CaseOverviewView.tsx`, `EstablishedVsUnclearSection.tsx`, `InvestigationPointsSection.tsx`, and `types.ts`.
- 2026-08-24 [CODE] Updated vitest suites `TechnicalContextView.test.tsx`, `technical-context.test.ts`, and `WorkspaceSidebar.test.tsx`.

## Decisions

- D001 ACTIVE 2026-08-23 [USER] Do not modify `rag_service/**` for this cutover.
- D002 ACTIVE 2026-08-23 [USER] Raw included user messages are the only authoritative incident evidence.
- D003 ACTIVE 2026-08-23 [CODE] RAG/MITRE/model output is analytical context, never reported evidence.
- D004 ACTIVE 2026-08-23 [CODE] Ask reuses the latest durable run-bound RagContext; initial, clarification, and add-info runs perform fresh RAG.
- D005 ACTIVE 2026-08-23 [USER] Do not retain compatibility shims for the deleted Case State architecture.
- D006 ACTIVE 2026-08-23 [CODE] Reports remain deterministic, template-first, provisional, and source-message traceable.
- D007 ACTIVE 2026-08-23 [CODE] Overview workspace is client-side projection over persisted analysis messages, enforcing trust boundaries (Blue/Violet/Amber/Red/Green) and source traceability without backend mutation.
- D008 ACTIVE 2026-08-24 [CODE] Standalone PDF/HTML reports use clean 1..7 standalone numbering + technical appendix, document-oriented evidence cards, and stacked MITRE cards.
- D009 ACTIVE 2026-08-24 [CODE] Case Materials and Technical Context are pure client-side read projections over existing persisted messages and trace metadata; no new tables or backend models.
- D010 ACTIVE 2026-08-24 [USER] Standalone Investigation Issues page is deleted; gaps and unconfirmed points remain integrated inside Overview.

## State (Done/Now/Next)

- 2026-08-24 [TOOL] Done: Visual and copy refinement pass complete. Investigation Issues deleted; Technical Context redesigned to flattened, quiet investigative notes.
- 2026-08-24 [TOOL] Next: Hand off full architectural and UX report to user.

## Receipts

- 2026-08-24 [TOOL] `.\env_mitre\Scripts\pytest.exe backend/tests`: 65 passed (100%).
- 2026-08-24 [TOOL] `npm run test -- --run`: 18 test files and 49 tests passed (100%).
- 2026-08-24 [TOOL] `npm run lint`: passed (0 errors, 0 warnings).
- 2026-08-24 [TOOL] `npm run build`: passed, static generation (5/5) and TypeScript compilation succeeded.



