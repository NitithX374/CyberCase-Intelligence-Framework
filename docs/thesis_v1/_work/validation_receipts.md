# Validation receipts

## Repository snapshot

- Date: 2026-08-27 (Asia/Taipei)
- Branch: `main`
- HEAD: `cdb66972dce7a9e475f3fbfd1ad7c04c9d511160`
- `origin/main`: same commit
- Working tree: dirty before thesis work; existing user-owned product changes preserved
- Thesis changes: new files under `docs/thesis_v1/**` only

## Backend tests

Command:

```powershell
.\env_mitre\Scripts\python.exe -m pytest backend\tests -q
```

Result: `147 passed, 2 subtests passed, 2 warnings in 4.95s`

Warnings:

1. Starlette TestClient deprecation concerning `httpx`/`httpx2`
2. pytest cache could not write `backend/.pytest_cache/.../nodeids` because of permission

## Frontend tests

Command:

```powershell
cd frontend
npm run test
```

First sandbox attempt failed before loading tests with `spawn EPERM`. The rerun outside that process restriction completed successfully.

Result: `23 passed test files, 88 passed tests, duration 53.45s`

## Frontend lint

Command:

```powershell
cd frontend
npm run lint
```

Result: exit code 0, no lint output.

## Thesis integrity checks

- All 15 required top-level thesis files exist
- All local Markdown links resolve
- All citation keys used in Markdown exist in `references.bib`
- Chapter headings 1.1–6.6 inspected
- Explicit TODO/VERIFY/FIGURE placeholders retained intentionally
- No product code, tests, migrations, research or experiment files were edited by this thesis task

## Not validated

- Docker Compose live stack
- Alembic upgrade from a new database
- Live LLM provider output
- Live Qdrant/Neo4j retrieval
- Browser end-to-end journey
- PDF visual rendering and Thai font output on current snapshot
- Expert/user evaluation

