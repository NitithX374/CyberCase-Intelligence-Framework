# Attribute-first Phase 1 implementation

Implemented 2026-09-08. This implements the bounded, case-only claim-anchored adaptation proposed in MAIN_ANALYSIS_V11_MIGRATION_AUDIT.md. It is not a full CAMS or ACL Attribute First reproduction. NLI/XNLI inference is not installed or enabled.

## Behavior

The opt-in overview pipeline now runs:

```text
admitted source registry
  -> extraction provider call
  -> unique exact quote binding
  -> deterministic coverage/budget selection
  -> generation provider call over selected claims AND quotations
  -> ID admission and existing AnalysisTraceV3
  -> case-only gap/follow-up processing
  -> existing run completion and report/frontend readers
```

Generation returns short text units referencing selected A-IDs. The backend requires all selected claims to remain referenced, copies the original claim statuses/citations, and builds answer and summary from the same admitted units. Source hashes and message-relative offsets are stored in an execution receipt outside the strict public trace.

Exact binding rejects absent, unknown-source and ambiguous quotations. A unique narrative span remains usable without a document page; page labels require hash-valid, complete coverage. The legacy citation facade retains its old behavior. Opposing roles for one source in one claim fail explicitly; extraction must represent those as separate attributed claims.

Selection keeps all candidates when they fit, deduplicates identical records, then reserves explicit unknown/uncertain/contradicted candidates and fills the remaining budget round-robin across sources in stable source/offset order. All omissions have reasons. This is a coverage policy, not trained salience ranking, semantic equivalence or reliable conflict detection. Required uncertainty candidates that cannot fit cause failure.

The new branch never invokes MITRE applicability/retrieval in Phase 1; metadata explicitly marks technical augmentation disabled/unavailable. Existing raw_direct and ASK behavior remains legacy. Full admitted case evidence still reaches gap analysis; the selected subset is not substituted for the original evidence.

## Enable

Default remains `CASE_ANALYSIS_PIPELINE=raw_direct`. Set the backend environment to:

```text
CASE_ANALYSIS_PIPELINE=claim_anchored
CHAT_ASK_MODEL=openai/gpt-5.6-luna
CLAIM_ANCHORED_INPUT_TOKENS=80000
CLAIM_ANCHORED_OUTPUT_TOKENS=16384
CLAIM_ANCHORED_SELECTION_TOKENS=24000
```

Docker Compose forwards these variables to the backend. Rebuild the backend image after installing the now-required existing tokenizer dependency in backend/requirements.txt. For local execution, install those requirements and restart the backend with the selected environment. No live deployment or persistent environment setting was changed by this implementation.

A new overview run pins its effective v11 model/provider, stage/pipeline versions, limits and timeout. Clarification inherits its root run's selection; idempotent retries reuse the original run payload. Changing the environment affects new independent runs, not a queued v11 run or its clarification chain. Historical records without configuration explicitly mean legacy raw_direct. Legacy v10 model routing remains unchanged, rather than being retroactively version-pinned.

Raw_direct remains available for the baseline; changing the setting back does not rewrite an already pinned run. ASK stays on v10 and cannot replace canonical overview state.

## Implementation boundaries

- `case_analysis/claim_anchored/`: typed intermediate records, binding, selection, provider calls, assembly and orchestration.
- `case_analysis/pipeline_config.py`: validated selection and pinned configuration.
- `case_analysis/evidence_quote_resolver.py`: shared literal page resolver; `source_citations.py` remains the legacy facade.
- `chat/analysis_run_config.py`: root-run inheritance at creation.
- `workflow/analysis_execution_receipt.py`: lease-owned stage checkpoints in existing run JSON.
- `workflow/analysis_pipeline_context.py`: case-only routing and outcome metadata.

Stage checkpoints record pending/completed/failed calls and reported usage. Previous attempt receipts survive interrupted retry. A killed in-flight provider request may have incurred unknown usage; no cost is invented when no response arrived. No stage cache, automatic provider fallback, fuzzy quote rescue, semantic repair loop or silent source truncation was added.

`SemanticVerifier` exposes asynchronous claim and generated-summary checks. It receives defensive copies and can reject the run. With no implementation injected, metadata says `semantic_verification=not_performed`; structural trace validation is not semantic entailment verification.

## Validation

- Synthetic Thai live smoke with OpenRouter GPT-5.6 Luna: both stages completed, three claims retained and all three referenced. Provider times: extraction 6.890s and generation 4.813s. Reported usage: 1,492 input and 652 output tokens total; reported cost USD 0.0010808. This single smoke establishes transport/schema compatibility, not accuracy or typical latency.
- Live receipt: `ATTRIBUTE_FIRST_SMOKE.json`; reproducible runner: `backend/scripts/smoke_claim_anchored.py`.
- Focused PostgreSQL tests exercised full worker completion, exception-group failure receipts, interrupted idempotent retry and clarification configuration inheritance, on a separate temporary PostgreSQL instance.
- Frontend: 151 tests passed; generated API types check passed. No frontend source changes.
- Python syntax, Ruff F/I checks and Compose configuration validation passed. Every touched Python code file is below 300 physical lines.
- Final backend suite with temporary PostgreSQL: 386 tests and 2 subtests passed, no skips; one upstream FastAPI/httpx deprecation warning. Full receipt is recorded in CONTINUITY.md.

Run the live synthetic smoke from backend with configured provider credentials:

```powershell
..\env_mitre\Scripts\python.exe -X utf8 -m scripts.smoke_claim_anchored --output ..\docs\research\ATTRIBUTE_FIRST_SMOKE.json
```

## Remaining limits

Extraction and generation remain learned semantic decisions. A correct literal quote can still accompany a misinterpreted claim; NLI qualification and independent Thai annotation remain subsequent work. Selecting claims can omit important facts, and automatic atomicity is not guaranteed. Output is an overview of admitted units, without synthesizing a report timeline from claim order. Multi-document equivalence/clustering, calibrated ranking, technical augmentation and a user-facing sentence-receipt viewer remain deferred.
