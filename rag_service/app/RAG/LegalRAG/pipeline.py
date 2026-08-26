"""
LegalRAG pipeline
=================
The one entry point the router uses: retrieve, then explain.

`query(text, mitre_table=None)` works with no MITRE table, just less well —
that is the contract, and it is what lets this side be exercised, and fail, on
its own. Nothing in this package imports GraphRAG; the table is read
structurally when it is offered.

Failure is always downward. Every path returns a `LegalResult`, and a broken
retriever, a missing collection, an unreachable model or a malformed reply all
end as an empty result carrying `degraded`. Losing a statute suggestion must
never cost the caller its MITRE mapping.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Sequence

from .generation import LegalGenerator
from .retriever import LegalRetriever
from .schema import LegalResult


class LegalRAG:
    """Retriever plus generator, sharing the service's models."""

    def __init__(self, embed_model=None, reranker=None, llm=None, client=None):
        # Injected, never constructed here: the service already holds one
        # BGE-M3 and one chat model, and a second copy of either costs memory
        # on a host that runs both pipelines.
        self.retriever = LegalRetriever(
            embed_model=embed_model, reranker=reranker, client=client
        )
        self.generator = LegalGenerator(llm=llm)

    def query(
        self,
        text: str,
        mitre_table: Sequence[Any] | None = None,
        incident_date: date | None = None,
        top_k: int = 8,
        rerank: bool = False,
    ) -> LegalResult:
        try:
            retrieval = self.retriever.query(
                text,
                mitre_table=mitre_table,
                incident_date=incident_date,
                top_k=top_k,
                rerank=rerank,
                chargeable_only=True,
            )
        except Exception as exc:  # noqa: BLE001
            return LegalResult(degraded=f"ค้นหาตัวบทไม่สำเร็จ: {exc}")

        try:
            return self.generator.generate(
                text,
                retrieval,
                mitre_table=mitre_table,
                incident_date=incident_date,
            )
        except Exception as exc:  # noqa: BLE001
            return LegalResult(degraded=f"สรุปข้อเสนอแนะไม่สำเร็จ: {exc}")

    def warmup(self) -> None:
        """Touch the collection so the first real query does not pay for it."""
        self.retriever.client()
