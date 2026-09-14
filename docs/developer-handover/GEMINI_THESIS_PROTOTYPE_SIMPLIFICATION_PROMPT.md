# Gemini Implementation Prompt — CyberCase Thesis Prototype Simplification

You are working in `F:\Cybercase Framework` on the current `main` branch.

Implement a focused simplification pass for a thesis prototype. This is not a production-hardening exercise. The development database contains no important data and may be reset/recreated. The objective is to make the code understandable to a thesis reader and maintainer while preserving the demonstrated CyberCase workflow.

## Product boundary

CyberCase is a Case-first prototype for:

```text
Case
  ├─ Documents and OCR/extraction
  ├─ Explicitly admitted evidence
  ├─ Evidence revision
  ├─ Persisted Case Analysis Result
  ├─ Clarification question and answer
  ├─ Optional ordinary Ask conversation
  └─ Deterministic report
```

The Case is the aggregate. Chat/Ask is a contextual Case conversation, not an independent product. MITRE ATT&CK/RAG is optional external technical context and is not Case evidence.

This is a thesis prototype, not a security-certified, forensic-chain-of-custody, multi-tenant production system.

## Primary simplification decision

Remove SHA-256 from the CyberCase application contract and persistence model.

Do not replace it with another homemade digest or security-looking fingerprint.

Use explicit IDs, foreign keys, evidence revisions, and exact source text/offsets for ordinary application binding.

The prototype must not claim that it detects database tampering, proves authenticity, proves chain of custody, or provides forensic certification.

## Target architecture

```text
Case
  ├─ CaseDocument
  │    └─ DocumentExtraction
  ├─ EvidenceSource
  │    └─ EvidenceRevision(source_id, revision)
  ├─ CaseEvidenceSnapshot(id, case_id, evidence_revision, manifest, input_text)
  ├─ CaseRun(snapshot_id)
  │    └─ CaseAnalysisResult(snapshot_id)
  ├─ ChatMessage(case_id, message_kind, in_reply_to_message_id, analysis_result_id?)
  └─ CaseReport(analysis_result_id, evidence_snapshot_id)
```

The binding rules are:

```text
Analysis → snapshot_id
Citation → source_id + source revision + exact quote + validated offsets
Clarification answer → admitted EvidenceSource revision
Ordinary Ask → current Analysis Result only; never evidence
Report → analysis_result_id + evidence_snapshot_id
Technical context → case_run_id + evidence_snapshot_id, external only
```

## Required work

### 1. Re-audit before editing

Inspect the current branch and trace every SHA/ChatThread caller before deleting anything. Create a short inventory in the implementation receipt with:

- current SHA fields and callers;
- current ChatThread routes and callers;
- current migration head;
- current frontend Case/Chat lifecycle;
- files that are historical-only versus production-active.

Do not rely on old cleanup documents without checking the live branch.

### 2. Remove SHA-256 fields and logic

Remove the following from models, schemas, services, generated API contracts, frontend adapters, tests, report metadata, and UI where they exist:

- `CaseDocument.content_sha256`;
- `DocumentExtraction.text_sha256`;
- `EvidenceRevision.text_sha256`;
- `CaseEvidenceSnapshot.text_sha256`;
- `CaseEvidenceSnapshot.manifest_sha256`;
- `CaseAnalysisTrace.evidence_sha256` and equivalent message metadata fields;
- `RagContext.query_sha256` and its index;
- `CaseReport.source_snapshot_hash`;
- report snapshot `evidence_sha256`/`manifest_sha256` fields;
- frontend `sha256.ts` and browser-side hash recomputation;
- SHA rows in report HTML/Markdown/PDF metadata;
- SHA-based default idempotency keys.

Replace behavior as follows:

- snapshot reuse: `(case_id, evidence_revision, format_version)`;
- analysis binding: `CaseRun.snapshot_id` and `CaseAnalysisResult.snapshot_id`;
- report binding: `analysis_result_id` and `evidence_snapshot_id`;
- RAG binding: `case_run_id` and `evidence_snapshot_id`;
- report default idempotency: deterministic readable key such as `report:{case_id}:{analysis_result_id}:{template_version}`;
- citation validation: source identity, source revision, exact quote, character offsets, document/page provenance when present;
- frontend citation presentation: use the validated backend projection and direct exact-text/offset checks only.

Do not weaken citation behavior into fuzzy matching. If a quote/page binding cannot be proven from source ID, revision, exact quote, offsets, and available provenance, fail closed to a source-level or narrative-level reference.

### 3. Remove ChatThread as an independent identity

Case owns at most one optional conversation. Remove the compatibility identity layer where practical:

- add `case_id` directly to `ChatMessage`;
- make message ordering/uniqueness Case-scoped;
- move ChatService operations to `case_id`;
- remove `ChatThread.title`, `ChatThread.user_id`, and computed `ChatThread.status` proxy behavior;
- remove `ChatThread` model/table if the resettable development schema makes this straightforward;
- remove frontend `activeThreadId`, thread-selection compatibility state, and thread-detail loading by ID;
- use Case-scoped chat endpoints only;
- keep `/chat` as a simple frontend redirect to `/case` if needed for the old link.

Do not remove Chat, transcript persistence, clarification, ordinary Ask, retry behavior, or analysis-result publications.

### 4. Retire legacy Chat API surface

After migrating active frontend callers, remove unused `/api/v1/chats/*` writers/readers/report routes and their compatibility DTOs. Keep only Case-scoped routes:

```text
POST /cases/{case_id}/chat
GET  /cases/{case_id}/chat
POST /cases/{case_id}/chat/messages
GET  /cases/{case_id}/chat/runs/{run_id}
```

Prove no supported frontend route or current test requires the deleted routes before removal. Update route-surface tests and generated API types.

### 5. Simplify deterministic report metadata

Reports remain functionally unchanged, but remove storage/API fields that are fixed implementation labels rather than thesis data:

- `provider` when always `deterministic`;
- `model` when always `case-template`;
- `decoding_settings` when always `{}`;
- duplicate snapshot hash fields.

Keep the report snapshot JSON, `prompt_version`/template version, analysis result ID, evidence snapshot ID, validation status, and PDF output semantics.

Do not redesign the report renderer or change report content except removing technical SHA display lines.

### 6. Keep the following invariants

Do not change:

- Case evidence admission semantics;
- source/revision semantics;
- exact quote and page provenance behavior;
- CaseRun claim, lease, retry, completion, and recovery behavior;
- clarification versus ordinary Ask semantics;
- ordinary Ask non-evidence behavior;
- persisted CaseAnalysisResult ownership;
- stale/current analysis behavior;
- optional MITRE applicability, retrieval, mapping, or RAG behavior;
- report generation meaning, persistence, validation, or PDF structure;
- prompts, LLM provider selection, analysis output schema meaning, or gap policy.

Do not add Redux, a global context, an event bus, generic repositories, plugin architecture, OCR changes, NER, or a new frontend navigation model.

## Database and migration policy

The development database is disposable. Prefer a clean, understandable current schema over compatibility shims.

Choose one of these implementation forms and document the choice:

1. Create one explicit forward migration that drops the obsolete columns/table and reset the development database.
2. If the old migration chain is already thesis-only and disposable, squash it into one readable baseline and reset the database.

Do not preserve old hash columns solely for hypothetical historical data. Do not create fake backfill values. Do not modify a live production database.

## Verification gates

Run after each phase:

```text
backend focused schema/route/workflow tests
frontend focused Case/Chat/Materials/Overview tests
```

Run before handoff:

```text
cd frontend
npm test -- --run
npx tsc --noEmit
npm run check:api-types
npm run lint
npm run build

cd ../backend
python -m pytest -q
```

Also run repository searches:

```text
rg -n "sha256|SHA-256|content_sha256|text_sha256|manifest_sha256|evidence_sha256|query_sha256|source_snapshot_hash" backend frontend
rg -n "/chats/|ChatThread|activeThreadId" frontend/src backend/app
```

Any remaining match must be classified as generated/history/test-only or removed. Do not leave unexplained production references.

Manually verify:

```text
create Case
add narrative
upload document
admit extraction
create evidence snapshot
run analysis
open Overview
open cited source
answer clarification in Ask
confirm evidence revision changes
ask ordinary question
confirm ordinary Ask does not create evidence
generate/open report
render technical and non-technical Cases
open /chat and confirm intended redirect
```

## Deliverables

Provide:

1. a concise implementation receipt;
2. before/after model and route diagram;
3. exact files/deletions;
4. migration/reset instructions;
5. tests and build results;
6. explicit list of retained complexity and why;
7. confirmation that `rag_service/**` was untouched;
8. confirmation that no deployment occurred.

Do not commit or push unless explicitly requested by the user. Do not modify unrelated dirty files.
