# Batched LLM-derived case views

Completion report, 2026-10-07. The implementation replaces the operationally
undesirable local extractor with one structured provider stage. Canonical Claims
remain the factual objects used by downstream analysis; Parties, Timeline and
Impacts are presentation views with Claim references.

## Inspected baseline and authority boundary

The fetched `origin/main` was `53fc4bcfdcc7fbd49557a0d6233687e5eca86afc`.
That version used GLiNER2. The current working tree, on
`refactor/evidence-unit-grounding` at `ca7fc6d6`, already contained the completed
Claims-only Reader and a local NuExtract3 replacement. Work proceeded against
that working tree without checking out, resetting, merging or publishing it.
The pre-existing compact Reader change was preserved.

Current production binding deterministically resolves Source unit references.
It does **not** semantically verify that the resolved content entails each Claim.
There is no production Claim-verification admission stage here. Consequently,
both new downstream branches receive exactly the canonical Claim set already
supplied to Judgement, including Claims with unresolved references. This task
introduces no independent Claim admission rule. Generic pinned NLI remains only
in the existing legacy advisory recovery path; the research experiment is separate.

## Before and after

Before, in the inspected working tree:

```text
Case -> N Sources / answered follow-ups -> Reader -> deterministic binding
                                                      |
                                              canonical Claims
                                                      |
                     supported-citation subset -> local NuExtract3, per Claim
                                                      |
                                          Parties / Timeline / Impacts
                                                      |
                                      Judgement, over all canonical Claims
                                                      |
                                            joined saved analysis
```

The local extraction happened before Judgement but its views were already
excluded from Judgement input. Main had the same factual isolation with GLiNER2.

After:

```text
Case -> N Sources / answered follow-ups -> Reader -> deterministic binding
                                                      |
                                              canonical Claims
                                             /                \
                          one batched structured call        Judgement
                                  |                             |
                      Parties / Timeline / Impacts       Summary / Gaps / MITRE
                                  \                            /
                                     joined saved analysis
                                              |
                                         UI / Report

Derived row -> claim_ids -> Claim -> Source unit -> original Source / page
```

Extraction and Judgement run concurrently and independently. Neither branch
consumes the other's output. MITRE remains conditional external interpretation.
The editable [architecture diagram](evidence-unit-grounding.drawio) and the
[Source/Claim contract](evidence-unit-grounding.md) have been updated.

## Request and exact extraction schema

The stable async entrypoint is `derive_claim_views(claims, *, config)`. It sends
only one compact Claim batch:

```json
{
  "claims": [
    {
      "claim_id": "A-01",
      "text": "Alice transferred $500 to Company A on 12 May 2026."
    }
  ]
}
```

No Source text, Source IDs, offsets, hashes, unit metadata, MITRE context or
Judgement output is supplied. The existing native-schema provider abstraction
receives the configured analysis model/provider with extraction-only settings:
temperature 0, thinking disabled, visible output at most 4,096 tokens and an
overall extraction deadline at most 60 seconds. Existing transport retries stay
inside that deadline. This is one batched stage, not one stage per Claim;
transport retries may still produce additional HTTP attempts. Reading and
Judgement settings are unchanged.

`view_schema.py` reuses the existing provider row bases. Every key shown below
is required; nullable fields must be present with `null` when unavailable.
Additional fields are forbidden.

| Model | Fields and constraints |
|---|---|
| `DerivedParty` | `name: str` (1-500 chars); `role: str \| None` (1-500 chars when present); `claim_ids: list[str]` (1-64 entries) |
| `DerivedTimelineEvent` | `time: str \| None` (1-500 chars when present); `event: str` (1-2,000 chars); `claim_ids: list[str]` (1-64 entries) |
| `DerivedImpact` | `description: str` (1-2,000 chars); `claim_ids: list[str]` (1-64 entries) |
| `DerivedCaseViewsReply` | `parties`, `timeline`, `impacts`: required arrays, each containing at most 64 corresponding rows |

Text fields are trimmed and whitespace-only values fail validation. Public
`claim_ids` is retained instead of adding a duplicate `source_claim_ids` field.
The existing `time` field holds the original explicitly stated date and/or clock
expression; no separate `date` field or normalization is introduced.

Example valid reply:

```json
{
  "parties": [
    {"name": "Alice", "role": null, "claim_ids": ["A-01"]},
    {"name": "Company A", "role": null, "claim_ids": ["A-01"]}
  ],
  "timeline": [
    {
      "time": "12 May 2026",
      "event": "Alice transferred $500 to Company A.",
      "claim_ids": ["A-01"]
    }
  ],
  "impacts": []
}
```

A transfer alone does not establish a loss. The prompt requires explicit facts,
attribution and uncertainty, prohibits inferred actor/legal roles, and does not
merge similar Thai names or aliases without an explicit Claim equivalence.
These are generation instructions, not a measured semantic guarantee.

## Validation, failure and cancellation

Schema parsing, required/nonempty fields and known Claim IDs are checked.
If any Claim ID in a row is unknown, the **whole row** is dropped and logged;
valid neighboring rows survive. Duplicate links are deduplicated in first-seen
order. `view_extraction.items_dropped` records rejected rows.

The backend attaches the existing structural `support` field:

| State | Exact meaning |
|---|---|
| `bound` | Every linked Claim has at least one resolved supporting citation. |
| `mixed` | Some linked Claims have resolved supporting citations. |
| `unbound` | None of the linked Claims has resolved supporting citations. |
| `no_claim` | No known Claim is linked; retained for historical records, not emitted by the new extractor. |

These states do not establish semantic support for a role, time, event or impact.
New rows have no fabricated field offsets or semantic projection verdict. Tests
explicitly demonstrate that an incorrect role returned with valid Claim IDs is
not semantically detected by this structural validator.

Provider/schema/timeout failures return all three empty view arrays, save
`status="failed"` and a warning code, and log the error. Judgement continues
independently. Empty Claim sets skip extraction with `status="skipped"`.
Successful extraction records `status="completed"`, input Claim IDs, model,
elapsed time and drop count. No local or second-model fallback is run.

Judgement failure or caller cancellation cancels and awaits outstanding extraction
before propagating the original failure. There are no orphan extraction tasks.
The final snapshot waits for both branches; its latency includes whichever takes
longer after binding. Actual provider latency and quality were not measured here.

## UI, report and persistence

Existing Parties/Timeline/Impacts sections and React Query ownership are retained.
Rows expose their linked Claim text and existing Claim-to-Source references.
The pipeline panel shows extraction status, elapsed time and invalid-ID drops;
failed extraction is visible. A null timeline time is displayed as not extracted,
not as proof that no date exists in the Claim.

Reports render derived rows directly from the saved analysis, separately from
Judgement's summary. Report generation invokes no extractor. New spanless Party
rows retain linked Claim context. Historical GLiNER/NuExtract metadata, field spans
and old semantic check records remain readable. No historical snapshot is rewritten.

The existing analysis JSON snapshot and Source/run revisions are reused. Reopening
an analysis or generating its report does not re-extract. A fresh analysis still
re-runs extraction; no new cross-analysis cache, revision system or table is added.

## Removed local implementation and dependencies

Removed local model loading, checkpoint/template checks, per-Claim inference,
field-string recovery and weight provisioning modules listed below. Compose no
longer defines the local `case-views` service, its backend dependency or weight
mount. `CASE_VIEW_MODEL_PATH`, `CASE_VIEW_SERVER_URL`, `CASE_VIEW_DEVICE` and
`CASE_VIEW_TIMEOUT_SECONDS` settings/environment entries were removed.

The starting working tree had already removed GLiNER/PEFT runtime requirements;
no additional package dependency change was needed in this task. Torch and
Transformers remain for generic NLI and encoder use. Source segmentation and
legacy quote/meaning recovery were not removed. No weight/image storage cleanup
was performed; the former local runtime is no longer running.

## Scoped files

This is the task delta against the starting working-tree hashes, not the larger
pre-existing Git diff. There are 35 modified files, five new files and eight
removed files. Concurrent NLI research additions are excluded.

| Change | Files |
|---|---|
| New extractor schema | `backend/app/analysis/view_schema.py` |
| New test helpers/transport/legacy tests | `backend/tests/case_view_test_support.py`, `backend/tests/test_case_view_provider.py`, `backend/tests/test_case_view_legacy.py` |
| New completion report | `docs/architecture/llm-derived-case-views.md` |
| Extractor/orchestration | `backend/app/analysis/view_prompt.py`, `backend/app/analysis/views.py`, `backend/app/analysis/write.py` |
| Config/metadata | `backend/app/config.py`, `backend/app/llm/settings.py`, `backend/app/trace/view_fields.py`, `backend/app/trace/trace.py`, `docker-compose.yml` |
| Report | `backend/app/reports/display.py`, `backend/app/reports/schemas.py`, `backend/app/reports/templates/case_report.html.j2` |
| Backend tests | `backend/tests/conftest.py`, `backend/tests/fake_case_views.py`, `backend/tests/test_claim_views.py`, `backend/tests/test_case_view_pipeline.py`, `backend/tests/test_case_workflow_http_postgres.py` |
| Frontend | `frontend/src/features/analysis/AnalysisPipeline.tsx`, `ProjectionReview.tsx`, `validationSummary.ts`, `types.ts`, `overview.ts`, `CaseDetails.tsx`, `progress.ts` (all seven under that same directory) |
| Generated API | `frontend/src/lib/api/generated/openapi.ts` |
| Frontend tests | `frontend/src/test/features/analysis/AnalysisPipeline.test.tsx`, `ClaimViewReview.test.tsx`, `overview.test.ts`, `AnalysisLayout.test.tsx`, `AnalysisProgress.test.tsx` (all five under that same directory) |
| Existing docs | `CLAUDE.md`, `backend/ARCHITECTURE.md`, `backend/README.md`, `frontend/README.md`, `docs/architecture/evidence-unit-grounding.md`, `docs/architecture/evidence-unit-grounding.drawio` |
| Removed local runtime | `backend/app/analysis/view_checkpoint.py`, `view_model.py`, `view_records.py`, `view_runtime.py` (all four under that same directory), `backend/scripts/copy_case_view_weights.py` |
| Removed obsolete local tests | `backend/tests/test_case_view_model.py`, `test_case_view_provisioning.py`, `test_nuextract_records.py` (all three under that same directory) |

## Tests and runtime verification

All new unit/provider/pipeline tests use mocked replies or HTTPX MockTransport;
no live model API request was made. Tests cover basic extraction, null role/time,
no mocked loss for mere risk, valid/multiple Claim links, invalid-row drops,
duplicate links, strict schema, Thai aliases, unresolved Claims, failure logging,
deadline/cancellation, concurrency and legacy saved records.

| Check | Actual result |
|---|---|
| Focused backend regression | 156 passed. |
| Full native Linux/PostgreSQL backend suite | 1,158 passed, 1 existing unrelated failure, 2 subtests passed, no skips. Seven Torch deprecation warnings. |
| Frontend analysis/report tests | 209 passed across 26 files. Final affected rerun: 63 passed across five files; counts overlap. |
| TypeScript, generated API freshness, scoped ESLint/Ruff/format, Git whitespace | Passed. |
| Active backend mocked whole-case/report smoke | Success and schema-failure conditions both complete Judgement and render a three-page PDF. Two documents, answered QA, cross-document Claim and page-2 provenance pass; three direct references resolve. Zero live provider calls or Case writes. |

Full backend command, in an isolated disposable PostgreSQL/Linux environment:

```text
python -m pytest tests -q --tb=short -p no:cacheprovider --ignore=tests/test_projection_evaluation.py
```

The paused projection experiment is explicitly excluded, unchanged. The sole
failure is `test_route_surface.py::test_health_case_and_nested_report_api_routes_are_registered`:
its expected route set omits the already-existing document `/reingest` endpoint.
Both route code and that test match their pre-task hashes. The full suite is not
reported as entirely passing. A legacy HTTP test double was updated to accept
the already-existing Reader adapter keyword; old quote tests remain and pass.

The backend was rebuilt/recreated with the new code. Health is `ok`, database
`connected`; other frontend/RAG/PostgreSQL container IDs and interpolated
environment values were preserved. Reading retains its 8,192 thinking budget.
The former local extractor was stopped during activation; its service and
mount/config are absent from the active backend. The prior image has a rollback tag.

Detailed logs, starting hashes, runtime smoke and scoped verification receipts
are under `tmp/llm-case-views/`. No commit or push was performed.

## Remaining limitations and technical debt

- Contract tests prove transport, structural traceability and isolation; mocked
  responses do not establish real Thai/English extraction quality or latency.
- Valid Claim IDs and `bound` cannot detect invented roles, incorrect pairings,
  unsupported impacts or Claim-level errors. No semantic view verifier is added.
- One additional provider stage introduces remote cost/rate-limit exposure.
  The 4,096-token cap may be insufficient for unusually dense Cases; rejection
  remains explicit, without silently creating partial fallback facts.
- Reading/Judgement provider model selection is reused, not a new pinned local
  checkpoint. Existing source-integrity semantics remain unchanged.
- Reports use derived views directly, so extraction mistakes can be displayed
  there even though these views cannot contaminate Judgement's input.
- New extraction preserves Claim links, not independently recovered exact field
  spans. Historical exact field spans remain available only on older snapshots.
- No cross-analysis extraction cache or alias/coreference resolution is added.
- The unrelated route-surface test failure remains outside this task.
