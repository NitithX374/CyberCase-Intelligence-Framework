# 1. FINAL VERDICT

**MODERATE REFACTOR.** Audit date: 2026-09-07. Local checkout: `70bffbc8b9faaf2a552bcc1665f99bd08bef9692`. Production analysis/workflow/follow-up paths have no committed diff from the previously audited `7a347b4`. Existing ledger changes and the earlier research assessment were preserved. Remote HEAD parity was not checked.

CyberCase can retain its entrypoint, admitted evidence snapshot, final v3 trace, persistence tables, report contract and frontend readers. New extraction and constrained-generation stages, a stricter internal span resolver, explicit selection and per-run routing are needed. This is more than a prompt change but far less than replacing the application.

If the only objective were preventing supplied MITRE text from influencing case findings, a case-only main prompt plus separate augmentation would be simpler than claim extraction. The proposed extraction stage is justified by the additional requirement to establish an inspectable evidence representation before selection/generation. Neither design guarantees semantic entailment.

[CAMS v4](https://arxiv.org/abs/2606.23989v4) distinguishes deterministic provenance from semantic faithfulness and uses claim extraction, clustering, selection, rewriting and verification. Its distinction is useful; its complete machinery is not required here. The [ACL 2024 method](https://aclanthology.org/2024.acl-long.182/) instead selects spans, plans sentence groups and generates sequentially. The proposal below is a CyberCase-specific claim-first adaptation, not a reproduction of either paper. Paper performance claims were not independently reproduced.

# 2. REUSE PERCENTAGE

Planning estimate for the scoped target infrastructure, not measured LOC, novelty or completed work:

| Category | Rough share | Meaning |
|---|---:|---|
| Reusable substantially as-is | 60% | Evidence ingestion/admission, public trace types, source hashes, provider/schema utilities, persistence lifecycle, canonical selection, frontend/report consumers |
| Existing infrastructure needing refactor | 25% | Quote resolution, service dispatch, workflow context construction, outcome/version metadata, gap/ASK boundaries |
| Genuinely new implementation | 15% | Internal candidates/bound spans/generated units, explicit selector, extraction/generation prompts and orchestration, augmentation boundary tests |

Uncertainty is at least ±10 percentage points. New test effort can exceed the apparent amount of new production logic. The core algorithm changes materially even though much surrounding infrastructure survives.

# 3. CURRENT → TARGET MAPPING TABLE

Paths are repository-relative. CA = `backend/app/services/case_analysis/`; WF = `backend/app/services/workflow/`; FU = `backend/app/services/followup/`.

| Current component / exact entry | Target role | Decision / compatibility |
|---|---|---|
| `chat/raw_evidence.py`: `build_raw_evidence_snapshot`, `load_raw_evidence_snapshot` | Ordered admitted source registry and full evidence hash | KEEP AS-IS. User-source inclusion, not salience selection. Do not replace the full hash with a selected-subset hash. |
| `chat/document_provenance.py`: `validated_document_source_payloads`, `_validated_source_payload`, `_span_matches` | Validate imported page metadata | KEEP AS-IS. Retains valid prefix of page spans; missing page provenance must remain explicit. |
| WF `pipeline_execution.py`: `_run_fresh_analysis` context construction | Separate case source context from retrieval context | MODIFY for v11 branch; retain v10 construction. |
| CA `case_analysis_prompt_builder.py`: `build_case_analysis_prompt`, `_separate_analysis_context`, `build_overflow_case_context` | Existing v10/ASK prompt | KEEP for v10. New v11 builders must whitelist case sources; do not reuse optional-context serialization for case-only stages. Prefix truncation is not a v11 selection policy. |
| CA `case_analysis_executor.py`: `MainCaseAnalysisService.analyze`, `request_case_analysis`, `_post` | Stable facade/legacy implementation and dispatch seam | REUSE WITH SMALL REFACTOR. Preserve call signature; dispatch explicitly by pinned pipeline and analysis mode. |
| CA `contracts.py`: `ProviderCaseAnalysisV3` | Legacy joint answer/summary/claims/MITRE output | KEEP for v10; REPLACE ONLY IN v11 provider requests with stage-specific internal schemas. |
| CA `contracts.py`: `AnalysisClaimV3` | Final public findings | KEEP shape/enums. Not a sufficient intermediate binding record: citations optional, offsets absent, normalized text can be wrong. |
| CA `contracts.py`: `AnalysisEvidenceCitation` | Public citation projection | KEEP. Reuse inside bound-span wrapper; do not add required offsets to persisted citations. |
| CA `contracts.py`: `AnalysisTraceV3` | Final public/persisted artifact | KEEP unchanged. Does not store sentence-to-claim links; store v11 internal receipt separately in metadata. |
| CA `case_analysis_response_parser.py`: `parse_case_analysis_response` | Legacy response parsing | KEEP for v10. v11 constructs final trace from admitted intermediate records rather than allowing a second call to recreate citations. |
| CA `source_citations.py`: `bind_analysis_claim_citations`, `_source_texts`, `_resolve_document_locator`, `_quote_occurrences`, `_valid_page_spans` | Shared literal resolution primitive, with legacy wrapper | REFACTOR. Add unique occurrence offsets and typed outcomes internally. Preserve legacy page/narrative behavior through wrapper. |
| CA `validation.py`: `validate_analysis_trace_v3`, `detect_forbidden_provenance` | Final compatibility checks plus v11 admission checks | KEEP existing validator semantics. ADD stricter v11 validator separately so old traces remain readable. |
| CA `mitre_applicability_gate.py`: `evaluate_mitre_applicability`; WF `rag_routing.py`: `attempt_mitre_applicability` | Optional augmentation admission | KEEP gate and source validation. REMOVE gate output/context from case-generation input. |
| WF `rag_routing.py`: `attempt_optional_rag`; `clients/rag_client.py` | Optional technical retrieval | KEEP client/partner API. Move its result to isolated augmentation. |
| `ProviderCaseAnalysisV3.mitre_associations` | Associations produced after immutable findings | REMOVE FROM v11 case generation; preserve legacy field for v10. Separate augmentation may project validated associations into final v3. |
| FU `gap_stage.py`: `run_gap_analysis_stage`; `gap_analysis.py`; CA `gap_assembly.py`: `enrich_case_analysis_result`, `assemble_claim_linked_gaps` | Case-only gap analysis after grounded generation | REUSE; supply raw admitted evidence and stable final claim IDs without RAG. Gap semantics remain learned. |
| FU `decision.py`: `evaluate_followup_outcome`; `stateful.py`: `select_next_gap`, `normalize_gap_key`; `policy.py` | Existing stateful question selection | KEEP mechanics; MODIFY supplied context for v11. Topic exhaustion is not semantic resolution. |
| CA `state_selector.py`: canonical trace validation/selection | Currentness and scope checks | KEEP. New internal IDs must project to unique final A-IDs before this boundary. |
| WF `outcome.py`: `fresh_analysis_outcome`, `question_outcome`, `bind_followup_question` | Versioned outcomes and internal receipt metadata | MODIFY. Current global `CASE_ANALYSIS_PROMPT_VERSION` would mislabel mixed pipelines; follow-up outcomes also need explicit receipt propagation. |

Current main analysis makes one provider call yielding answer, summary, claims and MITRE associations jointly, followed by deterministic binding/validation. Full workflow includes applicability, optional RAG, separate gap analysis and conditional question-policy calls. No case-only extraction/selection/rewriting pipeline exists in production.

Existing research overlap: `research/attribute_first_pilot` predicts QA attributes and passes full context into generation; no sentence plan or enforced selected-only input. `experiments/context_refinement` already implements isolated context compression, not claim anchoring. `evaluation/analysis_pilot` has historical RAW_DIRECT/EXTRACTED_STATE artifacts but imports removed extraction/router modules. Reuse research lessons and receipts, not these as production services or evidence of a completed v11.

# 4. MINIMUM VIABLE V11

```text
admitted source registry (case material only)
  → LLM claim extraction: text + copied quotes + source IDs + epistemic labels
  → deterministic exact binding with unique message-relative offsets
  → deterministic eligibility / exact deduplication / stable budget selection
  → LLM generated units referencing selected claim IDs
  → deterministic ID admission and projection
  → AnalysisTraceV3 + internal sentence/selection/provenance receipt
  → existing case-only gap / follow-up stages
```

Two sequential main-analysis provider calls for the bounded-input V1: extraction and generation. No LLM selector, clusterer or repair loop. Generator receives selected normalized claims **and their bound verbatim quotes**, never just paraphrased claims. Otherwise extractor errors are promoted into the sole apparent evidence. It may not rewrite claim epistemic metadata or supply new source IDs. Extraction atomization, claim–quote interpretation and generated prose remain fallible learned decisions.

Make the initial scope `case_overview`. Keep ASK explicitly on the documented v10 path until separately migrated; do not advertise source isolation for all modes. Keep analysis limits explicit: inputs too large for complete extraction fail with a clear budget error in the opt-in branch. Do not silently truncate, skip source batches or fall back to v10. Source-batched extraction is a later bounded extension, not an assumed two-call guarantee for arbitrarily large cases.

# 5. EXACT FILE PLAN

Proposed only; no production changes made. All new code files remain below 300 lines. Keep stable entrypoints; avoid expanding existing oversized modules.

**KEEP:** CA `contracts.py` public Pydantic trace/citation shapes; `case_analysis_prompt_config.py` v10 constant and prompts; `case_analysis_prompt_builder.py`; `case_analysis_response_parser.py`; `validation.py`; `state_selector.py`; `personalization.py`; `chat/raw_evidence.py`; `chat/document_provenance.py`; `clients/rag_client.py`; current provider/structured-output utilities; FU gap/policy/stateful modules; `rag_service/**`; frontend and report implementation; all historical research outputs.

**MODIFY (Phase 1):**

| File | Exact purpose |
|---|---|
| `backend/app/config.py` | Validated pipeline choice, default `raw_direct`; explicit stage input/output limits. Unknown values fail. |
| CA `case_analysis_executor.py` | Retain v10 service; route stable request facade to v11 orchestrator for explicitly enabled overview runs. Preserve injected-client test seam. |
| CA `source_citations.py` | Extract low-level matching/page helpers into resolver module, keeping legacy binding facade behavior. |
| CA `contracts.py` | Only if using the preferred internal-result approach: append optional internal execution receipt to `CaseAnalysisResult` dataclass, not to `AnalysisTraceV3` or provider v10 schemas. |
| CA `gap_assembly.py` | Preserve optional execution receipt when constructing enriched `CaseAnalysisResult`; verify summary immutability in v11 orchestration. |
| WF `pipeline_execution.py` | Explicit branch; v11 uses case-only contexts and suppresses augmentation until Phase 2. Leave v10 path unchanged. Delegate helpers to avoid additional bloat. |
| WF `outcome.py` | Accept effective pipeline/prompt version and receipt per result; persist for overview, Ask and follow-up outcomes. |
| `chat/chat_run_creation.py` | Pin effective pipeline in internal run payload at creation; maintain request fingerprint semantics and version across retry/clarification chain. |
| WF `chat_run_contracts.py`, `chat_run_claim.py` | Carry pinned configuration from run payload to execution. Pre-migration run records explicitly mean legacy v10; no inference-time failover. |

**ADD (Phase 1), under CA:**

| File | Responsibility |
|---|---|
| `evidence_quote_resolver.py` | Exact admitted-source/offset resolution and typed ambiguity outcome; shared by legacy wrapper and v11 binder. |
| `claim_anchored/contracts.py` | Internal source/candidate/bound/selection/generated-unit/receipt contracts. Split if needed for LOC limit. |
| `claim_anchored/source_registry.py` | Source-ID-to-immutable-text registry with hash and separately validated document metadata. |
| `claim_anchored/extractor.py` | Case-only provider extraction and strict candidate decoding. |
| `claim_anchored/binder.py` | Batch admission; reject invalid/external/ambiguous evidence links explicitly. |
| `claim_anchored/selector.py` | Deterministic eligibility, exact redundancy grouping, selection budget and decision receipt. |
| `claim_anchored/generator.py` | Generate summary/finding units referencing selected IDs and supplied exact quotes. |
| `claim_anchored/prompts.py` | Separate extraction/generation prompt versions and case-only payload whitelist. |
| `claim_anchored/provider.py` | Shared stage request envelope, timing/usage, injected HTTP client, explicit errors; reuse model routing/schema helpers. |
| `claim_anchored/assembly.py` | Check generated links, copy citations/statuses from admitted records, build v3 and deterministic answer rendering. |
| `claim_anchored/service.py` | Small orchestrator returning `CaseAnalysisResult`; no DB/session ownership. |

**ADD (Phase 2):** CA `technical_augmentation.py`, `technical_augmentation_contracts.py`, `technical_augmentation_prompt.py`; WF `analysis_contexts.py` if needed to isolate branch/context assembly. **MODIFY:** WF `pipeline_execution.py`, `outcome.py`; preserve existing RAG routing functions/client and partner code.

**Phase 3:** add `claim_anchored/relations.py` and dedicated relation contracts/tests only after real multi-document inputs justify them. No database/graph addition. **DELETE: none.**

Test file plan: `backend/tests/test_evidence_quote_resolver.py`, `test_claim_anchored_binding.py`, `test_claim_anchored_selection.py`, `test_claim_anchored_generation.py`, `test_claim_anchored_pipeline.py`, `test_analysis_pipeline_versioning.py`, `test_technical_augmentation_isolation.py`. Extend existing source-citation, canonical-state, optional-RAG, main-analysis, stateful-clarification and report tests where contracts intersect.

# 6. CONTRACT PLAN

Proposed typed records; types are illustrative contracts, not implemented code. Existing `ClaimType`, `EpistemicStatus`, `AnalysisEvidenceCitation` and `MitreAssociation` are reused. All records are scoped to an immutable run/snapshot.

```text
AdmittedSource
  source_message_id: str
  content: str
  content_sha256: str
  documents: tuple[validated document provenance, ...]

EvidenceClaimCandidate
  candidate_id: str
  text: str
  claim_type: ClaimType
  epistemic_status: EpistemicStatus
  evidence: nonempty tuple[QuoteCandidate, ...]
  reasoning_summary: str | null

QuoteCandidate
  source_message_id: str
  exact_quote: str
  role: supporting | contradicting

ResolvedEvidenceSpan
  citation: AnalysisEvidenceCitation
  source_text_sha256: str
  start_offset: int
  end_offset: int
  locator_status: document_page | narrative_only

BoundEvidenceClaim
  candidate_id: str
  text: str
  claim_type: ClaimType
  epistemic_status: EpistemicStatus
  reasoning_summary: str | null
  supporting_spans: tuple[ResolvedEvidenceSpan, ...]
  contradicting_spans: tuple[ResolvedEvidenceSpan, ...]

SelectionDecision
  candidate_id: str
  selected: bool
  reason: retained | exact_duplicate | budget_exceeded
  estimated_tokens: int

GeneratedUnit
  unit_id: str
  text: str
  candidate_ids: nonempty list[str]

AnalysisExecutionReceipt
  pipeline_version: str
  extraction_prompt_version: str
  generation_prompt_version: str
  evidence_sha256: str
  selected_candidate_ids: list[str]
  candidate_to_final_claim_id: dict[str, str]
  bound_claims: list[BoundEvidenceClaim]
  selection_decisions: list[SelectionDecision]
  generated_units: list[GeneratedUnit]
  stage_usage_and_failures: list[stage receipt]
```

Candidate evidence is a list now even if V1 typically extracts one quote; one normalized claim can require multiple passages. Require support for reported/inference candidates, reasoning for inference, and valid provenance for every attached span. Unknowns are assertions about missing knowledge, not invented observed events; preserve explicitly stated unknowns and let existing gap analysis handle omissions.

Offsets are zero-based Python Unicode code-point positions in the immutable **source message**, with exclusive end; they are not PDF coordinates, bytes, UTF-16 positions or document-local tokens. Document/page projection is optional and only provided when established by existing provenance. Snapshot and source hashes serve different scopes; neither is redundant. Filename/page/source ID are already inside the reused citation and should not be duplicated at every wrapper level. Counts derive from admitted spans; do not trust model-provided source_count.

No `ClaimCluster` required in V1. Exact duplicate bookkeeping is not semantic equivalence. Defer `canonical_claim`, cross-source union and conflict graph. Do not merge alleged and established variants or treat repeated quotations as independent corroboration.

Keep `AnalysisTraceV3` final. Assemble its claims by copying admitted records and assigning final A-IDs deterministically; do not permit generator-authored provenance/status replacement. Generate `summary` by joining validated units; render `answer` deterministically from the same units/findings. The internal receipt preserves unit-to-evidence links in existing assistant metadata, outside the strict trace schema. Existing consumers ignore this receipt. Thus public compatibility survives, but full sentence-level traceability is available only through the receipt until a later reader feature is authorized.

The current same-message support/contradiction exclusion cannot represent both roles for one claim even when different spans disagree. V1 must preserve those as separately attributed reported claims and defer their semantic relation, rather than assigning fabricated source IDs or weakening the old validator. If a candidate cannot project safely, fail that v11 run explicitly. Do not silently erase one side.

### Shared provenance primitive

`resolve_evidence_quote(source_id, exact_quote, source_texts, document_context)` is feasible. Extract `_source_texts`, `_quote_occurrences`, `_documents_for_source`, `_valid_page_spans` and locator logic behind a typed resolver.

Current quote start positions exist transiently in `_quote_occurrences`; page spans already have start/end/hash. Public citations discard quote offsets. `_resolve_document_locator` admits a unique document/filename/page tuple, not necessarily a unique occurrence: repeated text on the same page may still resolve. A v11 span primitive needs a stronger rule.

- Invalid or external source ID, missing/empty quote, no exact match: explicit admission error.
- One exact occurrence: bind message-relative offsets. Attach document/page only if unambiguous and hash-valid.
- Multiple occurrences: return ambiguity, never choose first. A later source-segment ID or surrounding exact context can disambiguate without fuzzy matching.
- Plain text, edited provenance or missing valid page metadata: a unique exact message span remains valid as `narrative_only`; do not invent page labels or silently claim document grounding.
- Stale hashes, overlapping/invalid page metadata, repeated quote across pages/documents, uncovered boundaries and partial cross-page coverage: preserve explicit diagnostic. Page-only ambiguity does not invalidate an otherwise unique message span.

For V1, any candidate admission failure fails the opt-in analysis with a precise code and preserves the failure receipt. This is intentionally stricter than the legacy post-generation drop policy; evaluate rejection rate and coverage. The legacy wrapper must retain its prior semantics. No fuzzy, embedding or normalized-text matching to manufacture provenance. Internal normalization used for ranking must never modify the hashed text or quote offsets.

# 7. CALL GRAPH

Current:

```text
process_chat_run → claim run / maintain lease
  fresh: gate → optional RAG → construct combined context
    → request_case_analysis → MainCaseAnalysisService.analyze
      → v10 prompt → one provider request
      → parse_case_analysis_response → bind citations → validate v3
    → gap stage → enrich/validate canonical trace → follow-up policy
    → outcome → complete run
  ASK: reusable context → same service(question_answer) → question_outcome
```

Recommended:

```text
process_chat_run → pinned pipeline and mode
  raw_direct: unchanged v10 branch
  claim_anchored / case_overview:
    source registry → extractor [LLM] → binder [code]
      → selector [code] → generator [LLM]
      → admitted unit/claim assembly [code] → AnalysisTraceV3
      → gap/follow-up [existing; case-only input]
      → optional isolated augmentation [Phase 2]
      → immutable merge / receipt → existing completion
  ASK: explicit legacy route until separately migrated and tested
```

Use small modules with functions or thin services plus one orchestrator, not separate microservices or a framework graph. Extraction and generation are separate provider calls; binder and selector are deterministic functions. Generator failure or invalid IDs fails v11; no automatic repair/retry loop that changes semantics. Existing transport/run retry policy remains separately bounded and accounted.

# 8. TRUST BOUNDARY

1. **Admission:** `build_raw_evidence_snapshot` admits included user material; provider-origin RAG is never registered here. User-submitted claims are not certified truths; allegations/OCR errors can still exist inside admitted material.
2. **Learned semantics:** extractor determines atomicity, normalized text and epistemic labels. These are candidates, not backend-certified facts.
3. **Deterministic provenance:** resolver proves an exact span exists in an admitted immutable source. It does not prove candidate entailment, OCR correctness or speaker attribution.
4. **Selection:** inspectable deterministic policy chooses among admitted candidates; relevance and contradiction signals, if later learned, must be labeled learned inputs to that policy.
5. **Generation:** selected claims plus original quotes only. No retrieval text, technique descriptions, model-generated external answer, or arbitrary analysis_context dictionary enters either main-stage prompt.
6. **Augmentation:** only after immutable case findings exist does another call see RAG. It cannot return case claims, summary text or epistemic updates in its schema.

The current architecture permits the proposed semantic-leakage example structurally: valid case IDs/quotes can accompany an unsupported fake-login-page assertion. It does not establish that the provider actually makes that error at a particular rate. Source-role isolation prevents exposure to the supplied RAG text in case-generation calls, not hallucination from pretrained knowledge.

### Smallest explicit selector

Do not invent uncalibrated salience weights. V1 is an auditable coverage/budget selector, not a claim of optimal importance ranking:

1. Reject unbound candidates before selection.
2. Deduplicate only identical text/type/status/evidence-role signatures; retain the audit record. Do not semantically merge across sources.
3. Keep all candidates if they fit the context and final claim-count limits.
4. Under pressure, reserve explicitly represented uncertainty/conflict-related candidates first, then choose remaining candidates round-robin across admitted source messages in stable source/offset order until budget. Preserve unresolved issues as such; selection priority is not truth priority.
5. Log every omission. If required uncertainty/conflict groups cannot fit, fail explicitly rather than presenting one side. Enforce output schema claim cap as well as token budget.

Signal audit: message/document counts are available but measure provenance multiplicity, not independent corroboration. Claim type/status are model estimates. Contradicting citations/status can signal a candidate issue but do not provide reliable conflict detection. Source offsets provide document order, not event chronology. Exact duplicates are deterministic; equivalence is not. Question/task relevance needs semantic estimation or a separately declared lexical heuristic; defer learned relevance for overview V1 and keep ASK unchanged. Filename/extraction method do not establish source authority or document genre. OCR quality exists as metadata, often unavailable/uncalibrated; use it as a flag, never an automatic truth weight or reason to drop exculpatory material. Token budgeting is deterministic subject to tokenizer/provider accounting limits. No ranking model is justified by current training data.

### MITRE scheduling and contract

The gate already uses case sources, so it need not move after analysis. Simplest Phase 2 scheduling is case analysis/gaps first, then existing gate/retrieval and augmentation. Gate/retrieval could run in parallel with case-only analysis if cancellation, cost and failure handling are explicit; this is an optimization, not required architecture. Reuse raw-evidence query behavior initially; changing retrieval query to selected findings is another treatment.

Proposed internal `TechnicalAugmentation`: `retrieval_context_id`, `associations: list[MitreAssociation]`, `status`, `failure_code`. Existing association `claim_ids`, `reason`, `status=candidate_only` and `support_role=external_technical_context` suffice for candidate mappings/explanations. Validate technique IDs against retrieved table and claim IDs against immutable final findings. Copy only associations/retrieval ID into a new final v3 instance; assert `claims`, `summary`, `gaps`, `evidence_sha256` and unit mappings are unchanged. Do not rerun a whole-summary rewriter after augmentation.

Keep `answer` case-only, or append a backend-rendered separately headed technical section if existing display needs it; never permit augmentation to supply replacement answer text. Optional RAG/augmentation failure retains valid case analysis with a recorded unavailable technical status. This follows the existing optional-RAG product boundary, not a fallback that pretends failed technical output succeeded. Broader free-form technical narratives require an explicit versioned sibling contract later.

# 9. MIGRATION PLAN

**Phase 1 — opt-in case-only claim anchoring: MEDIUM.** Implement the Phase-1 files above; preserve raw_direct default; pin run versions and retain strict public v3. Reuse evidence snapshots, provider routing/schema helpers, page binding, final validation and completion. Disable MITRE augmentation for this opt-in overview branch initially; leave v10 untouched. Tests cover all proposed internal stages, versions, failures and existing consumers. Risks: extraction omissions, copied misinterpretations, oversized input, failure amplification and unknowns lost during selection. Source isolation starts in Phase 1; it must not wait until Phase 2.

**Phase 2 — restore technical enrichment through isolation: MEDIUM.** Add typed augmentation and workflow branch, reusing gate, RAG client and association validator. Keep follow-up case-only. Test malicious augmentation attempts, unknown IDs, RAG unavailable, immutable findings and report/canonical-state binding. Risk: hidden reintroduction through gap/ASK/context dictionaries and outcome metadata. ASK either remains clearly legacy or gets a separately tested question-scoped extraction/selection path; never changes canonical overview through a Q&A result.

**Phase 3 — actual multi-document relations: LARGE relative to V1; DEFER.** Source-keyed spans and tuple-shaped evidence are useful now. Document-batch extraction, equivalence relations, cross-document contradiction grouping, distributed support and selection diversity need actual multi-document acceptance cases. Exact duplicate bookkeeping can happen now; semantic clustering and document weighting cannot be justified merely by a future requirement. Do not count copies of one police assertion as independent support. Any learned relation model requires calibrated labels and an ablation. No new persistent Case State or graph is necessary.

# 10. TEST PLAN

**Unit:** exact matching; invalid/external ID; repeated quote on same/different pages; unique narrative span without page; stale hashes; edited source; Unicode/Thai offsets; cross-page quote; no fuzzy acceptance; same-message opposing roles; precise exception codes. Selection determinism, actual budget accounting, over-64 limit, no confidence truth-weighting, omissions logged, required groups not split. Generator references unknown/unselected IDs, empty units and mutated claim/status/citation fields must fail.

**Contract:** old v2/v3 stored fixtures still parse; v10 schema/prompt behavior unchanged; v11 public result satisfies existing v3; internal receipt outside strict trace; mapping loss rejected; no misleading global prompt-version labels. Both final summary and answer derive from validated units. Mutation equality includes summary, not only fields currently checked by gap assembly.

**Integration:** injected transport records that extraction/generation payloads contain no external RAG fields; gate/augmentation see only their intended contexts. Fresh/clarification/retry runs retain selected pipeline and source hashes; v11 failure never invokes v10; failed augmentation cannot fail otherwise valid case findings. Lease heartbeat and interruption recovery cover two calls; retries produce one published outcome and record actual attempt cost. Follow-up question outcomes retain receipt, canonical trace and effective version.

**Regression:** existing main-analysis, citation, canonical-state, optional-RAG, gate, stateful-follow-up, ASK and report suites; frontend v3 readers with new emitted traces; report extraction of trace.summary; v10 and legacy missing-version records; unknown configuration errors. Synthetic structural tests cannot establish semantic faithfulness; use paired independently annotated outputs for that.

Executed during this audit: `pytest` on `test_source_citations.py`, `test_analysis_trace_v3.py`, `test_canonical_analysis_state.py`, `test_main_case_analysis.py`, `test_optional_rag_pipeline.py`, `test_mitre_applicability_pipeline.py`, `test_stateful_clarification_pipeline.py`: **53 passed in 10.50s**. No live provider calls, frontend suite or report suite were run in this turn. These are current baseline checks, not tests of unimplemented v11.

# 11. BREAKAGE RISKS

- **Persisted traces:** keep strict v3 Pydantic schema unchanged; no required offsets or clusters. Add receipt outside trace. No SQL migration expected because current run request/assistant metadata are JSON, but verify payload validation and size before implementation.
- **Frontend:** `case-overview-v3.ts` and `analysis-citations.ts` read current v3 fields. They can keep working with copied final citations; they will not automatically expose new sentence mappings. Do not insert raw internal citation syntax into summary text and assume it renders correctly.
- **Follow-up:** selected claims can omit relevant raw facts. Continue supplying full admitted evidence to gap analysis within its own limits; do not pretend a gap caused by selection is a missing document fact. Claim IDs remain local to a trace; preserve existing topic-based state. Ensure enrichment carries the receipt.
- **ASK:** `_run_question` reuses analysis_context, including technical context. Explicitly leave v10 behavior or implement a separate question-scoped v11 route; do not globally switch both modes accidentally. Label the effective pipeline in response metadata.
- **Reports:** `report_analysis_projection.py` uses snapshot trace.summary; `report_snapshot.py` and contract bind trace/retrieval. Keep summary semantics and retrieval table association consistency. Broader technical narrative display would be a new reader change.
- **Token budget:** existing overflow drops external context, then evidence suffix. V11 must instead operate within declared source coverage and selection budgets. Include system/schema overhead and provider output floors. Multiple sources may require batching; do not imply arbitrary document scale.
- **Retries/failures:** two sequential calls enlarge latency and partial-failure window. Reuse run lease/completion semantics. Stage cache is optional future work; whole-run retry must record cost and pinned config. No default method failover.
- **Versioning:** `CASE_ANALYSIS_PROMPT_VERSION` is currently `main_case_analysis_v10`; it is not a pipeline registry. Keep it for legacy, add explicit pipeline/extraction/generation versions. Freeze choice at run creation and carry across retry; continuation of an existing clarification chain should inherit its effective version. Do not let an environment edit change a queued run or existing idempotency key's treatment.
- **RAG:** outcome retrieval_context_id, trace retrieval_context_id and stored table must agree after augmentation. Optional failure remains explicit. Shared mutable dictionaries must not leak retrieved text into case-only/gap payloads.
- **Semantic support:** a normalized claim can contradict a perfectly located quote. This migration improves data-flow provenance and testability, not a guarantee of factual correctness or OCR reliability.

# 12. WHAT NOT TO IMPLEMENT

Defer all requested extras: Thai-NNER; LightGBM training; full CAMS reproduction; multiple NLI models; verification/repair loops; new graph database; Legal RAG; HTR; frontend redesign; new persistent Case State; multi-agent analysis; automatic OCR correction. None is necessary for the identified code seam or source-role boundary. Any future addition needs a measured failure, usable labels and a separate experiment. Use existing provider/dependency utilities rather than selecting a new framework.

# 13. EXPERIMENTAL VALUE

Preserving v10 is preferable to replacing it. `CASE_ANALYSIS_PIPELINE=raw_direct|claim_anchored` is feasible with strict validation and per-run pinning. Do not label the unchanged combined-context v10 arm as identical to a case-only one-call baseline: those are different input conditions.

| Comparison | What differs | What it can establish |
|---|---|---|
| v10 case-only vs v11 case-only | Joint generation versus extract/bind/select/generate package | Observed unsupported propositions, coverage, attribution and cost; not the isolated effect of each new stage |
| Original v10 combined-context vs case-only v10 + isolated augmentation | Source exposure/augmentation placement | More direct test of supplied-RAG semantic leakage without the extraction confound |
| Original v10 vs v11 + isolated augmentation | Both decomposition and context isolation | End-to-end architecture comparison; cannot assign causality to either component alone |
| Optional factorial: joint/claim-first × combined/isolated | Separate two treatments | Stronger mechanism attribution if annotation/cost permits |

Hold model/version, source/OCR snapshot, output target, decoding, source order, external-context packet and retry policy fixed as applicable. Count schemas, intermediate outputs, extra calls, failure and rejection rates. Judge actual summary propositions independently, not only the method's own claims. For source leakage, use relevant external descriptions of unestablished events and assess unsupported assertions/false case attribution; do not claim access to a model's internal causal reasoning from one output.

Multi-document provenance claims require actual multiple-document tests including overlapping/conflicting sources. OCR propagation requires clean verified transcription versus cached OCR input and critical-error annotation. Good citation existence does not prove either. This can support a conservative applied study; neither implementation resemblance to CAMS nor a new version number establishes novelty.

# 14. FINAL GO / NO-GO

**GO WITH LIMITED PHASE 1.** Preserve v10 and public v3; introduce small internal records, exact pre-binding, a transparent budget selector and a separate case-only generation call. Evaluate failure rate, retained coverage, semantic support and cost before promoting it to the default. Then restore optional technical enrichment with an immutable augmentation contract. Cross-document semantic clustering waits for real input requirements and evaluation evidence.

No production code was edited. This document and the continuity ledger are the only audit changes. Implementation remains proposed, not authorized by this audit request.
