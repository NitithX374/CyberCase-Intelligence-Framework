# Case-first migration and cutover audit

Date: 2026-09-10
Status: completed against the current dirty checkout; no commit, push, or staging performed.
Plan: [`CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md`](CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md)

## Scope and safety boundary

This audit separates the existing Docker database from a disposable populated rehearsal database. The live database was inspected and migrated in place only through the additive application startup migration path. The populated fixture was created in a separately named PostgreSQL database, used to exercise migrations and deletion behavior, and destroyed after validation.

No historical result, evidence source, provenance record, message ID, or snapshot was synthesized for the live database. A legacy value was bound in the rehearsal only when the fixture explicitly supplied the source message, result, snapshot, and evidence hashes. The unresolved legacy report remained unresolved.

## Live Docker PostgreSQL audit

Target: `cybercase-postgres` / `cybercase_framework` / PostgreSQL 16.15

Alembic is at `0010_preserve_chat_reports (head)`. The post-rebuild row counts were:

| Relation | Rows |
| --- | ---: |
| `cases` | 2 |
| `chat_threads` | 2 |
| `chat_messages` | 0 |
| `chat_runs` | 0 |
| `case_documents` | 0 |
| `document_extractions` | 0 |
| `case_evidence_sources` | 0 |
| `case_evidence_revisions` | 0 |
| `case_evidence_snapshots` | 0 |
| `case_runs` | 0 |
| `case_analysis_results` | 0 |
| `case_clarifications` | 0 |
| `chat_reports` | 0 |

The invariant query returned zero violations for: Case/Chat identity pairing, CaseRun and snapshot ownership, result/run/snapshot ownership, report Case/result/snapshot ownership, analysis-message result links, active Case and legacy Chat runs, Case latest-result pointer consistency, and duplicate analysis publications.

The live policy constraints were verified directly from PostgreSQL:

- `chat_reports.analysis_result_id` references `case_analysis_results` with `ON DELETE RESTRICT`.
- `chat_reports.evidence_snapshot_id` references `case_evidence_snapshots` with `ON DELETE RESTRICT`.
- `chat_reports.case_id` references `cases` with `ON DELETE CASCADE`.
- `chat_reports.thread_id` references `chat_threads` with `ON DELETE SET NULL`.
- `ux_case_runs_one_active_per_case` is a partial unique index for `status IN ('queued', 'running')`.

## Populated disposable migration rehearsal

Disposable database: `cybercase_casefirst_audit_20260910`. It was upgraded from `0001_raw_evidence_chat` through `0010_preserve_chat_reports` using the backend Alembic entrypoint and then dropped. A synthetic fixture contained one Case, its shared-ID ChatThread, one user message, one immutable Case snapshot, one completed CaseRun, one validated CaseAnalysisResult, one linked analysis-result assistant message, and two pre-0009 ChatReports.

The migration preserved both report IDs and both frozen report hashes. It established Case/result/snapshot bindings for the report whose analysis publication supplied a provable mapping. The ordinary-message report received a Case binding but retained a null `analysis_result_id` and was reported as unresolved rather than guessed.

| Rehearsal assertion | Result |
| --- | ---: |
| Reports before/after migration | 2 / 2 |
| Case-bound reports | 2 |
| Proven result bindings | 1 |
| Proven snapshot bindings | 1 |
| Unresolved result bindings | 1 |
| Preserved report IDs/hashes | 2 / 2 |
| Analysis publications | 1 |
| Case/result/snapshot orphan rows | 0 / 0 / 0 |

Deleting the optional ChatThread in the same disposable database left one Case, two reports, one result, and one snapshot. Both reports had `thread_id = NULL`; the one analysis-publication linkage had `analysis_message_id = NULL` while its result binding remained. The disposable database was then dropped and is absent from `pg_database`.

## PostgreSQL concurrency and synthetic workflow evidence

Against the real Docker PostgreSQL service, the isolated-schema Case-first tests passed `13 passed` after the rebuild. They cover concurrent evidence admission under the Case lock, concurrent same-key analysis enqueue, active-run conflict, pinned snapshot execution, atomic result/publication rollback, lease fencing, recovery, lazy Chat publication, clarification idempotency, and result/snapshot-bound report PDF generation. The complete backend verification cycle reported `450 passed, 1 skipped, 2 subtests passed` with one upstream Starlette/httpx deprecation warning.

The deterministic workflow tests use fake analysis output and synthetic evidence. They do not claim semantic quality or a paid-provider end-to-end result. No changes were made under `rag_service/**`.

## Runtime and cutover evidence

The four-service Compose stack was rebuilt and recreated with:

```powershell
doppler run --project env_cybercase_framework --config dev -- docker compose -p cybercaseframework up -d --build --force-recreate
```

Post-rebuild, PostgreSQL was healthy, backend `/api/v1/health` returned 200 with `database: connected`, frontend `/case/{case_id}/overview` returned 200, and RAG `/health` returned 200 after its normal BGE-M3 cold start. `docker exec cybercase-backend alembic upgrade head` completed successfully and remained at `0010_preserve_chat_reports`.

The authenticated browser smoke required by the plan was not completed: the available in-app browser and Edge connector had no signed-in session, so navigation redirected to `/login`. This is an environment limitation, not a passing UI assertion. Production build, route registration, frontend tests, and unauthenticated HTTP route checks do not replace that missing authenticated Case-first interaction smoke.

## Cutover limitations

- The live database contains no native historical analysis/result/report rows, so no historical backfill coverage can be claimed from it.
- No backup/restore drill or production maintenance-window drain was performed; this remains an operator cutover responsibility.
- No paid provider call was made for this cutover, and no semantic analysis-accuracy evaluation was performed.
- Full frontend lint still reports two pre-existing unrelated errors and one warning; the scoped Case-first lint passed.
- The frontend intentionally has no history/version selector, as required; historical state remains database/API-owned.
