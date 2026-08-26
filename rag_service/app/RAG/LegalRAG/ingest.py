"""
Qdrant ingestion for Thai statute sections
==========================================
Embeds parsed sections into their own collection, `thai_law_sections`.

Two things this module is careful about.

**It never touches the MITRE collections.** Every create, upsert and delete goes
through `config.assert_writable`, which allows exactly one collection name. The
MITRE vectors are built by a different pipeline from a STIX bundle; deleting
them costs a full rebuild, and mixing statutes into them would make a case
narrative match "มาตรา" where a technique belongs. Existing data is left alone:
the collection is created only when missing, and dropping it requires an
explicit `--recreate`.

**What is embedded is not what is returned.** The vector is built from an
enriched string — act label, chapter, section number, then the text — because a
case file says "แฮกเกอร์เจาะระบบเข้ามา" while the statute says "ผู้ใดเข้าถึงโดย
มิชอบซึ่งระบบคอมพิวเตอร์", and the surrounding context helps close that gap. The
payload keeps the verbatim section text separately, and that is what any caller
displays. Enrichment happens on the way in, never to the words of the law.

Point IDs are derived from (act, section, origin), so re-running updates rows
instead of accumulating duplicates.

Usage:
    cd rag_service/app/RAG
    python -m LegalRAG.ingest --dry-run      # show what would be sent
    python -m LegalRAG.ingest                # create if missing, then upsert
    python -m LegalRAG.ingest --recreate     # drop the legal collection first
"""

from __future__ import annotations

import argparse
import io
import sys
import uuid

from .config import (
    EMBED_DIM,
    EMBED_MODEL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_LEGAL,
    QDRANT_URL,
    assert_writable,
)
from .models import LegalSection
from .parser import parse_all

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:  # pragma: no cover - Windows console fallback
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_NAMESPACE = uuid.UUID("6f1b0c1e-6a41-5c2e-9b7a-4d3f5a2c8e10")

# Amending provisions are not indexed. Their text is the replacement wording
# they enact, which is already ingested as a section of the act being amended,
# so indexing both puts two near-identical vectors in competition; and
# "ให้ยกเลิกความในมาตรา ๑๔ ..." is not something anyone searches for.
SKIP_ROLES = ("amending",)


def point_id(section: LegalSection) -> str:
    return str(uuid.uuid5(_NAMESPACE, f"{section.act_slug}|{section.number}|{section.origin}"))


def embed_text(section: LegalSection) -> str:
    """The string that gets vectorised — context first, then the law verbatim."""
    head = f"{section.act_label} มาตรา {section.number}"
    if section.hierarchy:
        head += " " + " ".join(section.hierarchy)
    return f"{head}\n{section.text}"


def to_payload(section: LegalSection) -> dict:
    """Everything a caller needs to filter on, and to refuse to answer with.

    `effective_from_ts` duplicates the date as YYYYMMDD because Qdrant range
    filters on an integer are unambiguous, and picking the version of a section
    in force on the date of an incident is the whole reason both versions are
    indexed.
    """
    eff = section.effective_from
    return {
        "act_slug": section.act_slug,
        "act_label": section.act_label,
        "number": section.number,
        "number_thai": section.number_thai,
        "citation": section.citation,
        "hierarchy": section.hierarchy,
        # Verbatim. This is what callers display.
        "text": section.text,
        # Enriched. Stored so a retrieval result can be explained.
        "document": embed_text(section),
        "origin": section.origin,
        "role": section.role,
        "chargeable": section.chargeable,
        "cites": section.cites,
        "verification": section.verification,
        "verified_by_human": section.verified_by_human,
        "penalties_reliable": section.penalties_reliable,
        "effective_from": eff.isoformat() if eff else None,
        "effective_from_ts": int(eff.strftime("%Y%m%d")) if eff else 0,
        "effective_note": section.effective_note,
        "source_url": section.source_url,
        "text_sha256": section.text_sha256,
        "amends_act": section.amends_act,
    }


def selected(sections: list[LegalSection]) -> list[LegalSection]:
    return [s for s in sections if s.role not in SKIP_ROLES]


class LegalIngestor:
    def __init__(self, embed_model=None, client=None):
        # Injected by the service, which already holds one BGE-M3. Loading a
        # second copy costs another model in memory, and production runs on CPU
        # where that hurts more.
        self.embed_model = embed_model
        self.client = client

    def _model(self):
        if self.embed_model is None:
            from FlagEmbedding import BGEM3FlagModel

            print(f"[LEGAL] โหลด {EMBED_MODEL} ...")
            self.embed_model = BGEM3FlagModel(EMBED_MODEL, use_fp16=False)
        return self.embed_model

    def _client(self):
        if self.client is None:
            from qdrant_client import QdrantClient

            if not QDRANT_URL:
                raise SystemExit("[LEGAL] ไม่พบ QDRANT_URL")
            self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=120)
        return self.client

    def ensure_collection(self, recreate: bool = False) -> None:
        from qdrant_client.models import Distance, SparseVectorParams, VectorParams

        assert_writable(QDRANT_COLLECTION_LEGAL)
        client = self._client()
        exists = client.collection_exists(QDRANT_COLLECTION_LEGAL)

        if exists and recreate:
            assert_writable(QDRANT_COLLECTION_LEGAL)  # again, immediately before the drop
            print(f"[LEGAL] ลบ '{QDRANT_COLLECTION_LEGAL}' ตามที่สั่ง --recreate")
            client.delete_collection(QDRANT_COLLECTION_LEGAL)
            exists = False

        if exists:
            print(f"[LEGAL] ใช้ '{QDRANT_COLLECTION_LEGAL}' ที่มีอยู่ (upsert ทับ)")
            # A collection created before the indexes existed still needs them.
            self.ensure_indexes()
            return

        # Same shape as the MITRE collections: one named dense vector plus a
        # named sparse vector, so a hybrid retriever can query either.
        client.create_collection(
            collection_name=QDRANT_COLLECTION_LEGAL,
            vectors_config={"dense": VectorParams(size=EMBED_DIM, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )
        print(f"[LEGAL] สร้าง '{QDRANT_COLLECTION_LEGAL}' (dense {EMBED_DIM} cosine + sparse)")
        self.ensure_indexes()

    def ensure_indexes(self) -> None:
        """Payload indexes for the fields the guardrails filter on.

        Qdrant rejects a filter on an unindexed field outright, so without these
        the safety filters — only chargeable sections may be offered as charges,
        only the version in force on the incident date may be quoted — fail as a
        400 rather than degrading. Created here so that a collection can never
        exist in a state where those filters do not work.
        """
        from qdrant_client.models import PayloadSchemaType

        assert_writable(QDRANT_COLLECTION_LEGAL)
        client = self._client()
        fields = {
            "chargeable": PayloadSchemaType.BOOL,
            "penalties_reliable": PayloadSchemaType.BOOL,
            "verified_by_human": PayloadSchemaType.BOOL,
            "role": PayloadSchemaType.KEYWORD,
            "verification": PayloadSchemaType.KEYWORD,
            "act_slug": PayloadSchemaType.KEYWORD,
            "number": PayloadSchemaType.KEYWORD,
            "origin": PayloadSchemaType.KEYWORD,
            "effective_from_ts": PayloadSchemaType.INTEGER,
        }
        for name, schema in fields.items():
            try:
                client.create_payload_index(
                    collection_name=QDRANT_COLLECTION_LEGAL,
                    field_name=name,
                    field_schema=schema,
                )
            except Exception as exc:  # noqa: BLE001 — an existing index is not an error
                if "already exists" not in str(exc).lower():
                    raise
        print(f"[LEGAL] payload index พร้อม: {', '.join(fields)}")

    def ingest(self, sections: list[LegalSection], batch_size: int = 16) -> int:
        from qdrant_client.models import PointStruct, SparseVector

        assert_writable(QDRANT_COLLECTION_LEGAL)
        rows = selected(sections)
        model, client = self._model(), self._client()
        stored = 0

        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            output = model.encode(
                [embed_text(s) for s in batch],
                return_dense=True,
                return_sparse=True,
                return_colbert_vecs=False,
            )
            dense = output["dense_vecs"].tolist()
            sparse = output["lexical_weights"]

            points = []
            for i, section in enumerate(batch):
                weights = sparse[i]
                points.append(
                    PointStruct(
                        id=point_id(section),
                        vector={
                            "dense": dense[i],
                            "sparse": SparseVector(
                                indices=[int(k) for k in weights.keys()],
                                values=[float(v) for v in weights.values()],
                            ),
                        },
                        payload=to_payload(section),
                    )
                )
            client.upsert(collection_name=QDRANT_COLLECTION_LEGAL, points=points)
            stored += len(points)
            print(f"[LEGAL] {stored}/{len(rows)}", end="\r", flush=True)

        print(f"[LEGAL] เก็บแล้ว {stored}/{len(rows)} มาตรา" + " " * 20)
        return stored


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest Thai statute sections into Qdrant")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be sent, connect to nothing")
    ap.add_argument("--recreate", action="store_true", help="Drop the legal collection first")
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    sections, _ = parse_all()
    rows = selected(sections)
    skipped = len(sections) - len(rows)

    print(f"[LEGAL] แยกได้ {len(sections)} มาตรา — จะ ingest {len(rows)}, ข้าม {skipped} (role={SKIP_ROLES[0]})")
    roles: dict[str, int] = {}
    for s in rows:
        roles[s.role] = roles.get(s.role, 0) + 1
    for role, count in sorted(roles.items(), key=lambda kv: -kv[1]):
        print(f"         {role:<20}{count:>5}")
    unverified = sum(1 for s in rows if not s.verified_by_human)
    print(f"[LEGAL] ยังไม่ตรวจโดยมนุษย์ {unverified}/{len(rows)} — payload ติดธงไว้ทุกจุด")

    if args.dry_run:
        print("\n[LEGAL] --dry-run: ไม่ต่อ Qdrant แสดงตัวอย่างสิ่งที่จะส่ง\n")
        for s in rows[:2]:
            payload = to_payload(s)
            print(f"  id       : {point_id(s)}")
            print(f"  embed    : {embed_text(s)[:100]!r}...")
            for key in ("citation", "role", "chargeable", "verification", "effective_from", "cites"):
                print(f"  {key:<9}: {payload[key]}")
            print()
        return

    ingestor = LegalIngestor()
    ingestor.ensure_collection(recreate=args.recreate)
    ingestor.ingest(rows, batch_size=args.batch)


if __name__ == "__main__":
    main()
