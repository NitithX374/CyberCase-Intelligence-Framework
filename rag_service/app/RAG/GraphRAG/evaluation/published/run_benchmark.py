"""
Published-Baseline Benchmark Runner
=====================================
Runs this project's retrieval / RAG stack over the TechniqueRAG benchmark
splits (TRAM, Procedures, Expert) and scores it with the upstream protocol, so
the numbers sit in the same table as TechniqueRAG and H-TechniqueRAG.

What is being compared - read this before quoting any number
------------------------------------------------------------
These benchmarks are a short-text labelling task: 80-400 characters of English
CTI prose in, a set of ATT&CK IDs out. That is NOT what this pipeline is for
(a long Thai incident narrative in, a structured prosecutor case summary out).
The comparable slice is retrieval plus technique identification, so the agent
graph is deliberately bypassed: no router, no decomposition, no self-reflection
loop. Decomposition in particular would shred an 80-character input.

Arms
----
  retrieval   Hybrid retriever only, ranked ATT&CK IDs. No LLM, no cost.
              Compare against their retrieval/ranking baselines
              (BM25, NCE, Text2TTP, RankGPT).
  rag-en      Retrieval context -> core LLM -> English technique list.
              Compare against the TechniqueRAG rows.
  rag-th      Same context, Thai answer, IDs extracted from Thai prose.
              Cross-lingual delta - no published baseline does this.
  llm-only    No retrieval, zero-shot core LLM.
              Compare against their GPT-4o / DeepSeek v3 rows.

Fairness note to state in any write-up: their fine-tuned rows trained on the
matching train split. Every arm here is zero-shot, so the honest comparison is
against their zero-shot and off-the-shelf-retriever rows.

Gold labels are reconciled to ATT&CK v19 first (see attack_version_map.py);
without that, revoked families like T1562.* cap recall for reasons unrelated
to retrieval quality.

Usage:
    cd rag_service/app

    # 1. one-time setup
    python -m RAG.GraphRAG.evaluation.published.fetch_datasets
    python -m RAG.GraphRAG.evaluation.published.attack_version_map --stats

    # 2. free arm first - validates the harness end to end
    python -m RAG.GraphRAG.evaluation.published.run_benchmark --dataset tram --arm retrieval

    # 3. paid arms (announce cost first)
    python -m RAG.GraphRAG.evaluation.published.run_benchmark --dataset tram --arm rag-en --limit 100

    # 4. score whatever has been run
    python -m RAG.GraphRAG.evaluation.published.run_benchmark --score

Runs append to data/runs/<dataset>__<arm>.jsonl and resume by sample id, so a
credit outage or a Ctrl-C costs nothing already paid for.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .attack_version_map import BENCHMARKS, DATA_DIR, VersionMap
from .metrics import MARKDOWN_HEADER, MODES, extract_attack_ids, score_at_k, score_corpus

RUNS_DIR = DATA_DIR / "runs"
RESULTS_PATH = Path(__file__).resolve().parent / "RESULTS.md"

ARMS = ("retrieval", "rag-en", "rag-th", "llm-only")
TECHNIQUE_LABELS = {"Technique", "Subtechnique"}

# Kept close to the upstream instruction so task framing is not a confounder;
# only the output contract is tightened, because free-form prose would make ID
# extraction the thing under test instead of the retrieval.
_EN_PROMPT = (
    "You are a cybersecurity expert specializing in the MITRE ATT&CK framework. "
    "Identify the MITRE ATT&CK techniques described in the threat description below. "
    "Use the retrieved ATT&CK reference material as your evidence.\n\n"
    "Rules:\n"
    "- List only techniques actually described in the threat description.\n"
    "- Order them most-confident first.\n"
    "- Output one per line as: T#### - Name  (or T####.### - Name)\n"
    "- No preamble, no explanation, no other text.\n\n"
    "=== Retrieved ATT&CK reference ===\n{context}\n\n"
    "=== Threat description ===\n{query}\n"
)

_TH_PROMPT = (
    "คุณเป็นผู้เชี่ยวชาญด้านความมั่นคงปลอดภัยไซเบอร์ที่เชี่ยวชาญกรอบงาน MITRE ATT&CK\n"
    "จงระบุเทคนิค MITRE ATT&CK ที่ปรากฏในคำอธิบายภัยคุกคามด้านล่าง "
    "โดยใช้ข้อมูลอ้างอิง ATT&CK ที่ค้นคืนมาเป็นหลักฐาน\n\n"
    "กติกา:\n"
    "- ระบุเฉพาะเทคนิคที่ปรากฏจริงในคำอธิบายภัยคุกคาม\n"
    "- เรียงจากที่มั่นใจมากที่สุดก่อน\n"
    "- ตอบบรรทัดละหนึ่งรายการในรูปแบบ: T#### - ชื่อเทคนิคภาษาไทย (T####.### ได้เช่นกัน)\n"
    "- ห้ามมีคำนำหรือคำอธิบายอื่นใด\n\n"
    "=== ข้อมูลอ้างอิง ATT&CK ที่ค้นคืนได้ ===\n{context}\n\n"
    "=== คำอธิบายภัยคุกคาม ===\n{query}\n"
)

_LLM_ONLY_PROMPT = (
    "You are a cybersecurity expert specializing in the MITRE ATT&CK framework. "
    "Identify the MITRE ATT&CK techniques described in the threat description below.\n\n"
    "Rules:\n"
    "- Order them most-confident first.\n"
    "- Output one per line as: T#### - Name  (or T####.### - Name)\n"
    "- No preamble, no explanation, no other text.\n\n"
    "=== Threat description ===\n{query}\n"
)

_PROMPTS = {"rag-en": _EN_PROMPT, "rag-th": _TH_PROMPT, "llm-only": _LLM_ONLY_PROMPT}


# ──────────────────────────────────────────────────────────────────────────────
# Data
# ──────────────────────────────────────────────────────────────────────────────
def load_dataset(name: str, vmap: VersionMap) -> tuple[list[dict], int]:
    """Load a split with gold reconciled to the current release.

    Returns (samples, n_unscoreable). A sample whose every gold label is retired
    with no successor cannot be scored either way, so it leaves the corpus and
    is counted in the run header rather than silently zeroing recall.
    """
    path = DATA_DIR / (name + "_zeroshot_test.json")
    if not path.exists():
        raise FileNotFoundError(
            str(path) + " missing - run:\n"
            "  python -m RAG.GraphRAG.evaluation.published.fetch_datasets"
        )
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict] = []
    unscoreable = 0
    for i, row in enumerate(rows):
        mapped, dropped = vmap.map_gold(row["gold"])
        if not mapped:
            unscoreable += 1
            continue
        out.append(
            {
                "id": name + "-" + str(i).zfill(5),
                "input": row["input"],
                "gold_original": row["gold"],
                "gold": mapped,
                "gold_dropped": dropped,
            }
        )
    return out, unscoreable


def run_path(dataset: str, arm: str, tag: str = "") -> Path:
    """Runs are keyed by dataset+arm, plus an optional tag for config variants.

    A tag keeps a top-K sweep or an --include-graph run from appending into (and
    silently corrupting) the baseline run file.
    """
    stem = dataset + "__" + arm + ("__" + tag if tag else "")
    return RUNS_DIR / (stem + ".jsonl")


def load_done(path: Path) -> dict[str, dict]:
    done: dict[str, dict] = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    done[row["id"]] = row
    return done


# ──────────────────────────────────────────────────────────────────────────────
# Prediction
# ──────────────────────────────────────────────────────────────────────────────
def retrieval_ids(result, include_graph: bool, vmap: VersionMap) -> list[str]:
    """Ranked ATT&CK IDs out of a GraphRAGResult.

    Vector hits carry the reranker ordering, which is what P@k and MRR are meant
    to score. Graph neighbours have no comparable score, so when included they
    are appended after the ranked block, never interleaved.
    """
    ids: list[str] = []

    def add(attack_id) -> None:
        if not attack_id:
            return
        current = vmap.map_id(attack_id) or attack_id
        if current not in ids:
            ids.append(current)

    for vr in result.vector_results:
        meta = vr.metadata or {}
        if meta.get("node_label") in TECHNIQUE_LABELS:
            add(meta.get("attack_id"))

    if include_graph:
        for sg in result.graph_results:
            for node in sg.neighbors:
                if getattr(node, "label", None) in TECHNIQUE_LABELS:
                    add(getattr(node, "attack_id", None))

    return ids


def _make_llm():
    from ...config import LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE
    from ...llm_provider import create_core_chat_model, resolve_core_llm_target

    target = resolve_core_llm_target(LLM_MODEL)
    print("[BENCH] LLM: " + target.model + " (" + target.provider + ")")
    return create_core_chat_model(
        anthropic_model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=min(LLM_MAX_TOKENS, 1024),  # the output is a short ID list
    )


def run_arm(
    dataset: str,
    arm: str,
    limit: int = 0,
    top_k: int = 10,
    include_graph: bool = False,
    context_chars: int = 6000,
    tag: str = "",
) -> None:
    vmap = VersionMap.load()
    samples, unscoreable = load_dataset(dataset, vmap)
    if limit:
        samples = samples[:limit]

    out_path = run_path(dataset, arm, tag)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    done = load_done(out_path)
    todo = [s for s in samples if s["id"] not in done]

    print("[BENCH] dataset=" + dataset + " arm=" + arm)
    print("[BENCH] samples=" + str(len(samples)) + " (dropped as unscoreable: " + str(unscoreable) + ")")
    print("[BENCH] already done=" + str(len(done)) + " todo=" + str(len(todo)))
    if not todo:
        print("[BENCH] nothing to do")
        return

    retriever = None
    llm = None
    if arm != "llm-only":
        from ...retrieval.hybrid_retriever import HybridRetriever

        retriever = HybridRetriever()
    if arm != "retrieval":
        llm = _make_llm()

    started = time.time()
    n_fail = 0
    try:
        with out_path.open("a", encoding="utf-8") as out:
            for n, sample in enumerate(todo, start=1):
                try:
                    context = ""
                    predicted: list[str] = []
                    raw = ""

                    if retriever is not None:
                        result = retriever.retrieve(
                            sample["input"], top_k=top_k, expand_graph=include_graph
                        )
                        predicted = retrieval_ids(result, include_graph, vmap)
                        context = result.get_context_text(max_length=context_chars)

                    if llm is not None:
                        prompt = _PROMPTS[arm].format(context=context, query=sample["input"])
                        response = llm.invoke(prompt)
                        raw = getattr(response, "content", "") or ""
                        if isinstance(raw, list):  # some providers return blocks
                            raw = "".join(
                                b.get("text", "") if isinstance(b, dict) else str(b) for b in raw
                            )
                        predicted = [
                            vmap.map_id(i) or i for i in extract_attack_ids(raw)
                        ]
                        # dedupe after mapping, keeping first-mention order
                        seen: list[str] = []
                        for i in predicted:
                            if i not in seen:
                                seen.append(i)
                        predicted = seen

                    out.write(
                        json.dumps(
                            {
                                "id": sample["id"],
                                "arm": arm,
                                "input": sample["input"],
                                "gold": sample["gold"],
                                "predicted": predicted,
                                "raw": raw[:4000],
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    out.flush()
                except Exception as exc:  # noqa: BLE001 - keep going, resume later
                    n_fail += 1
                    print("  " + sample["id"] + ": FAILED - " + str(exc))

                if n % 25 == 0 or n == len(todo):
                    rate = n / max(time.time() - started, 1e-6)
                    print(
                        "  " + str(n) + "/" + str(len(todo))
                        + "  " + format(rate, ".2f") + "/s"
                        + "  eta " + format((len(todo) - n) / max(rate, 1e-6) / 60, ".1f") + "m"
                        + ("  failures " + str(n_fail) if n_fail else "")
                    )
    finally:
        if retriever is not None:
            retriever.close()

    print("[BENCH] wrote " + str(out_path))


# ──────────────────────────────────────────────────────────────────────────────
# Scoring
# ──────────────────────────────────────────────────────────────────────────────
def score_all(valid_only: bool = True) -> str:
    vmap = VersionMap.load()
    valid_ids = vmap.live if valid_only else None

    lines: list[str] = ["# Published-Baseline Results", ""]
    lines.append(
        "Scored with the TechniqueRAG protocol (see `metrics.py`). Gold labels "
        "reconciled to ATT&CK v19 (see `attack_version_map.py`). All arms are "
        "zero-shot: compare against the published zero-shot / off-the-shelf-retriever "
        "rows, not the fine-tuned ones."
    )
    lines.append("")

    found = False
    for dataset in BENCHMARKS:
        rows_for_dataset = []
        for path in sorted(RUNS_DIR.glob(dataset + "__*.jsonl")):
            rows = list(load_done(path).values())
            if not rows:
                continue
            found = True
            label = path.stem[len(dataset) + 2 :]
            pairs = [(r["predicted"], r["gold"]) for r in rows]
            rows_for_dataset.append((label, pairs))

        if not rows_for_dataset:
            continue

        lines.append("## " + dataset)
        lines.append("")
        for mode in MODES:
            lines.append("### mode = " + mode)
            lines.append("")
            lines.append(MARKDOWN_HEADER)
            for arm, pairs in rows_for_dataset:
                score = score_corpus(pairs, mode=mode, valid_ids=valid_ids)
                lines.append(score.as_row(arm + " (n=" + str(score.n_samples) + ")"))
            lines.append("")
            lines.append("P@k / R@k:")
            lines.append("")
            lines.append("| Run | P@1 | R@1 | P@3 | R@3 |")
            lines.append("|-----|-----|-----|-----|-----|")
            for arm, pairs in rows_for_dataset:
                at1 = score_at_k(pairs, 1, mode=mode, valid_ids=valid_ids)
                at3 = score_at_k(pairs, 3, mode=mode, valid_ids=valid_ids)
                lines.append(
                    "| " + arm
                    + " | " + format(at1.precision, ".4f")
                    + " | " + format(at1.recall, ".4f")
                    + " | " + format(at3.precision, ".4f")
                    + " | " + format(at3.recall, ".4f")
                    + " |"
                )
            lines.append("")

    if not found:
        return "No runs found under " + str(RUNS_DIR)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run/score published-baseline benchmarks")
    parser.add_argument("--dataset", choices=BENCHMARKS, help="benchmark split to run")
    parser.add_argument("--arm", choices=ARMS, help="pipeline arm to run")
    parser.add_argument("--limit", type=int, default=0, help="cap samples (0 = all)")
    parser.add_argument("--top-k", type=int, default=10, help="vector top-K before rerank")
    parser.add_argument("--include-graph", action="store_true", help="append graph neighbours")
    parser.add_argument("--tag", default="", help="suffix for the run file, e.g. a top-K variant")
    parser.add_argument("--score", action="store_true", help="score existing runs and write RESULTS.md")
    parser.add_argument(
        "--no-validity-filter",
        action="store_true",
        help="keep predicted IDs that are not live ATT&CK (upstream drops them)",
    )
    args = parser.parse_args()

    if args.score:
        report = score_all(valid_only=not args.no_validity_filter)
        print(report)
        RESULTS_PATH.write_text(report + "\n", encoding="utf-8")
        print("\n[BENCH] written to " + str(RESULTS_PATH))
        return

    if not args.dataset or not args.arm:
        parser.error("--dataset and --arm are required unless --score is given")

    run_arm(
        dataset=args.dataset,
        arm=args.arm,
        limit=args.limit,
        top_k=args.top_k,
        include_graph=args.include_graph,
        tag=args.tag,
    )


if __name__ == "__main__":
    main()
