# Case Analysis Evidence Unit grounding

Implemented against `origin/main` **1d3c997a2b95933b2d45215c552ddf79579f875f**, fetched and inspected on 2026-10-06 before modifying application code. This checkout was fast-forwarded to that commit. Existing deletions and research/document work were preserved. The implementation preserves whole-Case analysis and requires no database migration.

## Current-main audit, before implementation

| Question | Observed flow / chosen location |
|---|---|
| Case → documents → sources | `sources/service.py` stores the uploaded file as `CaseDocument` and extracted text/provenance as a document `CaseSource`. Narratives are additional sources. Native source additions increment Case `source_revision`. |
| Multiple sources | `sources/bundle.py` builds one ordered `CaseSourceBundle(revision, sources)`. `analysis/write.py` supplies all analysable sources to a single whole-Case Reading call. |
| Provider evidence | `trace/claims.py::CaseProviderClaim` previously carried supporting/contradicting `source_id + exact_quote`, converted to `CaseAnalysisClaim`. |
| Quote resolution | `checked_reading → bound_claims → resolve_claim → resolved_citations` located/canonicalized model-written quotes and bound document pages. Unlocated quotes could retain nearest/meaning passages as advisory pointers. |
| Projection support | `item_support` checked whether known linked claims had supporting citations; `bound_references` copied that state onto parties, timeline and impacts. |
| Meaning of bound | Evidence presence alone did not establish a party's role, an event at a time, or an impact description. John sending an email could incorrectly lend `bound` to John/Attacker. |
| Segmentation | `sources/evidence.py`, at analysis time, reuses `trace/sentences.py::sentence_spans`; no ingestion/storage redesign. |
| Evidence resolution | `trace/evidence_binding.py`, called by the existing binder before Judgement. |
| Migration | None: exact source text/provenance already persist; trace/report additions are compatible JSON fields; units are reproducible. |
| Minimum scope | Reading payload/prompt, citation schemas, binding/metrics, structured support validation, focused tests; small report/UI compatibility edits and generated API types are required for new diagnostics. |

The chosen structured-grounding strategy is **Option B**, reinforced by **Option A**. Main already contained a pinned multilingual mDeBERTa NLI loader for the meaning pointer. Reusing it to validate linked-claim text against a complete projection closes the independent semantic hole without another generation stage, new model/library, or pipeline. Reading is also instructed to write claims that explicitly contain every projected fact.

## Final Evidence Unit contract

```python
@dataclass(frozen=True)
class EvidenceUnit:
    unit_id: str
    source_id: str
    start: int
    end: int
    text: str
```

Offsets are Python Unicode code-point indices, start inclusive/end exclusive. For every unit, `unit.text == source.text[unit.start:unit.end]`. Ordered units partition and reconstruct the complete source, including leading/trailing whitespace and line separators. Empty text has no units; whitespace-only units cannot serve as evidence. Oversized sentence/fragments are deterministically split into at most 2,000-character units to fit the existing stored-citation bound. Units need not be grammatical sentences: OCR fragments, bullets, log lines and rows use the same abstraction.

IDs are globally scoped: `S1:U001-baf6fdfbbd4780cb`. The suffix is the first 16 lowercase hex characters of SHA-256 over `evidence_units_v1 + NUL + full exact source text`. Unit numbering begins at one with at least three digits. The same source/text and segmentation implementation generate the same IDs; another source cannot collide merely because its local unit number is the same. Changed source text produces stale IDs. A future change to segmentation must increment the version. Existing Case source-revision checks remain in force independently of these fingerprints.

Units are computed at analysis time, not persisted in a new table. The source owns original text, extraction method, verification status, warnings, page spans, document ID and filename. Resolved citations retain original offsets/text and document identity; the existing page-span bounds/order validation and locator derive page numbers when available and safe. OCR uncertainty remains source provenance.

## Provider claim citation contract

Supporting and contradicting citation arrays contain source-grouped references:

```json
{"source_id": "S1", "evidence_unit_ids": ["S1:U001-baf6fdfbbd4780cb", "S1:U002-baf6fdfbbd4780cb"]}
```

`source_id` is the Case Source identity; unit IDs address its content. A reference may contain up to 64 unit IDs, and each role may contain up to 64 groups. The backend materializes one citation per resolved unit, with room for every selected unit; stored traces are not silently truncated. An invalid provider shape fails existing reply validation/retry rather than being silently clipped. Model-provided quotation/offset fields accompanying ID references are ignored. The provider schema still accepts legacy `source_id + exact_quote` for older callers, but the Reading prompt and normal payload require Evidence Unit selection. Parties, timeline, impacts and summary receive no independent evidence citations.

## One-document Reading payload

The examples below were generated from the implemented payload/resolver using fictional sources. They are illustrative input/output contracts, not an API-backed model run.

```json
{
  "response_language": "english",
  "source_revision": 4,
  "case_sources": [
    {
      "source_id": "S1",
      "source_kind": "document",
      "document": {
        "document_id": "D1",
        "filename": "statement.pdf",
        "extraction_method": "ocr",
        "verification_status": "machine_read",
        "warnings": [
          "OCR text requires review"
        ]
      },
      "evidence_version": "evidence_units_v1",
      "evidence_units": [
        {
          "unit_id": "S1:U001-baf6fdfbbd4780cb",
          "start": 0,
          "end": 20,
          "text": "John is the victim.\n"
        },
        {
          "unit_id": "S1:U002-baf6fdfbbd4780cb",
          "start": 20,
          "end": 55,
          "text": "At 13:00, the server was encrypted."
        }
      ]
    }
  ],
  "followup_history": []
}
```

## Multiple-document Reading payload

One Case, two sources, one Reading call; no per-document summaries or merge stage.

```json
{
  "response_language": "english",
  "source_revision": 4,
  "case_sources": [
    {
      "source_id": "S1",
      "source_kind": "document",
      "document": {
        "document_id": "D1",
        "filename": "statement.pdf",
        "extraction_method": "ocr",
        "verification_status": "machine_read",
        "warnings": [
          "OCR text requires review"
        ]
      },
      "evidence_version": "evidence_units_v1",
      "evidence_units": [
        {
          "unit_id": "S1:U001-baf6fdfbbd4780cb",
          "start": 0,
          "end": 20,
          "text": "John is the victim.\n"
        },
        {
          "unit_id": "S1:U002-baf6fdfbbd4780cb",
          "start": 20,
          "end": 55,
          "text": "At 13:00, the server was encrypted."
        }
      ]
    },
    {
      "source_id": "S2",
      "source_kind": "document",
      "document": {
        "document_id": "D2",
        "filename": "logs.pdf"
      },
      "evidence_version": "evidence_units_v1",
      "evidence_units": [
        {
          "unit_id": "S2:U001-d663290f1d375ac5",
          "start": 0,
          "end": 42,
          "text": "The server encryption interrupted payroll."
        }
      ]
    }
  ],
  "followup_history": []
}
```

## Example model reply

A-02 consolidates the event/time in Document A and its impact in Document B. Only claims carry evidence references.

```json
{
  "version": "case_analysis_trace_v1",
  "claims": [
    {
      "claim_id": "A-01",
      "claim_type": "reported",
      "text": "John is the victim.",
      "epistemic_status": "reported",
      "supporting_source_ids": [
        "S1"
      ],
      "contradicting_source_ids": [],
      "supporting_citations": [
        {
          "source_id": "S1",
          "evidence_unit_ids": [
            "S1:U001-baf6fdfbbd4780cb"
          ]
        }
      ],
      "contradicting_citations": [],
      "reasoning_summary": null
    },
    {
      "claim_id": "A-02",
      "claim_type": "reported",
      "text": "At 13:00, the server was encrypted, interrupting payroll.",
      "epistemic_status": "reported",
      "supporting_source_ids": [
        "S1",
        "S2"
      ],
      "contradicting_source_ids": [],
      "supporting_citations": [
        {
          "source_id": "S1",
          "evidence_unit_ids": [
            "S1:U002-baf6fdfbbd4780cb"
          ]
        },
        {
          "source_id": "S2",
          "evidence_unit_ids": [
            "S2:U001-d663290f1d375ac5"
          ]
        }
      ],
      "contradicting_citations": [],
      "reasoning_summary": null
    }
  ],
  "involved_parties": [
    {
      "name": "John",
      "role": "the victim",
      "claim_ids": [
        "A-01"
      ]
    }
  ],
  "timeline": [
    {
      "time": "13:00",
      "event": "the server was encrypted",
      "claim_ids": [
        "A-02"
      ]
    }
  ],
  "impacts": [
    {
      "description": "Payroll was interrupted.",
      "claim_ids": [
        "A-02"
      ]
    }
  ]
}
```

## Deterministically resolved claim

The backend copies these spans from the sources; it performs no model-quote search on this path. The first citation binds to page 2 using its selected offset. The second preserves document identity even without page provenance.

```json
{
  "claim_id": "A-02",
  "claim_type": "reported",
  "text": "At 13:00, the server was encrypted, interrupting payroll.",
  "epistemic_status": "reported",
  "supporting_source_ids": [
    "S1",
    "S2"
  ],
  "contradicting_source_ids": [],
  "supporting_citations": [
    {
      "source_id": "S1",
      "exact_quote": "At 13:00, the server was encrypted.",
      "evidence_unit_ids": [
        "S1:U002-baf6fdfbbd4780cb"
      ],
      "pointer_state": "direct",
      "start": 20,
      "end": 55,
      "document_id": "D1",
      "filename": "statement.pdf",
      "page_numbers": [
        2
      ],
      "context": null,
      "tolerated_differences": [],
      "review_flags": []
    },
    {
      "source_id": "S2",
      "exact_quote": "The server encryption interrupted payroll.",
      "evidence_unit_ids": [
        "S2:U001-d663290f1d375ac5"
      ],
      "pointer_state": "direct",
      "start": 0,
      "end": 42,
      "document_id": "D2",
      "filename": "logs.pdf",
      "page_numbers": [],
      "context": null,
      "tolerated_differences": [],
      "review_flags": []
    }
  ],
  "contradicting_citations": [],
  "unverified_citations": [],
  "invalid_evidence": [],
  "reasoning_summary": null
}
```

## Cross-document claims and follow-up answers

One claim can reference several units within one source and/or several sources in the same bundle. Every selected unit is checked against its named source; there is no shared local-unit namespace or independent document analysis. Sources remain consolidated at the Case level by Reading.

Answered follow-ups are exposed through the same segmentation/resolution functions under `QA-03:U001-<answer fingerprint>`. Short answers normally produce one unit; longer answers can produce more. Unanswered exchanges are omitted. QA text remains a persisted conversation message and a recorded analysis follow-up snapshot, not a new `CaseSource` row, and it does not increment native `source_revision`.

## Structured projection grounding

The backend constructs a hypothesis containing the **complete** structured statement:

| Projection | Hypothesis | Premise |
|---|---|---|
| Party | `John is Attacker.` (Thai uses the name-role relation in Thai) | Only texts of its linked grounded claims |
| Timeline | `At 13:00, the server was encrypted` | Only texts of its linked grounded claims |
| Impact | The complete impact description | Only texts of its linked grounded claims |

No raw source text, unrelated claims or MITRE context enter this test. All referenced claims must exist, have resolved supporting evidence, and retain `epistemic_status=reported`; otherwise the result is explicitly unassessed. The existing pinned NLI model checks the joint premise/hypothesis with no truncation. Entailment must be the winning label and at least 0.5. The backend stores verdict, reason, model identity and entailment for audit. NLI is a fallible support classifier, not legal or factual confirmation.

Rejected and unassessed projections remain in the final trace and report, with separate semantic notes. They are excluded from Judgement's factual projection input and from the analysis projections supplied to chat. Supported projections still link only claim IDs. Summary continues to derive support through claims; this change does not add a summary semantic verifier or a new claim-to-original-evidence entailment stage.

## Exact state semantics

| Field/state | Meaning |
|---|---|
| `support=bound` | At least one known linked claim, and every known linked claim carries resolved supporting evidence. It says nothing about projection derivability or source truth. |
| `support=mixed` | Some known linked claims have resolved supporting evidence and others do not. |
| `support=unbound` | Known linked claims exist, but none has resolved supporting evidence. |
| `support=no_claim` | No known linked claim remains. Unknown IDs are filtered; projection validation independently records `unknown_claim` before filtering. |
| `projection_grounding.verdict=supported` | The complete projection passed linked-claim NLI entailment under the stated threshold; not confirmation of events or guilt. |
| `not_supported` | NLI did not establish entailment (neutral, contradiction, or low entailment). This does not mean the statement has been proven false. |
| `unassessed` | No/unknown/unbound/qualified linked claim, missing model, or an oversized pair. The reason is recorded, with model identity when available. |
| `pointer_state=direct` | A valid current Evidence Unit ID was deterministically resolved to original source content. |
| `pointer_state=recovered` | A legacy model-written quote was located/canonicalized by the existing matcher. It is distinguishable from ID addressing, even if the old quote happened to match exactly. |
| `pointer_state=unresolved` | A draft or invalid pointer has no resolved evidence location. Invalid IDs are recorded individually with reasons. |
| Claim `not_confirmed` | Existing epistemic demotion of a reported claim with no resolved supporting evidence; advisory passages do not promote it. |

Historical citations default to recovered and historical projections default to no semantic verdict. Reading old rows does not invent validation. Public pointer-state fields remain optional for historical API consumers. The trace version and stored-report format remain compatible.

## Invalid pointers and legacy recovery

The resolver rejects `unknown_source`, `malformed_id`, `cross_source`, `stale_id`, `unknown_unit`, `empty_unit` and `duplicate_id`. Duplicates within a claim, including across supporting/contradicting roles, never produce duplicate materialized citations. The same unit may validly support different claims. Invalid refs remain in `invalid_evidence`; nonduplicate unresolved pointers also appear in `unverified_citations` for display/advisory recovery. A valid subset remains resolved even if other IDs are invalid. A claim with no resolved supporting evidence is retained as not-confirmed, not silently deleted.

Legacy quote locating, folded/relaxed/OCR-tolerant matching, ellipsis handling, context, differences and review flags are preserved in `trace/quote_binding.py` and the unchanged quote/sentence machinery. A located legacy quote produces recovered evidence. Nearest and NLI meaning passages remain **advisory unresolved pointers**, as on main: they do not become supporting citations, improve direct-resolution metrics, change claim status or reach model factual input. Invalid IDs without a trustworthy quote can receive only that existing advisory meaning-pointer behavior when eligible. Recovery is never silently presented as direct addressing. No recovery algorithm was redesigned.

## Grounding introspection metrics

`CaseGroundingReport` adds `evidence_ids_claimed`, `evidence_ids_resolved`, `evidence_ids_invalid`, `evidence_id_resolution_rate`, `claims_with_direct_evidence`, `claims_with_recovered_evidence`, and `claims_without_resolved_evidence`.

Resolution rate is `resolved ID references / all model-generated ID references`, counting supporting and contradicting refs; duplicates are invalid. The same unit selected for different claims counts as a separate reference each time. Raw references are counted before duplicate claim removal. Zero ID references produces `null`, not a fabricated 100%. Claim metrics count supporting evidence; a claim may have both direct and recovered evidence and be counted in both categories. Existing citation/meaning-pointer counters are retained. Structural resolution does not measure semantic citation correctness or factual accuracy.

## Files changed

| Responsibility | Paths |
|---|---|
| Evidence representation | `backend/app/sources/evidence.py` |
| Citation/claim contracts | `backend/app/trace/citations.py`, `claims.py`, `trace.py` |
| Binding/metrics | `backend/app/trace/bind.py`, `evidence_binding.py`, `quote_binding.py`, `grounding.py` |
| Projection validation | `backend/app/trace/projection.py`, `support.py` |
| Reading/Judgement | `backend/app/analysis/write.py`, `reading_prompt.py`, `prompts.py` |
| Downstream compatibility | `backend/app/chat/compose.py`; `backend/app/reports/display.py`, `schemas.py`, `templates/case_report.html.j2` |
| Frontend contracts/navigation/notes | `frontend/src/lib/api/generated/openapi.ts`, `src/lib/api/types.ts`; `src/features/analysis/projectionNote.ts`, `overview.ts`, `types.ts`, `CaseFindingsSection.tsx`; `src/features/citations/sourceRefs.ts` |
| New backend tests | `backend/tests/test_evidence_units.py`, `test_evidence_binding.py`, `test_evidence_pipeline.py`, `test_evidence_report.py`, `test_projection_grounding.py` |
| Existing backend tests adapted | `backend/tests/test_analysis_write.py`, `test_claims_only_judgement.py`, `test_case_workflow_http_postgres.py`, `test_item_support.py` |
| Frontend tests | `frontend/src/test/features/analysis/projectionNote.test.ts`, `CaseFindingsSection.test.tsx`; `src/test/features/citations/evidenceOffsets.test.ts` |
| Architecture docs | `CLAUDE.md`, `backend/ARCHITECTURE.md`, `backend/README.md`, `frontend/README.md`, this document and `evidence-unit-grounding.drawio` |

No SQLAlchemy/Alembic, external RAG, MITRE concept, ingestion, dependency or provider-transport change. The existing source/claim contracts, binder entrypoints and legacy `write_request` entrypoint remain compatible. Quote recovery helpers belong to `trace/quote_binding.py`; chat and legacy tests import them there rather than through the binder. The retired quote-locator prompt constant is removed because Reading now selects Evidence Unit IDs. Frontend changes are small diagnostic/navigation adaptations, not a redesign.

## Validation and compatibility limits

- Full backend suite in a disposable Linux container, mounted current source/tests read-only, with an isolated PostgreSQL 16 database: **1,082 passed, 7 skipped, 2 subtests passed**. Includes native PDF rendering, schema/migration parity and PostgreSQL workflow tests. The seven real-model tests skip because the pinned model folder is absent in that disposable image. Receipt: `tmp/evidence-unit-refactor/backend-final.log`.
- Full frontend Vitest: **51 files / 361 tests passed**; the subsequently added invalid-ID rendering test and affected suites: **3 files / 20 tests passed**. Receipts: `tmp/evidence-unit-refactor/frontend-tests.log` and the focused command output.
- Ruff lint/format checks on all 25 changed/new Python files, targeted frontend Prettier, and `git diff --check` passed.
- `npm run generate:api-types`, `npm run check:api-types`, `npx tsc --noEmit`, `npm run lint`, and `npm run build` passed. Build receipt: `tmp/evidence-unit-refactor/frontend-build.log`.
- Real cached pinned NLI CPU smoke: **6/6 expected verdicts** (three mismatch negatives, three complete-relation positives). Receipt: `tmp/evidence-unit-refactor/nli-projection-smoke.json`; no provider API, download or training. This is bounded regression evidence, not an accuracy/calibration benchmark, particularly for Thai/legal cases.
- Focused backend tests cover deterministic exact reconstruction in English/Thai/OCR/blank/Unicode fragments, source namespace and stale/invalid/duplicate IDs, multi-unit/cross-document claims, page offsets/repeated text, QA, full reading/binding/projection/judgement/join, legacy quotes, report compatibility and explicit party-role/time-event/impact mismatches.

Evidence Unit labels add Reading payload overhead; the existing native-source admission budget is unchanged. NLI validation adds local work during binding. NLI availability is now material to whether projections enter Judgement. A missing checkpoint is explicit `unassessed`, and unsupported/unassessed projection rows remain visible with notes. Pairs longer than the model's 512-token context are not truncated or treated as supported. NLI can make classification errors; direct pointers establish addresses, not correctness of claim interpretation. Claim-to-evidence and summary entailment remain generation contracts, outside this surgical refactor. Older clients that forbid extra JSON properties need regeneration; stored legacy rows remain loadable. Segmentation changes require a version bump. No deployment or live API-backed Reading call was performed. An initial host-only PDF test was blocked by missing Windows native WeasyPrint libraries; the complete Linux run passed it.

The final backend command inside the disposable validation image was:

```text
python -m pytest tests -q --tb=short -p no:cacheprovider
```

`CYBERCASE_TEST_DATABASE_URL` and `DATABASE_URL` pointed to the isolated task database, so PostgreSQL tests ran. The full frontend command was `npm test -- --reporter=dot`; the added/affected tests ran with `npm test -- --run src/test/features/analysis/CaseFindingsSection.test.tsx src/test/features/analysis/projectionNote.test.ts src/test/features/citations/evidenceOffsets.test.ts`. The existing seven real-model test skips were supplemented by the separately executed cached-model projection smoke.

## Before / after

```text
Before: Case → N Sources → Reading (claims + model quotes)
        → quote locating → claims with evidence
        → projections inherit citation presence → Judgement → Trace

After:  Case → N Sources → deterministic Evidence Units
        → whole-Case Reading (claims + selected IDs)
        → backend ID resolution → claims with original source spans
        → claim-linked projections → separate NLI support check
        → Judgement → Trace / report

Legacy: quote locating → recovered evidence;
        nearest / meaning pointers → advisory unresolved location
MITRE:  conditional external interpretation → Judgement, never Case evidence
```

[Editable before/after diagram](evidence-unit-grounding.drawio).
