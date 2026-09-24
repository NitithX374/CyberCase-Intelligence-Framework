# Backend Model Configuration Consolidation Implementation Plan

## Approved contract

Implement `docs/superpowers/specs/2026-09-23-backend-model-config-consolidation-design.md`.

## Work sequence

1. Define `qwen/qwen3.8-27b:free` once in `backend/app/config.py`. Use it as the default for `Settings.case_analysis_model`, reject blank values, remove `chat_ask_model`, and have the backend model registry reuse the shared default for its canonical Qwen entry and default resolver.
2. Make `AnalysisPipelineConfig.model` resolve `settings.case_analysis_model` through the model registry, so new snapshots record the canonical ID for either a registry alias or full ID. Keep `configured_pipeline()` as the snapshot constructor. Update `read_pipeline()` so null and partial snapshots receive missing values from the current configured pipeline while explicit saved fields remain intact; preserve v10-to-v1 normalization.
3. Route `MitreApplicabilityGate` and the direct no-RAG diagnostic consumer through `case_analysis_model`. Remove `CHAT_ASK_MODEL` from only the backend environment block in `docker-compose.yml` and update the active backend configuration guidance; retain the current chat-answer model override and all RAG/OCR settings.
4. Add focused coverage for settings defaults, blank rejection, and environment overrides; registry canonicalization; null/empty/partial/explicit pipeline snapshots; chat's current-model behavior; and MITRE gate model selection. Update existing assertions only where required by the approved contract.
5. Run the focused backend tests, relevant Ruff checks, and the broader backend suite if focused tests pass. Validate Compose/backend configuration and inspect the final diff to confirm no database, frontend, RAG, or unrelated dirty-file changes were introduced.

## Likely files

- `backend/app/config.py`
- `backend/app/services/analysis/settings.py`
- `backend/app/services/analysis/mitre_gate/llm.py`
- `backend/app/services/llm/model_registry.py`
- `backend/tests/test_analysis_pipeline_versioning.py`
- `backend/tests/test_model_registry.py`
- `backend/tests/test_mitre_applicability_provider.py`
- `backend/tests/test_case_answer.py` (only if existing coverage needs a focused adjustment)
- `research/diagnostic/run_no_rag_diagnostic.py` (selector reference only)
- `CLAUDE.md` (active backend configuration guidance only)
- `docker-compose.yml` (backend environment only)

## Constraints

- Preserve all pre-existing dirty work; review each overlapping diff and make narrow edits.
- Do not edit `rag_service/**`, frontend files, database models, migrations, or persisted JSON schema.
- Keep OCR configuration, provider credentials, timeout settings, and current chat-answer model override unchanged.
- Do not stage or commit files unless explicitly requested.
