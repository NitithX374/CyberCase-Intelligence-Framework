"""
LegalRAG evaluation harness
===========================
Runs the retriever over a labelled set of incidents and scores it with the
multi-label metrics in `metrics.py`.

Retrieval is scored on its own, without the model. The generator can only
choose among sections retrieval already found, so a section missing from the
candidate list is unreachable no matter how good the model is — and retrieval
costs nothing to run, which means this can be run on every change instead of
once a month.

What the numbers do and do not mean is worth stating plainly, because the gold
labels are the weak part. They were written by reading the narratives, not by
a lawyer, and they were deliberately not derived from the ATT&CK ids attached
to each case: deriving them that way would test the technique-to-statute
mapping against itself. A score here says how well retrieval matches one
developer's reading of four incidents. It does not say the suggestions are
legally correct, and `--gaps` prints the reasons why not.

Usage:
    cd rag_service/app/RAG
    python -m LegalRAG.evaluation.run_eval
    python -m LegalRAG.evaluation.run_eval --k 5,10,20 --rerank
    python -m LegalRAG.evaluation.run_eval --with-mitre     # feed the ATT&CK ids
    python -m LegalRAG.evaluation.run_eval --per-case
    python -m LegalRAG.evaluation.run_eval --gaps
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

from ..decomposer import LegalDecomposer, merge_results
from ..llm_reranker import LlmReranker
from ..retriever import LegalRetriever
from .metrics import HEADER, CaseScore, score_case, summarise

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:  # pragma: no cover - Windows console fallback
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GOLD_PATH = Path(__file__).resolve().parent / "data" / "legal_gold.json"


def load_gold(path: Path = GOLD_PATH) -> dict:
    if not path.exists():
        raise SystemExit(f"ไม่พบชุดทดสอบ {path}")
    return json.loads(path.read_text(encoding="utf-8"))


ATTACK_NAMES = json.loads(
    (Path(__file__).resolve().parent / "data" / "attack_names.json").read_text(encoding="utf-8")
)


def _mitre_rows(case: dict) -> list[dict]:
    """The ATT&CK rows as the router would hand them over.

    `--with-mitre` cannot show what it was built to show on this dataset. The
    narratives were generated from ATT&CK chains and carry the technique names
    in English already — "ผู้โจมตีได้ใช้ Modify Registry เพื่อ…" — so appending
    them supplies nothing the query did not have. A real case file says
    "แก้ไขค่าใน registry" and never names a technique, which is the gap the
    MITRE table exists to close. Read this switch as untestable here, not as
    evidence against the design.
    """
    rows = []
    for tid in case.get("attack_ids", []):
        rows.append(
            {"technique_id": tid, "name": ATTACK_NAMES.get(tid, ""), "description": ""}
        )
    return rows


def run(
    ks: list[int],
    rerank: bool,
    with_mitre: bool,
    gold_data: dict,
    depth: int = 50,
    llm_rerank: bool = False,
    decompose: str = "",
) -> tuple[dict[int, list[CaseScore]], float]:
    """Retrieve once to a fixed depth, then score every cut-off against it.

    The depth is deliberately independent of the cut-offs. Tying it to max(ks)
    made "never retrieved" mean "not inside the deepest cut-off", so the same
    case reported a different number of missing sections depending on which ks
    were asked for — a property of the harness, not of the retriever.
    """
    retriever = LegalRetriever()
    # Costs money and takes ~15 s per case, so it is opt-in. Candidates are
    # capped separately: reranking cannot rescue a section retrieval never
    # returned, which is the whole story of inc_auto_015.
    reranker = LlmReranker() if llm_rerank else None
    decomposer = LegalDecomposer(style=decompose) if decompose else None
    llm_cost = 0.0
    depth = max(depth, max(ks))
    per_k: dict[int, list[CaseScore]] = {k: [] for k in ks}
    started = time.perf_counter()

    for case in gold_data["cases"]:
        common = dict(
            mitre_table=_mitre_rows(case) if with_mitre else None,
            rerank=rerank,
            chargeable_only=True,
            with_cited_context=False,
        )
        if decomposer is not None:
            clauses, degraded = decomposer.decompose(case["narrative"])
            llm_cost += decomposer.last_usage.get("cost", 0.0) or 0.0
            if degraded:
                print(f"[LEGAL] {case['case_id']}: {degraded}")
            # Each act gets its own quota, then the lists are interleaved. One
            # act cannot crowd out the others, which is the point of splitting.
            per_clause = [
                list(retriever.query(clause, top_k=max(depth // len(clauses), 5), **common).hits)
                for clause in clauses
            ]
            hits = merge_results(per_clause, depth)
        else:
            hits = list(retriever.query(case["narrative"], top_k=depth, **common).hits)
        if reranker is not None:
            reordered, degraded = reranker.rerank(case["narrative"], hits[:20])
            # Printed, not swallowed. A rerank that quietly falls back to the
            # dense order produces exactly the baseline numbers and looks like
            # a result — which is how two model-specific failures went unnoticed.
            if degraded:
                print(f"[LEGAL] {case['case_id']}: {degraded}")
            # Sections the model rejected keep their dense order behind the
            # ones it accepted, so nothing is lost from the measurement.
            kept = {h.citation for h in reordered}
            hits = reordered + [h for h in hits if h.citation not in kept]
            llm_cost += reranker.last_usage.get("cost", 0.0) or 0.0
        ranked = [hit.citation for hit in hits]
        gold = list(case["gold"].keys())
        for k in ks:
            per_k[k].append(score_case(case["case_id"], gold, ranked, k))

    if reranker is not None or decomposer is not None:
        print(f"[LEGAL] ค่าใช้จ่าย LLM rerank รวม ${llm_cost:.5f}")
    return per_k, time.perf_counter() - started


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate LegalRAG retrieval")
    ap.add_argument("--k", default="5,10,20", help="Cut-offs, comma separated")
    ap.add_argument("--rerank", action="store_true", help="Cross-encoder rerank (slow, local)")
    ap.add_argument("--llm-rerank", action="store_true", help="LLM rerank on elements (paid)")
    ap.add_argument("--decompose", default="", choices=["", "conduct", "legal"],
                    help="Split the narrative into acts before retrieving (paid)")
    ap.add_argument("--with-mitre", action="store_true", help="Enrich the query with ATT&CK ids")
    ap.add_argument("--depth", type=int, default=50, help="How deep to retrieve before scoring")
    ap.add_argument("--per-case", action="store_true", help="Show every case")
    ap.add_argument("--gaps", action="store_true", help="Print what this dataset cannot tell you")
    args = ap.parse_args()

    gold_data = load_gold()

    if args.gaps:
        print("ข้อจำกัดของชุดทดสอบนี้")
        print("=" * 70)
        print(f"  ตรวจโดยนักกฎหมาย: {gold_data.get('reviewed_by') or 'ยังไม่ได้ตรวจ'}")
        print(f"  {gold_data['review_note']}")
        print()
        for gap in gold_data.get("known_gaps", []):
            print(f"  - {gap}")
        return

    ks = sorted({int(x) for x in args.k.split(",") if x.strip()})
    per_k, elapsed = run(
        ks, args.rerank, args.with_mitre, gold_data, depth=args.depth,
        llm_rerank=args.llm_rerank, decompose=args.decompose,
    )

    setting = [f"ดึงลึก {args.depth}"]
    setting.append("rerank" if args.rerank else "ไม่ rerank")
    setting.append("มี MITRE" if args.with_mitre else "ไม่มี MITRE")
    if args.decompose:
        setting.append(f"decompose={args.decompose}")
    if args.llm_rerank:
        setting.append("LLM rerank")
    print(f"เคส {len(gold_data['cases'])} | {' | '.join(setting)} | {elapsed:.1f}s")
    print("=" * 70)
    print(HEADER)
    print("-" * 70)
    for k in ks:
        print(summarise(per_k[k], k).as_row())
    print("=" * 70)

    if args.per_case:
        smallest = ks[0]
        print(f"\nรายเคส (k={smallest})")
        for score in per_k[smallest]:
            status = "ครบ" if score.multi_hit else f"{len(score.gold) - len(score.missed) if False else ''}ไม่ครบ"
            print(f"\n  {score.case_id}  recall={score.recall:.2f}  {status}")
            for citation in score.gold:
                if citation in score.retrieved:
                    mark = f"อันดับ {score.retrieved.index(citation) + 1}"
                elif citation in score.missed:
                    mark = "ไม่เจอเลย"
                else:
                    mark = f"ต่ำกว่า k={smallest}"
                print(f"      {citation:<44} {mark}")

    unreviewed = gold_data.get("reviewed_by") is None
    if unreviewed:
        print(
            "\n⚠ ป้ายกำกับยังไม่ผ่านนักกฎหมาย — ตัวเลขนี้วัดความตรงกับการตีความของผู้พัฒนา"
            "\n  ดูข้อจำกัดทั้งหมดด้วย --gaps"
        )


if __name__ == "__main__":
    main()
