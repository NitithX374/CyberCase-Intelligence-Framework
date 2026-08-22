"""
Corpus Cleaning Experiment
============================
The indexed ATT&CK entity documents are raw STIX prose. Measured over the 821
technique/sub-technique documents, 18.5% of the corpus by character count is
boilerplate that carries no discriminative signal:

    (Citation: Microsoft Run Key)          85% of documents contain at least one
    [ftp](https://attack.mitre.org/...)    markdown links to attack.mitre.org
    <code>HKEY_CURRENT_USER\\...</code>     HTML tags around otherwise useful text

"Citation", "https" and "attack.mitre.org" appear in nearly every document, so
they cost sparse retrieval discriminative power and dilute what the dense
encoder and the cross-encoder actually see. Documents run to a median of 1,252
characters and a maximum of 4,728.

This script rebuilds the entity embeddings from cleaned text into a SEPARATE
collection, leaving the production one untouched. The benchmark then points at
it through the existing QDRANT_COLLECTION_ENTITIES environment variable, so the
only thing that differs between the two runs is the document text.

What is removed, and what is deliberately kept:

  removed   (Citation: ...) spans, the URL half of markdown links, HTML tags,
            repeated whitespace
  kept      the link's anchor text - "[ftp](...)" becomes "ftp", which is the
            part that matches a query
  kept      the contents of <code> blocks - a registry path like
            HKEY_CURRENT_USER\\...\\Run is exactly the string a procedure
            description tends to quote

Usage:
    cd rag_service/app

    # inspect the effect without writing anything
    python -m RAG.GraphRAG.evaluation.published.clean_corpus --dry-run

    # build the cleaned collection (embeds locally, needs the GPU/CPU model)
    python -m RAG.GraphRAG.evaluation.published.clean_corpus --build

    # then benchmark against it
    QDRANT_COLLECTION_ENTITIES=mitre_entities_clean \\
      python -m RAG.GraphRAG.evaluation.published.run_benchmark \\
      --dataset tram --arm retrieval --top-k 20 --technique-only --tag k20-clean
"""

from __future__ import annotations

import argparse
import io
import re
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CLEAN_COLLECTION = "mitre_entities_clean"

_CITATION = re.compile(r"\(Citation:[^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\(\s*https?://[^)]*\)")
_BARE_URL = re.compile(r"https?://\S+")
_TAG = re.compile(r"</?[a-zA-Z][^>]*>")
_WS = re.compile(r"\s+")


def clean_attack_text(text: str) -> str:
    """Strip STIX boilerplate while keeping every token that can match a query."""
    if not text:
        return ""
    out = _CITATION.sub(" ", text)
    out = _MD_LINK.sub(r"\1", out)  # keep the anchor text, drop the URL
    out = _TAG.sub(" ", out)  # <code>PATH</code> -> PATH
    out = _BARE_URL.sub(" ", out)
    out = out.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return _WS.sub(" ", out).strip()


def _connect():
    from ... import config as C  # noqa: F401 - kept for symmetry
    from ...config import QDRANT_API_KEY, QDRANT_URL
    from qdrant_client import QdrantClient

    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=120)


def _scroll_all(client, collection: str) -> list:
    points, offset = [], None
    while True:
        batch, offset = client.scroll(
            collection, limit=500, offset=offset, with_payload=True, with_vectors=False
        )
        if not batch:
            break
        points.extend(batch)
        if offset is None:
            break
    return points


def report(points: list) -> None:
    """Print what cleaning does, without writing anything."""
    before, after = [], []
    tech_before, tech_after = [], []
    examples = []

    for p in points:
        doc = p.payload.get("document") or ""
        cleaned = clean_attack_text(doc)
        before.append(len(doc))
        after.append(len(cleaned))
        if p.payload.get("node_label") in ("Technique", "Subtechnique"):
            tech_before.append(len(doc))
            tech_after.append(len(cleaned))
            if len(examples) < 2 and "(Citation:" in doc:
                examples.append((p.payload.get("attack_id"), doc, cleaned))

    tot_b, tot_a = sum(before), sum(after)
    print("[CLEAN] entities            : " + str(len(points)))
    print(
        "[CLEAN] all documents       : "
        + str(tot_b) + " -> " + str(tot_a) + " chars "
        + "(-" + format(100 * (tot_b - tot_a) / max(tot_b, 1), ".1f") + "%)"
    )
    if tech_before:
        tb, ta = sum(tech_before), sum(tech_after)
        print(
            "[CLEAN] technique documents : "
            + str(tb) + " -> " + str(ta) + " chars "
            + "(-" + format(100 * (tb - ta) / max(tb, 1), ".1f") + "%)"
        )
        print(
            "[CLEAN] technique median    : "
            + str(int(statistics.median(tech_before))) + " -> "
            + str(int(statistics.median(tech_after))) + " chars"
        )

    for attack_id, doc, cleaned in examples:
        print("\n[CLEAN] example " + str(attack_id))
        print("  before: " + repr(doc[:260]))
        print("  after : " + repr(cleaned[:260]))


def build(points: list, client) -> None:
    """Embed the cleaned text into a separate collection."""
    from qdrant_client.models import (
        Distance,
        PointStruct,
        SparseVector,
        SparseVectorParams,
        VectorParams,
    )

    from ...config import EMBED_MODEL, USE_FP16

    from FlagEmbedding import BGEM3FlagModel

    if client.collection_exists(CLEAN_COLLECTION):
        print("[CLEAN] dropping existing " + CLEAN_COLLECTION)
        client.delete_collection(CLEAN_COLLECTION)

    client.create_collection(
        collection_name=CLEAN_COLLECTION,
        vectors_config={"dense": VectorParams(size=1024, distance=Distance.COSINE)},
        sparse_vectors_config={"sparse": SparseVectorParams()},
    )
    print("[CLEAN] created " + CLEAN_COLLECTION)

    print("[CLEAN] loading " + EMBED_MODEL + " ...")
    model = BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)

    batch_size = 16
    written = 0
    for start in range(0, len(points), batch_size):
        chunk = points[start : start + batch_size]
        texts = [clean_attack_text(p.payload.get("document") or "") for p in chunk]

        encoded = model.encode(
            texts, return_dense=True, return_sparse=True, return_colbert_vecs=False
        )
        dense = encoded["dense_vecs"]
        sparse = encoded["lexical_weights"]

        batch_points = []
        for i, p in enumerate(chunk):
            payload = dict(p.payload)
            payload["document"] = texts[i]
            payload["document_raw_len"] = len(p.payload.get("document") or "")
            weights = {int(k): float(v) for k, v in sparse[i].items()}
            batch_points.append(
                PointStruct(
                    id=p.id,
                    vector={
                        "dense": dense[i].tolist(),
                        "sparse": SparseVector(
                            indices=list(weights.keys()), values=list(weights.values())
                        ),
                    },
                    payload=payload,
                )
            )

        client.upsert(collection_name=CLEAN_COLLECTION, points=batch_points)
        written += len(batch_points)
        if written % 320 == 0 or written >= len(points):
            print("  " + str(written) + "/" + str(len(points)))

    print("[CLEAN] wrote " + str(written) + " points to " + CLEAN_COLLECTION)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild entity embeddings from cleaned text")
    parser.add_argument("--dry-run", action="store_true", help="report the effect, write nothing")
    parser.add_argument("--build", action="store_true", help="create and populate the clean collection")
    args = parser.parse_args()

    if not args.dry_run and not args.build:
        parser.error("pass --dry-run or --build")

    from ...config import QDRANT_COLLECTION_ENTITIES

    client = _connect()
    source = QDRANT_COLLECTION_ENTITIES
    if source == CLEAN_COLLECTION:
        raise SystemExit(
            "QDRANT_COLLECTION_ENTITIES is already " + CLEAN_COLLECTION
            + "; unset it so the raw collection is the source"
        )

    print("[CLEAN] source collection   : " + source)
    points = _scroll_all(client, source)
    report(points)

    if args.build:
        build(points, client)


if __name__ == "__main__":
    main()
