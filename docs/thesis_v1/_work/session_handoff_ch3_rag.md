# Handoff — Chapter 3 RAG/Evaluation writing session

Written 2026-09-02. Purpose: let a **new chat** answer follow-up questions about the
Chapter 3 prose drafted in the previous session without re-deriving anything.

> New chat, start here: read this file first, then read the code paths cited below
> before answering. Every number in this file was read out of the repo, not recalled.

---

## 1. What was drafted (prose lives in the user's Word doc, not in this repo)

| Section | Topic | Status |
|---|---|---|
| 3.2 | RAG pipeline intro — rewritten for grammar + cross-lingual framing | drafted |
| 3.2.1 | Data ingestion intro (BGE-M3 dense+sparse) | drafted |
| 3.2.1.1 | Data parsing (STIX → typed entities) | drafted, concise version |
| 3.2.1.2 | Graph store construction (Neo4j) | drafted |
| 3.4 | Query decomposition (5 sub-sections) | drafted |
| 3.5 | Retrieval phase (6 sub-sections) | drafted |
| 3.6 | Self-reflection loop | drafted |
| 3.7 | Evaluation intro | drafted |
| 3.7.1 | Datasets & ground truth — **2 tiers only** (real-CTI + published) | drafted |
| 3.7.2 | Retrieval metrics | NOT YET WRITTEN |
| 3.7.3 | Generation metrics | NOT YET WRITTEN |

**Numbering is unstable.** The user used "3.4" for both Query decomposition and
Evaluation at different points. Confirm the live numbering in their Word file
before writing anything that cross-references a section number.

The user pastes drafts into Word and highlights passages they do not understand.
Expect questions of the form "why did you write X" about the sections above.

---

## 2. Verified pipeline facts (read from code, 2026-09-02)

### Ingestion — `rag_service/app/RAG/GraphRAG/ingestion/`
- `stix_parser.py` — two passes; tombstone set from `revoked` / `x_mitre_deprecated`
  collected BEFORE parsing. `tool` + `malware` → one `Software` entity with
  `software_type`. `attack-pattern` split by `x_mitre_is_subtechnique` into
  `Technique` / `Subtechnique`. ATT&CK ID + URL recovered from `external_references`.
- Derived edges with no STIX representation: `IN_TACTIC` (from `kill_chain_phases`),
  `HAS_COMPONENT` (from `x_mitre_data_source_ref`). Synthetic ids `derived--<src>--<tgt>`.
- `graph_loader.py` — clear DB → constraints on `stix_id` per label + shared `:Entity`
  → indexes (`attack_id`, `name`, `shortname`) → nodes via `UNWIND … MERGE` in
  batches of 5000 → edges via `CREATE` (dedup already done in Python).
- `vector_loader.py` — two Qdrant collections, each with named vectors
  `"dense"` (1024-dim, cosine) + `"sparse"`. Entity text = `"{label}: {name}. {desc}"`,
  relationship text = `"{src} {EDGE} {tgt}: {desc}"`. Truncated at 8000 chars.
  Batch size 16.
- `ATTACK_DOMAINS = {enterprise, mobile}` — **ICS is NOT ingested.**

### Retrieval — `rag_service/app/RAG/GraphRAG/retrieval/`

Per channel, in order:
1. BGE-M3 encodes query once → dense + sparse.
2. Qdrant `query_points` with two `Prefetch` branches, each `limit=max(top_k*5, 50)`,
   fused by **native `Fusion.RRF`**. The RRF smoothing constant is Qdrant's own and
   is NOT configurable through the client — do not state k=60 as the system's value.
3. `search_entities` over-fetches `top_k*3` then filters `domain == "enterprise"`
   client-side (no payload index on `domain` in the cloud collection).
   `search_relationships` gets `max(top_k//2, 3)` and is **not** domain-filtered
   (its payload has no `domain` field).
4. `_normalize_scores` min-max per collection, merge, sort, truncate to `top_k`.
5. `Reranker.rerank` — `bge-reranker-v2-m3`, docs truncated to 512, scores already
   in [0,1] (do NOT re-apply sigmoid; the old double-sigmoid is why an older note
   said "reranker saturates at 0.500").
6. `_reweight_by_type` — Technique/Subtechnique ×1.2, Tactic ×1.1, Software ×0.8,
   Group/Campaign ×0.75. Keys off `node_label`, so **relationships get no multiplier**.
7. Graph seeds taken in reranked order; a Relationship hit contributes BOTH endpoints.
8. `GraphRetriever.expand_batch` — **3 Cypher statements total** per call (centers,
   outgoing, incoming) via `UNWIND`, not 3 per seed.

### Key constants
| Symbol used in prose | Value | Code |
|---|---|---|
| K_v | 10 | `VECTOR_TOP_K` |
| K_f | 5 | `FINAL_TOP_K` (graph seeds on the single-query path only) |
| q | 3 | `per_query_k` in `retrieve_multi_quota` |
| max sub-queries | 10 | `_MAX_SUBQUERIES` in `query_decomposer.py` |
| merged vector cap | 15 | `max_vector`, passed twice (merge + `build_context`) |
| merged subgraph cap | 8 | `max_graph` |
| context char cap | 10000 | `build_context(max_context_length=...)` |
| broaden iterations | 2 | `MAX_RETRIES` in `evaluator.py` |

`build_context`'s `max_vector` default is `FINAL_TOP_K` (5). The agent must pass 15
explicitly or 10 retrieved results are silently dropped at render time. The literal
15 appears in three places; there is no shared constant.

### CORRECTION made this session
Graph expansion is **1 hop, incoming + outgoing** — NOT 2 hops. There is no
`GRAPH_DEPTH` setting anywhere. `get_multi_hop_path()` (4 hops) is a standalone
utility the pipeline never calls. CLAUDE.md said "2 hops" and was fixed.

### CODE CHANGE made this session
`hybrid_retriever.py`: added `graph_seed_k` param to `retrieve()`
(default `None` → `FINAL_TOP_K`, unchanged for every other path).
`retrieve_multi_quota` now passes `graph_seed_k=per_query_k`, so under quota
retrieval the graph seeds from the same 3 hits the quota keeps. Previously seeds
came from the top 5, meaning ranks 4–5 were dropped from the vector list yet
returned through the graph section. Rationale: the recall gain was not worth the
precision cost.
**This invalidates every retrieval number in `evaluation/results/` — see §4.**

---

## 3. Known limitations flagged to the user (all real, all in code)

1. **`PARTIAL_ANSWER` is dead.** The evaluator can return it and `gap_warning`
   reaches pipeline state, but nothing reads it, so the caveat never reaches the
   user. Documented as future work in the draft, deliberately not fixed.
2. **min-max normalisation destroys absolute scale.** An all-irrelevant
   relationship list still yields a 1.0 top score, so irrelevant relationships
   displace relevant entities *before* the reranker ever sees them. The reranker
   fixes final ordering but cannot recover what the merge already discarded.
   Proposed fix (NOT applied): skip the pre-rerank truncation, rerank all ~15,
   let the only comparable scale decide. Would invalidate eval numbers.
3. **Relationship collection is never domain-filtered** — mobile relationships can
   enter an enterprise query. Fixing needs a re-ingest.
4. **Graph expansion ignores the domain restriction** entirely.
5. **Mobile is ingested but unreachable** through entity retrieval — dead weight in
   the index.
6. `_normalize_scores` returns early when a list has <2 items or all-equal scores,
   leaving raw RRF scores (~0.016) to compete against normalised [0,1] scores.
7. Proposed but not done: hoist the literal `15` into `config.py`.
8. Proposed but not done: server-side `domain` filter via a Qdrant payload index
   (1 API call, no re-ingest, removes the ×3 over-fetch). User was asked and has
   not yet approved — it touches shared cloud infra.

---

## 4. Evaluation state

### Datasets
| Tier | n | Gold source | Has reference_answer? |
|---|---|---|---|
| Real-CTI | 100 samples / 347 steps | CTID emulation plans (50, Apache-2.0, pinned commit) + CISA advisories (50, Zenodo DOI 10.5281/zenodo.14659512, CC-BY-4.0) | **No — 0/100** |
| Published | TRAM 725 / procedures 1767 / expert 157 | released test splits | No |
| ~~Graph-derived~~ | 136 (+2223 variant) | Cypher against Neo4j | Yes — but **dropped from the thesis** on the user's instruction |

Real-CTI cue types: **61 named / 286 described** of 347 steps. Sources split 50/50.
Steps per sample: 3→69, 4→19, 5→9, 6→2, 7→1. Each sample carries `query_en`.

Consequence of dropping the graph-derived tier: no reference text anywhere, so
generation must use reference-free measures (RAGAS faithfulness / answer relevancy,
plus ATT&CK-ID agreement against `gold_attack_ids`). BERTScore / ROUGE-L / token-F1
are no longer available. This was judged acceptable — those references were
Cypher-template text and ROUGE against them measured template mimicry.

`named` cue doubles as the control condition that the dropped tier used to provide
(named@50 = .987 proves the pipeline is not broken).

### Results on disk — `evaluation/results/`
All on real-CTI, 100 samples. **All predate the §2 code change; all need re-running.**

`real_cti_retriever.md` — arm comparison, no quota:
Hit@5: Vector .370 / Graph .020 / Hybrid .490. Hybrid StepCoverage@5 .181
(described .105, named .500). MRR .398, MAP .140, 6857 ms.

`real_cti_quota.md` — quota arm, pre-reranker-fix (scores saturated at .500):
Hybrid+Quota Hit@5 .580, StepCoverage@5 .250 (described .229, named .421),
MRR .430, MAP .221, 25098 ms.

`real_cti_v3_scoresort.md` — **latest, post-fix**:
Hit@5 .640 @10 .810 @20 .900. StepCoverage@5 .320 @10 .434 @20 .551.
By cue @5: described .267, named .645. @50: described .594, named .987.
MRR .554, MAP .313, 14199 ms.

Headline progression for described-cue StepCoverage@5: .105 → .229 → .267.

`published/data/runs/` holds `tram__retrieval__k20-ml2048.jsonl` (432),
`thai-cti__rag-en__k20__qwen3-5-9b-nothink.jsonl` (100) and an
`-oracle-nothink` variant. **The oracle arm is the retrieval/generation error-
attribution mechanism** and should be written up in 3.7.3; it is currently only a
results file. Those runs used a local `qwen3-5-9b`, not the production
`openai/gpt-5.6-luna` — re-run before using as headline numbers.

### Metric definitions — `evaluation/retriever_metrics.py`
Hit@K, Recall@K (**capped**: hits / min(|relevant|, K), documented rationale),
Precision@K, MRR, NDCG@K, MAP, plus StepCoverage@K and StrictStepCoverage@K.
StepCoverage is subtopic recall (S-recall, Zhai et al., SIGIR 2003) with attack
steps as subtopics — cite that.

**Open definitional issue for 3.7.2:** `_collect_hybrid_ids` counts every graph
neighbour as a retrieved id, so one subgraph can contribute 200+ ids (logs show
`retrieved=192/212/265` from only 15 vector hits). Precision@50 is structurally
low as a result. 3.7.2 must define "retrieved" explicitly and justify it.

---

## 5. Standing instructions from the user

- Writing is a **Thai prosecutor case-analysis** framework; output language is Thai,
  documents are English. Reply to the user in Thai; thesis prose in English.
- Prefers concise answers. Wants concrete worked examples with real numbers.
- Wants limitations stated honestly in the thesis rather than elided — has
  repeatedly chosen the honest phrasing when offered the choice.
- Announce model + call count + estimated cost before any paid evaluation run.
- Do not verify API keys before running; the machine is configured.
- External benchmarks must run the served agent graph. Component-only arms
  (vector-only, graph-only, hybrid-without-quota) are **ablations, never headline**.
- `PYTHONUTF8=1` is required for any script that prints Thai on this machine.
