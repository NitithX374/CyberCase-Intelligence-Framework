# CyberCase Frontend

The Next.js App Router presents a Case-first workspace. `/case` is the Case Library; `/case/[caseId]` has three views (Sources, Analysis, Legal) and the Case-owned Ask/Chat panel.

The browser calls the FastAPI backend through each feature's `api.ts`, which share one HTTP client in `src/lib/api/http.ts`, and never calls `rag_service` directly. TanStack Query manages server state; analysis, upload, clarification, and report operations are request-scoped backend requests rather than a frontend run-status or polling workflow.

## Layout

Code is grouped by flow, so following one means opening one folder. Each folder under `src/features/` holds that flow's page, its components, its calls to the backend (`api.ts`), its hooks (`queries.ts` for the server state it owns), its parsing, and its tests beside the files they test. The folder names follow the backend's feature folders where they share a flow.

| Folder                | What it owns                                                                                                                                                                                                                                                                                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/app/`            | Routes only. Each page and the case layout render one feature component: `CaseWorkspace`, `SourcesPage`, `AnalysisPage` or `LegalPage`.                                                                                                                                                                                                                            |
| `features/workspace/` | The case shell: `CaseWorkspace` (the Ask panel, rename, new case, and how an analysis run ends, whichever page started it) and the header.                                                                                                                                                                                                                         |
| `features/cases/`     | The case library and a case's own record: list, create, rename, delete.                                                                                                                                                                                                                                                                                            |
| `features/sources/`   | The Sources page (`SourcesPage`): adding sources and reading them, the rail and viewer, and `useCaseSourceRows` (sources plus answered follow-ups).                                                                                                                                                                                                                |
| `features/citations/` | Showing what an answer or a finding cites, for the analysis and the chat: the citation chip, the source drawer (`useSourceDrawer`), and turning claims, citations and follow-up answers into source refs (`sourceRefs`, `followupSources`).                                                                                                                        |
| `features/analysis/`  | The Analysis page (`AnalysisPage`), running an analysis (`useRunCaseAnalysis`, which every Analyze button calls; `useAnalysisRunOutcome`, which `CaseWorkspace` uses to go to Analysis, open Ask, or say why a run failed) and reading its result: summary, findings, open questions. `technical-context/` holds the ATT&CK context the analysis was read against. |
| `features/legal/`     | The Legal page (`LegalPage`): the Thai provisions the RAG service returned, behind their notice.                                                                                                                                                                                                                                                                   |
| `features/reports/`   | Report versions, preview, and PDF.                                                                                                                                                                                                                                                                                                                                 |
| `features/chat/`      | The Ask panel and the follow-up questions it carries.                                                                                                                                                                                                                                                                                                              |
| `features/auth/`      | Session, sign-in forms, the account menu.                                                                                                                                                                                                                                                                                                                          |
| `src/components/`     | Shared UI with no flow of its own: icons, dialogs, empty states, and `Markdown` for the chat and the analysis summary.                                                                                                                                                                                                                                             |
| `src/lib/`            | Shared non-UI code: the HTTP client and the API contract (`lib/api/`), the case paths (`casePaths.ts`), query keys, formatting, parsing helpers.                                                                                                                                                                                                                   |
| `src/test/`           | Test support shared across features: fixtures, HTTP errors, chat responses.                                                                                                                                                                                                                                                                                        |

A feature may import another feature's hooks or types (Analysis reads sources); shared folders import no feature. There are no barrel files: import from the file that defines the name.

## Contracts

`src/lib/api/generated/openapi.ts` is generated from the backend's OpenAPI schema, and `src/lib/api/types.ts` names the schemas the UI uses. Regenerate it with `npm run generate:api-types` after a backend schema change; `npm run check:api-types` fails when it is stale. Both export the schema through Python (`env_mitre`, or the interpreter in `CYBERCASE_PYTHON`) and need no running backend. The UI must distinguish native Case sources, follow-up answers, analysis, optional technical context, and report status according to the current response schemas.

The Sources and Analysis views may project answered follow-up messages alongside native sources for reader navigation: Sources reads them from the chat (`features/sources/useCaseSourceRows.ts`), and Analysis reads the ones the analysis recorded (`features/analysis/analysisRecord.ts`). That display projection does not make a follow-up answer a persisted `CaseSource`.

## Commands

```powershell
npm install
npm run dev
npm run test
npm run lint
npm run build
npm run generate:api-types
```
