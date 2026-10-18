# Project inventory: verified scope and receipts

2026-09-30. Source authority: current code and saved outputs. Literature descriptions are in positioning_review.md. This is a read-only research audit, with documentation artifacts.

## Current implementation

| Boundary | Verified behavior | Evidence |
|---|---|---|
| Reading | Sources/follow-ups -> atomic claims, parties, timeline, impacts | backend/app/analysis/write.py:15-33 |
| Judgement | Receives original sources AND reading, plus optional technical context; produces summary/gaps/ATT&CK associations | write.py:35-43 and write_request |
| Joined trace | Copies claims/parties/timeline/impacts from reading; judgement cannot rewrite these fields through its output schema | write.py:103-117 |
| Binder | Finds quote occurrence/locators; no semantic-entailment judge; reported claim without remaining supporting citations downgraded | backend/app/trace/bind.py:220 and quote modules |
| Report | Code projection of saved trace; preservation depends on display/projection contracts, not determinism alone | backend/app/reports/generate.py; report-fidelity receipts |

Working HEAD4aa8b18ba61c3f94738169d5f54d12d8f480a622. Held-out analysis deliberately pins1e29bd3 and excludes later progress/gap-topic changes; report-v2 pins4aa8b18. Models/results from other revisions must not be presented as a single current end-to-end experiment.

## Analysis dev50

- Model google/gemma-4-26b-a4b-it; English CASIE narrative articles; one run per arm; MITRE/RAG disabled.
- Saved main + robustness: research/analysis_baseline/results/main_20260928_081639_robustness.md/.json.
- Annotated-argument mention recall: prose .641697; single .667090; two-call .778830. Two minus single .111741. This is coverage under the matching rule, not semantic fact accuracy.
- Failure-zero/case-paired tests and matcher/length sensitivity are useful but do not identify the isolated causal contribution of structure, prompt, extra call or evidence budget.
- Main-event selection is an earliest Actual-event heuristic; not a gold annotation of article salience.
- Saved A3: two-call own text at least as long as source in37/48completedcases; article-lead descriptive coverage .990 at matched budgets. Copy/lead coverage is a sanity control, not a same-estimand paired improvement figure; recall alone does not establish summary quality.
- Order receipt: research/analysis_baseline/results/main_20260929_233326_b2.md. late-single+.021 CI[-.043,.083],p=.5471;two-late+.091 CI[.004,.182],p=.0468,Holm=.0936. Late arm ran two days later.

## Scorer

- research/analysis_baseline/run.py: mention found anywhere in own text, no required argument role/event alignment; quotes themselves excluded from own-text credit.
- Gold-span citation coverage: any verified quote/gold span overlap, independently of whether the claim states the fact.
- research/analysis_baseline/heldout_analysis.py: descriptive stated-and-cited = intersection of these two sets; role inversions use an attacker/victim word lexicon for matched party names. No full semantic or native CASIE tuple F1 follows from these diagnostics.
- The added descriptions were fixed before held-out results; dev recomputation is post hoc. This audit did not run the scorer on incomplete data.

## Held-out analysis status

At2026-09-30T03:54:51UTC (latest snapshot in local_receipts.json): **368 saved run records of expected400**, arms prose100/single99/single_late99/cybercase70; no partial JSON lines. The file was still changing. This is completion metadata only; no interim effect estimate is reported.

Protocol: 100 new cases, four arms, one run/arm, offset50 from a150-case ordered sample; one primary two-versus-single test, three secondary Holm comparisons. Failed system outputs score0; budget/harness stops are reported separately. One primary pass is not evidence of multi-seed/model robustness. Receipt is a snapshot and can become stale as the user-owned run continues.

## Report-fidelity v1: historical evidence

- research/report_fidelity/runs/main/summary.json and RUN_NOTES.md.
- One-call DeepSeek-v4.1-flash;30selected,26valid traces,4failed and not replaced.
- 585 unique frozen claim records x3 renderings =1755 claim-rendering instances;26traces x3 =78reports/arm.
- Deterministic claim retention1755/1755, byte-identical26/26; LLM1707/1755 (.9726),byte-identical0/26,malformed2/78.
- Deterministic source-ID retention1092/1728 (.6319), contradiction-source retention0/3; LLM source retention1680/1728 (.9722),contradiction sources3/3.
- LLM status changes0/1707; absence of byte equality alone is not a semantic error. RUN_NOTES identifies a real date error separately.
- Conditional on a valid input trace; report retention does not validate truth or repair upstream omissions. Repeated deterministic renderings are not independent samples.

## Report-fidelity v2: pending main evaluation

- PROTOCOL_V2.md exports report4aa8b18 and consumes the first50 held-out Gemma two-call traces.
- Source fallback fix6da037f and gap display fixec50f9c supersede v1 display behavior.
- Two successful dry-run traces preserve all measured dimensions; a third has an upstream trace failure. Dry run is explicitly not main evidence.
- At inspection runs_v2/main/summary.json absent; RUN_NOTES says ArmA waits for held-out analysis. No v2 main result asserted.
- v1/v2 differ in model, cases, writer, report code and evaluator; compare descriptively only.

## Literature and rights

Twelve full reads, seven requested plus five closer works. Metadata verified freshly for eleven DOI records, including four arXiv-issued DataCite DOIs; Kramer verified separately against the USENIX publication/PDF because no DOI/arXiv ID was verified. This does not turn preprints into reviewed publications.

CASIE public access does not establish licence/redistribution rights. The audit does not redistribute articles/PDFs or certify evaluation-only permission.

## Workspace preservation

local_receipts.json compares all29 backend files inspected in the earlier same-day audit: all hashes unchanged. Pre-existing tmp_schema.json deletion and user-owned docs/thesis/component_evaluation_plans_2026-09-30.json preserved. This audit adds only research documents and updates CONTINUITY.md; no experiment results overwritten.

