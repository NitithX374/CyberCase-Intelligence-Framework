# Existing cluster replay and citation-context exposure — 2026-10-08

The completed experiment ran **20 clusters: 10 ID and 10 OOD**, with the same 60 original Claim/reference rows in No-Gate and frozen B1-LR conditions. Neither condition removed the citation passages from admitted Claims. A claims-text-only Judgement ablation has **not** been run.

This audit reads existing requests, outcomes and summaries. It performs no Reader/Judgement calls, model fitting, semantic gold labelling or production changes. All 40 saved payload hashes match their outcome receipts; gate payload IDs match their recorded admission sets.

Subsequent production payload cleanup, 2026-10-08: Judgement citation records now carry Source text only; Source/unit IDs and document locators remain on original Claims. The archived requests audited here are unchanged. Source-text exposure remains, and the claims-text-only ablation is still unrun.

## Measured result of the existing gate experiment

| Boundary | No gate | B1-LR | Denominator |
|---|---:|---:|---|
| Gold-negative rows admitted | 31/31 (100%) | 9/31 (29.03%) | All 20 clusters |
| Gold-positive rows retained | 29/29 (100%) | 20/29 (68.97%) | All 20 clusters |
| Gold-negative row IDs cited in summary | 18/18 (100%) | 4/18 (22.22%) | 15 observable paired outcomes |
| Gold-positive row IDs cited in summary | 24/24 (100%) | 17/24 (70.83%) | 15 observable paired outcomes |

Five pairs containing generation failures are excluded from downstream utilization. Across 40 conditions there are 30 completed generations, six failures and four abstentions. B1-LR alone has 13 completed generations, three failures and four abstentions. Failures are unknown, not safe outputs. The recorded cluster-level paired test is p=.015625; confidence intervals and failure details are in [the original report](B1_RESULTS_2026-10-07.md).

The utilization endpoint concerns original benchmark row IDs. It is not an unsupported-prose propagation rate and does not identify a citation-context effect.

## What Judgement actually receives

All 16 nonempty B1-LR request payloads retain citation passages: **29 admitted Claims and 138 citation spans** in total, including requests whose generation failed. `supporting_citations[].exact_quote` contains backend-reproduced original Source text, accompanied by unit IDs, offsets and Source identity.

The literal citation field named `context` is already excluded from Judgement, along with reasoning and semantic-grounding metadata. Therefore “citation context” here means the original passages in `exact_quote`, not that excluded field. Semantic selection controls the NLI premise; it does not redact the citation arrays passed to Judgement. These exposure counts are structural, not semantic leakage labels.

## Concrete source-text expansion candidate

OOD cluster `0b38d36a12a1cc95dd109195ec8bdc647d339fd8e39b3f5bf78c21db1007a500` has four admitted Claims:

- A-01: low survival rates for adult and calf giraffes.
- A-02: wild population estimate around **97,500**.
- A-04: low survival rates, with a different linked reference.
- A-06: IUCN vulnerability to extinction.

The output adds another population estimate, **32,550**, and frames the two estimates as conflicting, citing A-04 and A-06. **32,550 appears in none of the six original Claim texts**, but it appears in both cited Claims' saved Source passages:

> Overall, the approximate number of all populations accumulate to 32,550 in the wild.

The saved output and matching Source text demonstrate an extra-Claim fact in the generated summary with a plausible citation-text path. The fact itself was not the hypothesis checked by the Claim gate. This is not enough to label the added fact unsupported: there is no independent gold for that new proposition. Nor does content overlap alone establish that the model used the passages rather than prior knowledge. A paired citation-removal ablation is needed for causal attribution.

Inspect the [saved request](../../tmp/b1-downstream/ood-live/0b38d36a12a1cc95dd109195ec8bdc647d339fd8e39b3f5bf78c21db1007a500/verified/request.json), [saved Judgement](../../tmp/b1-downstream/ood-live/0b38d36a12a1cc95dd109195ec8bdc647d339fd8e39b3f5bf78c21db1007a500/verified/judgement.json), or the [audit receipt](../../tmp/b1-downstream/results/citation-context-audit.json).

## Distinguish other propagation paths

In ID cluster `02451a5c0197dbbba95ed31e7fbb86bad9e1241388e3d98f0e6444c678e61224`, withheld A-01 has exactly the same Claim wording as admitted A-03. The summary repeats that wording using A-03. Both rows have negative support gold, so this is an admitted false acceptance and an alternate Claim-text path. It cannot be credited to citation-context leakage. Its No-Gate generation failed, so it is outside the 15 observable pairs.

Benchmark support labels belong to Claim/reference rows. Repeating a proposition under another reference does not automatically transfer one row's negative label to the whole proposition or the final prose.

## Small controlled ablation that would answer the context question

Hold the B1-LR admission set, Claim IDs/text/metadata, output schema, model/provider, prompt, decoding and budgets fixed. Compare:

| Condition | Judgement input |
|---|---|
| B1-LR + citation passages | Existing admitted Claim records and their citations |
| B1-LR + Claim content only | Identical payload with the two citation arrays removed |

Both conditions retain the same gate. Comparing old No-Gate outputs directly with a new claims-only arm would change admission and citation availability together. If transport or prompt configuration changes, rerun both paired conditions under one recorded configuration rather than treating archived outputs as matched controls.

Freeze probes for specific extra-Claim facts before generation, such as 32,550 in the example, and inspect paired summary/gaps/MITRE outputs. Measure extra-Claim fact utilization separately from independently labelled unsupported-fact propagation and supported coverage. A small purposive probe set is diagnostic, not a population leakage estimate. No second NLI summary verifier or production payload change is required to run this research ablation.

The current evidence supports gate admission/utilization improvements and an observed extra-Claim source-text expansion example. It does not establish that citation-context leakage is frequent, that all such additions are unsupported, or that claims-only Judgement improves downstream factual quality.
