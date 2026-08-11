"""
Evaluation Runner
==================
CLI orchestrator for RAG evaluation.

Usage:
    cd backend/RAG/GraphRAG
    python -m evaluation.eval_runner --dataset evaluation/eval_dataset.json --mode retriever
    python -m evaluation.eval_runner --dataset evaluation/eval_dataset.json --mode generation
    python -m evaluation.eval_runner --dataset evaluation/eval_dataset.json --mode full

Modes:
    retriever  — Benchmark Vector / Graph / Hybrid retrievers
    generation — Evaluate LLM answer quality (RAGAS + fallback)
    full       — Run both retriever + generation evaluation
"""

from __future__ import annotations
import argparse
import io
import sys
from pathlib import Path

# Fix relative imports when run directly from IDE or wrong directory
if __package__ is None or __package__ == "evaluation":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    __package__ = "GraphRAG.evaluation"

sys.stdout.reconfigure(encoding='utf-8')
# UTF-8 FIX FOR WINDOWS
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from .generation_metrics import GenerationEvalResult, evaluate_generation
from .ground_truth import load_ground_truth
from .retriever_metrics import RetrieverEvalResult, evaluate_retriever

# ──────────────────────────────────────────────────────────────────────────────
# Retriever Adapters
# ──────────────────────────────────────────────────────────────────────────────


def _make_vector_retriever_fn(embed_model=None):
    """Create a retriever function for vector-only search."""
    from ..retrieval.vector_retriever import VectorRetriever

    retriever = VectorRetriever(embed_model=embed_model)

    def fn(query: str) -> list[str]:
        results = retriever.search_all(query, top_k=10)
        return [r.stix_id for r in results]

    return fn, None  # No cleanup needed for vector retriever


def _make_graph_retriever_fn():
    """Create a retriever function for graph-only search (requires STIX IDs as seed).

    Note: GraphRetriever expands from known STIX IDs, so for standalone eval
    we use it differently — we do a Cypher name search first.
    """
    from ..retrieval.graph_retriever import GraphRetriever
    import re

    retriever = GraphRetriever()

    def fn(query: str) -> list[str]:
        # Extract ATT&CK IDs (e.g., T1566, S0002, G0016)
        attack_ids = re.findall(r'[T|S|G]\d{4}', query, re.IGNORECASE)
        
        # Extract basic keywords (ignoring common words)
        ignore_words = {"what", "is", "the", "how", "can", "i", "do", "does", "are", "explain", "relationship", "between", "and", "in", "for", "to", "of", "a", "an", "all", "technique", "techniques", "exist", "does", "use", "detect", "data", "sources", "classified", "as", "work", "campaigns", "have", "targeted", "sector"}
        clean_query = re.sub(r'[^\w\s]', ' ', query).lower()
        keywords = [w for w in clean_query.split() if w not in ignore_words and len(w) > 2]
        
        match_clauses = []
        params = {}
        
        if attack_ids:
            for i, aid in enumerate(attack_ids):
                match_clauses.append(f"toUpper(n.attack_id) = $attack_id_{i}")
                params[f"attack_id_{i}"] = aid.upper()
                
        if keywords:
            for i, kw in enumerate(keywords):
                match_clauses.append(f"toLower(n.name) CONTAINS $kw_{i}")
                params[f"kw_{i}"] = kw
        
        # Fallback to whole string match if no keywords found
        if not match_clauses:
            match_clauses.append("toLower(n.name) CONTAINS toLower($query) OR toLower(n.description) CONTAINS toLower($query)")
            params["query"] = query
            
        where_clause = " OR ".join(match_clauses)
        
        # Find matching nodes, then expand 1 hop to simulate graph expansion
        cypher = f"""
        MATCH (n)
        WHERE {where_clause}
        WITH n LIMIT 5
        OPTIONAL MATCH (n)-[]-(m)
        WITH n, collect(m.stix_id) AS neighbor_ids
        RETURN n.stix_id AS stix_id, neighbor_ids
        """
        
        try:
            results = retriever.query_cypher(cypher, params=params)
            ids = set()
            for r in results:
                if r.get("stix_id"):
                    ids.add(r["stix_id"])
                for nid in r.get("neighbor_ids", []):
                    if nid:
                        ids.add(nid)
            return list(ids)
        except Exception as e:
            print(f"[GRAPH] Cypher error: {e}")
            return []

    return fn, retriever.close


def _subtechnique_parent_map() -> dict[str, str]:
    """sub-technique stix_id -> parent technique stix_id.

    Qdrant holds 2,195 entities including 522 sub-techniques; Neo4j holds 299
    parent techniques and no sub-techniques. Gold is resolved through Neo4j, so
    it is always parent-granular — while the retriever can and does return the
    sub-technique. Verified that the 299 parent stix_ids are identical in both
    stores, so the map can be built from Qdrant alone.
    """
    from .embed_ab.arms import make_client
    from ..config import QDRANT_COLLECTION_ENTITIES

    client = make_client()
    by_attack_id: dict[str, str] = {}
    subs: list[tuple[str, str]] = []  # (sub stix_id, parent attack_id)
    offset = None
    while True:
        points, offset = client.scroll(
            QDRANT_COLLECTION_ENTITIES, limit=1000, offset=offset, with_payload=True
        )
        for p in points:
            payload = p.payload or {}
            attack_id, stix_id = payload.get("attack_id"), payload.get("stix_id")
            if not attack_id or not stix_id:
                continue
            by_attack_id[attack_id] = stix_id
            if "." in attack_id:
                subs.append((stix_id, attack_id.split(".")[0]))
        if offset is None:
            break

    mapping = {
        sub_stix: by_attack_id[parent_aid]
        for sub_stix, parent_aid in subs
        if parent_aid in by_attack_id
    }
    print(f"[EVAL] Sub-technique -> parent map: {len(mapping)} entries")
    return mapping


def _normalise_to_parent(fn, parent_map: dict[str, str]):
    """Wrap a retriever fn so its ids are parent-granular, like the gold.

    Gold was rolled up to parent because the graph has no sub-techniques.
    Scoring predictions without the same roll-up compares the two at different
    granularities and marks a correct sub-technique hit as a miss — which is a
    defect in the measurement, not a concession to the retriever.

    Ids are replaced (not appended) and de-duplicated, so one retrieved item
    still occupies one rank and @K keeps its meaning.
    """
    def wrapped(query: str) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for stix_id in fn(query):
            canonical = parent_map.get(stix_id, stix_id)
            if canonical not in seen:
                seen.add(canonical)
                out.append(canonical)
        return out

    return wrapped


def _collect_hybrid_ids(result) -> list[str]:
    """Flatten a GraphRAGResult into an ordered, deduped STIX-id list
    (vector hits first, then each subgraph's center node + neighbors)."""
    ids: list[str] = []
    seen: set[str] = set()
    for vr in result.vector_results:
        if vr.stix_id not in seen:
            ids.append(vr.stix_id)
            seen.add(vr.stix_id)
    for gr in result.graph_results:
        if gr.center_node and gr.center_node.stix_id not in seen:
            ids.append(gr.center_node.stix_id)
            seen.add(gr.center_node.stix_id)
        for nb in gr.neighbors:
            if nb.stix_id not in seen:
                ids.append(nb.stix_id)
                seen.add(nb.stix_id)
    return ids


def _make_hybrid_retriever_fn(embed_model=None):
    """Create a retriever function for hybrid (Vector + Graph) search —
    single-query baseline (no decomposition)."""
    from ..retrieval.hybrid_retriever import HybridRetriever

    retriever = HybridRetriever(embed_model=embed_model)

    def fn(query: str) -> list[str]:
        result = retriever.retrieve(query, top_k=10)
        return _collect_hybrid_ids(result)

    return fn, retriever.close


def _make_hybrid_quota_retriever_fn(embed_model=None, use_local: bool = False):
    """Hybrid retriever with query decomposition + per-query quota — mirrors the
    production agent path (``_node_retrieve``). The incident is decomposed into
    atomic per-technique sub-queries, each retrieved under a quota and round-robin
    interleaved, so every technique survives the final trim. Compare against
    ``_make_hybrid_retriever_fn`` (single-query) to measure whether decompose +
    quota improves multi-technique recall.

    NOTE: decomposition needs an LLM (ANTHROPIC_API_KEY, or --local Ollama). With
    no LLM the decomposer falls back to the whole query → this degenerates to a
    single-query hybrid run (the eval would then just mirror the baseline).
    """
    from ..config import VECTOR_TOP_K
    from ..pipeline.query_decomposer import QueryDecomposer
    from ..retrieval.hybrid_retriever import HybridRetriever

    retriever = HybridRetriever(embed_model=embed_model)
    decomposer = QueryDecomposer(use_local=use_local)

    def fn(query: str) -> list[str]:
        sub_queries = decomposer.decompose(incident=query, verbose=False)
        # The full incident goes in FIRST, exactly as _node_retrieve does it:
        # production keeps it as a holistic channel because the atomic
        # sub-queries lose the surrounding context, and its own comment records
        # that this improves technique coverage. Omitting it here made the arm
        # score below the system it is supposed to represent.
        all_queries: list[str] = []
        for q in [query, *sub_queries]:
            if q and q.strip() and q not in all_queries:
                all_queries.append(q)
        result = retriever.retrieve_multi_quota(
            all_queries, per_query_k=3, top_k=VECTOR_TOP_K, max_vector=15, max_graph=8
        )
        return _collect_hybrid_ids(result)

    return fn, retriever.close


# ──────────────────────────────────────────────────────────────────────────────
# Generation Adapter
# ──────────────────────────────────────────────────────────────────────────────


def _make_generation_fn(embed_model=None, use_local: bool = False):
    """Create a generation function wrapping GraphRAGChain."""
    from ..pipeline.chain import GraphRAGChain

    chain = GraphRAGChain(embed_model=embed_model, use_local=use_local)

    def fn(query: str) -> tuple[str, list[str]]:
        """Returns (answer, list_of_context_chunks)."""
        # Get retrieval context (same dual-query flow as GraphRAGChain.query)
        from ..pipeline.cross_lingual import build_retrieval_queries

        english_query = chain.translator.translate_query(query)
        queries = build_retrieval_queries(query, english_query)
        graphrag_result = chain.retriever.retrieve_multi(queries)

        from ..pipeline.context_builder import build_context

        build_context(graphrag_result)

        # Get answer
        answer = chain.query(query, verbose=False)

        # Split context into chunks for RAGAS (one per semantic result)
        context_chunks = []
        for vr in graphrag_result.vector_results[:5]:
            context_chunks.append(vr.document)
        for gr in graphrag_result.graph_results:
            text = gr.to_text()
            if text:
                context_chunks.append(text)

        return answer, context_chunks

    return fn, chain.close


# ──────────────────────────────────────────────────────────────────────────────
# Main Runner
# ──────────────────────────────────────────────────────────────────────────────


class _ArmSkipped(Exception):
    """Raised to skip an arm the caller did not select in --arms."""


class EvalRunner:
    """Orchestrates the full evaluation pipeline."""

    # Only the quota arm spends money — it calls an LLM to decompose each
    # incident. Keeping the arms selectable means a free run is one flag away.
    ALL_ARMS = ("vector", "graph", "hybrid", "quota")
    PAID_ARMS = ("quota",)

    def __init__(self, dataset_path: str, mode: str = "full", use_local: bool = False,
                 max_samples: int = 0, arms: tuple[str, ...] | None = None,
                 k_values: list[int] | None = None):
        self.dataset_path = Path(dataset_path)
        self.mode = mode
        self.use_local = use_local
        self.arms = tuple(arms) if arms else self.ALL_ARMS
        # Hybrid returns hundreds of ids (vector hits + every graph neighbour).
        # Scoring only the top 10 cannot distinguish "never retrieved" from
        # "retrieved but ranked far down", so the cutoffs are configurable.
        self.k_values = k_values or [1, 3, 5, 10]

        all_samples = load_ground_truth(self.dataset_path)
        # Filter out samples with > 50 relevant STIX IDs
        self.samples = [
            s for s in all_samples
            if not s.relevant_stix_ids or len(s.relevant_stix_ids) <= 50
        ]

        filtered_count = len(all_samples) - len(self.samples)
        if filtered_count > 0:
            print(f"[EVAL] Filtered out {filtered_count} samples with > 50 relevant STIX IDs")

        if max_samples and max_samples < len(self.samples):
            self.samples = self.samples[:max_samples]
            print(f"[EVAL] Capped to {max_samples} samples (--max-samples)")

        print(f"[EVAL] Samples for evaluation: {len(self.samples)}")
        
        self._embed_model = None
        self._cleanups = []

    def _get_embed_model(self):
        """Lazy-load and share the embedding model."""
        if self._embed_model is None:
            from FlagEmbedding import BGEM3FlagModel
            from ..config import EMBED_MODEL, USE_FP16

            print(f"[EVAL] Loading embedding model {EMBED_MODEL}...")
            self._embed_model = BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)
        return self._embed_model

    def run(self) -> dict:
        """Execute evaluation and return results dict."""
        results = {}

        try:
            if self.mode in ("retriever", "full"):
                results["retriever"] = self._run_retriever_eval()

            if self.mode in ("generation", "full"):
                results["generation"] = self._run_generation_eval()
        finally:
            # Cleanup all opened resources
            for cleanup in self._cleanups:
                try:
                    cleanup()
                except Exception:
                    pass

        return results

    def _run_retriever_eval(self) -> list[RetrieverEvalResult]:
        """Run retriever benchmarks on all 3 retriever modes."""
        # Only use samples that have relevant STIX IDs
        eval_samples = [s for s in self.samples if s.relevant_stix_ids]
        print(
            f"\n[EVAL] Running retriever evaluation ({len(eval_samples)} samples with ground truth)"
        )

        results = []
        embed_model = self._get_embed_model()
        print(f"[EVAL] Arms: {', '.join(self.arms)}")
        parent_map = _subtechnique_parent_map()

        # 1. Vector Retriever
        print("\n" + "═" * 60)
        print("  Evaluating: Vector Retriever (ChromaDB)")
        print("═" * 60)
        if "vector" not in self.arms:
            print("  [SKIP] not selected in --arms")
        else:
            fn, cleanup = _make_vector_retriever_fn(embed_model)
            fn = _normalise_to_parent(fn, parent_map)
            if cleanup:
                self._cleanups.append(cleanup)
            vr_result = evaluate_retriever(
                fn, eval_samples, k_values=self.k_values,
                retriever_name="Vector (ChromaDB)"
            )
            results.append(vr_result)
            print(vr_result.to_table())

        # 2. Graph Retriever
        print("\n" + "═" * 60)
        print("  Evaluating: Graph Retriever (Neo4j)")
        print("═" * 60)
        try:
            if "graph" not in self.arms:
                raise _ArmSkipped()
            fn, cleanup = _make_graph_retriever_fn()
            fn = _normalise_to_parent(fn, parent_map)
            if cleanup:
                self._cleanups.append(cleanup)
            gr_result = evaluate_retriever(
                fn, eval_samples, k_values=self.k_values, retriever_name="Graph (Neo4j)"
            )
            results.append(gr_result)
            print(gr_result.to_table())
        except _ArmSkipped:
            print("  [SKIP] not selected in --arms")
        except Exception as e:
            print(f"  [SKIP] Graph retriever unavailable: {e}")

        # 3. Hybrid Retriever
        print("\n" + "═" * 60)
        print("  Evaluating: Hybrid Retriever (Vector + Graph)")
        print("═" * 60)
        try:
            if "hybrid" not in self.arms:
                raise _ArmSkipped()
            fn, cleanup = _make_hybrid_retriever_fn(embed_model)
            fn = _normalise_to_parent(fn, parent_map)
            if cleanup:
                self._cleanups.append(cleanup)
            hr_result = evaluate_retriever(
                fn, eval_samples, k_values=self.k_values, retriever_name="Hybrid (Vector+Graph)"
            )
            results.append(hr_result)
            print(hr_result.to_table())
        except _ArmSkipped:
            print("  [SKIP] not selected in --arms")
        except Exception as e:
            print(f"  [SKIP] Hybrid retriever unavailable: {e}")

        # 4. Hybrid + Quota (decompose → retrieve_multi_quota) — production agent path
        print("\n" + "═" * 60)
        print("  Evaluating: Hybrid + Quota (decompose + per-query quota)")
        print("═" * 60)
        try:
            if "quota" not in self.arms:
                raise _ArmSkipped()
            fn, cleanup = _make_hybrid_quota_retriever_fn(
                embed_model, use_local=self.use_local
            )
            fn = _normalise_to_parent(fn, parent_map)
            if cleanup:
                self._cleanups.append(cleanup)
            hq_result = evaluate_retriever(
                fn, eval_samples, k_values=self.k_values, retriever_name="Hybrid+Quota (decompose)"
            )
            results.append(hq_result)
            print(hq_result.to_table())
        except _ArmSkipped:
            print("  [SKIP] not selected in --arms")
        except Exception as e:
            print(f"  [SKIP] Hybrid+Quota retriever unavailable: {e}")

        # Comparison table
        self._print_comparison(results)
        return results

    def _run_generation_eval(self) -> GenerationEvalResult:
        """Run generation evaluation."""
        print("\n" + "═" * 60)
        print("  Evaluating: Answer Generation (GraphRAGChain)")
        print("═" * 60)

        embed_model = self._get_embed_model()
        fn, cleanup = _make_generation_fn(embed_model, use_local=self.use_local)
        if cleanup:
            self._cleanups.append(cleanup)

        gen_result = evaluate_generation(fn, self.samples, use_local=self.use_local)
        print(gen_result.to_table())
        return gen_result

    def _print_comparison(self, results: list[RetrieverEvalResult]) -> None:
        """Print a side-by-side comparison table."""
        if len(results) < 2:
            return

        print("\n" + "═" * 70)
        print("  RETRIEVER COMPARISON")
        print("═" * 70)

        # Header
        header = f"  {'Metric':<20}"
        for r in results:
            short = r.retriever_name.split("(")[0].strip()
            header += f"{short:>16}"
        print(header)
        print("  " + "─" * (20 + 16 * len(results)))

        # K=5 metrics (most common benchmark)
        k = 5
        for metric_name in ["Hit", "Recall", "Precision", "NDCG"]:
            row = f"  {metric_name + '@' + str(k):<20}"
            for r in results:
                metric_dict = getattr(r, f"{metric_name.lower()}_at_k")
                val = metric_dict.get(k, 0.0)
                row += f"{val:>16.3f}"
            print(row)

        # Scalar metrics
        for metric_name, attr in [("MRR", "mrr"), ("MAP", "map_score")]:
            row = f"  {metric_name:<20}"
            for r in results:
                val = getattr(r, attr)
                row += f"{val:>16.3f}"
            print(row)

        # Latency
        row = f"  {'Latency (ms)':<20}"
        for r in results:
            row += f"{r.avg_latency_ms:>16.1f}"
        print(row)
        print()


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="RAG Evaluation Runner for MITRE ATT&CK GraphRAG"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="evaluation/eval_dataset.json",
        help="Path to ground truth JSON file",
    )
    parser.add_argument(
        "--mode",
        choices=["retriever", "generation", "full"],
        default="full",
        help="Evaluation mode: retriever, generation, or full (both)",
    )
    parser.add_argument(
        "--output", type=str, help="Export output to file (.txt or .md)"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="Limit evaluation to first N samples (0 = no limit)",
    )
    parser.add_argument(
        "--arms",
        type=str,
        default="",
        help=(
            "Comma-separated retriever arms to run: vector,graph,hybrid,quota "
            "(default: all). Only 'quota' calls an LLM — "
            "'--arms vector,graph,hybrid' is a free run."
        ),
    )
    parser.add_argument(
        "--k",
        type=str,
        default="1,3,5,10",
        help="Comma-separated K cutoffs for @K metrics (default: 1,3,5,10)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help=(
            "Use local Ollama models instead of Claude/OpenRouter. "
            "Generation: qwen2.5:7b  |  RAGAS judge: gemma3:4b  "
            "(requires: ollama pull qwen2.5:7b && ollama pull gemma3:4b)"
        ),
    )

    args = parser.parse_args()

    if args.local:
        from ..config import LOCAL_LLM_MODEL, LOCAL_EVAL_MODEL, OLLAMA_BASE_URL
        print(f"\n[LOCAL MODE]  Generation model : {LOCAL_LLM_MODEL}")
        print(f"[LOCAL MODE]  RAGAS judge      : {LOCAL_EVAL_MODEL}")
        print(f"[LOCAL MODE]  Ollama URL        : {OLLAMA_BASE_URL}\n")

    if args.output:
        tee = open(args.output, "w", encoding="utf-8")

        class Tee:
            def write(self, data):
                sys.stdout_orig.write(data)  # type: ignore
                tee.write(data)

            def flush(self):
                sys.stdout_orig.flush()  # type: ignore
                tee.flush()

        sys.stdout_orig = sys.stdout  # type: ignore
        sys.stdout = Tee()  # type: ignore

    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip()) or None
    if arms:
        unknown = set(arms) - set(EvalRunner.ALL_ARMS)
        if unknown:
            parser.error(
                f"unknown arm(s): {', '.join(sorted(unknown))} — "
                f"choose from {', '.join(EvalRunner.ALL_ARMS)}"
            )
    k_values = sorted({int(k) for k in args.k.split(",") if k.strip()})
    runner = EvalRunner(dataset_path=args.dataset, mode=args.mode, use_local=args.local,
                        max_samples=args.max_samples, arms=arms, k_values=k_values)
    runner.run()

    print("\n" + "═" * 60)
    print("  EVALUATION COMPLETE")
    print("═" * 60)


if __name__ == "__main__":
    main()
