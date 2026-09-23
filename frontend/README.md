# CyberCase Frontend

The Next.js App Router presents a Case-first workspace. `/case` is the Case Library; `/case/[caseId]` has three views (Sources, Analysis, Legal) and the Case-owned Ask/Chat panel.

The browser calls the FastAPI backend through `src/lib/api/` and never calls `rag_service` directly. TanStack Query manages server state; analysis, upload, clarification, and report operations are request-scoped backend requests rather than a frontend run-status or polling workflow.

## Layout

Code is grouped by flow, so following one means opening one folder. Each folder under `src/features/` holds that flow's components, its hooks (`queries.ts` for the server state it owns), its parsing, and its tests beside the files they test. The folder names follow the backend's `services/` where they share a flow.

| Folder                        | What it owns                                                                                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/app/`                    | Routes only. A page reads the params and composes features.                                                                                            |
| `features/workspace/`         | The case shell: header, the three views and their routes, and `runAnalysis`, which every Analyze button calls.                                         |
| `features/cases/`             | The case library and a case's own record: list, create, rename, delete.                                                                                |
| `features/sources/`           | Adding sources and reading them: the rail and viewer, the source drawer, `useCaseSourceRows` (sources plus answered follow-ups), and citation parsing. |
| `features/analysis/`          | Running an analysis and reading its result: summary, findings, open questions.                                                                         |
| `features/technical-context/` | The ATT&CK context the analysis was read against.                                                                                                      |
| `features/legal/`             | The Thai provisions the RAG service returned, behind their notice.                                                                                     |
| `features/reports/`           | Report versions, preview, and PDF.                                                                                                                     |
| `features/chat/`              | The Ask panel and the follow-up questions it carries.                                                                                                  |
| `features/auth/`              | Session, sign-in forms, the account menu.                                                                                                              |
| `src/components/`             | Shared UI with no flow of its own: icons, dialogs, empty states.                                                                                       |
| `src/lib/`                    | Shared non-UI code: the API client, query keys, formatting, parsing helpers.                                                                           |

A feature may import another feature's hooks or types (Analysis reads sources); shared folders import no feature.

## Contracts

Generated declarations under `src/lib/api/generated/` reflect the backend OpenAPI contract. Update them only through the existing generation command when an API change is explicitly required. The UI must distinguish native Case sources, follow-up answers, analysis, optional technical context, and report status according to the current response schemas.

The Sources and Overview views may project answered follow-up messages alongside native sources for reader navigation. That display projection does not make a follow-up answer a persisted `CaseSource`.

## Commands

```powershell
npm install
npm run dev
npm run test
npm run lint
npm run build
```

With the backend running, `npm run generate:api-types` regenerates the ignored OpenAPI declaration.
