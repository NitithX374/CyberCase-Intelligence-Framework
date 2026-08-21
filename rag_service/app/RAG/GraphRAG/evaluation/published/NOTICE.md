# Published-baseline comparison tier — provenance and licence notes

This tier exists to answer one question: **how does this pipeline score on the
same data, with the same metric code, as the published work it will be compared
against?**

## Papers being compared against

| Short name | Paper | Datasets | Metrics |
|---|---|---|---|
| TTP-LM | *Advancing TTP Analysis: Harnessing the Power of Large Language Models with Encoder-Only and Decoder-Only Architectures* — [arXiv 2401.00280](https://arxiv.org/abs/2401.00280) | MITRE procedure examples | Precision, Recall |
| TechniqueRAG | *TechniqueRAG: Retrieval Augmented Generation for Adversarial Technique Annotation in Cyber Threat Intelligence Text* — ACL Findings 2025, [arXiv 2505.11988](https://arxiv.org/abs/2505.11988) | TRAM, Procedures, Expert | P, R, F1, P@k/R@k (k=1,3) |
| H-TechniqueRAG | *Hierarchical Retrieval Augmented Generation for Adversarial Technique Annotation in Cyber Threat Intelligence Text* — [arXiv 2604.14166](https://arxiv.org/abs/2604.14166) | CTI-RCM, MITRE CTI, TRAM | micro-F1, P, R, MAP@10, latency, LLM call count |

TRAM is the common split across all three, so it is the primary target.

## Datasets — fetched, not vendored

`data/*_zeroshot_test.json` are downloaded by `fetch_datasets.py` from:

- Repository: <https://huggingface.co/datasets/QCRI/TechniqueRAG-Datasets>
- Publisher: Qatar Computing Research Institute (QCRI)
- Files: `test/tram_zeroshot_test.json`, `test/expert_zeroshot_test.json`,
  `test/procedures_zeroshot_test.json` (725 / 157 / 1767 rows)
- Fetched on: 2026-08-21

They are gitignored rather than committed: the HuggingFace repo is the citable
source, and re-committing someone else's benchmark into this tree adds a
licence question for no reproducibility gain (`fetch_datasets.py` pins the exact
repo and filenames).

The upstream code repository <https://github.com/qcri/TechniqueRAG> is
**GPL-3.0**. No code from it is copied into this tree.

## Metric compatibility

`metrics.py` is an independent implementation of the scoring protocol described
in the paper and realised in upstream `evaluate.py`. It was verified against a
reference copy of the upstream functions on 400 randomly generated corpora in
both `technique` and `subtechnique` modes: **Precision, Recall and F1 agree to
1e-12**. The reference copy was kept outside this repository.

Two documented deviations:

1. **MRR.** Upstream computes reciprocal rank after `list(set(preds))`, which
   discards the model's ranking — and because Python randomises string hashing
   per process, the upstream MRR is not reproducible between runs. `metrics.py`
   reports `mrr` over the true ranking and also `mrr_upstream` reproducing the
   set-mangled variant. MRR is the one metric that is not strictly comparable.
2. **F1-of-means.** Upstream computes F1 from the averaged P and R rather than
   averaging per-sample F1. That is reproduced exactly as `f1` (it is the
   comparable number); `f1_micro` is reported alongside as the better-behaved
   estimator.

## ATT&CK version reconciliation

The benchmark gold labels are from an older ATT&CK release (upstream
`assets/mitre_kb.json` holds 780 technique IDs including long-revoked ones like
T1043 and T1064). This project indexes **ATT&CK v19.0** (821 live technique and
sub-technique IDs in Neo4j/Qdrant).

Without reconciliation, revoked families cap recall for reasons that have
nothing to do with retrieval quality — for example every `T1562.*` gold label is
unreachable, because MITRE renumbered Impair Defenses to `T1685` in v19.

`attack_version_map.py` derives the mapping from the STIX bundles already in
`Mitre_ATT&CK Doc/`, using `revoked-by` relationships (196 mappings) and
`x_mitre_deprecated` flags (25 dead ends). After mapping, **100% of gold label
mentions in all three benchmarks are reachable in this project's index**:

| Split | Samples | Unique gold | Remapped | Unscoreable |
|---|---|---|---|---|
| TRAM | 725 | 127 | 2 | 2 (T1043, T1064) |
| Expert | 157 | 152 | 3 | 0 |
| Procedures | 1767 | 300 | 8 | 0 |

Any write-up must state that this reconciliation was applied, and report both
the reconciled numbers and the count of dropped samples.

## Fairness caveats to state in the write-up

- Every arm here is **zero-shot**. Upstream's headline rows are fine-tuned on
  the matching train split. The honest comparison is against their zero-shot
  (GPT-4o, DeepSeek v3, Ministral 8B) and off-the-shelf-retriever (BM25, NCE,
  Text2TTP, RankGPT) rows.
- The agent graph is bypassed (no router, no decomposition, no reflection loop)
  because these inputs are 80–400 characters. What is measured is retrieval plus
  technique identification, not the production pipeline end to end.
- Upstream's default `--mode technique` rolls sub-techniques up to the parent.
  Both modes are reported here; state which one a quoted number came from.
