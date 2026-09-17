# CyberCase Intelligence Framework

CyberCase is a bachelor-thesis prototype for general investigative case summarization and grounded analysis. A user creates a Case, adds material, reads a structured analysis, answers a focused follow-up when needed, and can generate a preliminary report. MITRE ATT&CK is optional external technical context for cases that contain relevant cyber activity.

## Product

- `/case` is the Case Library.
- `/case/[caseId]` contains intake, materials, overview, technical context, report, and the Case-owned Ask/Chat panel.
- Case sources support case facts and findings. Assistant text and external MITRE/RAG context remain separate.
- Reports are preliminary, Case-scoped, deterministic, and template-first.

## Services

- `frontend/`: Next.js App Router, React, Tailwind CSS, and TypeScript.
- `backend/`: FastAPI, async SQLAlchemy, PostgreSQL, and Alembic. It owns authentication, Cases, received material, analysis runs, follow-up, Case Ask/Chat, and reports.
- `rag_service/`: separate MITRE ATT&CK retrieval service backed by Qdrant and Neo4j. The browser never calls it directly.

For implementation work, inspect current source, tests, generated contracts, and [`AGENTS.md`](AGENTS.md). [`docs/research/CURRENT_PROJECT_DIRECTION.md`](docs/research/CURRENT_PROJECT_DIRECTION.md) records thesis direction and research scope; it is not a runtime architecture authority.

## Run locally

```powershell
doppler run -- docker compose up --build
```

Or run the backend and frontend separately using the commands in [`AGENTS.md`](AGENTS.md) and the service READMEs.

## Checks

```powershell
./env_mitre/Scripts/python.exe -m pytest backend/tests -q
cd frontend
npm run test
npm run lint
npm run build
```
