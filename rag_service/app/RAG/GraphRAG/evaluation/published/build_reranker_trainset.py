"""
Re-ranker Training Set, With Leakage Removed
==============================================
Builds (query, positive technique, negative techniques) triples for fine-tuning
the cross-encoder, from data this project already holds.

Where the data comes from
-------------------------
Neo4j carries 18,383 `USES` edges from a Group/Software/Campaign to a Technique
or Sub-technique, each with a description that is a real procedure example:

    T1053.005  "TrickBot creates a scheduled task on the system that provides
                persistence."

That is exactly the shape of the benchmark input, and exactly the judgement the
re-ranker has to make: does this technique describe this behaviour? It is five
times the size of the labelled train split TechniqueRAG retrieves over (3,469),
and it comes from public MITRE STIX rather than anyone's annotation effort.

Why dedupe is not optional
--------------------------
The published benchmarks are themselves built from MITRE procedure examples, so
the training pool and the test set share a source. Measured: **228 of the 725
TRAM test items (31.4%) appear verbatim in the pool, 207 of them under the same
technique label.**

Training on those and then testing on them measures memorisation, not
capability. The score would rise and mean nothing, and it would not transfer to
the Thai case files this system actually has to handle.

Exact string matching does NOT catch this. TRAM strips the actor name from the
front of each sentence:

    MITRE   "[TrickBot](https://attack.mitre.org/software/S0266) creates a
             scheduled task on the system that provides persistence.(Citation: ...)"
    TRAM    "creates a scheduled task on the system that provides persistence."

so the strings are never equal and a naive check reports zero overlap. Matching
is therefore done on normalised text - citations and links stripped, lowercased,
punctuation removed - and by containment rather than equality.

Every fetched benchmark split is excluded, not just the one currently being
reported, so a later Expert or Procedures run cannot be contaminated by a model
trained today.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.published.build_reranker_trainset
    python -m RAG.GraphRAG.evaluation.published.build_reranker_trainset --negatives 12
"""

from __future__ import annotations

import argparse
import io
import json
import random
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .attack_version_map import BENCHMARKS, DATA_DIR, VersionMap

OUTPUT_PATH = DATA_DIR / "reranker_trainset.jsonl"
EXCLUDED_PATH = DATA_DIR / "reranker_excluded.jsonl"

_CITATION = re.compile(r"\(Citation:[^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\(\s*https?://[^)]*\)")
_NON_ALNUM = re.compile(r"[^a-z0-9 ]")

MIN_QUERY_CHARS = 40


def normalise(text: str) -> str:
    """Lowercase, drop citations/links/punctuation, collapse whitespace.

    This is the form both sides are compared in. Without it the actor-name
    stripping in the benchmarks hides the overlap entirely.
    """
    out = _CITATION.sub(" ", text or "")
    out = _MD_LINK.sub(r"\1", out)
    out = _NON_ALNUM.sub(" ", out.lower())
    return " ".join(out.split())


def load_procedure_pairs() -> list[dict]:
    """Every USES edge into a technique that carries a usable description."""
    from ...config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    query = """
        MATCH (a)-[r:USES]->(t)
        WHERE (t:Technique OR t:Subtechnique)
          AND t.attack_id IS NOT NULL
          AND r.description IS NOT NULL
          AND size(r.description) > 40
        RETURN t.attack_id AS attack_id, t.name AS name, r.description AS description
    """
    try:
        with driver.session() as session:
            return [dict(record) for record in session.run(query)]
    finally:
        driver.close()


def load_benchmark_texts() -> list[tuple[str, str]]:
    """(split, normalised text) for every fetched benchmark test item."""
    out: list[tuple[str, str]] = []
    for split in BENCHMARKS:
        path = DATA_DIR / (split + "_zeroshot_test.json")
        if not path.exists():
            print("[TRAIN] " + split.ljust(12) + "not fetched, cannot exclude it")
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        kept = 0
        for row in rows:
            text = normalise(row.get("input", ""))
            if len(text) >= MIN_QUERY_CHARS:
                out.append((split, text))
                kept += 1
        print("[TRAIN] " + split.ljust(12) + str(kept) + " test items to exclude")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a leakage-free re-ranker training set")
    parser.add_argument("--negatives", type=int, default=8, help="hard negatives per positive")
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args()

    random.seed(args.seed)
    vmap = VersionMap.load()

    pairs = load_procedure_pairs()
    print("[TRAIN] procedure examples in the graph : " + str(len(pairs)))

    benchmark = load_benchmark_texts()
    print("[TRAIN] benchmark items to exclude      : " + str(len(benchmark)))

    kept: list[dict] = []
    excluded: list[dict] = []
    seen_queries: set[str] = set()

    for pair in pairs:
        query = normalise(pair["description"])
        if len(query) < MIN_QUERY_CHARS:
            continue

        # Containment, not equality: the benchmark text is the tail of the
        # procedure sentence with the actor name removed from the front.
        leak = next(((split, text) for split, text in benchmark if text in query), None)
        if leak is not None:
            excluded.append(
                {
                    "attack_id": pair["attack_id"],
                    "description": pair["description"],
                    "matched_split": leak[0],
                    "matched_text": leak[1][:200],
                }
            )
            continue

        if query in seen_queries:  # the same procedure text can appear twice
            continue
        seen_queries.add(query)

        current = vmap.map_id(pair["attack_id"])
        if current is None:
            continue  # label retired with no successor; nothing to learn towards
        kept.append(
            {
                "query": " ".join((pair["description"] or "").split()),
                "positive": current,
                "positive_name": pair["name"],
            }
        )

    # Hard negatives: same parent technique where possible, so the model has to
    # separate sub-techniques rather than just topics.
    by_parent: dict[str, list[str]] = {}
    all_ids = sorted({row["positive"] for row in kept})
    for attack_id in all_ids:
        by_parent.setdefault(attack_id.split(".")[0], []).append(attack_id)

    for row in kept:
        parent = row["positive"].split(".")[0]
        siblings = [i for i in by_parent.get(parent, []) if i != row["positive"]]
        pool = [i for i in all_ids if i != row["positive"]]
        negatives = siblings[: args.negatives]
        while len(negatives) < args.negatives and pool:
            candidate = random.choice(pool)
            if candidate not in negatives and candidate != row["positive"]:
                negatives.append(candidate)
        row["negatives"] = negatives

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        for row in kept:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with EXCLUDED_PATH.open("w", encoding="utf-8") as handle:
        for row in excluded:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print()
    print("[TRAIN] kept      : " + str(len(kept)) + " training queries")
    print("[TRAIN] EXCLUDED  : " + str(len(excluded)) + " as benchmark leakage")
    print("[TRAIN] techniques: " + str(len(all_ids)) + " distinct labels")
    print("[TRAIN] negatives : " + str(args.negatives) + " per positive")
    print("[TRAIN] written   : " + str(OUTPUT_PATH))
    print("[TRAIN] excluded  : " + str(EXCLUDED_PATH) + "  (keep this - it is the audit trail)")

    if excluded:
        print()
        print("[TRAIN] examples of what was removed:")
        for row in excluded[:3]:
            print("  " + row["attack_id"] + " (" + row["matched_split"] + ")")
            print("    " + " ".join(row["description"].split())[:150])


if __name__ == "__main__":
    main()
