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

Three phases:
- ``run``      — resumable, one JSONL row per finished incident
- ``score``    — reads the rows, writes ``results/table_reread_e2e_<tag>.md``
- ``evidence`` — how often a row's evidence is the part of the case file the
  dataset ties that technique to, writes ``results/table_evidence_<tag>.md``.
  Every gold step carries its ``cue``, an exact span of the case file.

Usage (from rag_service/app; the model is whatever CORE_LLM_OPENROUTER_MODEL says):
    python -m RAG.GraphRAG.evaluation.table_reread_e2e --tag gemma --phase run
    python -m RAG.GraphRAG.evaluation.table_reread_e2e --tag gemma --phase score
    python -m RAG.GraphRAG.evaluation.table_reread_e2e --tag gemma --phase evidence
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
        trace = {} if trace is None else trace
        selection = self._reread.select(case_file, answer, trace)
        with _lock:
            self.seen[case_file] = {
                "seconds": round(time.perf_counter() - started, 2),
                "kept": None if selection is None else [e.attack_id for e in selection.kept],
                "quotes": trace.get("quotes") or {},
                "spans": trace.get("spans") or {},
            }
        return selection


def _row_dicts(table) -> list[dict]:
    return [
        {"technique_id": r.technique_id, "entity_type": r.entity_type, "source": r.source,
         "relevance": r.relevance, "score": r.score,
         "evidence": [[s.start, s.end, s.basis] for s in getattr(r, "evidence", None) or []]}
        for r in table
    ]


def run(tag: str, workers: int, max_samples: int | None, stride: int = 1) -> None:
    from routers.rag import _run_pipeline

    from ..config import CORE_LLM_EFFECTIVE_MODEL
    from ..pipeline.agent_graph import GraphRAGAgent
    from ..pipeline.case_evidence import locate_query
    from ..pipeline.mitre_table import _collect_candidates, build_mitre_table

    samples = json.loads(REAL_CTI_PATH.read_text(encoding="utf-8"))["samples"]
    samples = samples[::stride][:max_samples]
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
            # every query that returned something, and where its own words
            # are in the case file (null: nowhere)
            "sub_queries": [
                {"query": q, "located": locate_query(q, sample["query"])}
                for q in dict.fromkeys(
                    q for queries in (getattr(result, "retrieved_by", None) or {}).values() for q in queries
                )
                if q != sample["query"]
            ],
            # parent technique or STIX ID → the sub-queries that returned it
            "retrieved_by": dict(getattr(result, "retrieved_by", None) or {}),
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


# ══════════════════════════════════════════════════════════════════════════════
# Evidence
# ══════════════════════════════════════════════════════════════════════════════

# A row's evidence is right when it lies on the dataset's cue for that
# technique: the two share at least half of the shorter one.
_MIN_SHARED = 0.5


def _on_a_cue(span: tuple[int, int], cues: list[tuple[int, int]]) -> bool:
    for start, end in cues:
        shared = min(span[1], end) - max(span[0], start)
        if shared >= _MIN_SHARED * min(span[1] - span[0], end - start):
            return True
    return False


def score_evidence(tag: str) -> str:
    samples = {s["id"]: s for s in json.loads(REAL_CTI_PATH.read_text(encoding="utf-8"))["samples"]}
    rows = load_rows(tag)
    if not rows:
        raise SystemExit(f"no rows in {rows_path(tag)}")

    # One judgement per parent technique in a table: a sub-technique row
    # carries its parent's evidence.
    counted = {"technique rows": 0, "in the gold labels": 0}
    all_right = {"reread": 0, "retrieval": 0}  # every span of the basis is on a cue
    judged_alone = sum("retrieved_by" in row for row in rows.values())
    bases = ("reread", "retrieval", "either")
    has = {b: 0 for b in bases}
    has_gold = {b: 0 for b in bases}
    right = {b: 0 for b in bases}
    as_listed = {"has": 0, "any": 0, "all": 0}
    for row in rows.values():
        sample = samples[row["id"]]
        cues: dict[str, list[tuple[int, int]]] = {}
        for step in sample["attack_steps"]:
            at = sample["query"].find(step["cue"])
            for gold in step["gold_attack_ids"]:
                cues.setdefault(gold.upper().split(".")[0], []).append((at, at + len(step["cue"])))
        for r in row["table"]:
            tid = (r["technique_id"] or "").upper()
            if not _TECHNIQUE_ID.match(tid) or "." in tid:
                continue
            counted["technique rows"] += 1
            spans = {b: [(s, e) for s, e, basis in r.get("evidence") or [] if b in (basis, "either")]
                     for b in bases}
            # A row drops a retrieval span the re-read already gave. Judged on
            # its own, retrieval is every located source of every sub-query
            # that returned the technique.
            located = {q["query"]: tuple(q["located"]) for q in row.get("sub_queries") or [] if q["located"]}
            if "retrieved_by" in row:
                spans["retrieval"] = [located[q] for q in row["retrieved_by"].get(tid, []) if q in located]
            for b in bases:
                has[b] += bool(spans[b])
            if tid not in cues:
                continue
            counted["in the gold labels"] += 1
            for b in bases:
                has_gold[b] += bool(spans[b])
                right[b] += any(_on_a_cue(s, cues[tid]) for s in spans[b])
            for b in all_right:
                all_right[b] += bool(spans[b]) and all(_on_a_cue(s, cues[tid]) for s in spans[b])
            # What the row lists: the re-read's spans, or retrieval's when
            # the re-read has none. (Rows written before that rule listed
            # both; they are read by it here.)
            listed = spans["reread"] or [(s, e) for s, e, _ in r.get("evidence") or []]
            as_listed["has"] += bool(listed)
            as_listed["any"] += any(_on_a_cue(s, cues[tid]) for s in listed)
            as_listed["all"] += bool(listed) and all(_on_a_cue(s, cues[tid]) for s in listed)

    subs = [s for row in rows.values() for s in row.get("sub_queries") or []]
    quotes = [q for row in rows.values() if row["reread"] for qs in row["reread"]["quotes"].values() for q in qs]
    found = sum(len(v) > 0 for row in rows.values() if row["reread"] for v in row["reread"]["spans"].values())
    kept = sum(len(row["reread"]["spans"]) for row in rows.values() if row["reread"])

    def share(n: int, d: int) -> str:
        return f"{n} of {d} ({n / d:.0%})" if d else "0 of 0"

    n_rows, n_gold = counted["technique rows"], counted["in the gold labels"]
    out = [
        "# Case evidence on the MITRE table — the served pipeline on the real-CTI incidents",
        "",
        f"{len(rows)} incidents, model `{next(iter(rows.values()))['model']}`. A technique row's evidence is "
        "judged against the dataset's own cue for that technique: the exact part of the case file "
        "the source's label was written for. Only rows whose technique is in the gold labels can be "
        "judged; a row is right when one of its spans shares at least half of the shorter of span "
        "and cue.",
        "",
        "| evidence | technique rows that have it | of the gold rows, have it | of those, on the cue |",
        "| --- | --- | --- | --- |",
    ]
    names = {"reread": "from the re-read", "retrieval": "from retrieval", "either": "either"}
    for b in bases:
        out.append(f"| {names[b]} | {share(has[b], n_rows)} | {share(has_gold[b], n_gold)} "
                   f"| {share(right[b], has_gold[b])} |")
    out += [
        "",
        f"- Every span of the row is on a cue: re-read {share(all_right['reread'], has_gold['reread'])}, "
        f"retrieval {share(all_right['retrieval'], has_gold['retrieval'])}.",
        f"- Retrieval is judged on all the sub-queries that returned the technique for {judged_alone} of "
        f"{len(rows)} incidents; for the others only the spans the re-read had not already given were kept.",
        f"- As a row lists it (the re-read's spans, retrieval's only without them): "
        f"{share(as_listed['has'], n_gold)} gold rows have evidence, {share(as_listed['any'], as_listed['has'])} "
        f"include the cue's sentence, {share(as_listed['all'], as_listed['has'])} list nothing else.",
        f"- Sub-queries found in the case file by their own words: "
        f"{share(sum(bool(s['located']) for s in subs), len(subs))}.",
        f"- Re-read: {len(quotes)} sentences copied for {kept} kept techniques; "
        f"{share(found, kept)} kept techniques ended with at least one place in the case file.",
        "",
    ]
    report = "\n".join(out)
    (RESULTS / f"table_evidence_{tag}.md").write_text(report, encoding="utf-8", newline="\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--tag", required=True)
    parser.add_argument("--phase", choices=["run", "score", "evidence"], required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--stride", type=int, default=1, help="take every Nth incident")
    args = parser.parse_args()
    if args.phase == "run":
        run(args.tag, args.workers, args.max_samples, args.stride)
    elif args.phase == "score":
        print(score(args.tag))
    else:
        print(score_evidence(args.tag))


if __name__ == "__main__":
    main()
