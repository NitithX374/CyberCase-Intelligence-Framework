# CyberCase Frontend

The Next.js App Router presents a Case-first workspace. `/case` is the Case Library; `/case/[caseId]` contains overview, sources, technical context, report, and the Case-owned Ask/Chat panel.


The browser calls the FastAPI backend through `src/lib/api.ts` and never calls `rag_service` directly. TanStack Query manages server-state loading and polling while the backend remains authoritative for Case data, messages, runs, analysis, and reports.

## Contracts

Generated declarations under `src/lib/generated/` reflect the backend OpenAPI contract. Update them only through the existing generation command when an API change is explicitly required. The UI must present evidence, analysis, technical context, and report status according to the current response schemas rather than inventing client-only domain objects.

## Commands

```powershell
npm install
npm run dev
npm run test
npm run lint
npm run build
```

With the backend running, `npm run generate:api-types` regenerates the ignored OpenAPI declaration.
