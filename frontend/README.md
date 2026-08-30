# CyberCase Frontend

The Next.js frontend provides two persisted workspaces: Chat and Report. The deleted Case State inspector, extraction view, and relationship graph are not product routes.

The browser calls the FastAPI backend through `src/lib/api.ts` and never calls `rag_service` directly. TanStack Query owns server-state loading and polling; the backend remains authoritative for messages, run status, analysis, and reports.

## Routes

- `/chat`: create or select a chat
- `/chat/[threadId]`: persisted conversation and run polling
- `/chat/[threadId]/report`: report generation, history, preview, and PDF download

Unknown former workspace suffixes resolve to the Chat view rather than exposing compatibility screens.

## Analysis presentation

Assistant analysis metadata uses `analysis_trace_v2`. MITRE candidates render only when the trace is validated, binds a retrieval context and raw-evidence hash, links valid analysis claims, and references techniques admitted by the persisted MITRE table.

## Commands

```powershell
npm install
npm run dev
npm run test
npm run lint
npm run build
```

With the backend running, `npm run generate:api-types` regenerates the ignored OpenAPI declaration.
