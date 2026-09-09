# Codebase cleanup audit — 2026-09-08

## Scope and evidence

Read-only code audit of local main at b21b74c, including the uncommitted attribute-first implementation. No source files deleted, merged, staged, or committed. Remote parity was not checked. Inventory: 144 Python files under backend/app; 142 TS/TSX files under frontend/src including tests/generated types; 61 Python files under rag_service/app including evaluation tools. Research and evaluation references were searched when judging retirement candidates.

Method: Git baseline, physical line counts, Python AST symbol definitions, repository reference searches, route and package-export inspection, frontend consumers, evaluation entrypoints and test references. Absence of references is static evidence, not proof about external consumers. No database inventory, runtime coverage, build, or test suite was run for this audit. Ruff F401/F811 ran and reported the three unused imports below.

## A. Small cleanup candidates — high confidence within this checkout

| Candidate | Evidence | Proposed action and validation |
|---|---|---|
| backend/app/services/case_analysis/case_analysis_prompt_builder.py:232 `_bounded_json` | Only definition found; absent from exports. Its `maximum` argument is ignored. Active overflow builder has separate callers. | Delete this wrapper only; retain active budgeting. Run context-budgeting and analysis tests. |
| backend/app/services/followup/helpers.py:88,101,108 `_required_material_gap`, `_required_gap_question`, `_selected_askable_gap` | AST scan and repository symbol search found definitions only, including no test callers. | Remove these obsolete selection/question helpers; keep current decision/stateful paths. Run follow-up/stateful tests. |
| backend/app/services/document_ingestion/errors.py:47–59 four Segmentation*Error subclasses | Configuration, timeout, provider and response subclasses have no references. | Remove unused subclasses. KEEP DocumentSegmentationError: region_pipeline catches it. Run segmentation/routing tests. |
| frontend/package.json:17 `@xyflow/react` | Dependency declaration found, no application/test import or stylesheet reference found. | Remove with package manager and regenerate lockfile; run build and frontend tests. |
| frontend/public/cybercase-legacy-favicon.ico | No repository reference; root layout metadata uses cybercase-mark.png. | Remove obsolete asset if retaining its public URL is unnecessary. Check rendered favicon; external bookmarks were not inspected. |
| Three unused imports | Ruff: prompt_builder.py:6 settings; followup/context.py:7 settings and :11 estimate_tokens. | Remove imports, rerun Ruff. Do not remove the shared token estimator implementation. |

## B. Retire or migrate deliberately

1. **rag_service/app/RAG/GraphRAG/pipeline/chain.py**: GraphRAGChain has no discovered current production or evaluation caller; test_llm_content.py:208 still imports it. Its header claims eval_runner and crosslingual_benchmark need it, but eval_runner.py:267 now builds GraphRAGAgent and crosslingual benchmarks use CrossLingualLayer directly. Candidate to retire with its chain-specific test and stale documentation. Do not delete cross_lingual.py: agent_graph uses its static methods and benchmarks instantiate it. RAG changes should be a separate scoped batch.
2. **frontend/src/lib/case-overview-legacy.ts** and legacy AnalysisTrace contracts: active historical-data readers, not dead code. case-overview.ts selects the v2 reader; case-overview.test.ts explicitly verifies it; backend read_analysis_trace accepts both versions. Retirement requires inspecting persisted trace versions and migrating or deliberately retiring old records. Not necessary before OAuth.
3. **Follow-up compatibility**: helpers._invoke_policy_method, schemas.accept_legacy_action_shape and gap_stage's compatibility_skipped path still support injected custom policies/tests. Modernize the policy contract and callers together before removing. Do not bundle this behavioral change into dead-helper deletion.
4. **Research/evaluation/document scripts**: no application import is expected for CLI tools. Preserve experiment artifacts and entrypoints unless the research owner retires them. No blanket deletion of research/, evaluation/, migrations, or deliverables.

## C. File consolidation candidates

Counts are current physical lines added together before removing duplicate imports; they are not promised final sizes.

| Priority | Files | Combined upper estimate | Rationale / cost |
|---|---|---:|---|
| 1 | frontend/src/components/evidence/HighlightedEvidenceText.tsx + SourceEvidenceContent.tsx | 65 | High-confidence local merge: highlighter has one importing module. Keep SourceEvidenceContent exported for both drawer and popover. Verify literal quote highlighting and page display. |
| 2 | backend/app/services/case_analysis/response_identifiers.py + case_analysis_response_parser.py | 183 | Identifier normalization is specific to this parser; only other caller found is its boundary test. Move helper into parser and update test import. Keep parser entrypoint stable. |
| 3 | backend/app/services/reports/report_finding_projection.py + report_review_projection.py | 195 | Optional domain grouping of findings, unresolved issues and verification actions; builder uses both. Update imports and preserve output. Weaker benefit than the first two because responsibilities are separable. |

Do not merge merely because a module is small: pipeline.py is dependency composition; chat_run_store.py is a stable worker facade; api.ts is an API barrel; generated TS files belong to code generation; Next page.tsx files register routes; segmentation/base.py is the interface consumed by service/implementations. ClaimAnchoredFailure and source_registry remain explicit failure/provenance boundaries. Merging citation_contracts back into contracts would bring that file to roughly 326 lines. Existing PDF design helpers are already consolidated into pdf_design.py; do not recreate the retired font/theme files.

## D. Files that need splitting instead

| File | Physical lines | Proposed boundary |
|---|---:|---|
| backend/app/services/case_analysis/case_analysis_prompt_config.py | 339 | Separate prompt text by mode from failure/config definitions; keep imports stable. Includes prompt strings, not 339 executable statements. |
| backend/app/services/reports/report_pdf_story.py | 321 | Move provenance section builder (starts at 275) into a presentation helper; retain public story builder. |
| frontend/src/components/home/HomeSections.tsx | 399 | Split independent home sections. |
| frontend/src/components/ChatWorkspaceLayout.tsx | 340 | Split layout chrome/panels without moving session orchestration into presentation. |
| rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py | 782 | Later RAG-specific refactor: separate node implementations from graph wiring. Active production code. |

Other large RAG files include ingestion/stix_parser.py (467), pipeline/evaluator.py (370), evaluation/generate_eval_dataset.py (1726), and evaluation/crosslingual_generation_benchmark.py (922). These are maintainability candidates, not evidence of dead code. One frontend test file is also over 300 lines (ChatReportView.test.tsx, 329).

## E. Documentation drift

rag_service/ARCHITECTURE.md still describes use_agent=False routing into GraphRAGChain (83,98) and loading old ReportGenerator/chain components (269). chain.py's retirement rationale is also stale. Update these to traced runtime behavior; do not use the old diagrams as deletion evidence.

## Suggested order before authentication

1. Review/save the current attribute-first diff as its own change.
2. Small cleanup batch A, plus consolidation C1/C2 if desired.
3. Split the backend/frontend files above 300 lines as a distinct structural batch.
4. Implement authentication and ownership with a stable chat/report access boundary.
5. Keep RAG retirement, legacy data migration and custom-policy redesign separate; none is a prerequisite for login.

No broad rewrite is justified by this audit. Current findings support a small verified cleanup and a few scoped structural changes.
