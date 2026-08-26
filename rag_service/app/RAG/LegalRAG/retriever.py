"""
Legal retrieval
===============
Finds the statute sections an incident may fall under.

Three things shape this module, all of them measured rather than assumed.

**Narrative-to-statute retrieval is weak on its own.** On a ransomware narrative
the correct section (พ.ร.บ.คอม ม.๙) came back at rank 11 on dense search, and
sparse search did not return it in the top 30 at all. The reason is register,
not language: the case file says "ถูกเข้ารหัสจนใช้งานไม่ได้ เรียกค่าไถ่" and the
statute says "ทำให้เสียหาย ทำลาย แก้ไข เปลี่ยนแปลง" — both Thai, almost no words
in common. So `mitre_table` is accepted as an optional enrichment: a technique
name is much closer to statutory vocabulary than a victim's account of events.
It stays optional because the retriever has to work, and be debuggable, without
GraphRAG having run at all.

**Reranking is the expensive step.** 355 ms for 15 pairs on this GPU, but
2.0 s on CPU — and production runs on CPU. The candidate pool is therefore
deliberately small, and reranking can be turned off entirely without changing
the result shape.

**A section can exist in two versions at once.** พ.ร.บ.คอม ม.๑๒ has its original
2550 wording and the wording the 2560 amendment substituted, and they carry
different penalties. Both are indexed. Which one is returned depends on the date
of the incident, and when no date is supplied the later one wins — silently
returning both would hand a prosecutor two contradictory penalties for one
section.

This module never imports GraphRAG. `mitre_table` is read structurally, as a
sequence of objects or dicts carrying `technique_id`, `name` and `description`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Sequence

from .config import (
    EMBED_MODEL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_LEGAL,
    QDRANT_URL,
)

# Reranking this many candidates costs ~2 s on CPU. Raising it raises latency
# roughly linearly; see the module docstring.
RERANK_CANDIDATES = 15
SEARCH_LIMIT = 40
FINAL_TOP_K = 8


@dataclass
class LegalHit:
    """One retrieved section, with everything needed to present it safely."""

    citation: str
    act_slug: str
    act_label: str
    number: str
    text: str
    role: str
    chargeable: bool
    verification: str
    verified_by_human: bool
    penalties_reliable: bool
    effective_from: str | None
    effective_note: str
    source_url: str
    cites: list[str] = field(default_factory=list)
    hierarchy: list[str] = field(default_factory=list)
    score: float = 0.0
    # True when this section was pulled in because a retrieved section cited it,
    # rather than because it matched the query. Context, not a suggestion.
    via_citation_of: str | None = None


@dataclass
class LegalRetrievalResult:
    hits: list[LegalHit] = field(default_factory=list)
    context: list[LegalHit] = field(default_factory=list)
    query_used: str = ""
    reranked: bool = False
    elapsed_ms: int = 0
    degraded: str = ""

    @property
    def chargeable_hits(self) -> list[LegalHit]:
        return [h for h in self.hits if h.chargeable]


def _row_field(row: Any, name: str) -> str:
    value = row.get(name) if isinstance(row, dict) else getattr(row, name, "")
    return str(value or "")


def build_query(text: str, mitre_table: Sequence[Any] | None = None, max_rows: int = 6) -> str:
    """Case narrative, optionally widened with the techniques already identified.

    The technique names are appended rather than replacing the narrative: they
    supply statutory-adjacent vocabulary ("Data Encrypted for Impact") while the
    narrative keeps the facts that only it contains (a ransom demand, a mule
    account) which no ATT&CK technique describes.
    """
    if not mitre_table:
        return text
    terms: list[str] = []
    for row in list(mitre_table)[:max_rows]:
        name = _row_field(row, "name")
        if not name:
            continue
        technique_id = _row_field(row, "technique_id")
        terms.append(f"{name} ({technique_id})" if technique_id else name)
    return f"{text}\n\nเทคนิคที่ตรวจพบ: {', '.join(terms)}" if terms else text


def _to_hit(payload: dict, score: float) -> LegalHit:
    return LegalHit(
        citation=payload.get("citation", ""),
        act_slug=payload.get("act_slug", ""),
        act_label=payload.get("act_label", ""),
        number=payload.get("number", ""),
        text=payload.get("text", ""),
        role=payload.get("role", ""),
        chargeable=bool(payload.get("chargeable")),
        verification=payload.get("verification", ""),
        verified_by_human=bool(payload.get("verified_by_human")),
        penalties_reliable=bool(payload.get("penalties_reliable", True)),
        effective_from=payload.get("effective_from"),
        effective_note=payload.get("effective_note", ""),
        source_url=payload.get("source_url", ""),
        cites=list(payload.get("cites") or []),
        hierarchy=list(payload.get("hierarchy") or []),
        score=score,
    )


def pick_version(hits: Iterable[LegalHit], incident_date: date | None) -> list[LegalHit]:
    """Collapse duplicate versions of one section to the one then in force.

    Sections whose commencement could not be established (PDPA, whose chapters
    started on different days) carry no date. They are kept rather than dropped:
    an unknown date is a reason to show the section with its warning, not a
    reason to hide the law from the person asking.
    """
    best: dict[tuple[str, str], LegalHit] = {}
    for hit in hits:
        key = (hit.act_slug, hit.number)
        current = best.get(key)
        if current is None:
            best[key] = hit
            continue
        if _supersedes(hit, current, incident_date):
            best[key] = hit
    return sorted(best.values(), key=lambda h: h.score, reverse=True)


def _supersedes(candidate: LegalHit, current: LegalHit, incident_date: date | None) -> bool:
    cand_date = _as_date(candidate.effective_from)
    cur_date = _as_date(current.effective_from)
    if cand_date is None:
        return False
    if cur_date is None:
        return True
    if incident_date is not None:
        # In force on the day of the incident, and the later of those.
        cand_ok, cur_ok = cand_date <= incident_date, cur_date <= incident_date
        if cand_ok != cur_ok:
            return cand_ok
    return cand_date > cur_date


def _as_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


class LegalRetriever:
    """Statute retrieval over the `thai_law_sections` collection.

    The embedding model and reranker are injected. The service already holds one
    of each for GraphRAG; constructing a second copy would put another model in
    memory, which matters most on the CPU-only production host.
    """

    def __init__(self, embed_model=None, reranker=None, client=None):
        self._embed_model = embed_model
        self._reranker = reranker
        self._client = client

    # ── lazy resources, so a CLI run costs only what it uses ──────────────
    def model(self):
        if self._embed_model is None:
            from FlagEmbedding import BGEM3FlagModel

            self._embed_model = BGEM3FlagModel(EMBED_MODEL, use_fp16=False)
        return self._embed_model

    def client(self):
        if self._client is None:
            from qdrant_client import QdrantClient

            if not QDRANT_URL:
                raise RuntimeError("QDRANT_URL is not set")
            self._client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
        return self._client

    def query(
        self,
        text: str,
        mitre_table: Sequence[Any] | None = None,
        incident_date: date | None = None,
        top_k: int = FINAL_TOP_K,
        # Off by default on the evidence: reranking moved the correct section up
        # (ม.๙ from rank 11 to 5, and surfaced ม.๑๒) but cost 33 s against 0.7 s
        # without it, because the embedder and the reranker do not both fit on a
        # 4 GB GPU. Callers with headroom — or a CPU-only host, where there is no
        # such cliff — can turn it back on.
        rerank: bool = False,
        rerank_candidates: int = RERANK_CANDIDATES,
        chargeable_only: bool = False,
        with_cited_context: bool = True,
    ) -> LegalRetrievalResult:
        """Retrieve sections for an incident. Never raises; degrades instead.

        `mitre_table` is optional by contract: without it retrieval still works,
        just less well, and nothing here calls back into GraphRAG.
        """
        started = time.perf_counter()
        result = LegalRetrievalResult()
        query_text = build_query(text, mitre_table)
        result.query_used = query_text

        try:
            candidates = self._search(query_text, chargeable_only)
        except Exception as exc:  # noqa: BLE001 — a statute suggestion is an enhancement
            result.degraded = f"ค้นหาไม่สำเร็จ: {exc}"
            result.elapsed_ms = int((time.perf_counter() - started) * 1000)
            return result

        deduped = pick_version(candidates, incident_date)

        if rerank and deduped:
            try:
                deduped = self._rerank(query_text, deduped[:rerank_candidates])
                result.reranked = True
            except Exception as exc:  # noqa: BLE001 — ranking worse beats failing
                result.degraded = f"จัดอันดับใหม่ไม่สำเร็จ ใช้ลำดับเดิม: {exc}"

        result.hits = deduped[:top_k]
        if with_cited_context:
            result.context = self._cited_context(result.hits)
        result.elapsed_ms = int((time.perf_counter() - started) * 1000)
        return result

    def _search(self, query_text: str, chargeable_only: bool) -> list[LegalHit]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        vector = self.model().encode(
            [query_text], return_dense=True, return_sparse=False
        )["dense_vecs"][0].tolist()

        query_filter = None
        if chargeable_only:
            query_filter = Filter(
                must=[FieldCondition(key="chargeable", match=MatchValue(value=True))]
            )
        points = self.client().query_points(
            QDRANT_COLLECTION_LEGAL,
            query=vector,
            using="dense",
            limit=SEARCH_LIMIT,
            query_filter=query_filter,
            with_payload=True,
        ).points
        return [_to_hit(p.payload or {}, float(p.score)) for p in points]

    def _rerank(self, query_text: str, hits: list[LegalHit]) -> list[LegalHit]:
        reranker = self._reranker
        if reranker is None:
            import torch
            from sentence_transformers import CrossEncoder

            # Device must be explicit. Left to default, sentence_transformers
            # picked CPU here and 15 pairs took 48 s — enough on its own to make
            # the whole feature unusable.
            device = "cuda" if torch.cuda.is_available() else "cpu"
            reranker = self._reranker = CrossEncoder(
                "BAAI/bge-reranker-v2-m3", max_length=512, device=device
            )
        # GraphRAG's Reranker wraps CrossEncoder and takes VectorResult objects;
        # only the raw predict() is used here so the two stay independent.
        predict = getattr(reranker, "predict", None) or getattr(reranker.model, "predict")
        scores = predict([[query_text, h.text] for h in hits])
        for hit, score in zip(hits, scores):
            hit.score = float(score)
        return sorted(hits, key=lambda h: h.score, reverse=True)

    def _cited_context(self, hits: list[LegalHit]) -> list[LegalHit]:
        """Fetch the sections the results point at.

        PDPA ม.๘๓ reads "ผู้ใดฝ่าฝืน … มาตรา ๓๗ … ต้องระวางโทษ" and says nothing
        about what ม.๓๗ requires. Retrieved alone it is a rule about nothing, so
        the sections it names are fetched alongside it and marked as context.
        """
        from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

        wanted: dict[tuple[str, str], str] = {}
        have = {(h.act_slug, h.number) for h in hits}
        for hit in hits:
            for number in hit.cites:
                key = (hit.act_slug, number)
                if key not in have and key not in wanted:
                    wanted[key] = hit.citation
        if not wanted:
            return []

        out: list[LegalHit] = []
        by_act: dict[str, list[str]] = {}
        for act_slug, number in wanted:
            by_act.setdefault(act_slug, []).append(number)
        try:
            for act_slug, numbers in by_act.items():
                points, _ = self.client().scroll(
                    QDRANT_COLLECTION_LEGAL,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(key="act_slug", match=MatchValue(value=act_slug)),
                            FieldCondition(key="number", match=MatchAny(any=numbers)),
                        ]
                    ),
                    limit=len(numbers) * 2,
                    with_payload=True,
                )
                for point in points:
                    hit = _to_hit(point.payload or {}, 0.0)
                    hit.via_citation_of = wanted.get((hit.act_slug, hit.number), "")
                    out.append(hit)
        except Exception:  # noqa: BLE001 — context is a bonus, never a failure
            return []
        return pick_version(out, None)
