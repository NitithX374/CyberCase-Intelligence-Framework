# Case Analysis: Source units and canonical claims

Updated 2026-10-06 from the current working tree. This contract supersedes the
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
     ├→ GLiNER2 → Parties / Timeline / Impacts → display and report
     └→ Judgement → summary + gaps + conditional MITRE associations
     → reference binding → CaseAnalysisTrace → UI / deterministic report
```

Gap assessment and the bounded follow-up policy still run before expensive analysis.
MITRE context is external interpretation, never a Case Source, and is not supplied
to Reading. GLiNER2 is local extraction from Claims, with no extra generation call,
store or migration. Extracted views never enter Judgement or chat.
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
            "S1:U001-baf6fdfbbd4780cb"
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
      "contradicting_citations": []
    }
  ]
}
```

## Backend binding and canonical claims

`analysis/write.py:reading_from` creates internal `CaseAnalysisClaim` objects and
derives unique supporting/contradicting source-ID lists from selected citations.
`trace/evidence_binding.py` resolves each selected ID deterministically, materializes
one citation per unit, and derives original text, offsets, filename, document ID,
page locator and surrounding context. Selected IDs never authorize model-written
source text. Metadata and reasoning summaries are not supplied as generated state.

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
contain GLiNER2-derived display views linked to canonical Claims. UI Details keeps
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
the real `backend/experiments/analysis_arms.py` baseline consumer. They are not alternative
production Reader contracts. The stopped projection-validation research artifacts
remain frozen against the earlier implementation; this refactor does not rerun or
adapt that experiment.

## GLiNER2-derived views

`analysis/views.py` extracts all three views from each Claim with at least one
resolved supporting citation. Unresolved Claims remain available to Judgement
under their existing status but are excluded from extraction. Source truth and
claim-to-source semantic support are not checked by this extraction stage.

The backend verifies every selected field against its original Claim offsets,
then assigns `claim_ids` and `field_spans`. For example:

```json
{
  "name": "John",
  "role": null,
  "claim_ids": ["A-01"],
  "support": "bound",
  "projection_grounding": null,
  "field_spans": {"name": {"claim_id": "A-01", "start": 0, "end": 4}}
}
```

For `A-01 = "John sent an email."`, no role is fabricated by the backend. A role
selected by the extractor must also be an exact Claim span. A null role means
no role was selected, not that the Claim definitely has none. This does not prove
the extractor associated that role with the correct name: the original linked
Claim context is displayed for review. Timeline rows require both a time and an
event selection; event/impact display text preserves the complete Claim, including
attribution and uncertainty. Identical display rows merge their claim IDs; alias
resolution and cross-claim entity inference are not introduced.

`CaseClaimSpan(claim_id, start, end)` points inside the Claim, not inside a Source.
Source citations still belong only to Claims. Derived views have no new evidence
citations, no semantic verdict and no role in the Judgement/chat factual payload.
Historical saved projection verdicts remain readable separately.

The pinned model is `fastino/gliner2-multi-v1` revision
`ce747d79a8e362d3dee0b0b26d1201f7f1a8615a`, with `gliner2==1.3.2`. This existing
library version works with the project's Transformers 5 runtime; moving to the
newer GLiNER2.5 package would require a separate dependency decision. Official
references: [GLiNER2](https://github.com/fastino-ai/GLiNER2) and
[multilingual checkpoint](https://huggingface.co/fastino/gliner2-multi-v1).

Provision once from `backend`:

```powershell
python scripts/copy_case_view_weights.py
```

The ignored local `gliner_case_views/` folder carries a pinned manifest and weights;
Compose mounts it read-only. Runtime never downloads a checkpoint or substitutes
another extractor. Missing assets, pin mismatches and malformed spans fail explicitly.
Default configuration: `CASE_VIEW_MODEL_PATH=gliner_case_views`,
`CASE_VIEW_DEVICE=cpu`, `CASE_VIEW_THRESHOLD=0.5`. Thai text uses the existing
PyThaiNLP `newmm` tokenizer with exact offsets; other text uses native GLiNER2
word splitting. Extraction runs in a worker thread with serialized model calls.

`view_extraction` records model/revision, library version, device, threshold,
processed/excluded claim IDs and duration. Functional English/Thai probes live in
`tmp/gliner-case-views/`; missed fields and incorrect role association remain model
quality limitations. These probes do not establish extraction precision/recall,
semantic correctness or downstream summary improvement.

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
`tmp/claims-reader-refactor/` and `tmp/gliner-case-views/`. Model API-backed Reading/Judgement quality and final
factual correctness are not inferred from contract/regression tests.
