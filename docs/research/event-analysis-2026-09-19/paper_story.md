# Event-supported Cybersecurity Case Analysis

2026-09-19 [USER] Research and design only. No application implementation or empirical model runs are authorized by this document.

## Thesis

Test whether a small event representation improves the preservation of annotated event information in final structured case analysis beyond direct prompting and a matched prose-notes pipeline. Treat temporal enrichment as a secondary experiment at the resolution supported by ChronoCTI.

## Task boundary

- Inputs: fixed English cybersecurity documents; no retrieval in the primary experiment.
- Outputs: the same structured analysis schema for every condition, including human-readable event findings, their source spans, parties, timeline, impacts, and unresolved questions.
- Primary scope: preservation of annotated events and role-bearing arguments, not general investigative competence or legal correctness.
- Exclusions: training, multi-agent systems, graph databases, OCR, UI work, autonomous investigation, and new semantic validation stages.

## Literature position

- [CASIE, AAAI 2020](https://ojs.aaai.org/index.php/AAAI/article/view/6401): event nuggets, arguments, roles and status; five subtypes. [Original release](https://github.com/Ebiquity/CASIE) contains document text and event hoppers.
- [ChronoCTI, ICDM 2024 artifact](https://figshare.com/articles/dataset/ChronoCTI_Mining_Knowledge_Graph_of_Temporal_Relations_among_Cyberattack_Actions/26039518), [KAIS 2025 extension](https://link.springer.com/article/10.1007/s10115-025-02491-6): temporal relations between ATT&CK techniques, not distinct event instances.
- [AttacKG](https://github.com/li-zhenyuan/Knowledge-enhanced-Attack-Graph) and [AttacKG+, Computers & Security 2025](https://doi.org/10.1016/j.cose.2024.104220): attack graph construction already exists; AttacKG+ has temporal steps, behavior graphs, TTP labels and state summaries.
- [Agent-Event-Coder, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/40346): decomposition and typed schemas motivate simple extraction, but executable code, agents and verification loops are unnecessary here. [Release](https://github.com/UESTC-GQJ/AEC) includes CASIE evaluation resources.
- [Give Me Structure, SOUPS 2023](https://www.usenix.org/system/files/soups2023-kersten.pdf): human investigation process evidence, not proof of LLM representation benefits.
- [Kramer et al., SOUPS 2025](https://www.usenix.org/conference/soups2025/presentation/kramer): incident summarization omission and factual error motivation; private operational incidents are not the proposed benchmark.
- [CTINexus, EuroS&P 2025](https://ctinexus.github.io/): relation extraction, canonicalization and graph linking are adjacent tasks.
- [IntelEX v1 / ThreatPilot v2](https://arxiv.org/abs/2412.10872): attack-level structured intelligence; inspected as a preprint.
- [GenDFIR, Computers 2025](https://repository.londonmet.ac.uk/10080/): adjacent RAG-based timeline reconstruction, not the proposed treatment.
- [Automated TTP Extraction SoK, USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/buechel): taxonomy and task differences matter when comparing systems.
- [SR-LLM, ACL 2025](https://aclanthology.org/2025.acl-long.172/), [Talk Like a Graph, ICLR 2024](https://research.google/pubs/talk-like-a-graph-encoding-graphs-for-large-language-models/), [Serialization Strategies, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.437/): input serialization can affect model behavior; these findings do not establish a best cyber-event format.
- [SIABench preprint](https://arxiv.org/abs/2603.06422), [dataset](https://huggingface.co/datasets/SIABench/SIA_Dataset): artifact/tool investigation tasks, optional secondary evaluation only.
- [ExCyTIn official release](https://github.com/microsoft/SecRL), [dataset](https://huggingface.co/datasets/anandmudgerikar/excytin-bench): public logs and QA now available; repository reports ICML 2026 acceptance. A fixed-context QA subset would be a derivative evaluation, not the original agent benchmark.

## Contribution

A controlled empirical evaluation of event-supported final analysis. No claim of inventing event extraction, attack graphs, decomposition, or structured generation. The mechanism under test is preserving event-role bindings during synthesis.

## Representation

Source snapshot: source_id, revision, unchanged text, offset convention.

Event record: local event_id, event type, trigger source span, role-bearing argument spans, source-reported realis, and optional explicit time expression. Preserve native benchmark roles; null is not proof of an investigative gap. Keep mention records; do not build cross-document coreference.

Temporal record: from_id, to_id, relation, source reference. Event-instance relations and report-level technique relations are different views. ChronoCTI supports the latter; preserve its NEXT, OVERLAP and CONCURRENT definitions and multi-label pairs. No total chronology or transitive closure is inferred from technique aggregation.

Canonical storage: JSON. Default model input: original text plus deterministic labeled sentences generated from the records. Test JSON against labeled sentences with identical content and cached extractions. Graph serialization is an edge list, not a graph database.

## Experiments

| ID | Method | Calls per document | Role |
|---|---|---:|---|
| B0 | Raw source to final analysis | 1 | Primary direct control |
| P1 | Raw source to unstructured factual notes; raw source plus notes to final analysis | 2 | Essential extra-pass control |
| B1 | Raw source to events; raw source plus events to final analysis | 2 | Primary treatment |
| B2 | Same cached B1 events to temporal relations; raw source plus events and relations to final analysis | 3 | Secondary temporal treatment |
| B1-J | Same B1 events serialized as JSON | 2 logical calls | Format diagnostic |
| B1-O | Gold CASIE events plus raw source to final analysis | 1 model call | Oracle diagnostic, not a deployable system |

Optional temporal control: B1 plus one prose chronology pass, then final analysis (3 calls). Without this control, interpret B2 versus B1 as the combined temporal-stage and extra-compute effect.

Hold model snapshot, decoding, final schema, source text, instructions, source order and final output budget fixed. Keep RAG and follow-up disabled. Record intermediate and final token counts, elapsed time, failures, and prompts. Do not silently repair malformed outputs or substitute B0 after failures.

## Dataset protocol

CASIE: start from original annotations so realis and event hoppers survive. Use published document splits when identifiable and compatible; otherwise publish a new document-grouped manifest (40 development, 200 evaluation documents, seed 42, disjoint duplicate-story groups), explicitly not a replication of original scores. Do not split windows from the same document across partitions. Use English only for confirmatory claims.

ChronoCTI: preserve 73 train / 21 evaluation report masks. Select ten train reports for development. Reconstruct text by report and sentence index. Deduplicate exact triples; preserve distinct labels on the same pair; exclude incomplete rows from relation ground truth. Treat automatically generated NULL pairs as operational annotation negatives, not independently verified absent relations.

No joint event-plus-temporal benchmark is claimed. On ChronoCTI use a fixed taxonomy adapter for technique-labeled action records and compare report-level relation sets. Gold endpoint experiments are explicitly conditional/oracle evaluations; never present them as end-to-end extraction.

## Scoring

- Upstream: exact trigger span/type P/R/F1; argument span/role F1 conditional on correctly matched event and end-to-end; realis macro F1 plus accuracy on matched triggers.
- Downstream primary: coverage of actual-event gold hoppers by final visible event findings, matched by native type, exact source trigger span, and status. One hopper counts once. This is structured-record coverage, not automatic proof of free-text entailment.
- Arguments: role-bearing source-span recall and F1 in final visible findings; report per-role scores and extraction-to-final retention separately. Avoid claiming semantic entity equivalence without annotations.
- Temporal: per-label and macro F1 over native positive relation sets at report/technique-pair resolution; separate operational NULL results. Report end-to-end recovery of annotated precedence edges and conditional direction accuracy with coverage.
- Unsupported assertions: unmatched gold labels are not hallucinations. Blind-review a fixed sample against source text and classify supported / contradicted / not established; double-code a subset if a supervisor is available.
- Gaps: optional answerability probe using complete removal of all occurrences of a gold role value; do not equate synthetic slot masking with real investigative gap quality.

Use three repeated runs of one frozen model. Average per-document runs before inference. Use 10,000 paired document bootstrap resamples and paired permutation tests, with Holm correction for prespecified comparisons. Report effect sizes and 95% intervals, not only p-values. The 21-report temporal evaluation is exploratory and likely underpowered for small effects.

## Claim boundaries

Supported now: design and public-data feasibility, subject to stated licensing and annotation limitations.

Not yet supported: performance improvement, temporal benefit, cost effectiveness, reduced hallucination, generalization to Thai cases or operational analyst benefit. No model experiments have been run.

## Four-week schedule

1. Freeze splits, verify offsets/hoppers/native temporal labels, implement scorers, inspect 20 development documents.
2. Implement B0/P1/B1 and gold-event diagnostic; freeze prompts and test manifest.
3. Run main experiment; add bounded ChronoCTI B2 and format ablation if adapters are ready.
4. Blind error audit, paired statistics, report, and thin FastAPI integration using existing stage interface.

Fallback: complete B0/P1/B1 and serialization/error propagation analysis; omit temporal superiority claims. A null result is reportable.
