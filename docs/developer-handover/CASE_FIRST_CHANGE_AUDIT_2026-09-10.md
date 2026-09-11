# Case-first change audit

2026-09-10 — Read-only application review of the current dirty checkout. Documentation only was updated. Earlier pass counts are historical receipts, not certification of the paths below.

## Intent and design

Case ownership is justified by analysis without Chat. Retaining the monolith and PostgreSQL is appropriate. However, native workflow duplicates policy orchestration and bypasses existing integration guarantees; reuse those policies behind native-source adapters instead of certifying the parallel path from service tests alone.

## Findings

1. **P1: Authenticated mutations start a second transaction.** `get_optional_user` queries User using the cached `get_db` dependency. `case_analysis.py:46`, the material write routes and clarification answer route then enter `db.begin()` on that same session. Reproduced with real PostgreSQL: after the auth-equivalent User SELECT, `start_case_analysis` raises `InvalidRequestError: A transaction is already begun on this Session.` Fix transaction ownership across authentication and route/service boundaries; test actual authentication dependencies. `test_run_recovery_api.py:38` overrides authentication and therefore hides this failure.

2. **P1: Superseded failed analysis can be retried.** `case_run_service.py:59` changes failed to queued and returns before checking active/newer work or evidence revisions. The answered-clarification branch repeats this behavior. Real PostgreSQL reproduction: enqueue old, fail old, enqueue/complete newer, replay old key -> old becomes queued. Its later completion can replace the latest pointer with an older snapshot; replay during active work reaches the unique constraint instead of a domain conflict. Centralize retry checks under the Case lock and reject superseded work.

3. **P1: Native validation accepts reported claims without exact citations.** `case_native_validation.py:100` normalizes the supplied citation list but never requires coverage for supporting IDs. Reproduced locally: a reported claim with `supporting_source_ids=['s1']` and no citations returns `validation_status='validated'`, citation count zero. Require exact citations for every declared support/contradiction role before publishing canonical results. This is a structural provenance failure, not a semantic-entailment claim.

4. **P1: Follow-up history is discarded on every Case analysis.** `case_run_execution.py:139` supplies `clarification_exchanges=()` and `canonical_trace=None`. The unchanged follow-up engine uses exchange count for maximum rounds (`followup/decision.py:157`) and exchanges for exhausted-gap selection. Persisted CaseClarification history is never reconstructed into that call, so repeat-question/round bounds reset. Load the durable answered chain and adapt it into existing policy input.

5. **P1: Case clarification cannot be answered with Chat closed.** `use-case-queries.ts:74` fetches clarifications, but ChatWorkspace never consumes them; `answerCaseClarification` in `case-client.ts:209` has no caller under frontend/src. Add the Case-page question/answer action and its run invalidation. Endpoint presence and service tests do not satisfy the optional-Chat interaction requirement.

6. **P2: Analyze retry generates a new request and can duplicate evidence.** `use-case-workspace-actions.ts:120` admits narrative, then line 130 generates a fresh idempotency key on every submit. An uncertain analysis response followed by another click can re-admit identical narrative and create another logical analysis. Preserve the logical submission key and completed admission step until the operation resolves; send the expected revision as part of the saved request.

7. **P2: Saved document pages are not citation spans.** `case_materials.py` stores raw `DocumentPage.model_dump()` objects; `_analysis_context` passes those as `page_spans`. `DocumentPage` has no start_offset/end_offset, while `evidence_quote_resolver._valid_page_spans` requires both and stops at the first missing span. Therefore native uploaded-document page attribution drops to narrative-only. Construct offsets/hashes against the exact admitted text using the existing provenance builder, and verify repeated-quote/edited-text cases without inventing offsets.

## Verification and limits

- Inspected current Git status, native routes, authentication dependency, material/snapshot services, enqueue/claim/completion, clarification policy inputs, migration 0009, native validation, Case hooks and their callers.
- Two PostgreSQL reproductions used disposable isolated schemas via the existing test helper; they cleaned up their schemas and did not change public application rows.
- One pure validator reproduction confirmed missing citations are accepted.
- No full regression rerun, paid provider calls, deployment, or application fixes were performed for this audit.
- Prior populated migration rehearsal does not cover these authenticated/interaction failures. Existing A-E pass declarations are superseded by these findings; release gates remain open.

Verdict: fix-then-ship. Authenticated writes currently fail before the Case workflow can run.
