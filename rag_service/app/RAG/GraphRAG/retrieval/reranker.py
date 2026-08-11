"""
Cross-Encoder Reranker
=======================
Post-retrieval reranker that rescores vector search results using a
cross-encoder model for joint query-document relevance.  Replaces the
raw RRF fusion score with a more precise relevance signal before the
top-K cut that feeds graph expansion and the LLM context.
"""
from __future__ import annotations


from .vector_retriever import VectorResult
from ..config import DEVICE, FINAL_TOP_K, RERANKER_MODEL


class Reranker:
    """Reranks a list of VectorResults using a cross-encoder model."""

    def __init__(self, model_name: str = RERANKER_MODEL) -> None:
        from sentence_transformers import CrossEncoder
        print(f"[RERANKER] Loading {model_name} on {DEVICE}...")
        self.model = CrossEncoder(model_name, max_length=512, device=DEVICE)
        print(f"[RERANKER] Ready")

    def rerank(
        self,
        query: str,
        results: list[VectorResult],
        top_k: int = FINAL_TOP_K,
    ) -> list[VectorResult]:
        """Score each (query, document) pair and return top_k results sorted
        by cross-encoder score, in [0, 1].

        CrossEncoder.predict() already applies the sigmoid for a 1-label
        model, so the value it returns is the probability, not a logit.
        Applying sigmoid to it a second time (as this did) squashed the whole
        range into [0.5, 0.731]: a perfect match scored 0.731 and an obvious
        non-match 0.500, which is where the "reranker saturates at 0.500" note
        in config.py came from. Ordering was unaffected — sigmoid is monotonic
        — but every score-based threshold downstream was calibrated against a
        compressed scale.
        """
        if not results:
            return results

        pairs = [(query, r.document[:512]) for r in results]
        raw_scores = self.model.predict(pairs)

        for result, raw in zip(results, raw_scores):
            result.score = float(raw)

        reranked = sorted(results, key=lambda r: r.score, reverse=True)

        print(
            f"[RERANKER] Top-{min(top_k, len(reranked))} after reranking: "
            + ", ".join(
                f"{r.metadata.get('name', r.metadata.get('source_name', '?'))} ({r.score:.3f})"
                for r in reranked[:top_k]
            )
        )
        return reranked
