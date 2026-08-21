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
That mismatch is a caveat to state in the write-up, not a licence to benchmark
something other than the product. The headline arm is `agent`: the served
pipeline exactly as POST /query runs it. If the served path handles this input
shape badly, that is a finding to report, not a reason to swap in a different
pipeline.

The remaining arms are ablations of that one, each removing a stage so the
headline number can be explained rather than merely quoted. Nothing here may be
reported as "our pipeline scores X" except the agent arm.

One earlier assumption is worth recording because it was wrong. Decomposition
was skipped on the grounds that an 80-character input has nothing to split;
measurement refuted that. Input LENGTH is not the criterion, the number of
techniques packed into the sentence is. On single-label samples the decomposer
returns one sub-query (a no-op for structure, though it does rewrite the text,
which moves retrieval either way). On multi-label samples it splits along the
gold labels - "adds collected files to a temp.zip ... then base64 encodes it and
uploads it" becomes exactly the three sub-queries matching its three gold
techniques. TechniqueRAG decomposes too, folded into its re-ranker prompt
("break down the query into distinct attack steps"). The ablation arms expose it
as --decompose; the agent arm always does it, because production always does.

Arms
----
  agent       THE HEADLINE. The served pipeline exactly as POST /query runs it -
              router, decomposition, hybrid retrieval, sufficiency evaluation,
              BROADEN_SEARCH loop, generation. Every other arm below is an
              ablation of this one: they explain why the headline number is what
              it is, and none of them may be quoted as the system's score.
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .attack_version_map import BENCHMARKS, DATA_DIR, VersionMap
from .metrics import MARKDOWN_HEADER, MODES, extract_attack_ids, score_at_k, score_corpus

RUNS_DIR = DATA_DIR / "runs"
RESULTS_PATH = Path(__file__).resolve().parent / "RESULTS.md"

ARMS = ("agent", "retrieval", "rag-en", "rag-th", "llm-only")

# The served path. Everything else in ARMS is an ablation of it: useful for
# explaining why the headline number is what it is, never a substitute for it.
HEADLINE_ARM = "agent"
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


def candidate_context(result, vmap: VersionMap, max_chars: int = 9000) -> str:
    """Format every retrieved technique as a numbered candidate for the LLM.

    Deliberately NOT GraphRAGResult.get_context_text(): that caps its semantic
    section at FINAL_TOP_K (5), which would throw away three quarters of the
    candidate pool. The whole premise of this arm is that the retriever is a
    strong candidate generator (gold is somewhere in the top 20 for 83% of TRAM
    samples) and the LLM supplies the precision - so the LLM has to actually see
    all 20.
    """
    lines: list[str] = []
    seen: set[str] = set()
    for vr in result.vector_results:
        meta = vr.metadata or {}
        if meta.get("node_label") not in TECHNIQUE_LABELS:
            continue
        attack_id = meta.get("attack_id")
        if not attack_id:
            continue
        current = vmap.map_id(attack_id) or attack_id
        if current in seen:
            continue
        seen.add(current)
        name = meta.get("name", "")
        description = " ".join((vr.document or "").split())[:320]
        lines.append("[" + str(len(seen)) + "] " + current + " - " + name)
        if description:
            lines.append("    " + description)

    context = "\n".join(lines)
    if len(context) > max_chars:
        context = context[:max_chars] + "\n... [truncated]"
    return context


def model_slug(model: str) -> str:
    """Filename-safe short name for a model id, used to key the run file."""
    return model.split("/")[-1].replace(".", "-").replace(":", "-").lower()


def _make_llm(model: str = "", disable_thinking: bool = False):
    """Build the chat client, optionally overriding the configured model.

    An override goes through the same provider factory production uses, so the
    only thing that changes between model arms is the model id.

    ``disable_thinking`` matters for reasoning models. qwen/qwen3.5-9b thinks by
    default and, on this task, spends the entire token budget doing it: a plain
    call returns 4096 output tokens of which 3168 are thinking, stop_reason
    max_tokens, and NO text block at all - an empty prediction that costs
    $0.00103. With thinking disabled the same call answers in 31 tokens for
    $0.0000089, 115x cheaper.

    It is also the methodologically correct setting here. The row we compare
    against, Ministral 8B (RAG), is not a reasoning model, and unbounded
    thinking is extra inference compute that would both flatter our score and
    contradict the efficiency claim the comparison exists to support.
    """
    from ...config import LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE
    from ...llm_provider import create_core_chat_model, resolve_core_llm_target

    selected = model or LLM_MODEL
    target = resolve_core_llm_target(selected)
    print("[BENCH] LLM: " + target.model + " (" + target.provider + ")")
    if model and target.model != model:
        # resolve_openrouter_model silently falls back to the default for an
        # unknown name without a slash. Running the wrong model and labelling
        # the file with the requested one would quietly invalidate the whole run.
        raise SystemExit(
            "requested model '" + model + "' resolved to '" + target.model
            + "'. Pass the full vendor/model id."
        )
    llm = create_core_chat_model(
        anthropic_model=selected,
        temperature=LLM_TEMPERATURE,
        max_tokens=min(LLM_MAX_TOKENS, 1024),  # the output is a short ID list
    )
    if disable_thinking:
        print("[BENCH] thinking: disabled")
        llm = llm.bind(thinking={"type": "disabled"})
    return llm


def run_arm(
    dataset: str,
    arm: str,
    limit: int = 0,
    top_k: int = 10,
    include_graph: bool = False,
    context_chars: int = 9000,
    tag: str = "",
    technique_only: bool = False,
    concurrency: int = 8,
    decompose: bool = False,
    model: str = "",
    disable_thinking: bool = False,
) -> None:
    vmap = VersionMap.load()
    samples, unscoreable = load_dataset(dataset, vmap)
    if limit:
        samples = samples[:limit]

    # A model override becomes part of the run key: appending a second model
    # into one file would silently blend two systems into one score.
    file_tag = tag
    if model:
        file_tag = (tag + "__" if tag else "") + model_slug(model)
    if disable_thinking:
        # A thinking run and a non-thinking run of the same model are different
        # systems; keep their scores in different files.
        file_tag += "-nothink"
    out_path = run_path(dataset, arm, file_tag)
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
    decomposer = None
    agent = None

    if arm == "agent":
        # The served path, unmodified: router, decomposition, hybrid retrieval,
        # sufficiency evaluation and the BROADEN_SEARCH loop, exactly as
        # POST /query drives it. No knobs - the point of this arm is that there
        # are none.
        from ...pipeline.agent_graph import GraphRAGAgent

        agent = GraphRAGAgent()
        print("[BENCH] agent arm: full served pipeline, sequential")
    else:
        if arm != "llm-only":
            from ...retrieval.hybrid_retriever import HybridRetriever

            retriever = HybridRetriever()
            if decompose:
                from ...pipeline.query_decomposer import QueryDecomposer

                decomposer = QueryDecomposer()
                print("[BENCH] decomposition ON (one extra LLM call per sample)")
        if arm != "retrieval":
            llm = _make_llm(model, disable_thinking)

    labels = tuple(TECHNIQUE_LABELS) if technique_only else None

    def run_agent(sample: dict) -> tuple[list[str], str]:
        """One full served-pipeline call. Returns (predicted ids, answer text).

        IDs are read out of the finished answer rather than out of the retrieved
        context, because the answer is what the product actually hands back -
        anything the pipeline retrieved but declined to cite is, correctly, not
        a prediction.
        """
        response = agent.query(sample["input"], verbose=False)
        answer = response.answer or ""
        predicted: list[str] = []
        for attack_id in extract_attack_ids(answer):
            current = vmap.map_id(attack_id) or attack_id
            if current not in predicted:
                predicted.append(current)
        return predicted, answer

    def retrieve_one(sample: dict) -> tuple[list[str], str]:
        """Sequential half: embed, rerank, format. GPU-bound, so never threaded."""
        if retriever is None:
            return [], ""

        if decomposer is not None:
            # Multi-label samples pack several techniques into one short
            # sentence, and a single embedding of that sentence tends to land on
            # only one of them. Sub-queries get a per-query quota and are
            # round-robin interleaved, so every step keeps a seat in the list.
            sub_queries = decomposer.decompose(sample["input"], verbose=False)
            result = retriever.retrieve_multi_quota(
                sub_queries,
                per_query_k=max(top_k // max(len(sub_queries), 1), 3),
                top_k=top_k,
                max_vector=top_k,
                node_label_filter=labels,
            )
        else:
            result = retriever.retrieve(
                sample["input"],
                top_k=top_k,
                expand_graph=include_graph,
                node_label_filter=labels,
            )
        return (
            retrieval_ids(result, include_graph, vmap),
            candidate_context(result, vmap, max_chars=context_chars),
        )

    def generate_one(sample: dict, context: str) -> tuple[list[str], str]:
        """Concurrent half: one LLM round-trip, no shared state beyond the client."""
        prompt = _PROMPTS[arm].format(context=context, query=sample["input"])
        response = llm.invoke(prompt)
        raw = getattr(response, "content", "") or ""
        if isinstance(raw, list):  # some providers return content blocks
            raw = "".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in raw
            )
        predicted: list[str] = []
        for attack_id in extract_attack_ids(raw):
            current = vmap.map_id(attack_id) or attack_id
            if current not in predicted:
                predicted.append(current)
        return predicted, raw

    started = time.time()
    n_fail = 0
    n_done = 0

    def write(sample: dict, predicted: list[str], raw: str) -> None:
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

    try:
        with out_path.open("a", encoding="utf-8") as out:
            # Retrieval is sequential and LLM calls are I/O-bound, so the batch
            # is retrieved one by one and then generated all at once. Writes stay
            # on this thread, which keeps the resume file append-ordered and free
            # of interleaved partial lines.
            batch_size = max(concurrency, 1) if llm is not None else 1
            for start in range(0, len(todo), batch_size):
                batch = todo[start : start + batch_size]

                if agent is not None:
                    # The agent owns the GPU retriever and its own LLM calls, so
                    # it runs one sample at a time - threading it would only
                    # contend on the same models.
                    for sample in batch:
                        try:
                            ids, answer = run_agent(sample)
                            write(sample, ids, answer)
                            n_done += 1
                        except Exception as exc:  # noqa: BLE001 - resume later
                            n_fail += 1
                            print("  " + sample["id"] + ": AGENT FAILED - " + str(exc))
                    elapsed = max(time.time() - started, 1e-6)
                    seen = start + len(batch)
                    rate = seen / elapsed
                    print(
                        "  " + str(seen) + "/" + str(len(todo))
                        + "  " + format(rate, ".2f") + "/s"
                        + "  eta " + format((len(todo) - seen) / max(rate, 1e-6) / 60, ".1f") + "m"
                        + ("  failures " + str(n_fail) if n_fail else "")
                    )
                    continue

                retrieved: list[tuple[dict, list[str], str]] = []
                for sample in batch:
                    try:
                        ids, context = retrieve_one(sample)
                        retrieved.append((sample, ids, context))
                    except Exception as exc:  # noqa: BLE001 - resume later
                        n_fail += 1
                        print("  " + sample["id"] + ": RETRIEVE FAILED - " + str(exc))

                if llm is None:
                    for sample, ids, _ in retrieved:
                        write(sample, ids, "")
                        n_done += 1
                else:
                    with ThreadPoolExecutor(max_workers=batch_size) as pool:
                        futures = {
                            pool.submit(generate_one, sample, context): sample
                            for sample, _, context in retrieved
                        }
                        results: dict[str, tuple[list[str], str]] = {}
                        for future in as_completed(futures):
                            sample = futures[future]
                            try:
                                results[sample["id"]] = future.result()
                            except Exception as exc:  # noqa: BLE001 - resume later
                                n_fail += 1
                                print("  " + sample["id"] + ": LLM FAILED - " + str(exc))
                    # Write in batch order, not completion order, so a resumed
                    # run reads the same way a serial one would.
                    for sample, _, _ in retrieved:
                        if sample["id"] in results:
                            predicted, raw = results[sample["id"]]
                            write(sample, predicted, raw)
                            n_done += 1

                elapsed = max(time.time() - started, 1e-6)
                seen = start + len(batch)
                rate = seen / elapsed
                print(
                    "  " + str(seen) + "/" + str(len(todo))
                    + "  " + format(rate, ".2f") + "/s"
                    + "  eta " + format((len(todo) - seen) / max(rate, 1e-6) / 60, ".1f") + "m"
                    + ("  failures " + str(n_fail) if n_fail else "")
                )
    finally:
        if retriever is not None:
            retriever.close()
        if agent is not None:
            agent.close()

    print("[BENCH] wrote " + str(n_done) + " rows to " + str(out_path))
    if n_fail:
        print("[BENCH] " + str(n_fail) + " failed - rerun the same command to resume")


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
    parser.add_argument(
        "--disable-thinking",
        action="store_true",
        help=(
            "turn off extended thinking. Required for reasoning models such as "
            "qwen/qwen3.5-9b, which otherwise spend the whole token budget "
            "thinking and return no answer; also the fair setting against the "
            "non-reasoning Ministral 8B row"
        ),
    )
    parser.add_argument(
        "--model",
        default="",
        help=(
            "override the configured LLM with a full vendor/model id, e.g. "
            "qwen/qwen3.5-9b. The model becomes part of the run filename so two "
            "models can never be appended into the same score"
        ),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help=(
            "how many LLM calls to keep in flight. Retrieval stays sequential "
            "(GPU-bound); only the API round-trip is overlapped. Ignored by the "
            "retrieval arm"
        ),
    )
    parser.add_argument(
        "--decompose",
        action="store_true",
        help=(
            "split each input into atomic sub-queries before retrieving, then "
            "round-robin the per-sub-query results. Costs one extra LLM call per "
            "sample. Expect little on single-label splits and a lot on "
            "multi-label ones - TechniqueRAG does the same thing inside its "
            "re-ranker prompt"
        ),
    )
    parser.add_argument(
        "--technique-only",
        action="store_true",
        help=(
            "restrict vector search to Technique/Subtechnique nodes. On this task the "
            "reranker otherwise spends its top slots on the Group/Software pages the "
            "procedure text was lifted from, which is closer to how the published "
            "retrieval baselines search (their corpus is technique summaries only)"
        ),
    )
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
        technique_only=args.technique_only,
        concurrency=args.concurrency,
        decompose=args.decompose,
        model=args.model,
        disable_thinking=args.disable_thinking,
    )


if __name__ == "__main__":
    main()
