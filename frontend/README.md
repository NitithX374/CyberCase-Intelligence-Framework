# CyberCase Frontend

The Next.js App Router presents a Case-first workspace. `/case` is the Case Library; `/case/[caseId]` contains the overview, sources, analysis, optional technical context, report, and the Case-owned Ask/Chat panel.

The browser calls the FastAPI backend through `src/lib/api.ts` and never calls `rag_service` directly. TanStack Query manages server state; analysis, upload, clarification, and report operations are request-scoped backend requests rather than a frontend run-status or polling workflow.

## Contracts

Generated declarations under `src/lib/generated/` reflect the backend OpenAPI contract. Update them only through the existing generation command when an API change is explicitly required. The UI must distinguish native Case sources, follow-up answers, analysis, optional technical context, and report status according to the current response schemas.

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
