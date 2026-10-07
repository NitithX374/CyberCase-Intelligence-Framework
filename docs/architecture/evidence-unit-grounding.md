# Case Analysis: Source units and canonical claims

Updated 2026-10-07 from the current working tree. This contract supersedes the
projection-generating architecture in commit `ca7fc6d6`.

The Reader constructs contextual claims across a whole Case. Claims are its only
factual output. The backend binds selected Source units to original text; later
stages reason over claims rather than independently generated factual structures.

## Flow and ownership

```text
Case → N Documents / Narratives / answered follow-ups
     → deterministic Source units
     → one whole-Case Reading call → claims + selected unit IDs
     → deterministic binding → canonical claims with source provenance
     ├→ batched LLM extraction → Parties / Timeline / Impacts → display and report
     └→ Judgement → summary + gaps + conditional MITRE associations
     → reference binding → CaseAnalysisTrace → UI / deterministic report
```

Gap assessment and the bounded follow-up policy still run before expensive analysis.
MITRE context is external interpretation, never a Case Source, and is not supplied
to Reading or the view extractor. Extraction and Judgement run independently in
parallel over the same canonical Claims after binding. The extraction is one
additional structured provider stage, without a new store or migration. Derived
views are presentation only and never enter Judgement or chat.
The editable [architecture diagram](evidence-unit-grounding.drawio) shows this flow.

## Source unit contract

The internal class name remains `EvidenceUnit`; API keys remain stable. Product
labels use **Source** and **Source unit**.

```python
EvidenceUnit(unit_id: str, source_id: str, start: int, end: int, text: str)
```

`text == source.text[start:end]`. Units partition all characters, including
whitespace, and reconstruct the exact source when joined. Sentence/span machinery
is the initial segmenter; oversized spans split at the existing quotation-size
bound. This supports prose, Thai, OCR fragments, bullets and other extracted text.

IDs are source-scoped, for example `S1:U001-baf6fdfbbd4780cb`. The suffix is the first
16 lowercase hex characters of SHA-256 over `evidence_units_v1 + NUL + source.text`.
Identical source/text gives identical IDs; other sources cannot collide merely
because they also contain U001. Changed text makes earlier IDs stale. Segmentation
changes require a version bump. Persisted Case source revisions remain independent.

Units are computed at analysis time by `sources/evidence.py`, without a new table.
Document identity, filename, extraction method, verification status, warnings and
page offsets remain source provenance. OCR is not converted into trusted truth.

Reading sees source-scoped aliases `U001`, `U002`, etc., with each unit's exact
text. Its payload keeps the original `source_id` and document/quality header, but
does not repeat canonical IDs, revision hashes or offsets on every unit.
`analysis/reading_sources.py` captures the source revisions before the model call.
The same request-owned address book expands selected aliases to canonical IDs
before binding. It never decodes an old reply using newly read source text.
Offsets, page provenance and revision checks remain backend-owned; stored traces
continue to use full canonical IDs. `U001` under S1 and S2 addresses different
content. A valid local ID paired with the wrong existing source is structurally
resolvable and still requires semantic assessment of the selected content.

## Reader provider contract

`CaseProviderReadingReply` contains exactly `version` and `claims`. `CaseReadingClaim`
contains exactly claim ID/type/text/epistemic status and two citation lists. Each
selected citation contains only `source_id` and `evidence_unit_ids`.

- `claim_type`: `reported` or `unknown`. Reported covers attributed and qualified
  source assertions. Unknown is uncertainty explicitly stated in a source.
- `epistemic_status`: `reported`, `suspected`, `contradicted`, `not_established`,
  or `unknown`. The backend owns `not_confirmed` for unresolved reported claims.
- Every claim selects at least one supporting citation. Each citation selects
  1–64 unit IDs; each role has at most 64 citation groups; a reading has 0–64 claims.
- Extra fields fail provider validation: copied quotations, offsets, source-ID
  arrays, reasoning summaries, metadata, scores, summary, projections, gaps or MITRE.

The prompt preserves material attribution, qualification, dates, quantities,
conflicts and OCR uncertainty without producing independent party/timeline/impact
objects or analytical inferences. Higher-level interpretation belongs to Judgement.
Explicit participant roles stay in contextual Claims, and message content remains
attributed to the person reporting it. Relative dates/pronouns require selecting
the unit establishing the referent as well as the event unit; this prompt contract
is not a deterministic semantic guarantee.

Prompt-JSON Reading input is minified without changing source text. The optional
`reading_thinking_tokens` pipeline field / `CASE_READING_THINKING_TOKENS` setting
controls Reading alone: 0 disables reasoning, otherwise at least 1,024 tokens are
required. Historical configs without this field inherit `thinking_tokens`.
Compose retains 8,192 for Reading; Judgement and assessment retain their existing
shared budgets. The visible output budget is unchanged. The two-fixture pilot
found faster reasoning-off output but a strict-schema failure, so reasoning-off
is not promoted to the default. Provider-reported reasoning can exceed the
requested budget; the setting is not a verified hard provider-side limit.

### One document

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
          "unit_id": "U001",
          "text": "John is the victim.\n"
        },
        {
          "unit_id": "U002",
          "text": "At 13:00, the server was encrypted."
        }
      ]
    }
  ],
  "followup_history": []
}
```

### Multiple documents

One bundle, one Reading call; no per-document summaries or merge pipeline.

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
          "unit_id": "U001",
          "text": "John is the victim.\n"
        },
        {
          "unit_id": "U002",
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
          "unit_id": "U001",
          "text": "The server encryption interrupted payroll."
        }
      ]
    }
  ],
  "followup_history": []
}
```

### Model reply

A-02 selects the time/event from Document A and its stated impact from Document B.

```json
{
  "version": "case_analysis_trace_v1",
  "claims": [
    {
      "claim_id": "A-01",
      "claim_type": "reported",
      "text": "John is the victim.",
      "epistemic_status": "reported",
      "supporting_citations": [
        {
          "source_id": "S1",
          "evidence_unit_ids": [
            "U001"
          ]
        }
      ],
      "contradicting_citations": []
    },
    {
      "claim_id": "A-02",
      "claim_type": "reported",
      "text": "The server was encrypted at 13:00, and its encryption interrupted payroll.",
      "epistemic_status": "reported",
      "supporting_citations": [
        {
          "source_id": "S1",
          "evidence_unit_ids": [
            "U002"
          ]
        },
        {
          "source_id": "S2",
          "evidence_unit_ids": [
            "U001"
          ]
        }
      ],
      "contradicting_citations": []
    }
  ]
}
```

## Backend binding and canonical claims

`analysis/write.py:reading_from` first expands Reader aliases with the captured
`ReadingSources` address book, then creates internal `CaseAnalysisClaim` objects and
derives unique supporting/contradicting source-ID lists from selected citations.
`trace/evidence_binding.py` resolves each selected ID deterministically, materializes
one citation per unit, and derives original text, offsets, filename, document ID,
page locator and surrounding context. Selected IDs never authorize model-written
source text. Metadata and reasoning summaries are not supplied as generated state.

Malformed aliases remain unresolved. Well-formed ordinals outside the captured
source's units are diagnosed as `unknown_unit`; unknown sources, duplicates,
canonical cross-source IDs and stale revisions retain existing diagnostics.
Historical canonical citations and legacy quotes keep their existing binding
paths. Short aliases are transport-only: replay requires the matching request's
address book, while historical persisted traces need no alias decoding.

```json
{
  "claim_id": "A-02",
  "claim_type": "reported",
  "text": "The server was encrypted at 13:00, and its encryption interrupted payroll.",
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
        1
      ],
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
      "tolerated_differences": [],
      "review_flags": []
    }
  ],
  "contradicting_citations": [],
  "unverified_citations": [],
  "invalid_evidence": []
}
```

Internal canonical fields are claim ID/type/text/status, derived source lists,
resolved supporting/contradicting citations, unresolved-pointer diagnostics and
legacy advisory locations. `reasoning_summary` remains nullable only because stored
findings/reports contain it; new Reader output cannot generate it and model inputs
omit it. Internal `analytical_inference` remains readable for historical records.

Answered QA inputs use the same segmenter/index with the supplied `qa_id`, for
example `QA-03:U001-<answer fingerprint>`. Unanswered exchanges are omitted. QA
answers remain conversation rows and recorded follow-up snapshots, not native
CaseSource rows; they do not change native `source_revision`.

### Invalid references and states

| State | Meaning |
|---|---|
| `direct` | A valid selected ID resolved to its original Source unit. |
| `recovered` | A stored legacy quote was located by the existing matcher. |
| `unresolved` | No reliable supporting location resolved. |
| `not_confirmed` | A reported claim has no resolved supporting citation. This does not establish that it is false. |
| `bound` | Known linked claims all have resolved supporting citations. |
| `mixed` | Some known linked claims have supporting citations and others do not. |
| `unbound` | Known linked claims exist but none has a supporting citation. |
| `no_claim` | No known linked claim remains. |

Malformed shapes fail decoding/validation and the existing bounded provider retry.
Unknown sources, malformed/stale/unknown units, source-unit mismatch, blank units and
duplicates are diagnosed in `invalid_evidence`; they do not become direct citations.
Duplicate references materialize original content once per claim and are counted
as invalid generated references. A claim can still carry other valid references.

These states describe structural resolution, not source truth or semantic support.
No claim-to-source semantic verifier or summary entailment verifier is added.

## Judgement, historical views and report

`reading_payload` contains only `claims`. Source-ID lists, old reasoning summaries,
unverified pointers, review flags and surrounding context are omitted from model
input. Selected units' original text remains available through resolved citations.
Judgement also receives follow-up history and optional external MITRE context; it
must end every factual summary sentence with existing claim IDs. Summary-reference
binding and technique/context checks remain deterministic and unchanged.

No separate parties, timeline or impacts enter Judgement or chat. New joined traces
contain LLM-derived presentation views linked to canonical Claims. UI Details keeps
full Claim context and links to Findings. Reports render those saved views and
Findings without a new generation or extraction call.

Historical CaseAnalysisTrace/report fields and their saved `projection_grounding`
remain because existing UI/report snapshots consume them. Their linked claim IDs
are filtered deterministically. Saved checks are historical provenance, not a new
runtime verification stage. No independent factual authority is created from them.
The obsolete projection-specific verifier and its tests are removed. Generic NLI
continues to serve legacy meaning-pointer recovery, whose passage remains advisory
and never promotes an unresolved claim into supported evidence.

The single-call `CaseProviderAnalysis` and legacy provider-quote schema remain for
the real `research/analysis_baseline/run.py` baseline consumer. They are not alternative
production Reader contracts. The stopped projection-validation research artifacts
remain frozen against the earlier implementation; this refactor does not rerun or
adapt that experiment.

## LLM-derived presentation views

Canonical factual authority remains `Source → EvidenceUnit → Claim`. After the
existing binding step, `analysis/views.py` receives exactly the canonical Claim
set passed into Judgement. Production binding validates addresses and reproduces
Source text; it does not semantically verify every Claim. There is no separate
view-admission rule. Unresolved Claims therefore retain their existing status and
can appear in the extractor input, with corresponding `unbound` view support.

One compact request batches the whole Case's Claims, including Claims supported
by multiple documents or answered follow-ups:

```json
{"claims":[{"claim_id":"A-01","text":"Alice transferred $500 to Company A on 12 May 2026."}]}
```

The native Pydantic schema reuses existing provider row models and the public
`claim_ids` spelling for what conceptually means `source_claim_ids`:

```text
DerivedParty(name: str, role: str | null, claim_ids: nonempty list[str])
DerivedTimelineEvent(time: str | null, event: str, claim_ids: nonempty list[str])
DerivedImpact(description: str, claim_ids: nonempty list[str])
DerivedCaseViewsReply(parties: list[DerivedParty], timeline: list[DerivedTimelineEvent], impacts: list[DerivedImpact])
```

`time` is the existing combined date/time field, not a new normalized date. It
holds only the explicit expression, or null when neither date nor time is stated.
All three arrays are required, with at most 64 rows each. Role/time keys are
required but nullable. Field lengths follow the existing public row limits;
links require 1–64 strings. Extra fields are forbidden. Source metadata, hashes,
offsets, EvidenceUnit IDs, MITRE context and Judgement output are not sent.

Example reply:

```json
{
  "parties": [
    {"name":"Alice","role":null,"claim_ids":["A-01"]},
    {"name":"Company A","role":null,"claim_ids":["A-01"]}
  ],
  "timeline": [{"time":"12 May 2026","event":"Alice transferred $500 to Company A.","claim_ids":["A-01"]}],
  "impacts": []
}
```

The concise generation contract requires explicit content, preserves attribution,
uncertainty, names and values, and prohibits inferred roles, loss from mere risk,
alias merging, summaries, gaps, legal reasoning and ATT&CK mapping. It is a
generation instruction, not a semantic correctness guarantee. Validation checks
schema and links only. A row with any unknown ID is entirely dropped and logged;
valid neighbors survive and duplicate links are deduplicated. There is no second
LLM/NLI verifier, string-alignment recovery or fabricated field span/confidence.
Backend rows reuse `CaseInvolvedParty`, `CaseTimelineItem` and `CaseImpactItem`;
`claim_ids` lead to Claims and their existing Source citations. `field_spans` stay
empty and `projection_grounding` null on new views. Binding support retains its
existing structural meaning.

Traceability is `Derived view → claim_ids → Claim → EvidenceUnit → Source`.
Full linked Claim context remains visible in UI and party Report rows; report
finding references preserve traceability for all three views. Unknown time is
shown as unspecified, never the literal string None. Views are not authoritative
factual records and are never supplied to Judgement or chat.

The ordinary UI hides raw Claim/unit IDs and model/verifier diagnostics. A compact
collapsed preparation panel explains Sources -> Findings -> Summary and case
details. Related Findings are collapsed by default; opening them shows linked
Claim text and a link to the original Finding. Source filename/page inspection,
unresolved-link notices and historical semantic cautions remain available.
Backend IDs, offsets, provenance and structural counters are unchanged.

Extraction and Judgement begin concurrently after the claim set is established.
The stage uses the configured analysis model/provider order with thinking disabled,
temperature zero and at most 4,096 output tokens. An overall deadline of at most
60 seconds includes existing transport/whitespace retries. Empty Claims skip the
provider. Schema, transport, timeout or unexpected extraction failure yields all
three lists empty, an explicit warning/status, and normal independent Judgement.
External cancellation propagates; Judgement failure cancels outstanding extraction.

The existing trace JSON stores `view_extraction.method=llm`, model, input IDs,
duration, completed/failed/skipped status, warning code and dropped-item count.
There is no new table or revision system. GET/UI/Report reuse the stored snapshot;
a new analysis reruns extraction, without a cross-analysis cache.

Local view-extractor loading, per-Claim inference, exact-field recovery, model
provisioning and the Compose runtime/config/mount are removed. Model assets are
retained. Historical method metadata, offsets, thresholds and saved
projection verdicts remain readable. Torch/Transformers/PyThaiNLP remain for the
encoder gate, generic advisory NLI and source segmentation. NLI research artifacts
and the stopped projection study are not modified or rerun.

`CaseViewExtraction.method` is bounded descriptive text rather than a loader
enum, with `legacy` used for saved records missing the field. New extraction
explicitly writes `llm`; reading an old method name does not require its model.

## Structural introspection and verification

Existing counters remain: selected/resolved/invalid IDs, ID-resolution rate, claims
with direct or recovered support and claims with no resolved supporting citation.
Resolution rate is resolved references divided by all generated ID references,
including invalid and duplicate references. It is not semantic citation accuracy.

Tests cover claims-only acceptance/extra-field rejection, exact-span segmentation,
multi-unit/multi-document/QA binding, invalid-pointer integrity, claims-only Judgement,
summary references, conditional MITRE, unchanged gap/follow-up behavior, deterministic
reports, historical serialization and legacy quote/meaning recovery.

Verification receipts and generated examples for this change are under
`tmp/claims-reader-refactor/`, `tmp/gliner-case-views/`, `tmp/gliner25-upgrade/` and
`tmp/nuextract-integration/` and `tmp/llm-case-views/`. Model API-backed Reading/Judgement quality and final
factual correctness are not inferred from contract/regression tests.
