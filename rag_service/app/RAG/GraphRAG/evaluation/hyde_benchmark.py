"""
HyDE Retrieval Ablation (real-CTI tier)
=======================================
Does searching with a hypothetical ATT&CK entry (HyDE, see pipeline/hyde.py)
retrieve the techniques that a Thai case file only *describes*?

The baseline is the served retrieval path: decompose the incident, then
``retrieve_multi_quota`` over [incident, *sub_queries]. Every arm keeps that
structure — the incident slot first, then one slot per sub-query, quota 3,
round-robin — and changes only what a sub-query slot searches with and what the
reranker scores against:

    arm            searches with          reranks against
    quota          sub-query              sub-query          (baseline)
    hyde           HyDE entry             HyDE entry         (classic HyDE)
    hyde_desc      HyDE description only  HyDE description   (no guessed name)
    hyde_fuse      sub-query + HyDE entry HyDE entry
    hyde_fuse_sub  sub-query + HyDE entry sub-query

``hyde`` vs ``hyde_desc`` separates the model's guessed technique name from its
paraphrase of the behaviour. The fuse arms pool both candidate sets, so a
wrong guess can only add candidates, not remove the sub-query's own.

Three phases, each resumable and cached under results/hyde/:
    generate  decompose + write HyDE entries, once per sample (the only phase
              that calls an LLM — ~2 calls per sample)
    retrieve  every arm over the SAME cached sub-queries and entries, so arms
              are paired. No LLM. Graph expansion is skipped: every metric here
              is taken at K <= 15, which is the vector list alone (the quota
              caps it at 15 and subgraph ids are ranked after it)
    report    per-arm table + paired deltas vs quota (bootstrap CI, Wilcoxon)

This is a retrieval ablation, not the served agent end to end.

Usage (from rag_service/app, PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.evaluation.hyde_benchmark --phase all
    python -m RAG.GraphRAG.evaluation.hyde_benchmark --phase retrieve --arms quota,hyde
    python -m RAG.GraphRAG.evaluation.hyde_benchmark --phase generate --max-samples 3
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from .attack_id_metrics import _base_technique, extract_technique_names
from .crosslingual_generation_benchmark import (
    DEFAULT_DATASET,
    LOOKUP_PATH,
    _bootstrap_ci,
    _wilcoxon_p,
)
from .retriever_metrics import (
    hit_at_k,
    reciprocal_rank,
    scoreable_steps,
    step_coverage_at_k,
    step_coverage_by_cue_type,
)

OUT_DIR = Path(__file__).resolve().parent / "results" / "hyde"
GEN_PATH = OUT_DIR / "generation.jsonl"
K_VALUES = [1, 3, 5, 10, 15]
BASELINE = "quota"
ARMS = ("quota", "hyde", "hyde_desc", "hyde_fuse", "hyde_fuse_sub")


# ──────────────────────────────────────────────────────────────────────────────
# I/O
# ──────────────────────────────────────────────────────────────────────────────


def load_samples(path: Path, max_samples: int = 0) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    samples = data["samples"] if isinstance(data, dict) else data
    return samples[:max_samples] if max_samples else samples


def read_jsonl(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    rows = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                rows[row["id"]] = row
    return rows


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# Phase 1 — generate
# ──────────────────────────────────────────────────────────────────────────────


def phase_generate(samples: list[dict]) -> None:
    from ..pipeline.hyde import HydeWriter
    from ..pipeline.query_decomposer import QueryDecomposer

    done = read_jsonl(GEN_PATH)
    todo = [s for s in samples if s["id"] not in done]
    print(f"[GEN] {len(done)} cached, {len(todo)} to generate")
    if not todo:
        return

    decomposer = QueryDecomposer()
    writer = HydeWriter()
    if decomposer.llm is None or writer.llm is None:
        raise SystemExit("[GEN] no LLM configured — refusing to cache fallbacks")

    for i, s in enumerate(todo, 1):
        t0 = time.perf_counter()
        subs = decomposer.decompose(incident=s["query"], verbose=False)
        # decompose() returns [incident] when it fails; a HyDE entry for the
        # whole incident is not what this arm tests, so don't write one.
        decomposed = subs != [s["query"]]
        passages = writer.write(s["query"], subs) if decomposed else [None] * len(subs)
        append_jsonl(
            GEN_PATH,
            {
                "id": s["id"],
                "decomposed": decomposed,
                "sub_queries": subs,
                "hyde": [
                    {"name": p.name, "description": p.description} if p else None
                    for p in passages
                ],
            },
        )
        written = sum(p is not None for p in passages)
        print(
            f"[GEN] {i}/{len(todo)} {s['id']}: {len(subs)} sub-queries, "
            f"{written} HyDE entries ({time.perf_counter() - t0:.1f}s)"
        )


# ──────────────────────────────────────────────────────────────────────────────
# Phase 2 — retrieve
# ──────────────────────────────────────────────────────────────────────────────


def _slots(arm: str, incident: str, gen: dict) -> tuple[list[str], list[list[str] | None]]:
    """(rerank queries, search texts) for one arm. Incident slot first, always.

    A sub-query without a HyDE entry falls back to itself in every arm, so the
    arms differ only where an entry exists.
    """
    from ..pipeline.hyde import HydePassage

    queries: list[str] = [incident]
    search: list[list[str] | None] = [None]
    for sub, h in zip(gen["sub_queries"], gen["hyde"]):
        p = HydePassage(**h) if h else None
        entry = p.as_document() if p else sub
        if arm == "quota":
            q, st = sub, None
        elif arm == "hyde":
            q, st = entry, None
        elif arm == "hyde_desc":
            q, st = (p.description if p else sub), None
        elif arm == "hyde_fuse":
            q, st = entry, ([sub, entry] if p else None)
        elif arm == "hyde_fuse_sub":
            q, st = sub, ([sub, entry] if p else None)
        else:
            raise ValueError(f"unknown arm {arm}")
        queries.append(q)
        search.append(st)

    # Same dedup as production: an identical slot is retrieved once.
    seen: set[tuple] = set()
    out_q, out_s = [], []
    for q, st in zip(queries, search):
        key = (q, tuple(st) if st else None)
        if q.strip() and key not in seen:
            seen.add(key)
            out_q.append(q)
            out_s.append(st)
    return out_q, out_s


def _memoise_search(vector_retriever) -> None:
    """Cache ``search_all`` by (text, top_k); return fresh copies.

    Every arm searches the incident, and several search the same sub-query or
    entry. The reranker and the type re-weight overwrite ``score`` in place,
    so a cached hit must never be handed out twice.
    """
    original = vector_retriever.search_all
    cache: dict[tuple, list] = {}

    def search_all(query: str, top_k: int = 10):
        key = (query, top_k)
        if key not in cache:
            cache[key] = original(query, top_k=top_k)
        return [replace(vr) for vr in cache[key]]

    vector_retriever.search_all = search_all


def phase_retrieve(samples: list[dict], arms: list[str]) -> None:
    from ..config import VECTOR_TOP_K
    from ..retrieval.hybrid_retriever import HybridRetriever
    from .eval_runner import _collect_hybrid_ids, _subtechnique_parent_map

    gens = read_jsonl(GEN_PATH)
    missing = [s["id"] for s in samples if s["id"] not in gens]
    if missing:
        raise SystemExit(f"[RET] {len(missing)} samples not generated yet: run --phase generate")

    parent_map = _subtechnique_parent_map()
    retriever = HybridRetriever()
    _memoise_search(retriever.vector_retriever)
    try:
        for arm in arms:
            path = OUT_DIR / f"retrieval_{arm}.jsonl"
            done = read_jsonl(path)
            todo = [s for s in samples if s["id"] not in done]
            print(f"\n[RET] arm {arm}: {len(done)} cached, {len(todo)} to run")
            for i, s in enumerate(todo, 1):
                queries, search = _slots(arm, s["query"], gens[s["id"]])
                t0 = time.perf_counter()
                result = retriever.retrieve_multi_quota(
                    queries,
                    per_query_k=3,
                    top_k=VECTOR_TOP_K,
                    max_vector=15,
                    max_graph=8,
                    search_texts=search,
                    expand_graph=False,
                )
                ids: list[str] = []
                for sid in _collect_hybrid_ids(result):
                    sid = parent_map.get(sid, sid)
                    if sid not in ids:
                        ids.append(sid)
                append_jsonl(path, {"id": s["id"], "ids": ids,
                                    "latency_ms": (time.perf_counter() - t0) * 1000})
                print(f"[RET] {arm} {i}/{len(todo)} {s['id']}: {len(ids)} ids")
    finally:
        retriever.close()


# ──────────────────────────────────────────────────────────────────────────────
# Phase 3 — report
# ──────────────────────────────────────────────────────────────────────────────


def score_sample(ids: list[str], sample: dict) -> dict:
    """Per-sample metrics. Cue-split coverage is None when the sample has no
    step of that cue type, so it drops out of that mean instead of counting 0."""
    relevant = set(sample["relevant_stix_ids"])
    steps = scoreable_steps(sample.get("attack_steps") or [])
    cue_types = {st.get("cue_type") for st in steps}
    m: dict = {"mrr": reciprocal_rank(ids, relevant)}
    for k in K_VALUES:
        m[f"hit@{k}"] = hit_at_k(ids, relevant, k)
        m[f"step@{k}"] = step_coverage_at_k(ids, steps, k) if steps else None
        by_cue = step_coverage_by_cue_type(ids, steps, k)
        for cue in ("described", "named"):
            m[f"{cue}@{k}"] = by_cue.get(cue) if cue in cue_types else None
    return m


def _mean(xs: list) -> float:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def _guess_diagnostic(samples: list[dict], gens: dict[str, dict]) -> dict:
    """How often the HyDE entries name a gold technique, at parent level.

    Name matching goes through the alias map, which resolves names shared by
    enterprise and mobile to the mobile ID — so this under-counts slightly. It
    is a diagnostic for reading the arms, not a headline.
    """
    with open(LOOKUP_PATH, encoding="utf-8") as f:
        alias_map = json.load(f)["alias_map"]
    recalls, precisions, n_entries, n_slots = [], [], 0, 0
    for s in samples:
        g = gens.get(s["id"])
        if not g or not g["decomposed"]:
            continue
        names = [h["name"] for h in g["hyde"] if h]
        n_entries += len(names)
        n_slots += len(g["hyde"])
        guessed = {_base_technique(t) for n in names
                   for t in extract_technique_names(n, alias_map)}
        gold = {_base_technique(t) for t in s["gold_attack_ids"]}
        if gold:
            recalls.append(len(guessed & gold) / len(gold))
        if guessed:
            precisions.append(len(guessed & gold) / len(guessed))
    return {"recall": _mean(recalls), "precision": _mean(precisions),
            "entries": n_entries, "slots": n_slots}


def phase_report(samples: list[dict], arms: list[str], out_md: Path) -> None:
    gens = read_jsonl(GEN_PATH)
    by_id = {s["id"]: s for s in samples}
    scores: dict[str, dict[str, dict]] = {}
    latency: dict[str, float] = {}
    for arm in arms:
        rows = read_jsonl(OUT_DIR / f"retrieval_{arm}.jsonl")
        rows = {i: r for i, r in rows.items() if i in by_id}
        if not rows:
            print(f"[REPORT] no rows for {arm}, skipped")
            continue
        scores[arm] = {i: score_sample(r["ids"], by_id[i]) for i, r in rows.items()}
        latency[arm] = _mean([r["latency_ms"] for r in rows.values()])

    arms = [a for a in arms if a in scores]
    common = set.intersection(*(set(scores[a]) for a in arms)) if arms else set()
    n_steps = {c: sum(1 for i in common for st in scoreable_steps(by_id[i]["attack_steps"])
                      if st.get("cue_type") == c) for c in ("described", "named")}

    L: list[str] = []
    L.append("# HyDE Retrieval Ablation — real-CTI tier\n")
    L.append(f"Samples: {len(common)} (paired across arms). Steps: "
             f"{n_steps['described']} described, {n_steps['named']} named.")
    decomposed = sum(1 for i in common if gens.get(i, {}).get("decomposed"))
    g = _guess_diagnostic([by_id[i] for i in common], gens)
    L.append(f"Decomposed: {decomposed}/{len(common)}. HyDE entries written: "
             f"{g['entries']}/{g['slots']} sub-query slots.")
    L.append("Retrieval only (vector list, graph expansion skipped); every arm uses the "
             "same cached sub-queries and entries.\n")

    L.append("## Per-arm means\n")
    cols = ["hit@5", "step@5", "step@10", "described@5", "described@10",
            "named@5", "named@10", "mrr"]
    L.append("| arm | " + " | ".join(cols) + " | latency ms |")
    L.append("|---|" + "---|" * (len(cols) + 1))
    for arm in arms:
        vals = [_mean([scores[arm][i][c] for i in common]) for c in cols]
        L.append(f"| {arm} | " + " | ".join(f"{v:.3f}" for v in vals)
                 + f" | {latency[arm]:.0f} |")

    L.append("\n## StepCoverage by K\n")
    for cue in ("step", "described", "named"):
        L.append(f"**{cue}**\n")
        L.append("| arm | " + " | ".join(f"@{k}" for k in K_VALUES) + " |")
        L.append("|---|" + "---|" * len(K_VALUES))
        for arm in arms:
            L.append(f"| {arm} | " + " | ".join(
                f"{_mean([scores[arm][i][f'{cue}@{k}'] for i in common]):.3f}"
                for k in K_VALUES) + " |")
        L.append("")

    if BASELINE in arms:
        L.append(f"## Paired deltas vs `{BASELINE}`\n")
        L.append("Δ = arm − quota per sample. 95% CI: paired bootstrap (10,000). "
                 "p: two-sided Wilcoxon signed-rank on non-zero deltas. "
                 "Cue-split metrics use only samples that have a step of that cue.\n")
        L.append("| arm | metric | Δ mean | 95% CI | p | W/T/L | n |")
        L.append("|---|---|---|---|---|---|---|")
        for arm in arms:
            if arm == BASELINE:
                continue
            for metric in ("step@5", "step@10", "described@5", "described@10",
                           "named@5", "hit@5", "mrr"):
                pairs = [(scores[arm][i][metric], scores[BASELINE][i][metric])
                         for i in sorted(common)]
                deltas = [a - b for a, b in pairs if a is not None and b is not None]
                if not deltas:
                    continue
                lo, hi = _bootstrap_ci(deltas)
                p = _wilcoxon_p(deltas)
                w = sum(d > 0 for d in deltas)
                t = sum(d == 0 for d in deltas)
                lose = sum(d < 0 for d in deltas)
                L.append(f"| {arm} | {metric} | {_mean(deltas):+.3f} | "
                         f"[{lo:+.3f}, {hi:+.3f}] | "
                         f"{'n/a' if p is None else f'{p:.4f}'} | {w}/{t}/{lose} | "
                         f"{len(deltas)} |")

    L.append("\n## Diagnostic — does the HyDE entry name the gold technique?\n")
    L.append(f"Parent-level, via the alias map (under-counts names shared with mobile). "
             f"Per-sample recall of gold techniques among the guessed names: "
             f"**{g['recall']:.3f}**; precision of the guesses: **{g['precision']:.3f}**.")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\n[REPORT] written to {out_md}")


# ──────────────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--phase", choices=("generate", "retrieve", "report", "all"),
                    default="all")
    ap.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--max-samples", type=int, default=0)
    ap.add_argument("--output", type=Path,
                    default=Path(__file__).resolve().parent / "results" / "hyde_ablation.md")
    args = ap.parse_args()

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = set(arms) - set(ARMS)
    if unknown:
        raise SystemExit(f"unknown arms: {', '.join(sorted(unknown))}")

    samples = load_samples(args.dataset, args.max_samples)
    print(f"[HYDE-BENCH] {len(samples)} samples from {args.dataset.name}")
    if args.phase in ("generate", "all"):
        phase_generate(samples)
    if args.phase in ("retrieve", "all"):
        phase_retrieve(samples, arms)
    if args.phase in ("report", "all"):
        phase_report(samples, arms, args.output)


if __name__ == "__main__":
    main()
