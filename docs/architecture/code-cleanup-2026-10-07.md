# Function and legacy-code cleanup — 2026-10-07

This cleanup works on `main` at `34a948c2451e0674e2443d8366beb36b9cad0b8e`,
including the previously approved, uncommitted Finding traceability UI. It removes
unused implementation paths and consolidates repeated logic in the current system.
The existing Case, Source, Claim, Judgement and report contracts remain in place.

## Inspection coverage and deletion rule

| Starting area | Code files inventoried | Functions/methods inventoried |
| --- | ---: | ---: |
| `backend/app/` | 107 | 530 Python definitions |
| `rag_service/app/` | 70 | 523 Python definitions, including offline evaluation and report tooling |
| `frontend/src/` | 177 TypeScript files, including tests and generated types | 1,684 function bodies, including callbacks and tests |

Python AST inventories, repository-wide code references, imports, decorators,
string references, tests, CLI entrypoints and package exports generated candidates.
The frontend uses the installed TypeScript resolver/type checker to follow imports
from every App Router entrypoint, including type imports and dynamic imports.
Research scripts were included when checking consumers. All inventoried Python
files parsed successfully.

Candidates were inspected against actual consumers before deletion. Functions
called by their own module are used; framework routes, Pydantic validators,
protocol methods, package exports and CLI tools do not require an ordinary direct
call to be necessary. A second code-only reference pass prevented documentation
mentions from being mistaken for executable consumers.

This is a whole-source inventory and a caller/flow review of cleanup candidates,
not a proof of every function's semantic correctness. External scripts outside
this repository are outside the inspected consumer set.

## Removed files

| Removed file | Consumer evidence |
| --- | --- |
| `backend/app/analysis/view_model.py` | The GLiNER loader had no analysis caller. Its only importer was its weight provisioner; `analysis/views.py` now calls the configured LLM directly. |
| `backend/scripts/copy_case_view_weights.py` | Provisioned only that retired loader. No current script, service or test invokes it. |
| `frontend/src/features/analysis/ProjectionReview.tsx` | No App Router or production component reaches it. Only its dedicated test imported it. It also referenced fields removed from `ClaimBacked`, causing six TypeScript errors. |
| `frontend/src/features/analysis/projectionChecks.ts` | Consumers were the retired component, retired diagnostics aggregation and their test. |
| `frontend/src/features/analysis/validationSummary.ts` | Only its dedicated test imported it. Current traceability presentation uses saved Source linkage without implying a current projection verifier. |
| `frontend/src/test/features/analysis/ProjectionReview.test.tsx` | Tested the retired diagnostic component. Active related-Finding navigation and historical caution-note tests remain. |
| `frontend/src/test/features/analysis/validationSummary.test.ts` | Tested only the retired aggregation. |
| `frontend/src/test/features/analysis/validationFixtures.ts` | Only the removed aggregation test used its fixture. |
| `rag_service/app/RAG/GraphRAG/pipeline/chain.py` | No service, CLI, package export or current evaluation adapter imports `GraphRAGChain`. `eval_runner._make_generation_fn` uses `GraphRAGAgent`; current cross-lingual experiments implement their own variants. Only a chain-specific content test remained. |

The chain-specific test and its unused `StubRouter` were removed from
`rag_service/tests/test_llm_content.py`. Both tests that enumerate pipeline files
were updated to retain their guards over the remaining modules. Current generation
and translation experiments, datasets and recorded results are retained. Their
documentation now identifies the chain as retired.

## Removed functions and unused interfaces

The following RAG methods had only their definitions in executable repository
references, including tests, scripts and CLI code:

- `StixParser.get_entities_by_label`
- `StixParser.get_relationships_by_label`
- `GraphRetriever.get_multi_hop_path`
- `GraphRAGResult.get_context_text`

The served path still uses the existing graph expansion, technique catalogue and
`build_context` formatter. No new retrieval path replaces these unused helpers.

`model_registry.list_available_models` also had no caller. Its unused display-name
and description fields were removed from the internal preset records; aliases,
canonical IDs, defaults, family names and the CLI table remain. The alias map is
now one comprehension rather than two imperative loops.

Seven frontend values used only inside their defining module are now private:
`formatPageReference`, `FindingRow`, `STREAM_IDLE_TIMEOUT_MS`,
`stripInlineCitations`, `LEGAL_DISCLAIMER`, `sortCases` and `CaseStatus`.
Their implementations and rendered behavior remain. The final frontend graph has
111 reachable production files, no unreachable production files and no unused
value exports under the examined feature/component/library scope. Generated API
types and framework exports are excluded from that unused-value decision.

## Simplified active code

| Area | Change and retained behavior |
| --- | --- |
| OCR retry | One retry/log/backoff path replaces repeated branches. Timeout, terminal HTTP, transient HTTP, transport and JSON-decode failures retain their classifications, bounded attempts, exponential delays and exception causes. An impossible exhausted-loop state raises explicitly. |
| RAG evaluator response parsing | JSON candidate extraction feeds one `EvaluationResult` construction. Fenced and nested responses retain existing behavior. Invalid candidates are logged at debug level rather than caught with `pass`. The existing unparseable/unknown-verdict policy is preserved; this cleanup does not introduce a new admission policy. |
| RAG shutdown | `try/finally` attempts both graph and vector client closure. Shutdown exceptions are visible; the old empty catch hid vector-close failures and a graph-close failure prevented vector cleanup. |
| Qdrant identifiers | UUID parsing and deterministic historical MD5-derived IDs share one return path. Golden values taken from the starting implementation prove that existing identifiers do not change. |
| Ingestion/retrieval | Dictionary iteration replaces `.keys()` where only keys are needed. Guarded attribute access replaces constant `getattr`. Ambiguous variable names and redundant literal f-strings are cleaned up. |
| Config/dependencies | Retired GLiNER settings, its requirement and Compose environment/mount are removed. Torch/Transformers remain for active encoder/NLI consumers. Config imports are ordered without changing provider selection. |
| Tests | The existing RAG-response test now imports `ValidationError`, so it actually verifies rejection of an unknown evidence basis. OCR test imports are consolidated. |

Axios already owns ordinary HTTP requests through `frontend/src/lib/api/http.ts`.
The existing `Promise.all` calls refresh independent TanStack Query caches in
parallel. They are not HTTP client implementations and remain appropriate.
Streaming requests retain the existing fetch/reader path, heartbeat handling,
idle timeout and Axios-compatible error boundary.

## Kept because they have consumers

- Source identity, revisions, deterministic units/aliases, document/page offsets,
  OCR quality provenance, follow-up `QA-*` sources and multi-document binding.
- Quote locating, tolerant matching, nearest passages, advisory NLI meaning
  pointers and historical citation schemas. These still have runtime and saved
  analysis consumers; legacy status alone is not deletion evidence.
- Historical projection/extractor DTOs and caution notes, which keep stored
  analyses and reports readable. Removing an unused display does not remove
  these records.
- The configured LLM Claim-view extractor, canonical Claims-only Judgement/chat,
  lifecycle/ownership/idempotency checks and short database transactions.
- Conditional MITRE/RAG augmentation, the encoder gate, public offline query
  helpers, CLI and current translation/evaluation adapters.
- Research-only provider contracts, paused experiments, report-authoring tools,
  model assets, caches, migrations and existing result artifacts.

No Claim semantic verifier, confidence score, projection admission rule, source
database migration or new library is introduced.

## Validation obtained

| Check | Result |
| --- | --- |
| Full backend on native Linux with isolated PostgreSQL | 1,174 passed, 2 subtests passed, no skips; 7 existing Torch deprecation warnings. Includes the real pinned legacy-NLI smoke test. |
| Focused host backend checks | 53 passed, 2 subtests passed, covering OCR retries, RAG-response mapping and current/historical view paths. |
| Full frontend | 395 passed across 56 files. The initial tree had 404 passing tests; nine tests tied to the removed components were retired. |
| Full RAG, native image and no network | 178 passed, no skips; one existing Starlette/AnyIO deprecation warning. |
| TypeScript | Passed. The six initial ProjectionReview errors are eliminated. |
| Backend Ruff, `app` and `tests` | Passed. |
| RAG runtime Ruff | Passed over `app`, excluding offline `evaluation` and document-authoring `docs`. Touched RAG tests also pass. |
| Frontend full ESLint / scoped Prettier | Passed. |
| Generated API freshness / Compose config / diff whitespace | Passed. |
| Rendered Chrome via existing Playwright | Desktop 1440×1000 and mobile 390×844; original passages, cross-document drawer navigation, status filters, Escape/focus, no overflow, framework overlay, console errors or warnings. |
| Running backend | Health reports `ok`, database `connected`. |

The initial full backend run exposed the pre-existing missing `ValidationError`
import. It was fixed and the entire suite rerun. After chain deletion, one
provider-factory guard still enumerated `chain.py`; that stale filename was removed
and the full RAG suite rerun. No failing guard was discarded.

The browser uses synthetic GET-only fixtures rather than user Case writes.
Backend tests use a separately created test database/network, removed afterward.
Production service identities/images are unchanged. No live LLM/OCR/provider or
external graph/vector writes were issued by the test harnesses. The running image
is not rebuilt to uninstall packages; the cleaned requirements apply to future
builds. These checks establish regression compatibility, not semantic accuracy or
a measured latency improvement.

## Changed-file groups

- Backend: `app/config.py`, `app/sources/ingestion/recognition.py`,
  `requirements-encoder.txt`, `tests/test_chat_rag_client.py`,
  `tests/test_document_ingestion_typhoon.py`; new
  `tests/test_document_recognition_retry.py`.
- Frontend: `src/features/analysis/CaseFindingsSection.tsx`,
  `src/features/citations/sourceRefs.ts`, `src/features/cases/CaseCard.tsx`,
  `src/features/cases/caseDisplay.ts`, `src/features/chat/ChatTranscript.tsx`,
  `src/features/legal/legalReference.ts`, `src/lib/api/stream.ts`.
- RAG: `app/RAG/GraphRAG/config.py`, `model_registry.py`,
  `ingestion/graph_loader.py`, `ingestion/stix_parser.py`,
  `ingestion/vector_loader.py`, `pipeline/cross_lingual.py`,
  `pipeline/evaluator.py`, `retrieval/graph_retriever.py`,
  `retrieval/hybrid_retriever.py`, `retrieval/reranker.py`,
  `retrieval/vector_retriever.py`, `tests/test_core_llm_provider.py`,
  `tests/test_llm_content.py`; new `tests/test_retriever_lifecycle.py`,
  `tests/test_evaluator_response.py`, `tests/test_ingestion_identifiers.py`.
- Documentation/deployment: `CLAUDE.md`, `docker-compose.yml`, this report,
  and only the docstring of
  `rag_service/app/RAG/GraphRAG/evaluation/crosslingual_generation_benchmark.py`.
- The nine deleted paths are listed above. `CONTINUITY.md` is an ignored
  workspace briefing, updated separately.

Receipts, starting hashes and inventories are in `tmp/code-cleanup/`.
Browser screenshots/JSON are outside the repository in
`C:/Users/kkham/.codex/visualizations/2026/10/07/cybercase-code-cleanup/`.
The pre-existing traceability changes and read-only sanity-check report are
preserved. The branch remains `main`; nothing is staged or published.

The final scope receipt records 42 cleanup paths: 28 modified, nine removed and
five added. Of 1,393 starting file hashes, 1,356 are unchanged. Seventeen of the
19 pre-existing traceability paths are byte-for-byte unchanged; the other two
only lose unused value exports. The concurrent AttributionBench audit report
is excluded from this cleanup and preserved separately. `scopedmanifest.json`
records individual before/after hashes; `verification.json` records the scope,
service identities, empty index and completed checks.
