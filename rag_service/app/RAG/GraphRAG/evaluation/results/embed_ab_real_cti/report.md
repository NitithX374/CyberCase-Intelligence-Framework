# Embedding model comparison — retrieval (vector-only)

- corpus: MITRE ATT&CK (Neo4j-grounded gold, Qdrant vector corpus)
- query pairs: 100 Thai/English, identical gold IDs
- gold reachable in vector corpus: 90/90 (100.0%) — caps recall equally for all arms
- top-K = 10, metrics @ [1, 3, 5, 10, 15, 20, 50]


## Thai queries (primary)

| Arm | Model | Hit@5 | Recall@5 | NDCG@5 | MRR | MAP | Latency (ms) |
|---|---|---|---|---|---|---|---|
| A | bge-m3 dense+sparse (RRF) | 0.350 | 0.107 | 0.124 | 0.281 | 0.091 | 565 |
| B | bge-m3 dense only | 0.420 | 0.141 | 0.158 | 0.316 | 0.112 | 572 |
| C | multilingual-e5-large dense | 0.270 | 0.071 | 0.078 | 0.193 | 0.055 | 530 |

## English queries

| Arm | Model | Hit@5 | Recall@5 | NDCG@5 | MRR | MAP | Latency (ms) |
|---|---|---|---|---|---|---|---|
| A | bge-m3 dense+sparse (RRF) | 0.390 | 0.121 | 0.134 | 0.294 | 0.099 | 557 |
| B | bge-m3 dense only | 0.450 | 0.156 | 0.176 | 0.363 | 0.130 | 579 |
| C | multilingual-e5-large dense | 0.290 | 0.086 | 0.083 | 0.176 | 0.055 | 511 |

## Cross-lingual penalty (Thai − English, same gold)

| Arm | Model | ΔHit@5 | ΔNDCG@5 | ΔMRR |
|---|---|---|---|---|
| A | bge-m3 dense+sparse (RRF) | -0.040 | -0.010 | -0.014 |
| B | bge-m3 dense only | -0.030 | -0.019 | -0.047 |
| C | multilingual-e5-large dense | -0.020 | -0.005 | +0.017 |

## Sparse ablation (A − B, Thai)

Adding BGE-M3's lexical/sparse component to the same dense model moves NDCG@5 by **-0.034** and MRR by **-0.035**. Public leaderboards evaluate the dense vector alone, i.e. arm B.
