# 1. Verdict

**WEAK in the persisted local data inspected.** The current pipeline lets the
Reader select evidence before any proposed semantic filter. Among 101 latest
Claims with direct EvidenceUnit IDs, 78 (77.2%) cite only one or two units, 21
(20.8%) cite three or four, and two (2.0%) cite five. None of the 101 draws
direct support from multiple Sources. That leaves some multi-unit cases where
filtering might help, but the common case offers little room to remove
distractors. These pointers are addressable, not proven semantically correct.

**Recommendation C:** keep Semantic Evidence Filtering as a research/evaluation
component; its production use case is weak in this local snapshot. The database
is a local persisted dataset, not a verified representative production sample;
its case provenance is unknown. This verdict does not establish what a wider
deployment sees.

# 2. Current Runtime Flow

```text
CaseSourceBundle (all Case Sources + answered follow-up sources)
    ↓
evidence_units() — deterministic sentence spans, split at 2,000 characters
    ↓
ReadingSources.source_payload() — exact unit text + source-local U001, U002…
    ↓
one whole-Case case_reading request
    ↓
Reader-generated Claims + supporting/contradicting source_id/unit-ID groups
    ↓
ReadingSources.canonical_reply() — deterministic revision-bound IDs
    ↓
bound_claims() / bind_citations() — validate IDs and reproduce original spans
    ↓
possible research insertion: filter each Claim’s already-selected support units
    ↓
judgement_request() — Claims, resolved quote text and citations
```

| Stage | Current implementation | Owner |
|---|---|---|
| Source and segmentation | `backend/app/sources/bundle.py::CaseSourceBundle`; `backend/app/sources/evidence.py::evidence_units`, `EvidenceUnit`, `EvidenceIndex`; sentence/span segmentation and exact offsets are deterministic. | Backend |
| Reading input | `backend/app/analysis/write.py::write_trace`, `reading_request`; `backend/app/analysis/reading_sources.py::ReadingSources`. The request includes all Sources together, including answered follow-up sources; it does not create per-document summaries. | Backend builds; model reads |
| Unit IDs | Backend creates the available units and local labels such as `U001`. The model chooses which supplied `source_id` and local unit IDs to cite. Backend maps each selection to a revision-bound canonical ID. | Backend creates/resolves; model selects |
| Claim contract | `backend/app/trace/claims.py::CaseReadingClaim`; each Claim has supporting and contradicting `CaseEvidenceReference` lists. A reference contains one `source_id` and 1–64 unit IDs; up to 64 reference groups are allowed per side. | Model output validated by backend |
| Binding | `backend/app/trace/bind.py::bound_claims` → `resolve_claim`; `backend/app/trace/evidence_binding.py::bind_citations`, `direct_citation`. Valid IDs resolve to original text, offsets, document and page metadata. Invalid, duplicate, cross-source and stale pointers are excluded and diagnosed. | Deterministic |
| Judgement input | `backend/app/analysis/write.py::judgement_request`, `reading_payload`. Judgement receives Claim text and the resolved citations/quote text, without full Source text or quote context. | Backend builds; model judges |

One Reader request sees the Case’s Sources together. A Claim can cite multiple
units and multiple Sources. Returned unit order is preserved while binding
expands a multi-unit group into one resolved citation per unit. Source identity,
one citation group, one EvidenceUnit and one Claim are distinct objects.

# 3. Candidate Evidence Definition

For the proposed Claim verifier, the candidate support list is exactly the
distinct, valid unit IDs in that Claim’s **`supporting_citations`**, resolved to
their original unit text. Contradicting IDs are a separate list, not additional
positive support candidates. The ordinary EvidenceUnit path does not feed every
unselected unit from every Source to a per-Claim verifier. Old quote-only
citations have no EvidenceUnit IDs and must be reported separately.

The Reader may return one citation group containing several unit IDs, or groups
from several Sources. In binding, the backend resolves each ID separately and
stores its original text and locator; it does not merge those units into a new
passage for an NLI call. A current integration test proves a Claim can bind two
units from one document and a third unit from another.

No semantic filter runs on valid direct IDs. `test_evidence_pipeline.py` even
replaces `load_nli` with a function that raises, then verifies that direct
binding and Judgement complete. The reader prompt says both to select units
supporting attribution and quantities, and that a valid ID alone does not prove
semantic support. The direct path checks addressability and reproduces source
text; it does not test whether the cited text entails the Claim.

The clean insertion point for an experiment is after `checked_reading` returns
the bound Claim set and before `judgement_request` is made in
`backend/app/analysis/write.py::write_trace`. The verifier would inspect the
resolved support list there. If a future filter removes every unit, current code
defines no filter-specific restoration rule. Current invalid-address handling
fails closed: a reported Claim with no resolved support becomes `not_confirmed`.

# 4. Evidence Units per Claim

## Persisted local data

The local PostgreSQL database was queried in a `READ ONLY` transaction. The
query selected validated v1 traces attached as each Case’s latest analysis and
whose `source_revision` still matches the Case. It returned 23 Cases, 50
analysis-result rows, 24 validated v1 traces and **21 latest current analyses
containing 315 Claims**. Only aggregate counts were read into this report; Claim
text, Case titles and Source contents were not exported. The data’s real-case
versus synthetic-case provenance is not recorded here, so treat this as a
persisted local snapshot, not a verified production population.

The latest traces mix citation formats: **194 direct unit references**, 160
legacy quote-only supporting citations across 159 Claims, and 55 Claims with
no supporting citation. Three unverified citation records are present. No
duplicate direct unit references or invalid EvidenceUnit pointers appear in
this latest-current snapshot. The 214 Claims without direct unit IDs therefore
must not be read as 214 empty semantic-filter candidate sets: 159 use the
legacy quote format, and 55 have no supporting citation.

| Direct supporting EvidenceUnit IDs per Claim | All latest Claims, n=315 | Claims with direct IDs, n=101 |
|---|---:|---:|
| 0 | 214 (67.9%) | — |
| 1 | 40 (12.7%) | 40 (39.6%) |
| 2 | 38 (12.1%) | 38 (37.6%) |
| 3–4 | 21 (6.7%) | 21 (20.8%) |
| 5–9 | 2 (0.6%) | 2 (2.0%) |
| 10–19 | 0 (0%) | 0 (0%) |
| 20+ | 0 (0%) | 0 (0%) |

| Statistic | All latest Claims, n=315 | Direct-addressed Claims, n=101 |
|---|---:|---:|
| Mean units | 0.616 | 1.921 |
| Median | 0 | 2 |
| Population standard deviation | 1.049 | 0.961 |
| Min / p25 / p75 / p90 / p95 / max | 0 / 0 / 1 / 2 / 3 / 5 | 1 / 1 / 2 / 3 / 4 / 5 |

The zero-inclusive column describes the saved-trace pointer mix, including
legacy and uncited Claims. The direct-addressed column is the relevant candidate
set distribution for a new EvidenceUnit filter. Direct citations each contain
one unit after backend binding; before binding, one model citation group may
contain several IDs. In this snapshot all 101 direct-addressed Claims cite
exactly one Source; zero cite multiple Sources or multiple documents. Nine
point to Sources with no linked document row (for example, a narrative source
may be documentless); follow-up answers are not persisted as `CaseSource` rows.

The stored test corpus demonstrates mechanics, not frequency: synthetic tests
cover one-unit citations and a Claim using three units across two documents.
They do not establish a production distribution. The controlled
`research/projection_validation/results/pinned_cpu/` artifacts are experimental
outputs, not production Cases, and were not used to score this audit.

No confidence intervals are reported. These counts census the accessible local
snapshot, not a randomized sample from a defined production population.

## Reproduce the unit-count distribution

Run this SQL in a read-only transaction against the same local database. It
counts distinct direct EvidenceUnit IDs from the latest analysis at the current
Source revision, grouped by Claim:

```sql
BEGIN TRANSACTION READ ONLY;
WITH latest AS (
  SELECT a.trace_json
  FROM case_analysis_results a
  JOIN cases c ON c.latest_analysis_result_id = a.id
              AND c.source_revision = a.source_revision
  WHERE a.status = 'validated'
    AND a.trace_json->>'version' = 'case_analysis_trace_v1'
    AND jsonb_typeof(a.trace_json->'claims') = 'array'
), claims AS (
  SELECT x.value AS claim
  FROM latest a CROSS JOIN LATERAL jsonb_array_elements(a.trace_json->'claims') x(value)
), per_claim AS (
  SELECT (SELECT count(DISTINCT unit.value)
          FROM jsonb_array_elements(coalesce(claim->'supporting_citations','[]')) cite(value)
          CROSS JOIN LATERAL jsonb_array_elements_text(
            coalesce(cite.value->'evidence_unit_ids','[]')) unit(value)) AS units
  FROM claims
)
SELECT units, count(*) AS claims,
       round(100.0 * count(*) / sum(count(*)) over (), 1) AS pct
FROM per_claim GROUP BY units ORDER BY units;
COMMIT;
```

To restrict the result to unit-addressed Claims, add `WHERE units > 0` after
the `per_claim` CTE. The all-Claims view is useful for citation-format
coverage; the restricted view is the filtering candidate-size distribution.

# 5. Reader Citation Behavior

The Reader is **support-complete, not explicitly minimal**. Its prompt asks the
model to include units supporting the main proposition *and* its material
attribution, dates, quantities and qualifications; when pronouns need
resolution, it asks for the unit establishing the referent. It permits several
nearby units or Sources when they jointly support a Claim. It does not say to
include every merely relevant unit, nor does it minimize the candidate count.

The existing synthetic outputs follow the multi-unit contract when the test
constructs a multi-part Claim. Tests also show the backend rejects duplicate,
unknown and stale addresses. Those fixtures do not measure whether natural
Reader outputs are minimally sufficient or over-inclusive.

# 6. Research / System Alignment

1. **Structural alignment:** both tasks relate one Claim to one or more units.
   CyberCase supports multi-unit and multi-Source Claims.
2. **Main difference:** CyberCase’s Reader already selects a small support set
   from all Source units. A new filter would prune the Reader’s selected list,
   not a broad retrieval result. Most direct-addressed local Claims have only
   one or two candidates.
3. **Observed distractor opportunity:** limited in this snapshot. About 23% of
   direct-addressed Claims have at least three units; only 2% have five. No
   direct-addressed Claim combines multiple Sources here.
4. **Insertion point:** after deterministic binding and before Judgement is
   technically appropriate because Source text and offsets have been resolved.
5. **Existing semantic check:** the Reader’s selection is model-generated, but
   no independent NLI verifies direct cited units. Judgement receives the
   Claim’s resolved quote citations and can reason over them, but no per-Claim
   entailment verdict is computed.
6. **Complementary evidence risk:** real code and tests allow several units to
   jointly support attribution, time, or other parts of a Claim. Filtering each
   unit independently could remove a necessary qualifier or the second half of
   a multi-sentence support set.
7. **No-pass behavior:** the current direct binding path excludes invalid IDs
   and marks unsupported reported Claims `not_confirmed`. Legacy quote recovery
   is a separate compatibility path. There is no policy today for restoring
   candidates removed by a new semantic filter.

The optional pinned NLI is not a filter on valid EvidenceUnit candidates.
`backend/app/trace/meaning.py::meaning_pointed` is gated by
`quote_meaning_pointer`; it handles unresolved legacy supporting quotes. It
lexically narrows to at most three sentences, then runs pinned multilingual
mDeBERTa NLI and may attach an advisory passage. It does not remove directly
resolved units or promote an unresolved Claim into supported evidence. The
current backend setting is `on`. Of 21 latest-current saved traces, six contain
meaning-pointer counters and all six report zero eligible pointers; 15 traces
lack those counters, so historical NLI use cannot be reconstructed for them.

# 7. Risks and Limits

- A one-unit set has no distractor to remove; a filter can only keep it or
  reject its sole candidate.
- A claim can depend on complementary units. Independent similarity ranking
  does not prove that a retained subset still supports the full Claim.
- Reader selection already narrows the full Case sources, so a second stage may
  be redundant on typical one- or two-unit Claims. No labeled data measures its
  false-removal or false-acceptance rates here.
- IDs resolving correctly measure structure, not semantic entailment. This
  audit has no gold labels for citation support, so it cannot calculate filter
  precision, recall, accuracy or factual benefit.
- Local persisted data provenance and representativeness are unknown. The 101
  unit-addressed Claims are useful evidence of observed local behavior, not a
  guarantee about every deployment or language.

# 8. Final Recommendation

**C. Keep Semantic Evidence Filtering only as a research/evaluation component;
the observed production use case is currently weak.** The local persisted
distribution is dominated by small, Reader-selected support sets. This audit
does not show that direct pointers are semantically correct, or that a filter
would improve downstream Judgement. The code, tests and aggregate database
counts support only the narrower conclusion that the proposed filter usually
has one or two selected EvidenceUnits to inspect, with a smaller multi-unit
tail.

## Audit boundary

- Inspected `main` at `34a948c2451e0674e2443d8366beb36b9cad0b8e`; it matched
  `origin/main`. The starting working tree was clean.
- Code/schema facts, synthetic tests, and persisted local counts are labeled
  separately above. No test suite or provider call was run.
- The database work used only `SELECT` statements inside `BEGIN TRANSACTION
  READ ONLY`. No Case, Source, analysis result, or configuration was changed.
- Only this requested Markdown report was added; production code and tests were
  not modified.
