# Frontend Simplification Audit

Date: 2026-09-18

Repository: `F:\Cybercase Framework`

Branch: `audiit`
Phase: 1, audit only

This audit follows the current checkout, its route registrations, imports, tests, generated API contracts, and the backend schemas that produce the frontend payloads. The working tree already contains user-owned backend and frontend changes. No production frontend file was edited for this audit, and no existing dirty change was reverted.

The test and import results below are observations about the current checkout. A static no-caller result is treated as a deletion candidate until the route, export, test, generated-contract, and runtime paths are checked.

## Scope and inventory

The production frontend contains 65 TypeScript or TSX files and 9,115 lines. The frontend test tree contains 32 TypeScript or TSX files and 3,464 lines. Counts are raw file line counts and include generated frontend contracts. `node_modules` and generated dependencies were excluded from the audit.

`frontend/package.json` has no `typecheck` script. The repository equivalent is `npx tsc --noEmit --incremental false`. The relevant scripts are:

- `npm run check:api-types`
- `npm run lint`
- `npm test` (`vitest run`)
- `npm run build`
- `npm run e2e`

React Compiler is enabled in `frontend/next.config.ts`, so shallow `useMemo` and `useCallback` calls should not be retained as a default performance habit.

## A. Frontend overview

### Route map

| Route | Entry point | Main state/data owner | Rendered responsibility |
|---|---|---|---|
| `/` | `src/app/page.tsx` | `HomeSections` | Public landing page and its six sections |
| `/login` | `src/app/login/page.tsx` | `AccountForm` | Login form |
| `/register` | `src/app/register/page.tsx` | `AccountForm` | Registration form |
| `/case` | `src/app/case/page.tsx` | `CaseLibraryPage` | Case list, search, sort, create, and latest-case summary |
| `/case/[caseId]` | `src/app/case/[caseId]/page.tsx` | `casePath` and router redirect | Redirects to the case overview |
| `/case/[caseId]/overview` | `src/app/case/[caseId]/overview/page.tsx` | `CaseOverviewView` | Analysis summary, findings, open questions, evidence references |
| `/case/[caseId]/intake` | `src/app/case/[caseId]/intake/page.tsx` | `useCaseIntakeActions`, `CaseIntakeView` | Title/description, upload, evidence, submit, and analysis start |
| `/case/[caseId]/materials` | `src/app/case/[caseId]/materials/page.tsx` | `useCaseQueries`, `CaseMaterialsView` | Document list, source selection, original file, OCR preview |
| `/case/[caseId]/technical-context` | `src/app/case/[caseId]/technical-context/page.tsx` | `technicalContext`, `TechnicalContextView` | MITRE mappings, retrieved-only context, source drawer |
| `/case/[caseId]/report` | `src/app/case/[caseId]/report/page.tsx` | `CaseReportView`, `PersistedReportCard` | Generate/list/download reports and view saved HTML |
| `/case/layout` | `src/app/case/layout.tsx` | None | Empty fragment around children; no visible behavior |
| `/case/[caseId]/layout` | `src/app/case/[caseId]/layout.tsx` | Case shell | Sidebar, header, chat panel, route navigation, deletion, run status, workspace errors |

There is no standalone `/chat` route. Chat is a panel owned by the case shell.

### Shared boundaries

| Boundary | Files | Concrete responsibility |
|---|---|---|
| Application and auth | `src/app/layout.tsx`, `src/app/providers.tsx`, `src/components/auth/AccountGate.tsx`, `src/hooks/use-auth.ts` | Global fonts/metadata, React Query provider, session gate, redirect, cross-tab auth state |
| Landing/auth UI | `src/components/home/HomeSections.tsx`, `src/components/auth/AccountForm.tsx`, `src/components/common/UserProfileMenu.tsx` | Public marketing sections and account forms/menu |
| Case navigation shell | `src/app/case/[caseId]/layout.tsx`, `src/components/layout/WorkspaceSidebar.tsx`, `src/components/layout/WorkspaceHeader.tsx` | Selected case, workspace view, chat visibility, case navigation, create/delete actions |
| Server data access | `src/hooks/useCaseQueries.ts`, `src/hooks/useCaseDeletion.ts`, `src/lib/apiClient.ts`, `src/lib/api.ts` | React Query keys/hooks and direct HTTP endpoint wrappers |
| Case intake | `src/hooks/useCaseIntakeActions.ts`, `src/components/intake/CaseIntakeView.tsx` | Persisted intake fields, document/evidence status, upload and analysis start |
| Chat and follow-up | `src/features/chat/useCaseChat.ts`, `src/features/chat/useCaseChatSubmission.ts`, `src/features/chat/useChatDraft.ts`, `src/features/chat/chatSubmissionMessages.ts`, `src/lib/chat-followup.ts` | Chat query, draft/pending persistence, optimistic messages, follow-up selection, retries, reconciliation |
| Chat rendering | `src/components/conversation/WorkspaceChatPanel.tsx`, `src/components/conversation/ChatTranscript.tsx`, `src/components/conversation/ChatMessageMarkdown.tsx` | Transcript, analysis lead card, markdown, follow-up controls, composer |
| Evidence/source UI | `src/components/evidence/EvidenceCitationChip.tsx`, `src/components/evidence/SourceEvidenceDrawer.tsx` | Citation chips, source selection, quote/page display, source drawer focus |
| Analysis overview | `src/lib/caseOverview.ts`, `src/lib/caseOverviewSource.ts`, `src/lib/caseOverviewTypes.ts`, `src/components/overview/*` | Trace/evidence parsing and findings/question/source rendering |
| Technical context | `src/lib/technicalContext.ts`, `src/components/technical/TechnicalContextView.tsx` | External MITRE/RAG context mapping and disclosure |
| Reports | `src/components/report/CaseReportView.tsx`, `src/components/report/PersistedReportCard.tsx` | Saved report list, generation, PDF download, HTML object URL lifecycle |
| Small shared UI | `src/components/common/CyberCaseLogo.tsx`, `DeleteDialog.tsx`, `MeaningfulErrorModal.tsx`, `StatusPill.tsx`, `WorkspaceSectionHeader.tsx`, `types.ts`, `icons.tsx` | Shared controls, dialogs, status vocabulary, icon paths |
| Storage and routes | `src/lib/account-storage.ts`, `src/lib/workspaceRoutes.ts` | Account-scoped local storage and canonical case route parsing/building |
| Generated contracts | `src/lib/generated/*.ts`, `src/lib/apiTypes.ts` | OpenAPI output plus a small number of current auth/UI aliases |

### Main data flows

```text
AccountGate/useAuth
  -> React Query session
  -> protected route or login redirect

case route
  -> case/[caseId]/layout
  -> useCases/useCase/useCaseAnalysis/useCaseEvidence/useCaseRunPolling
  -> WorkspaceHeader/Sidebar/ChatPanel
  -> route page

intake page
  -> useCaseIntakeActions
  -> apiClient case/document/evidence/analysis calls
  -> query invalidation/refetch
  -> case run polling

overview page
  -> API analysis/evidence payloads
  -> buildCaseOverview
  -> caseOverviewSource/caseOverview trace and citation parsing
  -> findings, questions, source chips, source drawer

chat panel
  -> useCaseChat
  -> useChatDraft and useCaseChatSubmission
  -> API chat/follow-up call
  -> optimistic cache merge
  -> run cache seed/polling and chat reconciliation

report page
  -> report list/generate/download API calls
  -> CaseReportView/PersistedReportCard
  -> PDF blob or HTML object URL
```

### State ownership findings

- React Query owns server data and cache invalidation. The same case, analysis, evidence, and run query keys are observed by the case shell and several route children.
- The case shell owns navigation, selected case, chat open state, delete dialogs, and the global workspace error surface.
- `useCaseChat` owns chat query orchestration but currently exposes both direct fields and a second `session` facade.
- `useChatDraft` owns account-scoped draft and pending-submission persistence. This is real lifecycle/state behavior, not a trivial hook wrapper.
- Chat transcript, source drawer, report viewer, and error modal own ephemeral UI state close to where it is rendered.
- Run polling is currently mounted by the shell and by overview, intake, and report pages. React Query deduplicates the request key, but the ownership and settlement effect are repeated.
- `HomeNavigation` independently checks session/local storage even though `AccountGate` and `useAuth` already own session state.

## Classification register

The following register covers all 65 production `frontend/src` TypeScript/TSX files. `BACKEND RESPONSIBILITY` means the frontend code is currently carrying a contract/domain concern that could move behind a typed backend projection or endpoint; it does not mean the file can be deleted immediately.

### App routes and layouts

| Path | Classification | Evidence and proposed action |
|---|---|---|
| `src/app/case/[caseId]/intake/page.tsx` | SIMPLIFY | Thin route is needed, but it observes the same run through `useCaseRunPolling` as the shell. Keep route-specific intake wiring and remove duplicate polling ownership later. |
| `src/app/case/[caseId]/layout.tsx` | SIMPLIFY | Necessary shell, but it owns many unrelated concerns and repeats shell/page queries. Remove shallow memoization, make error ownership explicit, and centralize one run observer. |
| `src/app/case/[caseId]/materials/page.tsx` | SIMPLIFY | Route is needed. `handleUploadDocument` catches and discards every upload error at L20-L27; expose mutation error or let the existing error surface handle it. |
| `src/app/case/[caseId]/overview/page.tsx` | SIMPLIFY | Route wrapper is required, but its child observes run state already observed by the shell. Keep page entry and remove duplicate observer after ownership is chosen. |
| `src/app/case/[caseId]/page.tsx` | KEEP | Redirect entry is the canonical `/case/[caseId]` behavior. |
| `src/app/case/[caseId]/report/page.tsx` | SIMPLIFY | Route is required, but it repeats run polling and status derivation. Keep report route and use the shell-owned status contract. |
| `src/app/case/[caseId]/technical-context/page.tsx` | KEEP | Thin route passes the analysis/evidence contract to the technical view. |
| `src/app/case/layout.tsx` | DELETE | The file only renders `children` in a fragment and adds no import, state, metadata, or layout behavior. Verify the Next build after removal. |
| `src/app/case/page.tsx` | KEEP | Canonical case library entry. |
| `src/app/layout.tsx` | KEEP | Global metadata, font loading, and application wrapper are required. |
| `src/app/login/page.tsx` | KEEP | Required route shell for login. |
| `src/app/page.tsx` | KEEP | Required landing route and the only production caller of the home section exports. |
| `src/app/providers.tsx` | KEEP | React Query provider and global `AccountGate` are required application boundaries. |
| `src/app/register/page.tsx` | KEEP | Required route shell for registration. |

### Components

| Path | Classification | Evidence and proposed action |
|---|---|---|
| `src/components/auth/AccountForm.tsx` | KEEP | Shared login/register form owns submission and redirect behavior. A shared auth API wrapper is optional cleanup only after a typed endpoint exists. |
| `src/components/auth/AccountGate.tsx` | SIMPLIFY | Auth gate is required, but `/casefleet-preview` has no route or other repository caller. Remove that unreachable branch and leave one public-route rule. |
| `src/components/case-library/CaseLibraryPage.tsx` | SIMPLIFY | Active feature. Remove shallow `useMemo`, repeated recent sorting, and the identical `rounded-md` ternary at L291. |
| `src/components/common/CyberCaseLogo.tsx` | KEEP | Shared logo is used in the workspace and public UI. |
| `src/components/common/DeleteDialog.tsx` | KEEP | Shared native dialog, delete confirmation, and sign-out confirmation are used by multiple routes. Native dialog fallback is covered by tests and should not be removed casually. |
| `src/components/common/icons.tsx` | SIMPLIFY | Icon registry is active, but `issues`, `alert`, `expand`, and `collapse` have no production caller. Remove only those paths and enum entries. |
| `src/components/common/MeaningfulErrorModal.tsx` | KEEP | Focus, keyboard, retry, and technical detail behavior is a real user-facing error boundary. |
| `src/components/common/StatusPill.tsx` | KEEP | Shared status presentation is used by intake and chat. |
| `src/components/common/types.ts` | KEEP | `RunPhase`, `WorkspaceView`, and display labels are shared by shell and pages. |
| `src/components/common/UserProfileMenu.tsx` | KEEP | Shared account menu owns sign-out UI and account display. |
| `src/components/common/WorkspaceSectionHeader.tsx` | KEEP | Reused workspace heading structure. |
| `src/components/conversation/ChatMessageMarkdown.tsx` | KEEP | Markdown element mapping is required for current transcript formatting. Reduce mappings only with a visual contract, not by deleting styles blindly. |
| `src/components/conversation/ChatTranscript.tsx` | SIMPLIFY | Active transcript. It reparses evidence references beside overview parsing and carries several rendering branches; remove duplicate preparation only after preserving source drawer behavior. |
| `src/components/conversation/WorkspaceChatPanel.tsx` | SIMPLIFY | Active chat panel. Remove unused `closeButtonRef` if focus behavior remains intact and derive empty-state checks from the smallest necessary message collection. |
| `src/components/evidence/EvidenceCitationChip.tsx` | KEEP | Citation chip is a concrete source navigation control. |
| `src/components/evidence/SourceEvidenceDrawer.tsx` | KEEP | Source quote/page display and focus return are user-visible evidence behavior. |
| `src/components/home/HomeSections.tsx` | SIMPLIFY | Landing content is active, but `HomeNavigation` duplicates `AccountGate`/`useAuth`, calls `getSession`, and falls back to `localStorage`. Remove duplicate auth/session state while retaining navigation and sign-out behavior. |
| `src/components/intake/CaseIntakeView.tsx` | SIMPLIFY | Active controlled intake and upload UI. Share the duplicate latest-extraction selection with materials and make always-provided navigation callbacks required if no alternate caller exists. |
| `src/components/layout/WorkspaceHeader.tsx` | MERGE | Keep the file, but merge repeated desktop/mobile case switcher/new/delete action markup into one local render path. Preserve responsive placement. |
| `src/components/layout/WorkspaceSidebar.tsx` | SIMPLIFY | Active sidebar. Reduce prop forwarding and reconcile duplicated case status labels only if the user-visible wording can remain stable. |
| `src/components/materials/CaseMaterialsView.tsx` | SIMPLIFY | Active material preview. Remove shallow memoization, share duplicate extraction sorting, and delete test-only upload metadata props after tests migrate. |
| `src/components/overview/CaseFindingsSection.tsx` | SIMPLIFY | Active findings table. `FindingRow` is only used in the same file, so its public export is unnecessary; replace per-row style functions with a local map if it remains clearer. |
| `src/components/overview/CaseOverviewView.tsx` | SIMPLIFY | Active overview orchestration and rendering. Remove redundant fallback memos, the `key={caseId}` on the header, duplicate polling, and swallowed analysis errors while retaining tabs, findings, questions, and source drawer behavior. |
| `src/components/overview/OverviewStatusRail.tsx` | KEEP | Status metrics, run notice, and record selection are cohesive and actively rendered. |
| `src/components/report/CaseReportView.tsx` | SIMPLIFY | Active report list/generation/download. Shallow error memo and duplicated run status preparation can be removed after the shell status owner is settled. |
| `src/components/report/PersistedReportCard.tsx` | SIMPLIFY | Active HTML report viewer. Keep object URL lifecycle and retry behavior; remove shallow `htmlUserFacingError` memo if no referential contract needs it. |
| `src/components/technical/TechnicalContextView.tsx` | MERGE | Keep the file, but merge `TechnicalItem` and `RetrievedOnlyItem` around one details disclosure/render path; their current markup duplicates the same technical card affordance. |

### Chat features and hooks

| Path | Classification | Evidence and proposed action |
|---|---|---|
| `src/features/chat/chatSubmissionMessages.ts` | KEEP | Current optimistic/merge/remove operations are shared by the submission flow and represent a concrete cache contract. |
| `src/features/chat/useCaseChatSubmission.ts` | SIMPLIFY | Both follow-up and ordinary-content submissions repeat request, cache, error, and settlement steps. Share only the proven common tail; keep distinct idempotency, retry, follow-up status, and run seeding branches. |
| `src/features/chat/useCaseChat.ts` | SIMPLIFY | Direct hook fields are used by the case shell, while `sessionObj`, selectors, and a no-op restore method are legacy compatibility surface used only by tests. Migrate tests to direct fields and remove the facade. |
| `src/features/chat/useChatDraft.ts` | SIMPLIFY | Persistence and reconciliation are needed. Delete unused `failSelection` and `forgetCaseChat`, remove the duplicate `completeSubmission` alias, and keep one completion method. |
| `src/hooks/use-auth.ts` | KEEP | Session query, auth mutations, and cross-tab synchronization are the application auth state owner. |
| `src/hooks/useCaseDeletion.ts` | KEEP | Encapsulates the active case deletion flow and selection cleanup. |
| `src/hooks/useCaseIntakeActions.ts` | BACKEND RESPONSIBILITY | The hook is active, but it sequences title update, evidence insertion, refetch, revision handling, and analysis start. An atomic intake endpoint could own consistency; retain current behavior until that contract exists. |
| `src/hooks/useCaseQueries.ts` | SIMPLIFY | Query hooks are active, but `useCaseRun` at L102-L112 has no production or test caller, and polling is mounted in four places. Delete the unused hook and choose one polling owner. |

### Libraries and generated contracts

| Path | Classification | Evidence and proposed action |
|---|---|---|
| `src/lib/account-storage.ts` | KEEP | Account-namespaced draft and route storage is actively used by auth and chat persistence. |
| `src/lib/apiClient.ts` | BACKEND RESPONSIBILITY | Direct endpoint wrappers are needed. `normalizeCaseReport` and the optional `messages` fallback exist because generated types lag backend defaults; remove those adapters after the OpenAPI contract is corrected. |
| `src/lib/api.ts` | KEEP | Two-line re-export has 28 importers and is the stable public API facade. Deleting it would create broad import churn without removing behavior. |
| `src/lib/apiTypes.ts` | SIMPLIFY | Current auth types are needed because the generator does not emit all auth schemas. Report array aliases and `CaseChatDetail` can be removed once generated defaults are required. |
| `src/lib/caseOverviewSource.ts` | BACKEND RESPONSIBILITY | The frontend currently validates generic provenance/citation JSON. The fail-closed display checks are still required while the API exposes generic dictionaries; move to a validated evidence projection before deleting them. |
| `src/lib/caseOverview.ts` | KEEP | Trace, claims, gaps, and external-context mapping are used by overview and chat rendering. Current `trace_json` is persisted as a generic dictionary, so filtering malformed references protects display correctness. |
| `src/lib/caseOverviewTypes.ts` | KEEP | Shared typed view shapes are used by overview, chat, technical context, and source drawers. |
| `src/lib/chat-followup.ts` | SIMPLIFY | Follow-up ordering, supersession, metadata parsing, and pending selection are active domain behavior. Delete the one-line `chatTranscriptMessages` wrapper and call its underlying filter directly. |
| `src/lib/generated/caseTypes.ts` | KEEP | Generated API contract; do not hand-edit. |
| `src/lib/generated/chatTypes.ts` | KEEP | Generated API contract; its optional `messages` field currently explains an adapter and should be fixed at generation/schema level. |
| `src/lib/generated/evidenceTypes.ts` | KEEP | Generated API contract. |
| `src/lib/generated/reportTypes.ts` | KEEP | Generated API contract; optional arrays currently explain report normalization. |
| `src/lib/generated/runTypes.ts` | KEEP | Generated run contract used by query/polling and status rendering. |
| `src/lib/technicalContext.ts` | BACKEND RESPONSIBILITY | Technical mapping is active and keeps external context separate from Case evidence. Its generic `external_context_json` parsing can move behind a typed backend projection later. |
| `src/lib/user-facing-error.ts` | SIMPLIFY | User-facing categories and retry semantics are required. Its Axios/detail parsing overlaps `apiClient.getApiErrorMessage`; consolidate the parser without losing timeout, conflict, and validation distinctions. |
| `src/lib/workspaceRoutes.ts` | KEEP | Canonical route parser/builder has ten importers and protects workspace navigation consistency. |

## B. Complexity hotspots

| Priority | Files | Why it is complex | Likely removable code | Simplification risk |
|---|---|---|---|---|
| P0 | `src/components/home/HomeSections.tsx`, `src/components/auth/AccountGate.tsx`, `src/hooks/use-auth.ts` | Two independent session checks, local-storage fallback, duplicate route persistence, and a second logout path exist for the public landing navigation. | Approximately 70-100 lines of session state/effects and fallback handling; keep the visible menu/navigation. | Medium: sign-out focus, redirect timing, and public-page behavior must remain covered. |
| P0 | `src/app/case/[caseId]/layout.tsx` plus overview/intake/report routes | Shell owns case, analysis, evidence, run, chat, navigation, delete, and error state. Four places observe the same run. | Remove `cases` fallback memo, narrow callback dependencies, duplicate polling observers, and swallowed local-storage/action errors. | Medium-high: shell is a cross-feature boundary and run settlement invalidation must remain exactly once. |
| P0 | `src/features/chat/useCaseChat.ts` | Direct API and a second session facade expose overlapping selectors, getters, callbacks, and fields; `restoreCaseChat` is a no-op. | Approximately 60-90 lines of facade/selectors and no-op compatibility methods. | Medium: current tests use `session`; migrate them before deleting the surface. |
| P1 | `src/hooks/useCaseQueries.ts`, shell, overview, intake, report | `useCaseRun` is dead and `useCaseRunPolling` combines fetch, timer, completion invalidation, and status ownership in multiple observers. | Delete `useCaseRun`; make one owner poll and let other views read cached run data. | High if polling effect moves without a focused run lifecycle test. |
| P1 | `src/lib/caseOverviewSource.ts`, `src/lib/caseOverview.ts`, `src/lib/technicalContext.ts` | Several parsers walk generic persisted JSON and validate IDs, source relationships, quote occurrence, page spans, trace version, and external/case separation. | Remove only checks that duplicate a future typed backend projection; share primitive guards and maps where this reduces code without weakening fail-closed behavior. | High: deleting these checks can show a quote under the wrong document or present external context as Case evidence. |
| P1 | `src/features/chat/useCaseChatSubmission.ts`, `chatSubmissionMessages.ts`, `useChatDraft.ts` | Ordinary Ask and formal follow-up both implement optimistic insertion, request persistence, reconciliation, retries, and errors, but their run-seeding and status semantics differ. | Share a small proven completion/error tail; remove dead draft methods and duplicate completion alias. | High: idempotency, stale navigation, pending local storage, and late run settlement are race-sensitive. |
| P1 | `src/components/materials/CaseMaterialsView.tsx`, `src/components/intake/CaseIntakeView.tsx` | Both sort extraction history and interpret extraction provenance; materials also rebuild page records from generic JSON. | Share one latest-extraction selection helper and remove test-only upload metadata props. | Medium: page fallback and preview behavior must remain stable for existing documents. |
| P1 | `src/lib/apiClient.ts`, `src/lib/apiTypes.ts`, generated contracts | API wrappers normalize arrays that backend Pydantic defaults already guarantee, because generated OpenAPI output marks them optional. | Fix generation/schema and remove `normalizeCaseReport`, `CaseChatDetail` fallback, and redundant report aliases. | Medium: requires regenerated types and contract tests, not a hand edit to generated files. |
| P1 | `src/lib/user-facing-error.ts`, `src/lib/apiClient.ts` | Both classify Axios errors and parse detail/message/validation payloads. | One parser/classifier with the existing retryability and conflict semantics. | Medium: error copy and retry decisions are user-visible. |
| P2 | `src/components/layout/WorkspaceHeader.tsx`, `src/components/technical/TechnicalContextView.tsx` | Desktop/mobile action markup and mapped/retrieved-only technical item markup are duplicated within each feature. | Merge local render paths, preserving responsive layout and external-reference labeling. | Low-medium: visual regression coverage is needed. |
| P2 | `src/components/case-library/CaseLibraryPage.tsx`, report components, `CaseMaterialsView` | Shallow memoization and repeated pure fallbacks add navigation noise with React Compiler enabled. | Remove `useMemo` around simple fallbacks and repeated local formatting where output is unchanged. | Low. |
| P2 | `src/components/common/icons.tsx`, `src/app/globals.css`, `frontend/tailwind.config.ts`, `src/app/case/layout.tsx` | Unused icon paths, utility classes, animation definitions, and an empty layout remain in the shipped source. | Delete confirmed zero-use definitions. | Low after a production build and class search; CSS class names should be checked against any external/demo markup. |

## C. Deletion candidates

These are candidates for Phase 2, ordered by confidence. No item below was deleted during this audit.

| Candidate | Evidence | Expected reduction | Risk and gate |
|---|---|---:|---|
| `src/app/case/layout.tsx` | Ten-line fragment layout with no behavior. | 10 lines | Low; run Next build and route smoke test. |
| `useCaseRun` in `src/hooks/useCaseQueries.ts:L102-L112` | No production or test caller; all consumers use `useCaseRunPolling`. | 11 lines | Low; rerun API/type/tests. |
| `failSelection` in `src/features/chat/useChatDraft.ts:L108-L112` | Definition and returned property only; no caller. | 5 lines | Low; remove from return type and compile. |
| `forgetCaseChat` in `src/features/chat/useChatDraft.ts:L155-L160` | Definition and returned property only; no caller. | 6 lines | Low; verify no external session caller remains. |
| `restoreCaseChat` and session-only selectors in `src/features/chat/useCaseChat.ts:L166-L206` | `restoreCaseChat` is a no-op; `session` methods are used only by legacy chat tests/support. | 60-90 lines | Medium; migrate tests to direct hook fields first. |
| Duplicate `completeSubmission` alias in `useChatDraft.ts:L139-L166` | The same callback is exported under both `completeSubmission` and `completeSubmissionWithoutRun`; production can use one name. | 1-2 lines plus caller edits | Low. |
| `chatTranscriptMessages` wrapper in `src/lib/chat-followup.ts:L259-L263` | One-line wrapper around `filterSupersededClarificationAnswers`; only layout needs the behavior. | 4-5 lines | Low; update layout import/call. |
| `FindingRow` export in `src/components/overview/CaseFindingsSection.tsx` | Used only inside its defining module. | 1 keyword | Low. |
| `HomeMiniVisual` export in `src/components/home/HomeSections.tsx` | Used inside the same module; no external import requires a public export. | 1 keyword | Low. |
| `issues`, `alert`, `expand`, `collapse` icon entries in `src/components/common/icons.tsx` | Zero production uses after repository-wide search. | Approximately 35-45 lines | Low; rerun typecheck and icon search. |
| `/casefleet-preview` branch in `src/components/auth/AccountGate.tsx:L12-L15` | No route, page, test, or caller exists. | Approximately 4-8 lines | Low unless an external deployment links to this undocumented path. |
| Unused utilities in `src/app/globals.css` | `btn-secondary`, `btn-inverted`, `btn-outlined`, `card`, `panel`, `workspace-card`, `report-shell`, and `report-builder-grid` have no source class use. | Approximately 35-55 lines | Low-medium; run build and search for externally supplied class names. |
| Unused float animations in `frontend/tailwind.config.ts` | `animate-float-slow`, `animate-float-reverse`, and `animate-float-delayed` have no source class use. | Approximately 10 lines | Low; verify compiled CSS and any external/demo page. |
| `uploadingFilename` and `uploadingFileSize` props in `CaseMaterialsView` | Production `MaterialsPage` never supplies them; current references are tests only. | Approximately 8-15 lines | Low after migrating/removing test-only assertions. |

The following are intentionally not deletion candidates despite large line counts: `caseOverviewSource`, `caseOverview`, `technicalContext`, `SourceEvidenceDrawer`, `MeaningfulErrorModal`, `useChatDraft`, `useCaseChatSubmission`, and report object-URL code. Each protects a current user-visible boundary or a race/lifecycle contract.

## D. Merge candidates

| Current split | Proposed merge | Why it is safe enough to consider | Do not do this yet if |
|---|---|---|---|
| Desktop and mobile action blocks inside `WorkspaceHeader.tsx` | One local action renderer with placement-specific wrappers | The controls perform the same case select/new/delete behavior and differ mainly in layout classes. | A visual check shows desktop and mobile need genuinely different interaction semantics. |
| `TechnicalItem` and `RetrievedOnlyItem` inside `TechnicalContextView.tsx` | One internal technical card renderer with optional case-basis and relevance sections | Both render technique identity, definition disclosure, and external-reference treatment. | The two card types acquire different interactions or evidence semantics. |
| Latest extraction selection in `CaseMaterialsView.tsx` and `CaseIntakeView.tsx` | One local helper near the shared query boundary | The operation is the same sort-and-select rule. This is a small helper, not a new abstraction layer. | The backend changes one screen to a different extraction policy. |
| Axios/detail parsing in `apiClient.ts` and `user-facing-error.ts` | One error parser owned by the UI/API boundary | Removes duplicated string/detail/validation parsing while retaining user-facing classifications. | Retryability and conflict semantics cannot be expressed by one direct result. |
| Report array normalization in `apiClient.ts` and report aliases in `apiTypes.ts` | Generated contract plus direct response use | The backend report schema already supplies list defaults; the adapter is compensating for stale generated optional fields. | OpenAPI generation still marks the fields optional. |
| `useCaseChat` session facade and direct hook return | Direct hook return only | Current production shell consumes direct fields; the facade is test/legacy compatibility surface. | A supported non-test caller still requires session selectors. |

Files that should remain separate are `CaseReportView` and `PersistedReportCard` (PDF and HTML have different object URL lifecycles), intake and materials (different writes and navigation), and overview and technical context (different evidence/external-context semantics). Merging those files would reduce file count while increasing conceptual cost.

## E. Backend responsibility leaks

The frontend should trust a typed, validated backend projection when one exists. The current backend does not yet provide that projection for every payload, so some validation is still justified.

| Frontend code | Current behavior | Backend contract evidence | Recommended boundary |
|---|---|---|---|
| `CaseMaterialsView.getExtractionPages` at L190-L203 | Interprets `provenance_json.pages`, `page_number`, `text`, `merged_text`, and `text_method`, then invents page-number fallbacks. | Document extraction provenance is generic JSON in the current API. | Return normalized extraction pages from the backend; then render the list directly and delete this parser. |
| `caseOverviewSource.ts` | Validates source IDs, document binding, quote occurrences, page numbers, spans, and source provenance before opening a drawer. | Evidence/provenance payloads are generic dictionaries and can be malformed persisted data. | Keep fail-closed checks until backend returns a validated citation/evidence projection. Move relationship proof server-side later. |
| `caseOverview.ts` | Parses generic `trace_json`, verifies version/validated mode, filters unknown claim/gap/source IDs, and binds associations. | `CaseAnalysisResultRead.trace_json` is `dict[str, object] | None`; internal backend trace contracts are typed but not exposed as a nested API schema. | Expose a typed validated trace read model; then keep only display mapping. |
| `technicalContext.ts` | Reconstructs augmentation status, rows, association IDs, retrieval-only rows, and Case-source bindings from generic external context. | `external_context_json` is currently `dict[str, object]`. | Expose a typed technical-context projection; preserve the explicit external-versus-Case evidence distinction. |
| `apiClient.normalizeCaseReport` at L254-L273 | Rebuilds list defaults for sections, claims, source IDs, MITRE IDs, and limitations. | Backend `ReportSection` and `StructuredReport` already use list defaults; generated report types still mark arrays optional. | Correct OpenAPI generation and remove normalization/aliases. |
| `getCaseChat` response fallback in `apiClient.ts` | Replaces missing `messages` with an empty list. | Backend `CaseChatRead.messages` has `Field(default_factory=list)`. | Make generated `messages` required and use the response directly. |
| `useCaseIntakeActions` | Coordinates multiple writes and refetches to make intake appear atomic. | Current API exposes separate case update, evidence add, and analysis start calls. | Add an explicit atomic endpoint only if product requires transactional intake; otherwise keep the direct sequence. |
| `HomeNavigation` in `HomeSections.tsx` | Rechecks session and infers login from a local-storage account value. | `AccountGate` and `useAuth` already own session truth. | Remove duplicate auth proof from the landing page and consume the existing auth owner. |

### Defensive validation decision

The request correctly identifies `asRecord`, `asArray`, `asString`, source ID checks, page/offset checks, and relationship checks as suspicious duplication. They are not all equivalent:

- `CaseChatRead.messages` and report arrays are backend-guaranteed defaults. Their frontend fallbacks are contract drift and should disappear after generated types are corrected.
- `trace_json`, `provenance_json`, and `external_context_json` are still generic dictionaries at the API boundary. Removing all primitive and relationship checks today would make malformed persisted data render as authoritative evidence or attach a quote to the wrong source.
- The minimum safe frontend responsibility is to reject an invalid reference from display, show the remaining valid data, and preserve the distinction between Case evidence and external MITRE/RAG context. A typed backend projection would let the frontend delete most of this parsing later.

## Hook, effect, state, and memo audit

### Keep

- `useAuth` effects synchronize authentication across tabs and handle route redirects.
- `useChatDraft` effects/ref state persist drafts and pending submissions across refresh/navigation and reconcile them after the server responds.
- `useCaseRunPolling` refetches queued/running runs and invalidates dependent caches once on terminal status.
- `OriginalFilePreview` creates and revokes object URLs for a blob; that lifecycle cannot be replaced by a derived value.
- Dialogs and source drawers manage focus return, keyboard dismissal, and modal state.

### Simplify

- `cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data])` in the case shell is a pure fallback.
- Overview `evidenceQuery.data ?? []` and `followupsQuery.data ?? []` memos are pure fallbacks.
- `SystemOcrPreview` memoizes a small page mapping; React Compiler and the small data shape make this unnecessary unless profiling proves otherwise.
- `CaseLibraryPage.visibleCases` and report `activeError`/`htmlUserFacingError` use shallow memoization with no demonstrated referential contract.
- Many navigation callbacks are wrappers around `router.push`; retain only wrappers that also perform a state/error side effect or are passed to a memoized child.
- `clearWorkspaceError` depends on the entire `chat` object instead of the specific `chat.clearQueryError` method, which causes avoidable callback churn.

### State that should remain local

- `selectedCaseId`, `selectedSource`, dialog open state, and chat open state each drive visible UI and should not become global state.
- Draft text and pending request records are account-scoped persistence, not derived display values.
- `runId` is correctly derived from the active/latest Case fields; storing a second selected run object would add stale state.

## F. Estimated cleanup

Estimates are ranges from the current source and intentionally exclude generated files until the API contract is regenerated.

| Work tier | Files/symbols | Estimated reduction | Confidence |
|---|---:|---:|---|
| High-confidence deletion | 1 file, 10-14 symbols/definitions | 90-150 production lines | High after route/type/test checks |
| Direct simplification | 8-12 files | 150-280 production lines | Medium; preserve current UI and race behavior |
| Internal merges | 2 feature files plus two local helpers | 40-90 production lines | Medium; needs visual and component tests |
| Contract-driven cleanup | 3-5 adapters/types after backend/OpenAPI correction | 80-160 production lines | Conditional; not safe to count before contract change |
| Optional chat orchestration cleanup | 1-2 files | 50-120 production lines | Low-medium; idempotency and stale navigation need focused tests |

A realistic Phase 2 target without backend schema changes is one deleted route file plus roughly 250-450 production lines removed or inlined. Contract-driven work could remove more, but it should be reported separately because it requires backend/generated-contract changes. No after-count is claimed in this Phase 1 report.

## Validation baseline

Commands were run from `frontend/` against the current dirty checkout:

| Command | Result |
|---|---|
| `npm run check:api-types` | PASS |
| `npx tsc --noEmit --incremental false` | PASS |
| `npm run lint` | PASS with one existing warning at `src/components/home/HomeSections.tsx:239` for `@next/next/no-img-element` |
| `npm test -- --reporter=dot` | FAIL: 27 files passed, 2 failed; 106 tests passed, 2 failed (108 total) |

The two current test failures are:

1. `src/test/components/chat/AnalysisEvidenceReferences.test.tsx` expects the accessible name `Source source-1`; the dirty tree currently renders the friendly label `Case narrative` and keeps the old identifier only in the title.
2. `src/test/components/technical/TechnicalContextView.test.tsx` expects `/Source — Source .*/i`; the dirty tree currently renders `Source — Case narrative`.

Those failures are a label-contract mismatch in the existing dirty change to `caseOverviewSource.ts`, not a cleanup edit from this audit. The build and Playwright E2E were not run because Phase 1 was read-only and no cleanup diff exists to validate.

## Additional scan: one-time components and multi-hop props

This pass uses the TypeScript compiler to count JSX call sites and the import graph to count production importers. It then traces the actual prop expressions by hand through the parent/child render paths. A static one-time JSX call is not the same as a one-time runtime instance: components rendered from `.map()` run once per item, and a route-level component runs on every visit to that route.

### One-time component results

The scan found 57 named components with exactly one static JSX call in production code. It also found 15 component modules with exactly one direct production importer. That signal is useful for finding unnecessary wrappers, but it is not a deletion rule.

| Group | Components | Finding |
|---|---|---|
| Route, provider, or feature boundary | `Providers`, `AccountGate`, `CaseLibraryPage`, `HomeNavigation`, `HomeHero`, `HomePlatform`, `HomeWorkflow`, `HomeIntelligence`, `HomeFooter`, `CaseIntakeView`, `WorkspaceHeader`, `WorkspaceSidebar`, `WorkspaceChatPanel`, `CaseMaterialsView`, `CaseOverviewView`, `OverviewStatusRail`, `CaseReportView`, `PersistedReportCard`, `TechnicalContextView`, `ChatTranscript` | KEEP. Each is a route/layout boundary or a coherent screen feature. A single importer is expected and does not justify flattening the route. `AccountGate` is rendered by the global provider on every protected page, and the home sections are rendered as a collection rather than reused widgets. |
| Static call once but runtime repeated | `HomeMiniVisual`, `CaseLibraryCard`, `FindingRow`, `FollowUpActionCard`, `TechnicalItem`, `RetrievedOnlyItem` | KEEP. The call appears once in source but is inside a collection or message render path. Removing the component would only move repeated JSX into a parent. Remove the unnecessary public export from `HomeMiniVisual` and `FindingRow`; keep the local functions. |
| One-use component with real state, effects, or a domain interaction | `CaseAnalysisLeadCard`, `AnalysisEvidenceReferences`, `FollowUpStepper`, `FollowUpReminder`, `ChatComposer`, `SourceEvidenceContent`, `UploadControl`, `MaterialPreviewViewport`, `MaterialSourceRail`, `WorkspaceCaseDrawer`, `CaseOverviewHeader`, `OpenQuestionsSection`, `RunNotice`, `ReportVersionSelector`, `ReportHtmlViewer`, `ReportFailure`, `CaseLibraryHeader`, `LatestCaseSection`, `CaseLibraryToolbar` | KEEP. These components either own hooks/focus/object URL behavior, render a meaningful section, or keep a large branch readable. Their one-time use is a cohesion decision, not dead code. |
| Pure one-use wrapper or short state branch | `CaseLibraryLoadingState`, `CaseLibraryErrorState`, `CaseLibraryEmptyState`, `NoMatchingCases`, `EmptyChatIntakeNotice`, `EmptyPreview`, `OverviewSummarySection`, `ContextStatus`, `NewCaseCard`, `DeleteCaseDialog` | INLINE or remove the wrapper in Phase 2. These have no independent state and a small prop surface. The parent can retain the same empty/loading/error UI directly. `DeleteCaseDialog` can be replaced by a direct `ConfirmDialog` call in the case shell while `ConfirmDialog` remains shared. |

The scan also surfaced two prop declarations that do not carry behavior:

- `WorkspaceChatPanelProps.hasAnalysisContext` is passed from `src/app/case/[caseId]/layout.tsx:L184` and supplied by chat tests, but `WorkspaceChatPanel` never destructures or reads it. Delete the prop and the shell expression. This is the clearest dead prop in the frontend.
- `HomeMiniVisual` and `FindingRow` are exported even though their only JSX references are in their defining modules. Remove only the `export` modifier; do not remove the functions because the parent maps still use them.

### Multi-hop prop chains

| Chain | Props crossing the chain | What each hop adds | Assessment |
|---|---|---|---|
| `src/app/case/[caseId]/layout.tsx` → `WorkspaceSidebar` → `WorkspaceCaseDrawer` | `cases`, `activeCaseId`, `casesLoading`, `casesError`, `deletingCaseId`, `onRequestDelete`; `onNewCase` and `onSelectCase` are wrapped to close the drawer | The shell owns server state; the sidebar owns rail/drawer open state; the drawer owns the saved-case list UI. | Medium forwarding cost, but the close-after-action wrappers are real behavior. Destructure the sidebar props and keep the drawer boundary, or inline the drawer only if the shell becomes easier to read. |
| `layout.tsx` → `WorkspaceChatPanel` → `ChatTranscript` → `AnalysisEvidenceReferences` → `SourceEvidenceDrawer` | `onNavigateToSource` crosses four component boundaries; `leadResult` and `evidenceSources` cross two; `messages` is split into raw and visible collections | Panel owns open/close, empty intake notice, follow-up answer state, and composer; transcript owns ordering and lead card; references owns citation selection; drawer owns focus and quote display. | Deep but behavior-bearing. Do not flatten the whole chain. Remove `hasAnalysisContext`, consider deriving visible messages in one place, and require callbacks that are always present in production after test callers migrate. |
| `CaseOverviewView` → `CaseFindingsSection` → `FindingRow` → `SourceGroup` → `EvidenceCitationChip` | `onSelectSource`, `onNavigateToSource`, and `activeSourceKey` are spread through three child layers; `sources`, `findingId`, and `role` are added locally | Overview owns source drawer state; findings owns grouping/collapse; row owns finding columns; source group owns supporting/conflicting lists; chip owns button semantics. | Highest pure prop-plumbing cost. Keep grouping/collapse and the chip, but collapse `FindingRow`/`SourceGroup` into the section's local map or pass source actions through one closure. This removes repeated `FindingSourceActions` spreading without introducing context. |
| `technical-context/page.tsx` → `TechnicalContextView` → `TechnicalItem` → `SourceEvidenceDrawer` | `onNavigateToSource` crosses the view to the drawer; `activeSourceKey` and `onSelectSource` cross the view to mapped items | The view owns selected source state; each item owns its disclosure and source button; drawer owns evidence focus. | Two hops with distinct state ownership. The internal mapped/retrieved item markup is a merge candidate, but the callback chain itself is justified. |
| `materials/page.tsx` → `CaseMaterialsView` → `MaterialSourceRail` and `MaterialPreviewViewport` → `EmptyPreview`/previews | `onOpenIntake` reaches `EmptyPreview`; `caseId`, `document`, and `extraction` reach preview implementations; upload metadata reaches the rail | Materials view owns selected IDs and preview mode; rail owns source list/upload control; preview viewport owns representation tabs; original/OCR previews own their fetch/lifecycle. | Keep the preview boundaries. Inline `EmptyPreview`, remove production-dead `uploadingFilename`/`uploadingFileSize` props or deliberately wire them, and keep object URL/query lifecycles local. |
| `report/page.tsx` → `CaseReportView` → `PersistedReportCard` → `ReportHtmlViewer`/nested error modal | `caseId`, `caseTitle`, report identity, and PDF callback cross one or two boundaries | Report view owns list/generation/PDF mutation; persisted card owns saved version display; HTML viewer owns blob fetch/object URL and retry. | Required lifecycle separation. Do not merge these files merely because the importer count is one. Make `NoSavedReport.onOpenOverview` required if this remains the only caller. |
| `intake/page.tsx` → `CaseIntakeView` → `UploadControl` | Upload callback and busy state cross one child boundary | Intake view owns persisted fields and submission; upload control owns the file input reset and accept list. | Low cost and readable. No multi-hop problem. |
| `layout.tsx` → `WorkspaceHeader` → `IconAction` | New/delete callbacks and disabled state cross one local helper; the same attributes are repeated in desktop and mobile markup | Header owns responsive placement; `IconAction` owns icon-button semantics. | Merge the duplicated desktop/mobile action block inside `WorkspaceHeader`; keep `IconAction` if it still removes repeated button markup. |

### Optional and unused prop audit

| Prop | Current production callers | Additional finding |
|---|---|---|
| `WorkspaceChatPanel.hasAnalysisContext` | Shell passes a boolean; no component code reads it | DELETE. It is dead data, not merely optional plumbing. |
| `WorkspaceHeader.isChatOpen` and `onToggleChat` | Always passed by the case shell; tests exercise both | Make required and remove the conditional chat-button branch only if the component is not intended as a standalone test fixture. Otherwise keep optionality as a deliberate test/embedding contract. |
| `CaseIntakeView.onOpenOverview` and `onOpenMaterials` | The intake route always passes both; tests omit them | Make required if this view is only the canonical intake screen, then remove the two guards. If isolated no-navigation rendering remains a supported test fixture, keep the guards. |
| `CaseOverviewHeader.onOpenMaterials` | The overview view always passes it | Make required and remove the conditional button branch, unless another embedding is added. |
| `NoSavedReport.onOpenOverview` | `CaseReportView` always passes it | Make required; this is an internal component with one caller. |
| `CaseMaterialsView.uploadingFilename` and `uploadingFileSize` | The materials route never passes either; only materials tests exercise the optimistic row | DELETE from the materials production path unless the product intentionally adds upload-progress metadata there. Intake already receives `uploadingFilename` from `useCaseIntakeActions`. |
| `EvidenceCitationChip.onNavigateToSource` fallback | Current production chip call sites also provide `onSelect`; the fallback is not selected in the normal path | Low-confidence deletion candidate. Keep until the chip's standalone navigation contract is explicitly removed; do not break the source drawer behavior while simplifying prop chains. |

### Additional cleanup estimate

The one-time and prop pass adds the following realistic Phase 2 range:

- Delete one unused prop (`hasAnalysisContext`) and remove 5-10 lines of related plumbing.
- Inline 6-10 pure one-use wrappers for approximately 45-90 lines, depending on whether the parent remains readable.
- Remove two unnecessary export modifiers and one thin `DeleteCaseDialog` wrapper for approximately 10-25 lines.
- Collapse the findings source-action forwarding for approximately 25-50 lines without changing the citation drawer contract.
- Make 3-5 production-only callbacks required, removing approximately 10-25 lines of optional branches after tests are updated.

This raises the conservative Phase 2 target to roughly 300-500 production lines removed or inlined, still excluding the conditional backend/OpenAPI contract cleanup. It does not justify deleting the stateful feature boundaries or adding a prop context/store.

## Phase 2 boundary

Phase 2 was not executed. The frontend production tree remains untouched by this audit. The first implementation slice should delete the empty case layout and confirmed zero-caller symbols, then simplify duplicated auth/polling/session ownership with focused tests. Evidence, citation, trace, and external-context parsers should only be reduced after a typed backend projection or a test-backed proof that the current generic payload cannot violate the display boundary.
