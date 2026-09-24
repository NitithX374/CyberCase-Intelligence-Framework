# Backend Model Configuration Consolidation Design

## Goal

Make backend Case Analysis use one configured OpenRouter model for its model-backed operations, while keeping environment settings distinct from the versioned configuration snapshot persisted with each analysis.

The selected model is `qwen/qwen3.8-27b:free`. `CASE_ANALYSIS_MODEL` is the only backend environment setting that selects this model.

## Scope

This change covers backend model selection, its OpenRouter registry/default resolution, the analysis pipeline snapshot builder/reader, the MITRE applicability gate, backend Compose environment, focused tests, and the direct diagnostic consumer of backend settings.

The one selected model applies to:

- Main Case Analysis.
- Chat answers generated from a case analysis.
- The LLM-based MITRE applicability gate when that gate mode is selected.

This change does not:

- Modify `rag_service/**` or its model configuration. RAG is a separate service with a separate model lifecycle.
- Change the specialized OCR model setting.
- Redesign research experiments; only update the diagnostic harness that directly reads the removed backend selector.
- Change provider credentials, URLs, timeouts, prompts, routes, response contracts, or analysis semantics.
- Change persisted pipeline JSON shape, analysis tables, migrations, or historical analysis records.
- Perform the broader backend route/data-model refactor.

## Current behavior

- `Settings.case_analysis_model` is environment-backed, but its current code default is `qwen/qwen3.8-27b` without the `:free` suffix.
- `Settings.chat_ask_model` is a second selector, also currently defaulted to `qwen/qwen3.8-27b`; `MitreApplicabilityGate` resolves this value independently.
- Backend Compose currently forwards both `CASE_ANALYSIS_MODEL` and `CHAT_ASK_MODEL`, each with a `qwen/qwen3.8-27b:free` fallback. The RAG service has a separate `CORE_LLM_OPENROUTER_MODEL` variable and is out of scope.
- `configured_pipeline()` writes `Settings.case_analysis_model` into `AnalysisPipelineConfig`, which is persisted with analysis results. The snapshot also holds versioned pipeline and token-budget metadata.
- `AnalysisPipelineConfig.model` currently has a separate literal default of `qwen/qwen3.8-30b`. `read_pipeline(None)` returns that default rather than the configured model; partial snapshots also rely on the class defaults.
- Chat answer generation currently replaces the model read from its saved pipeline snapshot with the current configured pipeline model. Preserve this current-model behavior.
- The backend registry currently has a separate `DEFAULT_OPENROUTER_MODEL` literal without `:free`; the dirty working-tree test expects the `:free` ID. The configured default, registry default, pipeline default, and Compose default therefore do not currently form one consistent contract.

These observations describe the inspected working tree; existing local edits remain user-owned and are not assumed to be committed.

## Design

### One environment-backed selector

`Settings.case_analysis_model` remains the sole runtime model selector for backend Case Analysis. Its default is the exact selected ID `qwen/qwen3.8-27b:free`. Define that default once in `backend/app/config.py`; the setting field uses that constant. Remove `chat_ask_model` as a second setting and remove `CHAT_ASK_MODEL` from the backend Compose environment.

The MITRE applicability gate resolves the same effective model used by Main Case Analysis. A deployment that previously set only `CHAT_ASK_MODEL` must move that value to `CASE_ANALYSIS_MODEL`; the old variable is no longer a supported selector. Keep `chat_ask_timeout_seconds` because it controls request timing, not model choice.

The model registry remains responsible for aliases and canonical OpenRouter IDs, not for an independent backend model choice. It imports the shared default constant from `app.config`; its default and Qwen preset use that same value. Production callers pass the effective `Settings.case_analysis_model` explicitly, so an environment override takes precedence over the code default. Pipeline snapshots store the canonical resolved ID when the selector is an alias. Preserve direct OpenRouter model-ID passthrough and unknown-alias errors.

### Environment settings versus persisted snapshot

Keep `Settings` and `AnalysisPipelineConfig` as separate types because they have different owners and lifetimes:

- `Settings.case_analysis_model` is current process/deployment configuration.
- `AnalysisPipelineConfig.model` is the effective model recorded with a particular analysis, alongside the versioned pipeline and token-budget metadata.

The snapshot is not a second model selector. New snapshots are constructed from the current setting. `AnalysisPipelineConfig` must not contain an independent model literal that can diverge from that setting; its model default is resolved through the registry from the configured setting.

`read_pipeline` must resolve a missing snapshot or missing snapshot fields from the current configured pipeline, while preserving fields explicitly present in a stored snapshot. It must retain existing validation behavior and the current `main_case_analysis_v10` to `main_case_analysis_v1` compatibility normalization without mutating the saved input. Chat answer generation continues to use the current configured model as it does today.

No persisted JSON keys or types change. Existing explicit historical snapshot values are not rewritten, and no database migration or backfill is needed.

### Configuration boundaries

Only the backend environment block in `docker-compose.yml` changes: it forwards `CASE_ANALYSIS_MODEL` with the selected `qwen/qwen3.8-27b:free` default and no longer forwards `CHAT_ASK_MODEL`. Do not alter the RAG service environment block, including `CORE_LLM_OPENROUTER_MODEL`.

Do not merge environment settings and pipeline snapshots into one file or class. They share the effective model value but remain separate contracts; consolidation is of model selection, not unrelated configuration responsibilities.

## Error behavior

Keep existing fail-closed model alias validation, structured-output/provider errors, and missing OpenRouter credential behavior. Do not add a silent fallback to another provider or model. An invalid configured alias continues to fail clearly through the existing resolver, and a blank `CASE_ANALYSIS_MODEL` is rejected during Settings validation rather than falling through to the registry default.

If `CHAT_ASK_MODEL` remains in a developer or deployment environment, it is not read as a model selector after this change. Operators must use `CASE_ANALYSIS_MODEL` for all covered backend model calls.

## Verification

Focused tests must verify:

- `CASE_ANALYSIS_MODEL` is the only backend model selector, including environment-backed settings construction.
- A blank configured model is rejected rather than treated as a request for the registry default.
- The default, Qwen registry entry, and `default` alias resolve to the exact `qwen/qwen3.8-27b:free` ID.
- A configured registry alias is canonicalized before it is written to a new pipeline snapshot; an unknown alias fails clearly.
- A configured model override is used consistently by the pipeline snapshot, Main Case Analysis target, chat answer target, and LLM MITRE applicability gate.
- `read_pipeline(None)`, empty snapshots, and partial legacy snapshots obtain missing defaults from the current configured pipeline.
- Explicit model values in a saved snapshot are not mutated by reading it; the existing v10-to-v1 normalization remains covered.
- Chat answer generation continues to use the current configured model even when its context contains a different persisted model value.
- Backend Compose has one model selector and the RAG environment block is unchanged.
- `chat_ask_timeout_seconds`, OCR model configuration, model credentials, and current error behavior remain unchanged.

Run the focused settings, registry, pipeline-versioning, case-answer, and MITRE gate tests, followed by the backend test suite if the focused changes pass. No live provider call or database migration is needed.

## Acceptance criteria

1. `CASE_ANALYSIS_MODEL` is the only environment-controlled model selection for Main Case Analysis, chat answers, and the LLM MITRE gate.
2. The default effective model is exactly `qwen/qwen3.8-27b:free` throughout backend settings and registry resolution.
3. New analysis pipeline snapshots record the configured model, without an independent pipeline-model default.
4. Missing fields in older snapshots resolve from current configuration, while explicit historical JSON remains unchanged.
5. The existing chat-answer current-model override and pipeline version compatibility behavior remain intact.
6. The `pipeline_config` persisted JSON shape and database schema are unchanged; no migration is added.
7. `CHAT_ASK_MODEL` is removed from backend settings and backend Compose; RAG and OCR model configuration are untouched.
