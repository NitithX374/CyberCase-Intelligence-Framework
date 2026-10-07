# UI cleanup and component necessity audit

2026-10-07. Scope: simplify end-user analysis UI, remove the remaining retired
extractor integration and proven-unused legacy components/tests, then assess
which parts of the current system are necessary. This continues the batched LLM
view extractor implementation without changing its factual authority or prompts.

The working tree was inspected and snapshotted before edits: branch
`refactor/evidence-unit-grounding`, HEAD `ca7fc6d6`, empty index, 1,361 existing
file hashes. Pre-existing edits and concurrent research work are separate from
this cleanup. No commit, push, live provider request or Case data write was made.
The final manifest records 33 owned paths: 26 modified, 6 removed and 1 added.
There are 1,326 unchanged baseline files and three separate concurrent NLI research
changes. One ignored `.env` key is removed separately; all other bytes are unchanged.

## User-facing changes

- Findings no longer display raw Claim IDs such as `#A-01`. Internal IDs remain
  in anchors, links, citations and backend data; summary reference numbers still
  link to the matching finding.
- The large diagnostic pipeline panel is now a compact, collapsed explanation:
  Sources -> Findings -> Summary and case details. It shows finding/source
  coverage and useful incomplete-result notices, not unit IDs, resolution rates,
  verifier details, model brands, timing/configuration or old admission counters.
- Parties/Timeline/Impacts expose original linked Claim text under a collapsed
  **Related findings** disclosure. **View finding** navigates to the original
  finding without displaying its raw ID. Source filename/page buttons remain.
- Progress messages describe user outcomes rather than schema/model mechanics.
- Unresolved Source warnings, failed extraction, omitted detail notices and
  historical unsupported-description warnings remain visible. A resolved Source
  link is not presented as semantic or factual confirmation.

## Removed code and test surface

The local model loader, runtime, provisioning and Compose service had already
been removed in the preceding implementation. This cleanup removes the remaining
model-specific enum/UI/test branches and unused `CASE_VIEW_HOST_PATH` environment
entry. Metadata now accepts a bounded generic method name, defaulting to `legacy`
for old records without a method. New extraction explicitly records `llm`.
Saved method names remain descriptive data, never a choice of runtime/loader.

Generic ignore patterns still exclude old local model assets from Git and Docker
builds. No model/cache directory was deleted, and encoder/NLI dependencies remain.
Historical research results and dated completion receipts are not rewritten.

| Removed | Why removal is valid |
|---|---|
| `frontend/src/features/analysis/ProjectionReview.tsx` | Its historical-verifier/model/admission display is replaced by a direct, compact Claim-context disclosure; saved caution notes remain in `projectionNote.ts`. |
| `frontend/src/features/analysis/projectionChecks.ts` | Only the removed diagnostics components consumed its reason/status label machinery. |
| `frontend/src/features/analysis/validationSummary.ts` | Only the former diagnostic panel consumed its overlapping citation populations and historical projection counters. Structural metrics remain in the backend trace. |
| `frontend/src/test/features/analysis/ProjectionReview.test.tsx` | Tested the removed display, not a current production verification stage. Current navigation/context/caution behavior retains test coverage. |
| `frontend/src/test/features/analysis/validationSummary.test.ts` | Tested the removed diagnostic aggregation. |
| `frontend/src/test/features/analysis/validationFixtures.ts` | No remaining consumer after those tests and panel-specific tests were removed/replaced. |
| `analysis/write.py::provider_evidence_payload` | Repository search found only a wrapper definition/export and one test consumer. The test now exercises the actual `ReadingSources.source_payload` entrypoint. |
| `view_fields.py::SelectedViewFieldIssue` | A single-use intermediate base from the retired adapter; the compatibility record is flattened without changing its field contract. |
| Frontend `ClaimBacked` metadata duplicates | Model/field-span/projection-verdict duplicates no longer drive UI routing. Original Claim text, Source links and rendered caution notes remain. |

Brand-specific tests are replaced by a generic saved-metadata round-trip test.
It proves that opening a historical trace does not require installing its original
extractor. Strict revision validation and stored Claim spans remain covered.

## Which components are actually needed?

This table uses route/orchestration/caller/persistence evidence, not a blanket
"static unused" report. Conditional or research-only does not mean dead.

| Component | Current consumer / purpose | Assessment |
|---|---|---|
| Source extraction, document/OCR provenance and Source revisions | Source ingestion, Reader, citation resolution, historical runs/reports | Essential. Removing them would break multi-document traceability and stale-run protection. |
| EvidenceUnit segmentation, Reading aliases and deterministic binding | `analysis/write.py` / `reading_sources.py`, `trace/evidence_binding.py`; original offsets/pages resolved by backend | Essential. Hide internal IDs from end users; retain addressing and metrics internally. |
| Reader | Whole-Case canonical Claim construction before both downstream branches | Essential. It owns factual representation across Sources; no per-document summary system is added. |
| Judgement | Summary, gaps and conditional external interpretation from canonical Claims | Essential for the current analysis product. It still excludes derived views. |
| Batched LLM view extractor | Details and deterministic Report presentation | Necessary for the current Parties/Timeline/Impacts UX, but optional relative to canonical factual authority. Future simplification could omit/lazily compute it if those views are no longer required; this is not implemented here. |
| Gap assessment + follow-up decision/history | `analysis/pipeline.py::advance_case`, `analysis/assess.py`, `followup/clarification.py` | Purposeful pre-analysis triage: it can stop expensive analysis to ask material questions. Its gaps overlap conceptually with Judgement gaps, but removing it changes the clarification workflow. Measure that trade-off first. |
| MITRE gate and RAG augmentation | `analysis/technical_context/gate.py` / `retrieve.py`, `rag_service/` | Conditional, not the General Case Summarization core. Retain for explicitly technical behavior; external context never becomes Case evidence. |
| Encoder gate and shadow mode | Configurable alternatives in `technical_context/gate_encoder.py` / `gate.py` | Optional. Not necessary when only the LLM gate is selected and shadow mode is off. There are real configured paths, so this cleanup does not delete them. |
| Generic NLI / quote / OCR-tolerant / meaning recovery | `trace/evidence_binding.py`, `quote_binding.py`, `quotes.py`, `meaning.py`, `nli_model.py`; saved citation compatibility and advisory recovery | Conditional rather than primary. Not needed to resolve valid unit IDs, but still has real recovery/saved-record consumers and regression tests. Retained. |
| Historical projection/field-span/extractor DTOs | Strict saved `CaseAnalysisTrace` parsing and Report rendering | Minimal compatibility data, not active semantic validation or model code. Removing the fields without a migration would make old snapshots unreadable. |
| Single-call provider schema/prompt | `research/analysis_baseline/run.py` imports `CaseProviderAnalysis` and `case_system_prompt` and builds comparison schemas | Research-only production-adjacent debt. Not used by current Reader/Judgement orchestration, but not dead. Candidate for a later move under the experimental boundary, preserving reproducibility. |
| Detailed historical projection diagnostics UI | Former `ProjectionReview`/`projectionChecks`/`validationSummary` | Unnecessary for this end-user flow; removed. Relevant saved caution messages remain. |
| Raw Claim/unit/model IDs, per-row offsets and internal counters in normal UI | Former Finding badge and diagnostics panel | Unnecessary for ordinary case reading; removed from rendered UI. Backend identifiers/provenance/logs remain. |
| Empty MITRE section when augmentation is unavailable/not applicable | `technical-context/TechnicalContextView.tsx` always renders an explanatory section; observed in desktop/mobile QA | Further UI simplification candidate: conditionally hide empty sections for cases where augmentation was never requested, while preserving actual mappings and service-failure notices. Assessed, not changed here. |
| Analysis preparation panel and AnalysisMeta | A compact explanation versus snapshot freshness/document coverage | Some informational overlap. Both currently have a distinct user task; the cleanup reduces the former. Removing it entirely is an optional product decision. |
| Auth/ownership, short transactions, source freshness and idempotency | Case/source/analysis/chat/report routes and services | Essential lifecycle protections, not removable simplification targets. |

The strongest immediate simplification was deleting the local view-extractor
stack and its UI diagnostics, while keeping Claims and deterministic Source
addressing. Remaining model stages should be judged by actual product use and
measured cost/coverage, not removed solely because they are conditional.

## Validation actually obtained

| Check | Result |
|---|---|
| Focused backend | 115 passed. |
| Full native Linux/PostgreSQL suite | 1,157 passed, 1 unchanged route-surface failure, 2 subtests passed, no skips; 7 Torch deprecation warnings. The paused projection evaluation is explicitly excluded. |
| Full frontend | 381 passed across 53 files. |
| TypeScript / generated API freshness / scoped ESLint / Ruff / format / whitespace | Passed. |
| Real rendered UI, mocked read-only API | Chrome/Playwright against `http://localhost:3000`; desktop 1440x1000 and mobile 390x844. Findings IDs hidden; Related findings closed/opened; finding link navigation; Source drawer original text/Page 1; no overflow, blank page, framework overlay, console errors or warnings. |

The Browser plugin was not available; the existing Playwright dependency/system
Chrome was used without installation. All API reads were fulfilled inside the
isolated browser context. No analysis, login, report or Case was written and no
provider was called. These tests do not measure extraction quality or latency.

The sole backend failure is unchanged from the starting tree:
`test_route_surface.py::test_health_case_and_nested_report_api_routes_are_registered`
omits the existing document `/reingest` route from its expected set. The full suite
is therefore not described as entirely passing. Disposable test PostgreSQL,
network and volume were removed after identity/ownership checks; production
service IDs remained unchanged.

The initial frontend run identified an optional historical citation array and a
JSDOM limitation around closed native `details`; the guard/test assertion were
corrected. Browser QA then verified real closed/open behavior. Its initial mock
citation lacked `page_numbers`; the fixture was corrected to match the existing
backend-resolved citation contract, without changing the locator.

Logs, starting hashes, scoped manifest and runtime verification are under
`tmp/ui-cleanup/`. Rendered screenshot evidence is outside the repository under
`C:/Users/kkham/.codex/visualizations/2026/10/07/cybercase-ui-cleanup/`.
