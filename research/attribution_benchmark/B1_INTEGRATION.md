# Frozen B1-LR integration and matched downstream evaluation

Updated 2026-10-07. The working tree integrates the selected verifier; deployment
into a newly built Docker image must be checked separately. Historical saved
analyses retain their original methods and thresholds.

The 20-cluster downstream replay and all 3,296 EN/Google MT-TH pairs are complete.
[Measured results and limitations](B1_RESULTS_2026-10-07.md) distinguish admission,
row-ID utilization, language transfer, runtime and deferred deployment.

## Production boundary

Sources, including document and formal follow-up Sources, enter Reader together.
Reader returns canonical Claims with Source-unit IDs. The backend binds those IDs
to original offsets, text and document/page provenance. Binding establishes an
address, not semantic support or real-world truth.

Only the resolved **supporting** units linked to each Claim are candidates for
verification. The filter does not search other Case Sources or create citations.
Duplicate spans are removed; Source order follows first appearance and located
units within each Source are ordered by offsets. Original unit text is retained,
including OCR markup. No quote search, text normalization or context-window
expansion replaces the model-selected units in this method.

The frozen method is:

1. `paraphrase-multilingual-mpnet-base-v2`, revision
   `4328cf26390c98c5e3c738b4460a05b95f4911f5`, normalized embeddings, 128-token
   encoder limit. Retain cosine similarity >= 0.20; if none pass, retain the first
   maximum, as specified by the research method.
2. Join retained original units with one newline.
3. `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`, revision
   `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`, forward premise/Claim pair,
   `truncation=True`, `max_length=512` (longest first).
4. Feed `[P(entailment), P(neutral), P(contradiction)]` to the frozen WiCE
   TRAIN-fitted logistic regression, admitting its score >= 0.50.

`backend/app/trace/b1_lr.json` holds the coefficients, pins and original artifact
hash. They are not retrained at startup. The score is a task-specific linear
decision boundary, **not calibrated factual confidence**. An NLI argmax label or
`P(entailment) >= .80` is not the current decision rule.

Claims with no resolved support, an unresolved nonduplicate supporting pointer,
declared conflicting support or an uncertain epistemic status remain
`unassessed` and withheld. Eligible scored Claims are `supported` or
`not_supported`. Excess length is truncated and recorded rather than itself
causing abstention. Missing or mismatched model assets raise an error; there is
no fail-open verifier.

Only admitted Claims reach Views and Judgement. Parties, Timeline and Impacts
are display projections derived from those Claims; they are not independent
Judgement inputs. Raw follow-up answers cannot bypass the gate. Zero admission
produces an abstention without calling Judgement. Final references to withheld
Claims fail validation. All original Claims, citations, verdicts and provenance
remain in the trace, including selected/considered citation indices, similarities,
three NLI probabilities, LR score, raw token count, truncation and timing.

Judgement still receives the original bound citation text attached to admitted
Claims, including units excluded by semantic selection. The filter controls the
verification premise; it does not redact their text from Judgement.
Consequently a withheld proposition could be reconstructed from another admitted
Claim or its Source passages. Reference validation controls cited IDs, not every
implicit statement. Downstream row-ID utilization must not be presented as proof
that all unsupported factual content was eliminated.

Production payload cleanup, 2026-10-08: citation records sent to Judgement contain
only `exact_quote`, reproduced by the backend. Claim IDs remain; Source/unit IDs,
document/page/offset locators and other citation metadata stay on the original
Claims. This changes metadata serialization, not the admission gate or Source-text
exposure. The completed replay's saved requests and outcomes remain unchanged.

User decision, 2026-10-07: a stricter Judgement payload containing only Claim
text/IDs, with nested citation/context removed, is deferred until after the
thesis if measured leakage warrants it, or a separately controlled small
ablation. Leakage frequency has not been measured. This is not a production
change or an additional condition in the completed replay.

The Source-row segmentation fix changes current unit IDs to version v2 and
preserves exact offsets. Historical IDs are not silently mapped onto new units;
stored historical citation text remains readable. Frontend passage joining is
display-only and does not alter the verifier premise.

## Assets and runtime

The Docker backend uses local read-only mounts for `backend/nli_mdeberta` and
`backend/source_selector_mpnet`. The latter can be provisioned using
`backend/scripts/copy_source_selector.py` with the exact pinned cached snapshot.
The paths are controlled by `CLAIM_NLI_PATH` and `CLAIM_SELECTOR_PATH`; the old
meaning-pointer environment names no longer configure the current verifier.
`sentence-transformers==6.0.0` is required by `requirements-encoder.txt`.

The observed native integration uses CPU with checkpoint float16 NLI and float32
selector weights. The transfer harness can explicitly use the same frozen assets
and loaded dtypes on CUDA, reports its device/library versions, and
recomputes both EN and TH under the same execution configuration. Archived EN
cache predictions are retained separately to expose numerical/runtime drift.
No new model or production GPU policy is introduced.

## Matched downstream experiment

`run_propagation.py --champion` uses the original frozen B1-LR feature caches and
the exact original AttributionBench row IDs, Claims, references and gold labels.
Asset hashes and row/gold order are checked. Legacy caches lack per-text hashes;
the receipt explicitly records this limitation and verifies the raw corpus
manifest separately. All 4,366 cached WiCE/ID/OOD LR decisions match the original
joblib classifier; this checks the decision implementation, not model accuracy.

The agreed live scope is 20 label-blind clusters: first 10 eligible hash-ordered
ID clusters and first 10 OOD clusters. It contains 60 row-local Claim/reference
examples (29 attributable, 31 non-attributable). Duplicate Claim wording with
different references remains separate; gold must not be transferred to a unique
proposition or newly synthesized summary.

Both arms use identical fixed A IDs, original Claims, native Judgement prompt,
model/provider configuration and temperature 0. No Reader is called. The
`unfiltered` arm admits all Claims, while `verified` admits B1-LR positives.
Claim-link-only admission is equivalent to unfiltered in this slice because
every selected row has valid links. The old `experiments/analysis_arms.py` calls
the production gate in both conditions and is not a clean No-Gate control.

PowerShell example, run from the repository root:

```powershell
$env:PYTHONPATH="$PWD\backend;$PWD"
python -m research.attribution_benchmark.run_propagation --champion --split test --limit 10 --execute --judgement-model google/gemma-4-26b-a4b-it --judgement-providers nextbit/bf16,coreweave/bf16 --continue-on-error --output tmp/b1-downstream/id-live
```

Use `test_ood` with a separate output for OOD. `--resume` preserves recorded arms,
including failures, and continues only missing arms. It does not rerun failed
generations or erase the original receipt. Provider retries within a stage are
counted separately where raw capture is available.

Admission measures supported retention and unsupported admission against row
gold. Downstream measurement is **non-attributable benchmark Claim ID citation
utilization**, including rejected IDs as a separate protocol violation. It does
not verify the final prose, implicit facts, gaps or MITRE semantics. Failed
generations are unknown, not safe outputs. Zero-admission abstentions are
explicitly separated. Paired outcome comparisons use observed valid pairs;
cluster bootstrap intervals reflect the small clustered sample. No second
summary verifier is added.

## EN to machine-translated TH

`translate_th.py` uses the official Google Translation v2 API, explicit EN/TH,
`nmt`, plaintext and a content-addressed resumable cache. It translates each
original English Claim/unit once and retains row IDs, reference order, unit
order and original gold. Full ID/OOD coverage is 3,296 rows, 33,583 distinct
texts and 3,856,265 characters. An incomplete cache cannot produce a complete
transfer result. Credentials remain in `.env` and are never saved in receipts.

```powershell
python -m research.attribution_benchmark.translate_th --output tmp/attribution-mt-th --execute
python -m research.attribution_benchmark.evaluate_mt_th --translations tmp/attribution-mt-th --output tmp/b1-mt-th --device cuda
```

The verifier, selector threshold and LR coefficients remain frozen. Translation
does not create human Thai gold: label invariance is an explicit assumption and
translation errors are a possible confound. Empty-reference rows are scored with
an empty premise in both research languages, matching the archived EN protocol;
production separately withholds Claims without resolved support. No Thai tuning,
new dataset, backbone search or retraining is part of this experiment.
The benchmark preserves the original champion's English reference segmentation
and translates those units one-for-one. Production candidates are Reader-cited
Source-v2 units. Shared verifier identity does not imply identical candidate
scope/granularity or end-to-end Case performance.
Translation errors stop by default. The explicit `--transient-attempts 3` option
retries only HTTP 502/503/504 with bounded waits and an error receipt. It does not
retry quota/authentication failures or change providers, inputs or gold labels.

## Scope of conclusions

Focused unit/pipeline checks establish addressing, decision implementation and
admission routing. Real EN/TH/multi-unit smoke checks are diagnostic examples.
AttributionBench metrics estimate support classification on that benchmark.
The downstream experiment measures citation utilization under a fixed replay;
it cannot establish whole-system factual or legal correctness. Translation
transfer measures machine-translated language sensitivity rather than native
Thai Case accuracy. Results, generation failures and runtime/deployment limits
must be reported separately.
