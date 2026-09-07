# Backend and frontend refactor

## Result

The six proposed areas are implemented in the existing chat architecture. The work is uncommitted. No migration, additional service, provider library, standalone API route, or change to `rag_service` is required.

| Boundary | Responsibility |
| --- | --- |
| Frontend chat session | React Query owns thread detail; one polling function serves selection and submission. Draft state owns retry identity. |
| Main Analysis parser | Provider envelope decoding and local identifier formatting are separate from trace validation and exact citation binding. |
| Chat metadata | Backend schemas describe known metadata fields while preserving historical extension fields. Frontend chat types derive from local OpenAPI. |
| Follow-up | A resolution contains a question, audit metadata and gap analysis. The workflow constructs and persists the assistant outcome. |
| Report rendering | Snapshot validation, findings, MITRE rows and review actions have separate modules. Historical section parsing runs explicitly when no snapshot is present. |
| Run recovery | Existing PostgreSQL run leases support heartbeats, expiration, stale-worker rejection and explicit retry of the original request. |

## Behavior changes

- Source IDs must match authoritative message IDs. Numeric aliases, positional aliases and missing-source guesses are no longer repaired. Formatting `claim-12` as `A-12` preserves its number; claims are not renumbered by array position. Structure failures retain the existing trace-unavailable result; provenance failures reject the analysis.
- Malformed report snapshots raise validation errors. A snapshot with no MITRE rows does not recover mappings from historical section text. Snapshot unresolved issues remain visible. Report text does not claim that the disabled custom binding validator ran.
- Follow-up prompt text is unchanged and lives in versioned UTF-8 files under `followup/prompt_templates`.
- Active workers renew their six-minute leases every 30 seconds. Startup and a 30-second monitor mark expired running work, and queued work older than six minutes, as interrupted. Provider execution does not restart automatically.
- Interrupted requests can be retried from the UI after reload. The same idempotency key, original action, document input, run and user evidence message are reused. A newer message blocks retry of an older request. Other provider/validation failures keep their existing behavior.
- Backend startup now fails when the database or initial recovery check fails; it no longer announces successful startup with unavailable persistence.

## Contracts and historical records

`ChatThreadDetail.retry_request` is additive and nullable. Existing persisted metadata and version-specific analysis readers remain supported. Known metadata fields have types; legacy trace payloads and extension fields remain explicitly open records. New document requests still use the strict document schema.

Run requests now retain their validated original API input for retry. Older interrupted requests expose a retry only when reconstruction matches their persisted request fingerprint. No new evidence is inferred during recovery.

## Verification commands

From `frontend`:

```powershell
npm run generate:api-types
npm run check:api-types
npx tsc --noEmit
npm run lint
npm run test -- --maxWorkers=2
npm run build
```

Type generation uses `env_mitre` by default. Set `CYBERCASE_PYTHON` to use another compatible backend Python environment. The generator exports local OpenAPI without starting the server or connecting to the database, and writes individual schema modules below 300 lines.

From `backend`:

```powershell
$env:CYBERCASE_TEST_DATABASE_URL = 'postgresql+asyncpg://TEST_USER@127.0.0.1:TEST_PORT/TEST_DATABASE'
..\env_mitre\Scripts\python.exe -m pytest tests -q
```

Recovery tests create and drop a uniquely named schema. Use a disposable database. Without the environment variable, the four PostgreSQL tests skip explicitly. They cover concurrent retries, evidence identity, heartbeat renewal, expired-owner fencing, queued interruptions, superseded requests and the HTTP contract.

The original frontend slice passed synthetic browser QA. The continuation adds hook and real PostgreSQL/API tests; no live LLM, RAG or OCR provider call is part of this verification.

## Final validation receipt

2026-09-05: 351 backend tests and 2 subtests passed, including all four PostgreSQL tests. Frontend: 150 tests across 36 files. TypeScript, full ESLint, generated API drift check, production build, scoped Ruff/format and Git whitespace checks passed. Every changed code file is below 300 physical lines. The disposable PostgreSQL server was stopped after verification.
