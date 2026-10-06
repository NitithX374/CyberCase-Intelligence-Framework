"""
MITRE table re-read — the served pipeline, end to end
=====================================================
Every real-CTI incident goes through ``routers.rag._run_pipeline``, the function
``POST /query`` hands to its worker thread: the agent graph, then the re-read of
the case file, then the table. Nothing is replayed and nothing is stubbed. The
one addition is a recorder around the re-read, which notes what it returned and
how long it took and passes the result on unchanged.

The answer-grounded table is built from the same run — the same retrieval and
the same answer — so the two tables differ in the re-read and in nothing else.

Scores are parent-level technique F1, the granularity of the gold labels and
the scoring ``agentic_ablation.score_answer`` applies to answers.

Two phases:
- ``run``   — resumable, one JSONL row per finished incident
- ``score`` — reads the rows, writes ``results/table_reread_e2e_<tag>.md``

Usage (from rag_service/app; the model is whatever CORE_LLM_OPENROUTER_MODEL says):
    python -m RAG.GraphRAG.evaluation.table_reread_e2e --tag gemma --phase run
    python -m RAG.GraphRAG.evaluation.table_reread_e2e --tag gemma --phase score
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .attack_id_metrics import extract_technique_ids, technique_set_score
from .mitre_threshold_calibration import REAL_CTI_PATH

RESULTS = Path(__file__).resolve().parent / "results"
_TECHNIQUE_ID = re.compile(r"^T\d{4}(?:\.\d{3})?$")
_lock = threading.Lock()


def rows_path(tag: str) -> Path:
    return RESULTS / f"table_reread_e2e_{tag}.jsonl"


def split_of(sample_id: str) -> str:
    """dev 55 / test 45, the split the table stage was designed and held out on."""
    return "dev" if int(hashlib.sha1(sample_id.encode()).hexdigest(), 16) % 5 < 3 else "test"


def load_rows(tag: str) -> dict[str, dict]:
    path = rows_path(tag)
    if not path.exists():
        return {}
    rows = (json.loads(line) for line in open(path, encoding="utf-8") if line.strip())
    return {row["id"]: row for row in rows}


# ══════════════════════════════════════════════════════════════════════════════
# Run
# ══════════════════════════════════════════════════════════════════════════════


class _Recorder:
    """Stands where the agent's re-read stands and passes every call through."""

    def __init__(self, reread) -> None:
        self._reread = reread
        self.seen: dict[str, dict] = {}

    def select(self, case_file: str, answer: str, trace=None):
        started = time.perf_counter()
        selection = self._reread.select(case_file, answer, trace)
        with _lock:
            self.seen[case_file] = {
                "seconds": round(time.perf_counter() - started, 2),
                "kept": None if selection is None else [e.attack_id for e in selection.kept],
            }
        return selection


def _row_dicts(table) -> list[dict]:
    return [
        {"technique_id": r.technique_id, "entity_type": r.entity_type, "source": r.source,
         "relevance": r.relevance, "score": r.score}
        for r in table
    ]


def run(tag: str, workers: int, max_samples: int | None) -> None:
    from routers.rag import _run_pipeline

    from ..config import CORE_LLM_EFFECTIVE_MODEL
    from ..pipeline.agent_graph import GraphRAGAgent
    from ..pipeline.mitre_table import _collect_candidates, build_mitre_table

    samples = json.loads(REAL_CTI_PATH.read_text(encoding="utf-8"))["samples"][:max_samples]
    done = load_rows(tag)
    todo = [s for s in samples if s["id"] not in done]
    print(f"[E2E] {len(todo)} of {len(samples)} incidents to run, model "
          f"{CORE_LLM_EFFECTIVE_MODEL}", file=sys.stderr, flush=True)
    if not todo:
        return

    agent = GraphRAGAgent()
    if agent.table_reread is None:
        raise SystemExit("the re-read is off (MITRE_TABLE_REREAD) or no model is configured")
    recorder = agent.table_reread = _Recorder(agent.table_reread)

    def one(sample: dict) -> dict:
        started = time.perf_counter()
        response, table = _run_pipeline(agent, sample["query"])
        seconds = round(time.perf_counter() - started, 2)
        result = response.graphrag_result
        retrieved = sorted(
            {c["technique_id"].upper() for c in _collect_candidates(result).values()
             if c["technique_id"]} if result is not None else set()
        )
        return {
            "id": sample["id"],
            "model": CORE_LLM_EFFECTIVE_MODEL,
            "seconds": seconds,
            "answer": response.answer,
            "reread": recorder.seen.get(sample["query"]),
            "table": _row_dicts(table),
            "answer_grounded": _row_dicts(build_mitre_table(result, response.answer)),
            "retrieved_ids": retrieved,
        }

    finished = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(one, s): s["id"] for s in todo}
        for future in as_completed(futures):
            try:
                row = future.result()
                with _lock, open(rows_path(tag), "a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                finished += 1
                print(f"[E2E] {finished + failed}/{len(todo)} {row['id']} {row['seconds']}s",
                      file=sys.stderr, flush=True)
            except Exception as exc:  # noqa: BLE001 — one incident must not end the run
                failed += 1
                print(f"[E2E] FAILED {futures[future]}: {type(exc).__name__}: {exc}",
                      file=sys.stderr, flush=True)
    agent.close()
    print(f"[E2E] {finished} written, {failed} failed", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# Score
# ══════════════════════════════════════════════════════════════════════════════


def _parents(ids) -> set[str]:
    return {i.upper().split(".")[0] for i in ids if _TECHNIQUE_ID.match((i or "").upper())}


def _table_parents(rows: list[dict]) -> set[str]:
    return _parents(r["technique_id"] for r in rows)


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def _interval(xs: list[float], seed: int = 11, n_boot: int = 10000) -> tuple[float, float]:
    rng = random.Random(seed)
    means = sorted(_mean(rng.choice(xs) for _ in xs) for _ in range(n_boot))
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot)]


def _paired(a: list[float], b: list[float]) -> dict:
    diffs = [x - y for x, y in zip(a, b)]
    lo, hi = _interval(diffs, seed=7)
    return {
        "mean": _mean(diffs), "lo": lo, "hi": hi,
        "wtl": (sum(d > 1e-12 for d in diffs), sum(abs(d) <= 1e-12 for d in diffs),
                sum(d < -1e-12 for d in diffs)),
    }


ARMS = {
    "answer (the IDs it cites)": lambda row: _parents(extract_technique_ids(row["answer"])),
    "answer-grounded table": lambda row: _table_parents(row["answer_grounded"]),
    "table as served (re-read)": lambda row: _table_parents(row["table"]),
}
BASELINE = "answer-grounded table"


def score(tag: str) -> str:
    gold = {s["id"]: {g.upper().split(".")[0] for g in s["gold_attack_ids"]}
            for s in json.loads(REAL_CTI_PATH.read_text(encoding="utf-8"))["samples"]}
    rows = load_rows(tag)
    if not rows:
        raise SystemExit(f"no rows in {rows_path(tag)}")
    model = next(iter(rows.values()))["model"]

    out = [
        "# MITRE table re-read — the served pipeline on the real-CTI incidents",
        "",
        f"Model `{model}`. Each incident ran once through `routers.rag._run_pipeline` "
        "(agent graph, re-read, table). The answer-grounded table is built from the same "
        "retrieval and the same answer. Parent-level technique F1; intervals are 95% "
        "bootstrap over incidents, differences are paired.",
        "",
    ]
    for split in ("test", "dev", "all"):
        chosen = [r for r in rows.values() if split in ("all", split_of(r["id"]))]
        scores = {name: [technique_set_score(pick(r), gold[r["id"]]) for r in chosen]
                  for name, pick in ARMS.items()}
        base = [s["f1"] for s in scores[BASELINE]]
        out += [f"## {split} — {len(chosen)} incidents", "",
                "| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
        for name, pick in ARMS.items():
            f1 = [s["f1"] for s in scores[name]]
            lo, hi = _interval(f1)
            d = _paired(f1, base)
            delta = "—" if name == BASELINE else f"{d['mean']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]"
            wtl = "—" if name == BASELINE else "/".join(map(str, d["wtl"]))
            out.append(
                f"| {name} | {_mean(s['precision'] for s in scores[name]):.3f} "
                f"| {_mean(s['recall'] for s in scores[name]):.3f} "
                f"| {_mean(f1):.3f} [{lo:.3f}, {hi:.3f}] | {delta} | {wtl} "
                f"| {_mean(len(pick(r)) for r in chosen):.2f} |")
        out.append("")

    every = list(rows.values())
    decided = [r for r in every if r["reread"] and r["reread"]["kept"] is not None]
    added = [len(_table_parents(r["table"]) - _parents(r["retrieved_ids"])) for r in decided]
    reread_s = sorted(r["reread"]["seconds"] for r in every if r["reread"])
    total_s = sorted(r["seconds"] for r in every)
    out += [
        "## What the re-read did",
        "",
        f"- Decided the technique rows on {len(decided)} of {len(every)} incidents; the "
        f"other {len(every) - len(decided)} kept the answer-grounded table.",
        f"- Rows for a technique retrieval had not returned: {sum(added)} "
        f"({_mean(added):.2f} an incident, on {sum(a > 0 for a in added)} incidents).",
        f"- Time in the re-read: median {reread_s[len(reread_s) // 2]:.1f} s, "
        f"90th percentile {reread_s[int(len(reread_s) * 0.9)]:.1f} s. Whole request: median "
        f"{total_s[len(total_s) // 2]:.1f} s. Incidents ran several at a time on one "
        "machine, so these are not what one request alone takes.",
        "",
    ]
    report = "\n".join(out)
    (RESULTS / f"table_reread_e2e_{tag}.md").write_text(report, encoding="utf-8", newline="\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--tag", required=True)
    parser.add_argument("--phase", choices=["run", "score"], required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-samples", type=int, default=None)
    args = parser.parse_args()
    if args.phase == "run":
        run(args.tag, args.workers, args.max_samples)
    else:
        print(score(args.tag))


if __name__ == "__main__":
    main()
