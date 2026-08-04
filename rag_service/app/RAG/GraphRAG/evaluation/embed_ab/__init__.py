"""Embedding-model A/B experiment (thesis section 5.1).

Three vector-retrieval arms over one identical corpus and one identical
query set, so that the embedding model is the only variable that moves:

  A  bge-m3-hybrid   BGE-M3, dense + sparse, Qdrant native RRF  (deployed stack)
  B  bge-m3-dense    BGE-M3, dense only                          (controlled)
  C  e5-dense        multilingual-e5-large, dense only           (controlled)

B vs C isolates the model. A vs B measures what the sparse component adds —
the ablation that shows why a dense-only public benchmark understates BGE-M3.
"""
