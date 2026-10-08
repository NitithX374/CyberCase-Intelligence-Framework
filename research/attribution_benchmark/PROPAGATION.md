# Controlled downstream claim-propagation dry run

The research question is whether claim-level evidence verification reduces citation of non-attributable benchmark rows downstream while retaining attributable rows. This harness prepares a matched unfiltered/verified pair from existing AttributionBench rows and can call the existing CyberCase Judgement stage explicitly. The default performs offline preparation only.

The endpoint is **benchmark-labelled claim–evidence row ID citation propagation**. A label describes the original row and its original cited references. It is not a universal proposition-truth label. A summary citing a row does not prove that it restates that row faithfully: citation misuse, altered propositions, omitted citations and uncited statements cannot be assigned semantic factuality from inherited labels. No final-summary factuality, hallucination reduction, Reader accuracy or case-domain effectiveness conclusion follows from this dry run.

## Fixed boundaries

- Read the pinned official files through `data.read_split()` and verify all four raw hashes with `data.verify_manifest()`. No downloads, training, inference by a verifier, new dataset, generated input claims or annotations.
- Group by the existing `cluster_key()` of `[src_dataset, question, response]`.
- Select the first 1–5 eligible cluster hashes, default one on dev. Eligibility requires at least two distinct original claim texts and nonempty reference bundles for every row. Exclusion counts are recorded. This is a convenience dry-run slice, not a representative evaluation sample; OOD eligibility is especially restrictive.
- Sort original row IDs and assign `A-01`, `A-02`, … **before filtering**. Labels do not affect selection, ordering, IDs or native epistemic status. Duplicate claim texts remain separate rows, even if their labels disagree.
- Each reference becomes a row-local virtual Source. Native `evidence_units()` and `direct_citation()` represent its full exact text with offsets. Unit text must reconstruct each reference exactly, including whitespace. No evidence is merged across rows. No pages or document metadata are fabricated. Original claim whitespace is restored after native schema validation; original claim text is preserved.
- Require one existing complete, independently verified candidate run. Check dataset/model identity, summary/score hashes, complete row identity, claims, references, gold labels and cluster keys. Reuse its cached `p_supported >= selection.threshold` decisions. No threshold, model, truncation policy or test-selected configuration changes.
- Git may translate file line endings. Recorded text hashes must match the LF or CRLF encoding of otherwise identical bytes; both physical and LF hashes are retained. This does not alter escaped claim/reference text in JSON records. Any other byte change fails.
- Prepare native `judgement_request()` payloads with constant `reported` claim type/status, English output, empty follow-up history and no technical context. Only admitted Claims and their row-local citations are sent. Original full responses, questions, gold labels and verifier probabilities stay outside Judgement input.
- Execute only `request_stage(stage="case_judgement")` with the existing prompt and `CaseProviderJudgement` schema, temperature zero and the same explicit native configuration for both arms. Reader, claim views, production pipeline, Case persistence and RAG are bypassed.
- Empty admission sets produce `no_accepted_claims`, no model request and null propagation metrics. They are not successful final summaries. Errors remain errors, produce failure artifacts and exit nonzero; no semantic fallback is substituted.

The cached verifier's existing input policy can truncate evidence. Its original row bundle and gold remain unchanged; cached length diagnostics and the frozen model/input policy are recorded. Judgement sees the original full bundle represented by exact units, not a newly labelled subset of the evidence.

## Offline preparation

From repository root using the existing environment:

```powershell
& '.\env_mitre\Scripts\python.exe' 'research/attribution_benchmark/run_propagation.py' `
  --verifier-run 'research/attribution_benchmark/runs/candidates_en_20261006T010418Z/minicheck_cuda_float32_b1' `
  --split dev --limit 1 `
  --output 'tmp/claim-propagation-harness/my-offline-preparation'
```

The explicit verifier path is a usage example, not a newly selected best model. Other existing verified candidate runs use the same interface. Running them separately preserves identical cluster selection and row IDs for the same split/limit. Output directories must be new; existing artifacts are never overwritten.

An omitted output path creates a new ignored directory under `propagation_runs/`. Each run contains its manifest, exact Judgement prompt, per-cluster row mapping, per-arm request and outcome. Mapping artifacts reference original IDs and content hashes; they are experiment receipts, not a new labelled corpus. Offline output has `status: prepared`, null propagation metrics and no Judgement responses.

## Explicit bounded live execution

Add `--execute --judgement-model <provider/model>` with an explicit output directory for live execution. Candidate-cache runs retain the five-cluster cap. The `--champion` adapter allows an explicit limit up to 100; the agreed B1-LR study uses 10 ID and 10 OOD clusters. There are at most two logical Judgement stages per cluster, with no stage for empty admission. Native bounded retries may issue additional provider requests. A research response-capture transport records replies without altering production request defaults or services. See [B1_INTEGRATION.md](B1_INTEGRATION.md).

Live runs save native Judgement replies and citation metrics. Rejected or unknown IDs are never silently removed. Failures and protocol violations stop by default. Explicit `--continue-on-error` records them separately and continues the remaining arms; the final status is `completed_with_failures`. `--resume` preserves recorded failed arms rather than rerunning them. Failed generations are unknown outcomes, not safe summaries.

## Metrics and denominators

The scoring sidecar uses original row labels; labels never enter the model payload. `summary_pieces()` supplies the existing citation-block parser. Blocks are not guaranteed to be individual sentences. Duplicate citations count once in row-level endpoints.

| Metric | Numerator | Denominator |
|---|---|---|
| Non-attributable admission | Accepted negative rows | All original negative rows in the cluster |
| Attributable admission retention | Accepted positive rows | All original positive rows |
| Non-attributable propagation | Accepted negative row IDs cited in summary | All original negative rows |
| Attributable downstream retention | Accepted positive row IDs cited in summary | All original positive rows |
| Conditional propagation / retention | Cited accepted rows of the corresponding label | Accepted rows of that label |
| Citation exposure including rejected rows | Any cited known negative row IDs | All original negative rows |

Every ratio stores numerator, denominator and value; a zero denominator yields null. Unknown IDs, rejected IDs, malformed claim brackets and uncited blocks are separate diagnostics. The new `summarize_propagation.py` aggregates the agreed matched study with cluster-bootstrap intervals and exact paired McNemar tests, separating generation failures and empty-admission abstentions. It measures row-ID citation utilization, not final-summary semantic correctness or a model ranking.

## Validation without model calls

```powershell
& '.\env_mitre\Scripts\python.exe' -m pytest -c backend/pytest.ini `
  backend/tests/test_claim_propagation.py backend/tests/test_b1_research_evaluation.py -q
```

The propagation checks are now in normal backend test discovery and reuse pinned local raw rows/caches. The evaluation checks exercise cache integrity, metrics and failure accounting using controlled fixtures. Neither calls a live provider. The separate `test_b1_real_model.py` requires explicit `B1_REAL_MODEL=1` and local pinned model assets; Reader/Judgement remain mocked in that integration smoke.
